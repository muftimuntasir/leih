
from openerp import api
from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class cash_collection(osv.osv):
    _name = "cash.collection"



    @api.onchange('type')
    def _onchange_tpe(self):
        child_list=[]




        # mr_obj = self.pool.get("leih.money.receipt").search(self.cr, self.uid, [('date','>=',self.date)])
        if self.type=='bill':
            mr_obj=self.env['leih.money.receipt'].search(
            [('bill_id', '!=', False)])
            for record in mr_obj:
                abc = {}
                abc['bill_admission_opd_id']=record.bill_id.name
                abc['mr_no']=record.name
                abc['amount']=record.amount
                child_list.append([0, False, abc])
        if self.type=='admission':
            mr_obj=self.env['leih.money.receipt'].search(
            [('admission_id', '!=', False)])
            for record in mr_obj:
                abc = {}
                abc['bill_admission_opd_id']=record.admission_id.name
                abc['mr_no']=record.name
                abc['amount']=record.amount
                child_list.append([0, False, abc])


        self.cash_collection_lines = child_list

    def action_button_confirm(self, cr, uid, ids, context=None):
        contex = context
        cc_ids=ids
        for id in cc_ids:
            ids =[id]
            cc_obj = self.browse(cr, uid,ids , context=context)
            if cc_obj.state == 'approve':
                raise osv.except_osv(_('Already Confirmed'), _('Sorry, it is already confirmed'))
            else:
                ## start create journal from here

                if context is None: context = {}
                if context.get('period_id', False):
                    return context.get('period_id')
                periods = self.pool.get('account.period').find(cr, uid, context=context)
                period_id= periods and periods[0] or False

                if context is None:
                    context = {}

                line_ids = []

                line_ids.append((0, 0, {
                    'name': 'mufti Muntasir Ahmed',
                    'account_id': 237,
                    'debit': cc_obj.total,
                }))

                line_ids.append((0, 0, {
                    'name': 'mufti Muntasir Ahmed',
                    'account_id': 2742,
                    'credit': cc_obj.total,
                }))

                j_vals = {'name': '/',
                          'journal_id': 7,
                          'date': fields.date.today(),
                          'period_id': period_id,
                          'ref': 'mufti',
                          'line_id': line_ids

                          }

                jv_entry = self.pool.get('account.move')
                saved_jv_id = jv_entry.create(cr, uid, j_vals, context=context)
                if saved_jv_id > 0:
                    journal_id = saved_jv_id
                jv_entry.button_validate(cr, uid, [saved_jv_id], context)

                ## Ends here


                ## Confirm the Cash Colletion And flaggin the MR's

                confirm_cash_collection_query = "UPDATE cash_collection SET state='approve',journal_id={0} WHERE id={1}".format(saved_jv_id, id)
                cr.execute(confirm_cash_collection_query)
                cr.commit()


                ## Flagging



                for line_items in cc_obj.cash_collection_lines:
                    mr_id = line_items.mr_no.id
                    cr.execute( "UPDATE leih_money_receipt SET already_collected=True WHERE id={0}".format(mr_id))
                    cr.commit()


                ## Ends here Cash collection and Flagging




        return True


    _columns = {

        'date': fields.date("Date"),
        'type': fields.selection([('bill','Bill'),('opd','OPD'),('admission','Admission')], 'Type'),
        'total': fields.float("Total"),
        'journal_id':fields.many2one('account.move', 'Journal '),
        'cash_collection_lines': fields.one2many("cash.collection.line","cash_collection_line_id",'cash collection', required=True),
         'state': fields.selection([
           ('pending', 'Pending'),
           ('approve', 'Confirmed'),
            ('cancel', 'Cancelled')], 'State', default = 'pending', readonly = True),

    }

    _defaults = {
        'state': 'pending',

    }



class cash_collection_line(osv.osv):
    _name="cash.collection.line"

    _columns = {
        'cash_collection_line_id':fields.many2one("cash.collection","Cash Collection"),
        'mr_no':fields.many2one("leih.money.receipt","Mr No."),
        'bill_admission_opd_id':fields.char("Bill/Admission/OPD Number"),
        'amount':fields.float("Amount")
    }