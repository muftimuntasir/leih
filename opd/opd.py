# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time, datetime
from openerp import api
from openerp import SUPERUSER_ID


class opd_ticket(osv.osv):
    _name = "opd.ticket"
    _order = 'id desc'




    def _totalpayable(self, cr, uid, ids, field_name, arg, context=None):
        Percentance_calculation = {}
        sum = 0
        for items in self.pool.get("opd.ticket").browse(cr,uid,ids,context=None):
            total_list=[]
            for amount in items.opd_ticket_line_id:
                total_list.append(amount.total_amount)

            for item in total_list:
                sum=item+sum
                for record in self.browse(cr, uid, ids, context=context):
                    Percentance_calculation[record.id] = sum
                    # import pdb
                    # pdb.set_trace()
        return Percentance_calculation


    _columns = {

        # 'patient_id': fields.char("Patient ID"),
        'name':fields.char("Name"),
        'mobile': fields.char(string="Mobile",store=False),
        'patient_id': fields.char(related='patient_name.patient_id',string="Patient Id",readonly=True),
        'patient_name': fields.many2one('patient.info', "Patient Name"),
        'address': fields.char("Address",store=False),
        'age': fields.char("Age",store=False),
        'sex':fields.char("Sex",store=False),
        'already_collected':fields.boolean("Money Collected",default=False),
        # 'date':fields.datetime("Date", readonly=True,default=lambda self: fields.datetime.now()),
        'date':fields.date("Date", readonly=True,default=lambda self: fields.datetime.now()),
        'ref_doctors': fields.many2one('doctors.profile','Reffered by'),
        'opd_ticket_line_id': fields.one2many('opd.ticket.line', 'opd_ticket_id', 'Investigations',required=True),
        'user_id': fields.many2one('res.users', 'Assigned to', select=True, track_visibility='onchange'),
        'state': fields.selection(
            [('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')],
            'Status', default='confirmed', readonly=True),
        'total': fields.float(string="Total"),
        'with_doctor_total': fields.float(string="with_doctor_total"),
    }
    _defaults = {
        'user_id': lambda obj, cr, uid, context: uid,
        # 'opd_ticket_line_id':[[0, False, {'department': 'Medicine', 'price': 100, 'name': 1, 'total_amount': 100}]],
    }

    def opd_cancel(self, cr, uid, ids, context=None):
        cr.execute("select id as jounral_id from account_move where ref = (select name from opd_ticket where id=%s limit 1)",(ids))
        joural_ids = cr.fetchall()
        context = context

        itm = [itm[0] for itm in joural_ids]
        if len(itm) > 0:
            uid = 1
            moves = self.pool.get('account.move').browse(cr, uid, itm, context=context)
            moves.button_cancel()  ## Cancelling
            moves.unlink()  ### Deleting Journal

        #### Ends Here

        ## Bill Status Will Change

        cr.execute("update opd_ticket set state='cancelled' where id=%s", (ids))
        cr.commit()
        return "C"


    def onchange_total(self,cr,uid,ids,name,context=None):
        tests = {'values': {}}
        dep_object = self.pool.get('leih.tests').browse(cr, uid, name, context=None)
        abc = {'total': dep_object.rate}
        tests['value'] = abc
        # import pdb
        # pdb.set_trace()
        return tests

    def onchange_patient(self,cr,uid,ids,name,context=None):
        tests={}
        dep_object = self.pool.get('patient.info').browse(cr, uid, name, context=None)
        # import pdb;pdb.set_trace()
        abc={'mobile':dep_object.mobile,'address':dep_object.address,'age':dep_object.age,'sex':dep_object.sex}
        tests['value']=abc
        return tests





    def create(self, cr, uid, vals, context=None):
        context = context or {}

        # Use a savepoint so any failure rolls back cleanly
        try:
            cr.execute("SAVEPOINT opd_ticket_create_sp")

            # 1) Create OPD ticket first
            ticket_id = super(opd_ticket, self).create(cr, uid, vals, context=context)

            # 2) Generate OPD name and write it (NO commit)
            name_text = 'OPD-0%s' % ticket_id
            super(opd_ticket, self).write(cr, SUPERUSER_ID, [ticket_id], {'name': name_text}, context=context)

            ticket = self.browse(cr, uid, ticket_id, context=context)

            # Basic sanity
            if not ticket:
                raise osv.except_osv(_('Error'), _('OPD ticket could not be loaded after creation.'))

            if not ticket.total:
                # optional: allow zero? if not, error
                # raise osv.except_osv(_('Error'), _('OPD total is zero. Cannot create journal entry.'))
                pass

            # 3) Prepare journal lines
            line_ids = []

            periods = self.pool.get('account.period').find(cr, uid, context=context)
            period_id = periods and periods[0] or False
            has_been_paid = ticket.total or 0.0

            # Debit cash
            line_ids.append((0, 0, {
                'name': ticket.name,
                'account_id': 6,          # Cash account id
                'debit': has_been_paid,
                'credit': 0.0,
                'partner_id': False,
                'analytic_account_id': False,
                'tax_code_id': False,
                'tax_amount': 0.0,
                'currency_id': False,
                'date_maturity': False,
                'amount_currency': 0.0,
            }))

            # Credit income lines
            for l in ticket.opd_ticket_line_id:
                if not (l.name and l.name.accounts_id and l.name.accounts_id.id):
                    raise osv.except_osv(
                        _('Configuration Error'),
                        _('Income account not set for item "%s". Please set accounts_id on opd.ticket.entry.')
                        % (l.name and l.name.name or 'Unknown')
                    )

                line_ids.append((0, 0, {
                    'name': l.name.name or ticket.name,
                    'account_id': l.name.accounts_id.id,
                    'debit': 0.0,
                    'credit': float(l.total_amount or 0.0),
                    'partner_id': False,
                    'analytic_account_id': False,
                    'tax_code_id': False,
                    'tax_amount': 0.0,
                    'currency_id': False,
                    'date_maturity': False,
                    'amount_currency': 0.0,
                }))

            if len(line_ids) < 2:
                raise osv.except_osv(
                    _('Error'),
                    _('No OPD lines found. Cannot create journal entry.')
                )

            # 4) Create account.move
            move_obj = self.pool.get('account.move')
            move_vals = {
                'name': '/',
                'journal_id': 2,          # Sales journal
                'date': ticket.date,
                'period_id': period_id,
                'ref': ticket.name,
                'line_id': line_ids,
            }

            move_id = move_obj.create(cr, uid, move_vals, context=context)

            # 5) Validate / post move
            try:
                move_obj.button_validate(cr, uid, [move_id], context=context)
            except Exception as e:
                # If validate fails, delete move and raise
                try:
                    move_obj.unlink(cr, uid, [move_id], context=context)
                except:
                    pass
                raise osv.except_osv(
                    _('Journal Error'),
                    _('Journal entry could not be validated/posted.\n\nDetails: %s') % (unicode(e) if 'unicode' in globals() else str(e))
                )

            # 6) All good — release savepoint (optional)
            cr.execute("RELEASE SAVEPOINT opd_ticket_create_sp")
            return ticket_id

        except Exception:
            # Rollback everything related to this create (ticket + journal)
            try:
                cr.execute("ROLLBACK TO SAVEPOINT opd_ticket_create_sp")
            except:
                pass
            # Re-raise so Odoo shows the error and does NOT create OPD
            raise





    @api.onchange('opd_ticket_line_id')
    def onchange_total(self):
        total=0
        with_doctor_total=0
        for item in self.opd_ticket_line_id:
            total=total+item.total_amount
            with_doctor_total=with_doctor_total+item.name.total_cash
        self.total=total
        self.with_doctor_total=with_doctor_total
        return 'O'



    def write(self, cr, uid, ids,vals,context=None):
        if vals.get('opd_ticket_line_id') or uid == 1:
            cr.execute("select id as journal_ids from account_move where ref = (select name from opd_ticket where id=%s limit 1)",(ids))
            journal_ids = cr.fetchall()
            context=context
            updated = super(opd_ticket, self).write(cr, uid, ids, vals, context=context)
            itm = [itm[0] for itm in journal_ids]
            if len(itm)>0:
                uid=1
                moves =self.pool.get('account.move').browse(cr, uid, itm, context=context)
                xx=moves.button_cancel()
                # import pdb;pdb.set_trace()
                ## Cancelling
                moves.unlink()

                stored_obj = self.browse(cr, uid, [ids[0]], context=context)
                if stored_obj:

                    line_ids = []

                    if context is None: context = {}
                    if context.get('period_id', False):
                        return context.get('period_id')
                    periods = self.pool.get('account.period').find(cr, uid, context=context)
                    period_id = periods and periods[0] or False
                    has_been_paid = stored_obj.total

                    line_ids.append((0, 0, {
                        'analytic_account_id': False,
                        'tax_code_id': False,
                        'tax_amount': 0,
                        'name': stored_obj.name,
                        'currency_id': False,
                        'credit': 0,
                        'date_maturity': False,
                        'account_id': 6,  ### Cash ID
                        'debit': has_been_paid,
                        'amount_currency': 0,
                        'partner_id': False,
                    }))

                    for cc_obj in stored_obj.opd_ticket_line_id:
                        # import pdb
                        # pdb.set_trace()
                        total = 0

                        if cc_obj.name.name:
                            # ledger_id = 611
                            # try:
                            #     ledger_id = cc_obj.name.accounts_id.id
                            # except:
                            #     ledger_id = 611  ## Diagnostic Income Head , If we don't assign any Ledger

                            if context is None:
                                context = {}

                            line_ids.append((0, 0, {
                                'analytic_account_id': False,
                                'tax_code_id': False,
                                'tax_amount': 0,
                                'name': cc_obj.name.name,
                                'currency_id': False,
                                'account_id': cc_obj.name.accounts_id.id,
                                'credit': cc_obj.total_amount,
                                'date_maturity': False,
                                'debit': 0,
                                'amount_currency': 0,
                                'partner_id': False,
                            }))
                        # import pdb
                        # pdb.set_trace()

                    jv_entry = self.pool.get('account.move')

                    j_vals = {'name': '/',
                              'journal_id': 2,  ## Sales Journal
                              'date': stored_obj.date,
                              'period_id': period_id,
                              'ref': stored_obj.name,
                              'line_id': line_ids

                              }

                    # import pdb
                    # pdb.set_trace()

                    saved_jv_id = jv_entry.create(cr, uid, j_vals, context=context)
                    if saved_jv_id > 0:
                        journal_id = saved_jv_id
                        try:

                            jv_entry.button_validate(cr, uid, [saved_jv_id], context)
                        except:
                            import pdb
                            pdb.set_trace()
                    return updated
                    ### Ends the journal Entry Here
            else:
                updated = super(opd_ticket, self).write(cr, uid, ids, vals, context=context)
                # raise osv.except_osv(_('Warning!'),
                #                      _("You cannot Edit the bill"))
                return updated







class test_information(osv.osv):
    _name = 'opd.ticket.line'

    _columns = {

        'name': fields.many2one("opd.ticket.entry","Item Name", ondelete='cascade'),
        'opd_ticket_id': fields.many2one('opd.ticket', "Information"),
        'price': fields.integer("Price"),
        'department':fields.char('Department'),
        'total_amount': fields.integer("Total Amount")

    }



    # @api.onchange('total_amount')
    # def change_item_price(self):
    #     opd_ticket_line_id=list()
    #     opd_ticket_line_id.append({
    #         'total':500
    #     })
    #
    #     ticket_id=self.opd_ticket_id
    #     return "Nothing"


    def onchange_item(self,cr,uid,ids,name,context=None):
        tests = {'values': {}}
        dep_object = self.pool.get('opd.ticket.entry').browse(cr, uid, name, context=None)
        abc = {'price': dep_object.fee,'department':dep_object.department.name,'total_amount':dep_object.fee}
        tests['value'] = abc
        # import pdb
        # pdb.set_trace()
        return tests



