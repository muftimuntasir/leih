from openerp import api
from openerp.exceptions import ValidationError
from openerp.osv import fields, osv
from openerp import SUPERUSER_ID, api
from openerp.tools.translate import _
from datetime import date, time, timedelta, datetime
from openerp.tools.amount_to_text_en import amount_to_text


class bill_register(osv.osv):
    _name = "bill.register"
    _order = 'id desc'

    # pdf=PDF()

    # pdf.lines()
    # pdf.titles()

    def _totalpayable(self, cr, uid, ids, field_name, arg, context=None):
        Percentance_calculation = {}
        sum = 0
        for items in self.pool.get("bill.register").browse(cr, uid, ids, context=None):
            total_list = []
            for amount in items.bill_register_line_id:
                total_list.append(amount.total_amount)

            for item in total_list:
                sum = item + sum

                for record in self.browse(cr, uid, ids, context=context):
                    Percentance_calculation[record.id] = sum

        return Percentance_calculation

    def _delivery_dates(self, cr, uid, ids, field_name, arg, context=None):
        delivery_date = {}
        test_delivery_date = []
        max_day = 0
        for items in self.pool.get("bill.register").browse(cr, uid, ids, context=None):
            total_list = []
            for amount in items.bill_register_line_id:
                for test in amount.name:
                    test_delivery_date.append(test.required_time)

        if len(test_delivery_date):
            max_day = max(test_delivery_date)
        #
        # import pdb
        # pdb.set_trace()

        # for item in total_list:
        #     sum=item+sum
        for record in self.browse(cr, uid, ids, context=context):
            delivery_date[record.id] = date.today() + timedelta(days=max_day)

        # import pdb
        # pdb.set_trace()
        return delivery_date

    def _default_payment_type(self):
        return self.env['payment.type'].search([('name', '=', 'Cash')], limit=1).id

    _columns = {

        # 'patient_id': fields.char("Patient ID"),
        'name': fields.char("Name"),
        'mobile': fields.char(string="Mobile", store=False),
        'patient_id': fields.char(related='patient_name.patient_id', string="Patient Id", readonly=True),
        'patient_name': fields.many2one('patient.info', "Patient Name", required=True),
        'address': fields.char("Address", store=False),
        'age': fields.char("Age", store=False),
        'sex': fields.char("Sex", store=False),
        'diagonostic_bill': fields.boolean("Diagonstic Bill"),
        'ref_doctors': fields.many2one('doctors.profile', 'Referred by'),
        'referral': fields.many2one('brokers.info', 'Referral'),
        'bill_register_line_id': fields.one2many('bill.register.line', 'bill_register_id', 'Item Entry', required=True),
        'bill_register_payment_line_id': fields.one2many("bill.register.payment.line", "bill_register_payment_line_id",
                                                         "Bill Register Payment"),
        'bill_journal_relation_id': fields.one2many("bill.journal.relation", "bill_journal_relation_id", "Journal"),
        # 'footer_connection': fields.one2many('leih.footer', 'relation', 'Parameters', required=True),
        # 'relation': fields.many2one("leih.investigation"),
        # 'total': fields.float(_totalpayable,string="Total",type='float',store=True),
        'total_without_discount': fields.float(string="Total without discount"),
        'total': fields.float(string="Total"),
        'doctors_discounts': fields.float("Doctor Discount(%)"),
        'after_discount': fields.float("Discount Amount"),
        'other_discount': fields.float("Other Discount"),
        'grand_total': fields.float("Grand Total"),
        'paid': fields.float(string="Paid", required=True),
        'type': fields.selection([('cash', 'Cash'), ('bank', 'Bank')], 'Payment Type'),
        'card_no': fields.char('Card No.'),
        'bank_name': fields.char('Bank Name'),
        'due': fields.float("Due"),
        'date': fields.datetime("Date", readonly=True, default=lambda self: fields.datetime.now()),
        'user_id': fields.many2one('res.users', 'Assigned to', select=True, track_visibility='onchange'),
        'state': fields.selection(
            [('pending', 'Pending'), ('confirmed', 'Confirmed'),('released', 'Released'),('cancelled', 'Cancelled')],
            'Status', default='pending', readonly=True),
        'old_journal': fields.boolean("Old Journal"),
        # new attributes for payment type
        'payment_type': fields.many2one("payment.type", "Payment Type", default=_default_payment_type),
        'service_charge': fields.float("Service Charge"),
        'to_be_paid': fields.float("To be Paid"),
        'account_number': fields.char("Account Number"),
        'discount_remarks': fields.char("Discount Remarks")

    }
    _defaults = {
        'diagonostic_bill': False,
        'user_id': lambda obj, cr, uid, context: uid,
    }

    
    def _assert_bill_integrity(self, cr, uid, bill, journal_id, mr_id, context=None):
        """Hard validation: if anything is missing -> raise -> rollback."""
        if not journal_id:
            raise osv.except_osv(_('Error!'), _('Journal entry was not created.'))

        mv = self.pool.get('account.move').browse(cr, uid, journal_id, context=context)
        if not mv:
            raise osv.except_osv(_('Error!'), _('Journal entry record is missing.'))
        if mv.state != 'posted':
            raise osv.except_osv(_('Error!'), _('Journal entry is not posted.'))

        # relation must exist
        cr.execute("""
            SELECT COUNT(*)
            FROM bill_journal_relation
            WHERE journal_id=%s AND bill_journal_relation_id=%s
        """, (journal_id, bill.id))
        if cr.fetchone()[0] == 0:
            raise osv.except_osv(_('Error!'), _('bill.journal.relation is missing for this bill.'))

        # If paid > 0 then MR + payment line must exist
        if bill.paid and bill.paid > 0:
            if not mr_id:
                raise osv.except_osv(_('Error!'), _('Money receipt was not created though Paid > 0.'))

            mr = self.pool.get('leih.money.receipt').browse(cr, uid, mr_id, context=context)
            if not mr:
                raise osv.except_osv(_('Error!'), _('Money receipt record is missing.'))

            cr.execute("""
                SELECT COUNT(*)
                FROM bill_register_payment_line
                WHERE bill_register_payment_line_id=%s AND money_receipt_id=%s
            """, (bill.id, mr_id))
            if cr.fetchone()[0] == 0:
                raise osv.except_osv(_('Error!'), _('Bill payment line is missing for this money receipt.'))

        return True


    @api.onchange("payment_type")
    def onchnage_payment_type(self):
        if self.payment_type.active == True:
            interest = self.payment_type.service_charge
            if interest > 0:
                service_charge = (self.paid * interest) / 100
                self.service_charge = service_charge
                self.to_be_paid = self.paid + service_charge
            else:
                self.to_be_paid = self.paid
                self.service_charge = 0
        return "X"

    @api.multi
    def amount_to_text(self, amount, currency='Bdt'):
        text = amount_to_text(amount, currency)
        new_text = text.replace("euro", "Taka")
        # initializing sub string
        sub_str = "Taka"
        final_text = new_text[:new_text.index(sub_str) + len(sub_str)]

        # final_text = new_text.replace("Cent", "Paisa")
        return final_text

    @api.multi
    def advance_paid(self, name):
        bill_obj = self.env['bill.register'].search([('name', '=', name)])
        if bill_obj.state != 'confirmed':
            raise osv.except_osv(_('Warning!'),
                                 _('Confirm your bill first.'))
        elif bill_obj.state == 'confirmed':
            mr = self.env['leih.money.receipt'].search([('bill_id', '=', name)])
            advance = 0
            paid = 0
            if len(mr) > 2:
                for i in range(len(mr) - 1):
                    advance = advance + mr[i].amount
                paid = mr[len(mr) - 1].amount
                # mr_ids=self.pool.get('leih.money.receipt').search([('bill_id', '=', name)], context=context)

                lists = {
                    'advance': advance,
                    'paid': paid
                }
            elif len(mr) == 2:
                advance = advance + mr[0].amount
                paid = paid + mr[1].amount
                lists = {
                    'advance': advance,
                    'paid': paid
                }
            elif len(mr) == 1:
                advance = advance + mr[0].amount
                lists = {
                    'advance': advance,
                    'paid': 0
                }
            elif len(mr) < 1:
                lists = {
                    'advance': 0,
                    'paid': 0
                }

        # final_text = new_text.replace("Cent", "Paisa")
        return lists

    # if same item exist in line
    # @api.multi
    # @api.constrains('bill_register_line_id')
    # def _check_exist_item_in_line(self):
    #     for item in self:
    #         exist_item_list = []
    #         for line in item.bill_register_line_id:
    #             if line.name.id in exist_item_list:
    #                 raise ValidationError(_('Item should be one per line.'))
    #             exist_item_list.append(line.name.id)

    def bill_confirm(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        if not ids:
            return True

        stored_obj = self.browse(cr, uid, ids[0], context=context)
        journal_object = self.pool.get("bill.journal.relation")
        diagonostic_bill = stored_obj.diagonostic_bill

        if stored_obj.state == 'confirmed':
            raise osv.except_osv(_('Warning!'), _('Already this Bill is Confirmed.'))

        # Minimum payment rule (your code had ">=0", so it always passes)
        grand_total = stored_obj.grand_total
        paid_amount = stored_obj.paid
        percent_amount = (paid_amount * 100.0 / grand_total) if grand_total else 0.0

        if not (percent_amount >= 0 or grand_total == 0):
            raise osv.except_osv(_('Warning!'), _('PLease Pay minimum amount.'))

        try:
            cr.execute("SAVEPOINT bill_register_confirm")

            stored = int(ids[0])

            # ---------- LAB/SAMPLE creation (NO COMMIT) ----------
            get_all_tested_ids = [x.name.id for x in stored_obj.bill_register_line_id]

            already_merged = []
            for items in stored_obj.bill_register_line_id:
                sample_id = False
                custom_name = ''
                state = 'sample'
                if items.name.sample_req is False or items.name.sample_req is None:
                    state = 'lab'

                if items.name.manual != True or items.name.lab_not_required != True:
                    custom_name = custom_name + ' ' + str(items.name.name)

                    if items.name.id not in already_merged:
                        child_list = []
                        value = {
                            'bill_register_id': stored,
                            'test_id': int(items.name.id),
                            'department_id': items.name.department.name,
                            'state': state
                        }

                        for test_item in items.name.examination_entry_line:
                            child_list.append([0, False, {
                                'test_name': test_item.name,
                                'ref_value': test_item.reference_value,
                                'bold': test_item.bold,
                                'group_by': test_item.group_by
                            }])

                        if items.name.merge is True:
                            for entry in items.name.merge_ids:
                                test_id = entry.examinationentry_id.id
                                if test_id in get_all_tested_ids:
                                    custom_name = custom_name + ', ' + str(entry.examinationentry_id.name)
                                    already_merged.append(test_id)
                                    for m_test_line in entry.examinationentry_id.examination_entry_line:
                                        child_list.append([0, False, {
                                            'test_name': m_test_line.name,
                                            'ref_value': m_test_line.reference_value,
                                            'bold': m_test_line.bold,
                                            'group_by': m_test_line.group_by
                                        }])

                        value['sticker_line_id'] = child_list
                        value['full_name'] = custom_name

                        sample_obj = self.pool.get('diagnosis.sticker')
                        sample_id = sample_obj.create(cr, uid, value, context=context)

                    if sample_id:
                        sample_text = 'Lab-0' + str(sample_id)
                        cr.execute('UPDATE diagnosis_sticker SET name=%s WHERE id=%s', (sample_text, sample_id))

            # ---------- JOURNAL (NO COMMIT) ----------
            line_ids = []
            periods = self.pool.get('account.period').find(cr, uid, context=context)
            period_id = periods and periods[0] or False

            has_been_paid = 0.0
            ar_amount = 0.0
            account_id = 6

            if stored_obj.payment_type:
                has_been_paid = stored_obj.paid
                ar_amount = stored_obj.due
                account_id = stored_obj.payment_type.account.id

            if ar_amount > 0:
                line_ids.append((0, 0, {
                    'analytic_account_id': False,
                    'tax_code_id': False,
                    'tax_amount': 0,
                    'name': stored_obj.name,
                    'currency_id': False,
                    'credit': 0,
                    'date_maturity': False,
                    'account_id': 195,
                    'debit': ar_amount,
                    'amount_currency': 0,
                    'partner_id': False,
                }))

            if has_been_paid > 0:
                line_ids.append((0, 0, {
                    'analytic_account_id': False,
                    'tax_code_id': False,
                    'tax_amount': 0,
                    'name': stored_obj.name,
                    'currency_id': False,
                    'credit': 0,
                    'date_maturity': False,
                    'account_id': account_id,
                    'debit': has_been_paid,
                    'amount_currency': 0,
                    'partner_id': False,
                }))

            for cc_obj in stored_obj.bill_register_line_id:
                ledger_id = 611
                try:
                    ledger_id = cc_obj.name.accounts_id.id
                except:
                    ledger_id = 611

                line_ids.append((0, 0, {
                    'analytic_account_id': False,
                    'tax_code_id': False,
                    'tax_amount': 0,
                    'name': cc_obj.name.name,
                    'currency_id': False,
                    'account_id': ledger_id,
                    'credit': cc_obj.total_amount,
                    'date_maturity': False,
                    'debit': 0,
                    'amount_currency': 0,
                    'partner_id': False,
                }))

            if stored_obj.service_charge > 0:
                line_ids.append((0, 0, {
                    'analytic_account_id': False,
                    'tax_code_id': False,
                    'tax_amount': 0,
                    'name': stored_obj.payment_type.name,
                    'currency_id': False,
                    'credit': stored_obj.service_charge,
                    'date_maturity': False,
                    'account_id': stored_obj.payment_type.service_charge_account.id,
                    'debit': 0,
                    'amount_currency': 0,
                    'partner_id': False,
                }))

            jv_entry = self.pool.get('account.move')
            j_vals = {
                'name': '/',
                'journal_id': 2,
                'date': stored_obj.date,
                'period_id': period_id,
                'ref': stored_obj.name,
                'line_id': line_ids
            }

            saved_jv_id = jv_entry.create(cr, uid, j_vals, context=context)
            if not saved_jv_id:
                raise osv.except_osv(_('Error!'), _('Failed to create journal entry.'))

            jv_entry.button_validate(cr, uid, [saved_jv_id], context=context)

            # confirm state (NO COMMIT)
            cr.execute("UPDATE bill_register SET state='confirmed' WHERE id=%s", (ids[0],))

            # relation (NO COMMIT)
            journal_object.create(cr, uid, vals={
                'journal_id': saved_jv_id,
                'bill_journal_relation_id': stored_obj.id
            }, context=context)

            # ---------- MR + payment line (NO COMMIT) ----------
            mr_id = False
            if stored_obj.paid and stored_obj.paid > 0:
                mr_value = {
                    'date': stored_obj.date,
                    'bill_id': stored,                 # your MR uses integer bill_id
                    'amount': stored_obj.paid,
                    'type': stored_obj.type,
                    'p_type': 'advance',
                    'bill_total_amount': stored_obj.total,
                    'due_amount': stored_obj.due
                }
                mr_obj = self.pool.get('leih.money.receipt')
                mr_id = mr_obj.create(cr, uid, mr_value, context=context)
                if not mr_id:
                    raise osv.except_osv(_('Error!'), _('Money Receipt creation failed.'))

                mr_name = 'MR#' + str(mr_id)
                cr.execute(
                    'UPDATE leih_money_receipt SET name=%s, diagonostic_bill=%s WHERE id=%s',
                    (mr_name, diagonostic_bill, mr_id)
                )

                bill_payment_obj = self.pool.get('bill.register.payment.line')
                bill_payment_id = bill_payment_obj.create(cr, uid, vals={
                    'date': stored_obj.date,
                    'amount': paid_amount,
                    'type': stored_obj.payment_type.name,
                    'bill_register_payment_line_id': stored,
                    'money_receipt_id': mr_id
                }, context=context)
                if not bill_payment_id:
                    raise osv.except_osv(_('Error!'), _('Bill payment line creation failed.'))

            # ---------- STRICT CHECK ----------
            # reread bill because state updated via SQL
            bill_now = self.browse(cr, uid, ids[0], context=context)
            self._assert_bill_integrity(cr, uid, bill_now, journal_id=saved_jv_id, mr_id=mr_id, context=context)

            cr.execute("RELEASE SAVEPOINT bill_register_confirm")

        except Exception as e:
            try:
                cr.execute("ROLLBACK TO SAVEPOINT bill_register_confirm")
            except:
                pass
            raise osv.except_osv(_('Error!'), _('Bill confirm failed and rolled back: %s') % (str(e),))

        return self.pool['report'].get_action(cr, uid, ids, 'leih.report_bill_register', context=context)

    def onchange_total(self, cr, uid, ids, name, context=None):
        tests = {'values': {}}
        dep_object = self.pool.get('leih.tests').browse(cr, uid, name, context=None)
        abc = {'total': dep_object.rate}
        tests['value'] = abc
        return tests


    def onchange_patient(self, cr, uid, ids, name, context=None): 
        tests = {}
        dep_object = self.pool.get('patient.info').browse(cr, uid, name, context=None)
        abc = {'mobile': dep_object.mobile, 'address': dep_object.address, 'age': dep_object.age, 'sex': dep_object.sex}
        tests['value'] = abc
        return tests

    # def onchange_patient(self, cr, uid, ids, name, context=None):
    #     res = {'value': {}}
    #     dep = self.pool.get('patient.info').browse(cr, uid, name, context=context)

    #     # Calculate age dynamically from DOB
    #     age = 0
    #     if dep.date_of_birth:
    #         from datetime import datetime, date
    #         dob = datetime.strptime(dep.date_of_birth, "%Y-%m-%d").date()
    #         today = date.today()
    #         age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    #     res['value'] = {
    #         'mobile': dep.mobile,
    #         'address': dep.address,
    #         'age': age, 
    #         'sex': dep.sex,
    #     }
    #     return res


    def add_new_test(self, cr, uid, ids, context=None):
        if not ids: return []

        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'leih', 'add_bill_view')
        #
        inv = self.browse(cr, uid, ids[0], context=context)
        # import pdb
        # pdb.set_trace()
        return {
            'name': _("Pay Invoice"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'add.bill',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'bill_id': ids[0],
                'default_price': 500,
                # 'default_name':context.get('name', False),
                'default_total_amount': 200,
            }
        }
        raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))

    def button_dummy(self, cr, uid, ids, context=None):

        return True

    def bill_cancel(self, cr, uid, ids, context=None):
        """
        One-transaction cancel:
        - Cancel & delete related account moves (by ref=bill.name)
        - Delete related bill.journal.relation rows
        - Mark bill_register state cancelled
        - Cancel diagnosis_sticker
        - Cancel leih_money_receipt
        If any step fails -> rollback and show error.
        """
        if context is None:
            context = {}
        if not ids:
            return True

        try:
            cr.execute("SAVEPOINT bill_register_cancel")

            bill_id = ids[0]

            # Get bill name safely (used as account_move.ref)
            bill = self.browse(cr, uid, bill_id, context=context)
            if not bill:
                raise osv.except_osv(_('Error!'), _('Bill not found.'))

            # Find all moves linked by ref=bill.name
            cr.execute("""
                SELECT id
                FROM account_move
                WHERE ref=%s
            """, (bill.name,))
            move_ids = [r[0] for r in cr.fetchall()]

            if move_ids:
                # Cancel then delete bill.journal.relation for those moves
                cr.execute("""
                    DELETE FROM bill_journal_relation
                    WHERE journal_id IN %s
                """, (tuple(move_ids),))

                # Cancel & unlink moves (use SUPERUSER like your original code)
                suid = 1
                move_obj = self.pool.get('account.move')
                moves = move_obj.browse(cr, suid, move_ids, context=context)

                # Cancel posted moves
                for mv in moves:
                    if mv.state == 'posted':
                        mv.button_cancel()

                # Delete move lines first to avoid FK issues, then delete moves
                cr.execute("DELETE FROM account_move_line WHERE move_id IN %s", (tuple(move_ids),))
                move_obj.unlink(cr, suid, move_ids, context=context)

            # Mark bill cancelled (NO COMMIT)
            cr.execute("UPDATE bill_register SET state='cancelled' WHERE id=%s", (bill_id,))

            # Cancel lab stickers (NO COMMIT)
            cr.execute("UPDATE diagnosis_sticker SET state='cancel' WHERE bill_register_id=%s", (bill_id,))

            # Cancel receipts (NO COMMIT)
            # Your receipt model uses bill_id field (you used search [('bill_id','=',name)] elsewhere),
            # but here you used id in SQL. Keeping consistent with cancel-by-bill-id.
            cr.execute("UPDATE leih_money_receipt SET state='cancel' WHERE bill_id=%s", (bill_id,))

            cr.execute("RELEASE SAVEPOINT bill_register_cancel")
            return True

        except Exception as e:
            try:
                cr.execute("ROLLBACK TO SAVEPOINT bill_register_cancel")
            except:
                pass
            raise osv.except_osv(_('Error!'), _('Bill cancel failed and rolled back: %s') % (str(e),))


    def btn_pay_bill(self, cr, uid, ids, context=None):
        if not ids: return []
        inv = self.browse(cr, uid, ids[0], context=context)
        if inv.state == 'pending':
            raise osv.except_osv(_('Warning'), _('Please Confirm and Print the Bill'))
        if inv.total <= inv.paid:
            raise osv.except_osv(_('Full Paid'), _('Nothing to Pay Here. Already Full Paid'))

        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'leih',
                                                                             'bill_register_payment_form_view')
        #

        # total=inv.total
        # import pdb
        # pdb.set_trace()
        return {
            'name': _("Pay Invoice"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'bill.register.payment',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'default_bill_id': ids[0],
                'default_amount': inv.due
            }
        }
        raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))

    def add_discount(self, cr, uid, ids, context=None):
        # import pdb
        # pdb.set_trace()
        if not ids: return []

        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'leih', 'discount_view')
        #
        inv = self.browse(cr, uid, ids[0], context=context)
        # import pdb
        # pdb.set_trace()
        return {
            'name': _("Pay Invoice"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'discount',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'pi_id': ids[0]
            }
        }
        raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))

    def create(self, cr, uid, vals, context=None):
        if vals.get("due"):
            if vals.get("due") < 0:
                raise osv.except_osv(_('Warning!'),
                                     _("Check paid and grand total!"))

        if context is None:
            context = {}

        child_ids = ["MRI", 'X-Ray', 'Radiology & Imaging', 'Pathology', 'Bio-Chemistry', 'Haematology', 'Serology',
                     'Micro-Biology', 'CT Scan', 'USG', 'Diagnostic', 'X-Ray', 'Echocardiogram', 'Hormone',
                     'Immunology']

        ### Check Diagonostice Items available or not. If avvailable then no ther component will be there

        get_all_depts = []
        if vals.get('bill_register_line_id'):
            for items in vals.get('bill_register_line_id'):
                if items[2].get('department'):
                    if items[2].get('department') not in get_all_depts:
                        get_all_depts.append(items[2].get('department'))

        ## Check Diagnsis exists
        mixed_up = False
        vals['diagonostic_bill'] = False

        intersection_result = list(set(child_ids) & set(get_all_depts))
        if len(intersection_result) > 0 and len(intersection_result) == len(get_all_depts):
            mixed_up = False
            vals['diagonostic_bill'] = True
        elif len(intersection_result) > 0 and len(intersection_result) != len(get_all_depts):
            mixed_up = True

        if mixed_up == True:
            raise osv.except_osv(_('Attention'),
                                 _('This investigation has diagnosis and others department mix up'))

        ### Ends Here Diagonostic Items
        #
        #
        # import pdb
        # pdb.set_trace()

        stored = super(bill_register, self).create(cr, uid, vals, context)  # return ID int object

        if stored is not None:
            name_text = 'Bill-0' + str(stored)
            cr.execute('update bill_register set name=%s where id=%s', (name_text, stored))
        return stored

    # write procedures:

    def _get_bill_moves(self, cr, uid, bill, context=None):
        cr.execute("SELECT id FROM account_move WHERE ref=%s ORDER BY id", (bill.name,))
        return [x[0] for x in cr.fetchall()]

    def _identify_sales_and_due_moves(self, cr, uid, move_ids, cash_account_id, context=None):
        sales_move_id = None
        due_move_id = None

        for mid in move_ids:
            cr.execute("""
                SELECT COUNT(*) 
                FROM account_move_line 
                WHERE move_id=%s AND account_id NOT IN (%s,195)
            """, (mid, cash_account_id))
            cnt = cr.fetchone()[0]

            if cnt > 0 and not sales_move_id:
                sales_move_id = mid
            elif cnt == 0 and not due_move_id:
                due_move_id = mid

        return sales_move_id, due_move_id

    def _cancel_moves(self, cr, uid, move_ids, context=None):
        move_obj = self.pool.get('account.move')
        for mid in move_ids:
            mv = move_obj.browse(cr, uid, mid, context=context)
            if mv.state == 'posted':
                mv.button_cancel()
        return True

    def _validate_moves(self, cr, uid, move_ids, context=None):
        move_obj = self.pool.get('account.move')
        for mid in move_ids:
            move_obj.button_validate(cr, uid, [mid], context=context)
        return True

    def _remove_income_line(self, cr, uid, move_id, account_id, credit_amount, context=None):
        cr.execute("""
            DELETE FROM account_move_line
            WHERE id = (
                SELECT id FROM account_move_line
                WHERE move_id=%s AND account_id=%s AND credit=%s
                LIMIT 1
            )
        """, (move_id, account_id, credit_amount))

    def _add_income_line(self, cr, uid, move_id, line_name, account_id, credit_amount, context=None):
        ml_obj = self.pool.get('account.move.line')
        ml_obj.create(cr, uid, {
            'move_id': move_id,
            'name': line_name,
            'account_id': account_id,
            'debit': 0.0,
            'credit': credit_amount,
        }, context=context)

    def _update_cash_line(self, cr, uid, move_id, cash_account_id, amount, context=None):
        cr.execute("""
            UPDATE account_move_line
            SET debit=%s, credit=0
            WHERE move_id=%s AND account_id=%s
        """, (amount, move_id, cash_account_id))

    def _update_receivable_debit(self, cr, uid, move_id, amount, context=None):
        cr.execute("""
            UPDATE account_move_line
            SET debit=%s, credit=0
            WHERE move_id=%s AND account_id=195
        """, (amount, move_id))

    def _update_receivable_credit(self, cr, uid, move_id, amount, context=None):
        cr.execute("""
            UPDATE account_move_line
            SET credit=%s, debit=0
            WHERE move_id=%s AND account_id=195
        """, (amount, move_id))

    def _delete_receivable_line(self, cr, uid, move_id, context=None):
        cr.execute("""
            DELETE FROM account_move_line
            WHERE move_id=%s AND account_id=195
        """, (move_id,))

    def _balance_sales_move_by_ar(self, cr, uid, sales_move_id, cash_account_id, context=None):
        cr.execute("SELECT COALESCE(SUM(credit),0) FROM account_move_line WHERE move_id=%s", (sales_move_id,))
        total_credit = cr.fetchone()[0]

        cr.execute("""
            SELECT COALESCE(SUM(debit),0)
            FROM account_move_line
            WHERE move_id=%s AND account_id=%s
        """, (sales_move_id, cash_account_id))
        cash_debit = cr.fetchone()[0]

        new_ar_debit = total_credit - cash_debit
        if new_ar_debit < 0:
            new_ar_debit = 0

        self._update_receivable_debit(cr, uid, sales_move_id, new_ar_debit, context=context)

    def _balance_due_move_cash_and_ar(self, cr, uid, due_move_id, cash_account_id, context=None):
        cr.execute("""
            SELECT COALESCE(SUM(debit),0)
            FROM account_move_line
            WHERE move_id=%s AND account_id=%s
        """, (due_move_id, cash_account_id))
        due_cash = cr.fetchone()[0]
        self._update_receivable_credit(cr, uid, due_move_id, due_cash, context=context)

    def _remove_due_move(self, cr, uid, due_move_id, context=None):
        move_obj = self.pool.get('account.move')

        mv = move_obj.browse(cr, uid, due_move_id, context=context)
        if mv.state == 'posted':
            mv.button_cancel()

        cr.execute("DELETE FROM bill_journal_relation WHERE journal_id=%s", (due_move_id,))
        cr.execute("DELETE FROM account_move_line WHERE move_id=%s", (due_move_id,))
        move_obj.unlink(cr, uid, [due_move_id], context=context)
        return True

    def _rebuild_income_lines(self, cr, uid, bill, sales_move_id, cash_account_id, context=None):
        cr.execute("""
            DELETE FROM account_move_line 
            WHERE move_id=%s AND account_id NOT IN (%s,195)
        """, (sales_move_id, cash_account_id))

        for line in bill.bill_register_line_id:
            income_acc = line.name.accounts_id.id if line.name.accounts_id else 611
            self._add_income_line(cr, uid, sales_move_id, line.name.name, income_acc, line.total_amount, context=context)

    def _apply_bill_line_commands(self, cr, uid, sales_move_id, vals, removed_line_info, context=None):
        for old in removed_line_info:
            self._remove_income_line(cr, uid, sales_move_id, old['account_id'], old['amount'], context=context)

        for cmd in vals.get('bill_register_line_id', []):
            if cmd[0] == 0:
                new_vals = cmd[2]
                exam = self.pool.get('examination.entry').browse(cr, uid, new_vals.get('name'), context=context)
                income_acc = exam.accounts_id.id if exam.accounts_id else 611
                income_amt = new_vals.get('total_amount', 0.0)
                self._add_income_line(cr, uid, sales_move_id, exam.name, income_acc, income_amt, context=context)

        return True

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}

        if vals.get("due") and vals.get("due") < 0:
            raise osv.except_osv(_('Warning!'), _("Check paid and grand total!"))

        trigger_fields = ('bill_register_line_id', 'paid', 'grand_total', 'due')
        need_journal_update = any(f in vals for f in trigger_fields)

        removed_line_info = []
        has_update_cmd = False

        if vals.get('bill_register_line_id'):
            for cmd in vals['bill_register_line_id']:
                if cmd[0] == 2:
                    line_id = cmd[1]
                    old_line = self.pool.get('bill.register.line').browse(cr, uid, line_id, context=context)
                    if old_line and old_line.name:
                        acc_id = old_line.name.accounts_id.id if old_line.name.accounts_id else 611
                        removed_line_info.append({
                            'line_id': line_id,
                            'account_id': acc_id,
                            'amount': old_line.total_amount,
                        })
                if cmd[0] == 1:
                    has_update_cmd = True

        res = super(bill_register, self).write(cr, uid, ids, vals, context=context)

        if not need_journal_update:
            return res

        bill = self.browse(cr, uid, ids[0], context=context)

        cash_account_id = 6
        if bill.payment_type and bill.payment_type.account:
            cash_account_id = bill.payment_type.account.id

        move_ids = self._get_bill_moves(cr, uid, bill, context=context)
        if not move_ids:
            return res

        sales_move_id, due_move_id = self._identify_sales_and_due_moves(cr, uid, move_ids, cash_account_id, context=context)
        if not sales_move_id:
            return res

        self._cancel_moves(cr, uid, move_ids, context=context)

        if has_update_cmd:
            self._rebuild_income_lines(cr, uid, bill, sales_move_id, cash_account_id, context=context)
        else:
            self._apply_bill_line_commands(cr, uid, sales_move_id, vals, removed_line_info, context=context)

        # Special scenario (Option B):
        # If there are two moves and due is now zero or less
        # - Remove journal 2
        # - Remove AR from journal 1
        # - Set cash in journal 1 to bill.grand_total (or bill.paid if that is the desired logic)
        if len(move_ids) > 1 and bill.due <= 0 and due_move_id:
            self._remove_due_move(cr, uid, due_move_id, context=context)
            self._delete_receivable_line(cr, uid, sales_move_id, context=context)

            new_cash_amount = bill.grand_total
            if new_cash_amount < 0:
                new_cash_amount = 0

            self._update_cash_line(cr, uid, sales_move_id, cash_account_id, new_cash_amount, context=context)

            self.pool.get('account.move').button_validate(cr, uid, [sales_move_id], context=context)
            return res

        # Normal logic for one journal
        if len(move_ids) == 1:
            self._update_cash_line(cr, uid, sales_move_id, cash_account_id, bill.paid, context=context)
            self._update_receivable_debit(cr, uid, sales_move_id, bill.due, context=context)

        # Normal logic for two journals
        else:
            self._balance_sales_move_by_ar(cr, uid, sales_move_id, cash_account_id, context=context)
            if due_move_id:
                self._balance_due_move_cash_and_ar(cr, uid, due_move_id, cash_account_id, context=context)

        # Validate remaining moves
        remaining_moves = []
        for mid in move_ids:
            if mid != due_move_id:
                remaining_moves.append(mid)

        self._validate_moves(cr, uid, remaining_moves, context=context)

        return res



# end 







    @api.onchange('bill_register_line_id')
    def onchange_test_bill(self):
        sumalltest = 0
        total_without_discount = 0
        for item in self.bill_register_line_id:
            sumalltest = sumalltest + item.total_amount
            total_without_discount = total_without_discount + item.price

        self.total = sumalltest
        after_dis = (sumalltest * (self.doctors_discounts / 100))
        self.after_discount = 0

        self.grand_total = sumalltest
        self.due = sumalltest - self.paid
        self.total_without_discount = total_without_discount
        # import pdb
        # pdb.set_trace()
        #

        return "X"

    @api.onchange('paid')
    def onchange_paid(self):
        self.due = self.grand_total - self.paid
        if self.payment_type:
            if self.payment_type.name == 'Visa Card':
                interest = self.payment_type.service_charge
                service_charge = (self.paid * interest) / 100
                self.service_charge = service_charge
                self.to_be_paid = self.paid + service_charge
        return 'x'

    @api.onchange('doctors_discounts')
    def onchange_doc_discount(self):
        discount = self.doctors_discounts

        for item in self.bill_register_line_id:
            item.discount_percent = round((item.price * discount) / 100)
            item.discount = discount
            item.total_discount = item.flat_discount + item.discount_percent
            item.total_amount = item.price - item.total_discount

            # if item.discount>0:
            #     dis = round(item.price * discount / 100)
            #     dis_amount=round(item.price-dis)
            #     item.discount=discount
            #     item.total_discount=item.price-item.total_amount
            #     item.total_amount=dis_amount
            #
            # elif item.flat_discount>0 or item.discount<=0:
            #     dis = round(item.total_amount * discount / 100)
            #     dis_amount = round(item.total_amount - dis)
            #     item.discount = discount
            #     item.total_discount = item.price-item.total_amount
            #     item.total_amount = dis_amount
        return "X"

    @api.onchange('other_discount')
    def onchange_other_discount(self):
        other_discount = self.other_discount
        total = self.total_without_discount
        if total > 0:
            discount_distribution = other_discount / total
            for item in self.bill_register_line_id:
                item.flat_discount = 0
                item.flat_discount = round(item.price * discount_distribution)
                item.total_discount = item.flat_discount + item.discount_percent
                item.total_amount = item.price - item.total_discount

            # discount_dec=other_discount/total
            # discount_figure=1-discount_dec
            #
            # for item in self.bill_register_line_id:
            #     dis_amount = round(item.price*discount_figure)
            #     item.flat_discount =round((item.price-dis_amount))
            #     item.total_discount = round(item.flat_discount+item.discount)
            #     item.total_amount =dis_amount

        #
        #
        #
        #
        # self.grand_total = self.total - self.other_discount
        # self.due=self.total - self.other_discount- self.paid
        return 'Y'


class test_information(osv.osv):
    _name = 'bill.register.line'

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('bill.register')
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            rate = record.price
            discount = record.discount
            interst_amount = int(discount) * int(rate) / 100
            total_amount = int(rate) - interst_amount
            res[record.id] = total_amount
            # import pdb
            # pdb.set_trace()
        return res

    _columns = {

        'name': fields.many2one("examination.entry", "Item Name", ondelete='cascade'),
        'bill_register_id': fields.many2one('bill.register', "Information"),
        'department': fields.char("Department"),
        'product_qty': fields.float('Quantity'),
        'delivery_date': fields.date("Delivery Date"),
        'date': fields.datetime("Date", readonly=True, default=lambda self: fields.datetime.now()),
        # 'currency_id': fields.related('pricelist_id', 'currency_id', type="many2one", relation="res.currency",
        #                               string="Currency", readonly=True, required=True),
        # 'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute=dp.get_precision('Account')),
        'price': fields.integer("Price"),
        'discount': fields.integer("Discount (%)"),
        'flat_discount': fields.integer("Flat Discount"),
        'total_discount': fields.integer("Total Discount"),
        'discount_percent': fields.integer("Discount Percent"),
        'total_amount': fields.integer("Total Amount"),
        'assign_doctors': fields.many2one('doctors.profile', 'Doctor'),
        'commission_paid': fields.boolean("Commission Paid"),
    }

    def onchange_test(self, cr, uid, ids, name, context=None):
        tests = {'values': {}}
        # code for delivery date

        dep_object = self.pool.get('examination.entry').browse(cr, uid, name, context=None)
        delivery_required_days = dep_object.required_time
        delivery_date = date.today() + timedelta(days=delivery_required_days)
        # import pdb
        # pdb.set_trace()
        abc = {'department': dep_object.department.name, 'product_qty': 1, 'price': dep_object.rate,
               'total_amount': dep_object.rate, 'bill_register_id.paid': dep_object.rate,
               'delivery_date': delivery_date}
        tests['value'] = abc
        # import pdb
        # pdb.set_trace()
        return tests

    @api.onchange('product_qty')
    def onchange_qty(self):
        self.total_amount = self.price * self.product_qty

    def onchange_discount(self, cr, uid, ids, price, discount, context=None):
        tests = {'values': {}}

        dis_amount = round(price - (price * discount / 100))

        abc = {'total_amount': dis_amount, 'total_discount': dis_amount}
        tests['value'] = abc

        return tests

    def create(self, cr, uid, vals, context=None):
        # deliry_min_time
        stored = super(test_information, self).create(cr, uid, vals, context)
        bill_register_line_object = self.browse(cr, uid, stored, context=context)
        test_name = bill_register_line_object.name
        required_time = test_name.required_time
        today = date.today()
        delivery_date = today + timedelta(days=required_time)
        cr.execute("update bill_register_line set delivery_date=%s where id=%s", (delivery_date, stored))
        cr.commit()

        # today = datetime.datetime.strftime(datetime.datetime.today(), '%d/%m/%Y-%Hh/%Mm')

        return 0

    # def write(self, cr, uid, vals, context=None):
    #     import pdb
    #     pdb.set_trace()


class admission_payment_line(osv.osv):
    _name = 'bill.register.payment.line'

    _columns = {
        'bill_register_payment_line_id': fields.many2one('bill.register', 'bill register payment'),
        'date': fields.date("Date"),
        'amount': fields.float('Amount'),
        'type': fields.char("Type"),
        'card_no': fields.char('Card Number'),
        'bank_name': fields.char('Bank Name'),
        'money_receipt_id': fields.many2one('leih.money.receipt', 'Money Receipt ID'),

    }


class bill_journal_relations(osv.osv):
    _name = 'bill.journal.relation'

    _columns = {
        'bill_journal_relation_id': fields.many2one('bill.register', 'bill register payment'),
        'admission_journal_relation_id': fields.many2one('leih.admission', 'Admission Journal'),
        'general_admission_journal_relation_id': fields.many2one('hospital.admission', 'General Admission Journal'),
        # 'hospital_admission_journal_relation_id': fields.many2one('hospital.leih.admission', 'Admission Journal'),
        'journal_id': fields.integer("Journal Id"),
    }

# class accoun_move(osv.osv):
#     _inherit ="account.move"
#
#     def write(self, cr, uid,ids, vals, context=None):
#         import pdb
#         pdb.set_trace()
