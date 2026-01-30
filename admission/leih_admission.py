# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import api
from openerp.tools.amount_to_text_en import amount_to_text


class leih_admission(osv.osv):
    _name = "leih.admission"
    _order = 'id desc'

    # ----------------------------
    # Helpers: transaction + checks
    # ----------------------------
    def _assert_admission_integrity(self, cr, uid, admission, journal_id, mr_id, context=None):
        """Hard validation: if any required piece is missing -> raise (forces rollback)."""
        if not admission:
            raise osv.except_osv(_('Error!'), _('Admission not found.'))

        if not journal_id:
            raise osv.except_osv(_('Error!'), _('Journal entry was not created.'))

        mv = self.pool.get('account.move').browse(cr, uid, journal_id, context=context)
        if not mv:
            raise osv.except_osv(_('Error!'), _('Journal entry record is missing.'))
        if mv.state != 'posted':
            raise osv.except_osv(_('Error!'), _('Journal entry is not posted.'))

        # bill.journal.relation must exist for this journal and admission
        cr.execute("""
            SELECT COUNT(*)
            FROM bill_journal_relation
            WHERE journal_id=%s AND admission_journal_relation_id=%s
        """, (journal_id, admission.id))
        if cr.fetchone()[0] == 0:
            raise osv.except_osv(_('Error!'), _('bill.journal.relation is missing for this admission.'))

        # If paid > 0 then MR + payment line must exist
        if admission.paid and admission.paid > 0:
            if not mr_id:
                raise osv.except_osv(_('Error!'), _('Money receipt was not created though Paid > 0.'))

            mr = self.pool.get('leih.money.receipt').browse(cr, uid, mr_id, context=context)
            if not mr:
                raise osv.except_osv(_('Error!'), _('Money receipt record is missing.'))

            cr.execute("""
                SELECT COUNT(*)
                FROM admission_payment_line
                WHERE admission_payment_line_id=%s AND money_receipt_id=%s
            """, (admission.id, mr_id))
            if cr.fetchone()[0] == 0:
                raise osv.except_osv(_('Error!'), _('Admission payment line is missing for this money receipt.'))

        return True

    def _default_payment_type(self):
        # Odoo old API: env is available in new api contexts; keep as you had it
        return self.env['payment.type'].search([('name', '=', 'Cash')], limit=1).id

    _columns = {
        'name': fields.char("Name"),
        'mobile': fields.char(string="Mobile", store=False),
        'patient_id': fields.char(related='patient_name.patient_id', string="Patient Id"),
        'patient_name': fields.many2one('patient.info', "Patient Name"),
        'address': fields.char("Address", store=False),
        'age': fields.char("Age", store=False),
        'sex': fields.char("Sex", store=False),
        'ref_doctors': fields.many2one('doctors.profile', 'Reffered by'),
        'operation_date': fields.date("Operation Date"),
        'release_note': fields.text("Release Note"),
        'package_name': fields.many2one("examine.package", string="Package"),
        'leih_admission_line_id': fields.one2many('leih.admission.line', 'leih_admission_id', 'Investigations'),
        'guarantor_line_id': fields.one2many("patient.guarantor", "admission_id", "Guarantor Name"),
        'bill_register_admission_line_id': fields.one2many("bill.register.admission.line", "admission_line_id", "Bill Register"),
        'admission_payment_line_id': fields.one2many("admission.payment.line", "admission_payment_line_id", "Admission Payment"),
        'admission_journal_relation_id': fields.one2many("bill.journal.relation", "admission_journal_relation_id", "Journal"),

        'emergency': fields.boolean("Emergency Department"),
        'total_without_discount': fields.float(string="Total without discount"),
        'total': fields.float(string="Total"),
        'doctors_discounts': fields.float("Discount(%)"),
        'after_discount': fields.float("Discount Amount"),
        'other_discount': fields.float("Other Discount"),
        'grand_total': fields.float("Grand Total"),
        'advance': fields.float("Advance"),
        'paid': fields.float("Paid"),
        'due': fields.float("Due"),

        'type': fields.selection([('cash', 'Cash'), ('bank', 'Bank')], 'Payment Type'),
        'card_no': fields.char('Card No.'),
        'bank_name': fields.char('Bank Name'),
        'date': fields.datetime("Date", readonly=True, default=lambda self: fields.datetime.now()),
        'user_id': fields.many2one('res.users', 'Assigned to', select=True, track_visibility='onchange'),
        'state': fields.selection(
            [('pending', 'Pending'), ('activated', 'Admitted'), ('released', 'Released'), ('cancelled', 'Cancelled')],
            'Status', default='pending', readonly=True,
        ),
        'emergency_covert_time': fields.datetime("Admission Convert time"),
        'old_journal': fields.boolean("Old Journal"),

        # payment type attributes
        'payment_type': fields.many2one("payment.type", "Payment Type", default=_default_payment_type),
        'service_charge': fields.float("Service Charge"),
        'to_be_paid': fields.float("To be Paid"),
        'account_number': fields.char("Account Number"),

        # general
        'father_name': fields.char("Father's Name"),
        'mother_name': fields.char("Mother's Name"),
        'religion': fields.selection(
            [('islam', 'Islam'), ('hindu', 'Hinduism'), ('buddhism', 'Buddhism'), ('christianity', 'Christianity')],
            'Religion'
        ),
        'blood_group': fields.char('Blood Group'),
        'reffered_to_hospital': fields.many2one('brokers.info', 'Referred to this hospital by'),
        'occupation': fields.char('Occupation'),
        'business_address': fields.char('Business Address'),
        'admitting_doctor': fields.many2one('doctors.profile', 'Admitting Doctor'),

        # hospital use only
        'bed': fields.char('Bed'),
        'received_by': fields.char('Received/Registered By'),
        'clinic_diagnosis': fields.char('Clinical Diagnosis'),
        'discount_remarks': fields.char('Discount Remarks'),
    }

    _defaults = {
        'user_id': lambda obj, cr, uid, context: uid,
    }

    # ----------------------------
    # Onchange / utility
    # ----------------------------
    @api.onchange("payment_type")
    def onchnage_payment_type(self):
        if self.payment_type and self.payment_type.active is True:
            interest = self.payment_type.service_charge
            if interest and interest > 0:
                service_charge = (self.paid * interest) / 100.0
                self.service_charge = service_charge
                self.to_be_paid = self.paid + service_charge
            else:
                self.to_be_paid = self.paid
                self.service_charge = 0.0
        return "X"

    def onchange_patient(self, cr, uid, ids, name, context=None):
        if context is None:
            context = {}

        # If no patient selected, clear fields
        if not name:
            return {
                'value': {
                    'mobile': False,
                    'address': False,
                    'age': False,
                    'sex': False,
                }
            }

        patient = self.pool.get('patient.info').browse(cr, uid, name, context=context)

        return {
            'value': {
                'mobile': patient.mobile or False,
                'address': patient.address or False,
                'age': patient.age or False,
                'sex': patient.sex or False,
            }
        }

    def btn_pay(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return True

        inv = self.browse(cr, uid, ids[0], context=context)
        if inv.state in ('pending', 'cancelled'):
            raise osv.except_osv(_('Warning'), _('Please Confirm and Print the Bill'))
        if inv.total <= inv.paid:
            raise osv.except_osv(_('Full Paid'), _('Nothing to Pay Here. Already Full Paid'))

        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(
            cr, uid, 'leih', 'admission_payment_form_view'
        )

        return {
            'name': _("Pay Invoice"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'admission.payment',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'default_admission_id': ids[0],
                'default_amount': inv.due,
            }
        }
    def add_discount(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return True

        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(
            cr, uid, 'leih', 'discount_view'
        )

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
                'pi_id': ids[0],
                'default_admission_id': ids[0],
            }
        }

    

    @api.multi
    def amount_to_text(self, amount, currency='Bdt'):
        text = amount_to_text(amount, currency)
        new_text = text.replace("euro", "Taka")
        sub_str = "Taka"
        final_text = new_text[:new_text.index(sub_str) + len(sub_str)]
        return final_text

    # ----------------------------
    # CREATE: remove cr.commit(), keep name set
    # ----------------------------
    def create(self, cr, uid, vals, context=None):
        if vals.get("due") and vals.get("due") < 0:
            raise osv.except_osv(_('Warning!'), _("Check paid and grand total!"))

        if context is None:
            context = {}

        stored = super(leih_admission, self).create(cr, uid, vals, context)

        # IMPORTANT: NO cr.commit() here (single transaction)
        if stored is not None:
            if vals.get("emergency") is False:
                name_text = 'A-0' + str(stored)
            else:
                name_text = 'E-0' + str(stored)
            cr.execute('UPDATE leih_admission SET name=%s WHERE id=%s', (name_text, stored))

        return stored

    # ----------------------------
    # CHANGE STATUS (CONFIRM): ONE TRANSACTION + SAVEPOINT + STRICT CHECKS
    # ----------------------------
    def change_status(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        stored_obj = self.browse(cr, uid, [ids[0]], context=context)

        if stored_obj.state == 'activated':
            raise osv.except_osv(_('Warning!'), _('Already this Bill is Confirmed.'))

        journal_object = self.pool.get("bill.journal.relation")

        try:
            cr.execute("SAVEPOINT leih_admission_confirm")

            stored = int(ids[0])

            # ---- LAB/SAMPLE CREATION (your original logic; removed commits) ----
            get_all_tested_ids = []
            for items in stored_obj.leih_admission_line_id:
                get_all_tested_ids.append(items.name.id)

            already_merged = []
            custom_name = ''

            for items in stored_obj.leih_admission_line_id:
                custom_name = ''
                state = 'sample'
                if items.name.sample_req is False or items.name.sample_req is None:
                    state = 'lab'
                if items.name.indoor is True:
                    state = 'indoor'

                if items.name.manual != True or items.name.lab_not_required != True:
                    custom_name = custom_name + ' ' + str(items.name.name)

                    if items.name.id not in already_merged:
                        child_list = []
                        value = {
                            'admission_id': int(stored),
                            'test_id': int(items.name.id),
                            'department_id': items.name.department.name,
                            'state': state
                        }

                        for test_item in items.name.examination_entry_line:
                            tmp_dict = {
                                'test_name': test_item.name,
                                'ref_value': test_item.reference_value,
                                'bold': test_item.bold,
                                'group_by': test_item.group_by
                            }
                            child_list.append([0, False, tmp_dict])

                        if items.name.merge is True:
                            for entry in items.name.merge_ids:
                                test_id = entry.examinationentry_id.id
                                if test_id in get_all_tested_ids:
                                    custom_name = custom_name + ', ' + str(entry.examinationentry_id.name)
                                    already_merged.append(test_id)
                                    for m_test_line in entry.examinationentry_id.examination_entry_line:
                                        tmp_dict = {
                                            'test_name': m_test_line.name,
                                            'ref_value': m_test_line.reference_value,
                                            'bold': m_test_line.bold,
                                            'group_by': m_test_line.group_by
                                        }
                                        child_list.append([0, False, tmp_dict])

                        value['sticker_line_id'] = child_list
                        value['full_name'] = custom_name

                        sample_obj = self.pool.get('diagnosis.sticker')
                        sample_id = sample_obj.create(cr, uid, value, context=context)

                    if sample_id is not None:
                        sample_text = 'Lab-0' + str(sample_id)
                        cr.execute('UPDATE diagnosis_sticker SET name=%s WHERE id=%s', (sample_text, sample_id))

            # ---- ACCOUNTING (your original logic; removed commits; hard errors on failure) ----
            has_been_paid = 0.0
            line_ids = []

            periods = self.pool.get('account.period').find(cr, uid, context=context)
            period_id = periods and periods[0] or False

            # payment method logic exactly as you had
            if stored_obj.payment_type.name == 'Cash':
                has_been_paid = stored_obj.paid
                ar_amount = stored_obj.due
                account_id = 6
            elif stored_obj.payment_type.name == 'Visa Card':
                has_been_paid = stored_obj.to_be_paid
                ar_amount = stored_obj.due
                account_id = stored_obj.payment_type.account.id
            else:
                # keep safe default
                has_been_paid = stored_obj.paid
                ar_amount = stored_obj.due
                account_id = 6

            if ar_amount > 0:
                line_ids.append((0, 0, {
                    'analytic_account_id': False,
                    'tax_code_id': False,
                    'tax_amount': 0,
                    'name': stored_obj.name,
                    'currency_id': False,
                    'credit': 0,
                    'date_maturity': False,
                    'account_id': 195,  # AR
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
                    'account_id': account_id,  # Cash/Bank
                    'debit': has_been_paid,
                    'amount_currency': 0,
                    'partner_id': False,
                }))

            for cc_obj in stored_obj.leih_admission_line_id:
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
                'journal_id': 2,         # Sales Journal
                'date': stored_obj.date,
                'period_id': period_id,
                'ref': stored_obj.name,
                'line_id': line_ids
            }

            saved_jv_id = jv_entry.create(cr, uid, j_vals, context=context)
            if not saved_jv_id:
                raise osv.except_osv(_('Error!'), _('Failed to create journal entry.'))

            # Post journal
            jv_entry.button_validate(cr, uid, [saved_jv_id], context=context)

            # Update admission state (NO commit)
            cr.execute("UPDATE leih_admission SET state='activated' WHERE id=%s", (ids[0],))

            # Create relation (NO commit)
            journal_dict = {'journal_id': saved_jv_id, 'admission_journal_relation_id': stored_obj.id}
            journal_object.create(cr, uid, vals=journal_dict, context=context)

            # Create MR + payment line (your logic; NO commit)
            mr_id = False
            if stored_obj.paid != False and stored_obj.paid > 0:
                ad_vals = {
                    'date': stored_obj.date,
                    'admission_id': stored_obj.id,
                    'amount': stored_obj.paid,
                    'type': stored_obj.type,
                    'p_type': 'advance',
                    'bill_total_amount': stored_obj.total,
                    'due_amount': stored_obj.due,
                }
                mr_obj = self.pool.get('leih.money.receipt')
                mr_id = mr_obj.create(cr, uid, ad_vals, context=context)
                if not mr_id:
                    raise osv.except_osv(_('Error!'), _('Money Receipt creation failed.'))

                mr_name = 'MR#' + str(mr_id)
                cr.execute('UPDATE leih_money_receipt SET name=%s WHERE id=%s', (mr_name, mr_id))

                admission_payment_obj = self.pool.get('admission.payment.line')
                service_dict = {
                    'date': stored_obj.date,
                    'amount': stored_obj.paid,
                    'type': stored_obj.payment_type.name,
                    'admission_payment_line_id': stored_obj.id,
                    'money_receipt_id': mr_id
                }
                bill_payment_id = admission_payment_obj.create(cr, uid, vals=service_dict, context=context)
                if not bill_payment_id:
                    raise osv.except_osv(_('Error!'), _('Admission payment line creation failed.'))

            # Final strict validation (if anything missing -> raise -> rollback)
            self._assert_admission_integrity(cr, uid, stored_obj, journal_id=saved_jv_id, mr_id=mr_id, context=context)

            cr.execute("RELEASE SAVEPOINT leih_admission_confirm")

        except Exception as e:
            # Rollback only this method's work, then raise hard error (full request rollback)
            try:
                cr.execute("ROLLBACK TO SAVEPOINT leih_admission_confirm")
            except:
                pass
            raise osv.except_osv(_('Error!'), _('Transaction failed and was rolled back: %s') % (str(e),))

        return self.pool['report'].get_action(cr, uid, ids, 'leih.report_admission', context=context)

    # ----------------------------
    # CANCEL: remove commits; raise on failure
    # ----------------------------
    def admission_cancel(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        try:
            cr.execute("SAVEPOINT leih_admission_cancel")

            cr.execute("""
                SELECT id
                FROM account_move
                WHERE ref = (SELECT name FROM leih_admission WHERE id=%s LIMIT 1)
            """, (ids[0],))
            joural_ids = [x[0] for x in cr.fetchall()]

            if joural_ids:
                # use superuser for cancel/unlink as your original code did
                suid = 1
                move_obj = self.pool.get('account.move')
                moves = move_obj.browse(cr, suid, joural_ids, context=context)
                moves.button_cancel()
                moves.unlink()

            cr.execute("UPDATE leih_admission SET state='cancelled' WHERE id=%s", (ids[0],))
            cr.execute("UPDATE leih_money_receipt SET state='cancel' WHERE admission_id=%s", (ids[0],))

            cr.execute("RELEASE SAVEPOINT leih_admission_cancel")

        except Exception as e:
            try:
                cr.execute("ROLLBACK TO SAVEPOINT leih_admission_cancel")
            except:
                pass
            raise osv.except_osv(_('Error!'), _('Cancel failed and was rolled back: %s') % (str(e),))

        return True


    @api.multi
    def advance_paid(self, name=None):
        self.ensure_one()

        mrs = self.env['leih.money.receipt'].search(
            [('admission_id', '=', self.id)],
            order='id'
        )

        advance = 0.0
        paid = 0.0
        if len(mrs) >= 2:
            for r in mrs[:-1]:
                advance += (r.amount or 0.0)
            paid = (mrs[-1].amount or 0.0)
        elif len(mrs) == 1:
            advance = (mrs[0].amount or 0.0)

        return {'advance': advance, 'paid': paid}

    # ----------------------------
    # WRITE: keep your existing code (as you pasted)
    # IMPORTANT: remove any cr.commit() inside it (your pasted write() had none)
    # ----------------------------
    # NOTE: You already provided a big write() with journal update logic.
    # Keep it as-is, but ensure:
    #   - No cr.commit()
    #   - No "except: pdb.set_trace()" (raise error instead)
    #   - If you want strict validation after write, you can call _assert_admission_integrity
    #
    # Paste your write() here exactly as you already have it (without commits/debugger).


    def _get_admission_moves(self, cr, uid, admission, context=None):
        cr.execute("SELECT id FROM account_move WHERE ref=%s ORDER BY id", (admission.name,))
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

    def _remove_due_move(self, cr, uid, due_move_id, context=None):
        move_obj = self.pool.get('account.move')

        mv = move_obj.browse(cr, uid, due_move_id, context=context)
        if mv.state == 'posted':
            mv.button_cancel()

        cr.execute("DELETE FROM bill_journal_relation WHERE journal_id=%s", (due_move_id,))
        cr.execute("DELETE FROM account_move_line WHERE move_id=%s", (due_move_id,))
        move_obj.unlink(cr, uid, [due_move_id], context=context)
        return True

    def _rebuild_income_lines(self, cr, uid, admission, sales_move_id, cash_account_id, context=None):
        cr.execute("""
            DELETE FROM account_move_line
            WHERE move_id=%s AND account_id NOT IN (%s,195)
        """, (sales_move_id, cash_account_id))

        for line in admission.leih_admission_line_id:
            income_acc = line.name.accounts_id.id if line.name.accounts_id else 611
            self._add_income_line(cr, uid, sales_move_id, line.name.name, income_acc, line.total_amount, context=context)

    def _apply_admission_line_commands(self, cr, uid, sales_move_id, vals, removed_line_info, context=None):
        for old in removed_line_info:
            self._remove_income_line(cr, uid, sales_move_id, old['account_id'], old['amount'], context=context)

        for cmd in vals.get('leih_admission_line_id', []):
            if cmd[0] == 0:
                new_vals = cmd[2]
                exam = self.pool.get('examination.entry').browse(cr, uid, new_vals.get('name'), context=context)
                income_acc = exam.accounts_id.id if exam.accounts_id else 611
                income_amt = new_vals.get('total_amount', 0.0)
                self._add_income_line(cr, uid, sales_move_id, exam.name, income_acc, income_amt, context=context)

        return True

    def _get_total_credit_and_advance_cash(self, cr, uid, sales_move_id, cash_account_id, context=None):
        cr.execute("""
            SELECT COALESCE(SUM(credit),0)
            FROM account_move_line
            WHERE move_id=%s
        """, (sales_move_id,))
        total_credit = cr.fetchone()[0]

        cr.execute("""
            SELECT COALESCE(SUM(debit),0)
            FROM account_move_line
            WHERE move_id=%s AND account_id=%s
        """, (sales_move_id, cash_account_id))
        advance_cash = cr.fetchone()[0]

        return total_credit, advance_cash

    def _adjust_two_journal_case(self, cr, uid, sales_move_id, due_move_id, cash_account_id, admission, context=None):
        """
        sales_move:  Debit Cash(advance) + Debit AR(open after advance), Credit Income(total)
        due_move:    Debit Cash(paid after advance) , Credit AR(paid after advance)
        """

        # 1) Total sale amount = total credits in sales move
        cr.execute("""
            SELECT COALESCE(SUM(credit),0)
            FROM account_move_line
            WHERE move_id=%s
        """, (sales_move_id,))
        total_credit = float(cr.fetchone()[0] or 0.0)

        # 2) Advance cash = cash debit inside SALES move (this is the initial/advance payment)
        cr.execute("""
            SELECT COALESCE(SUM(debit),0)
            FROM account_move_line
            WHERE move_id=%s AND account_id=%s
        """, (sales_move_id, cash_account_id))
        advance_cash = float(cr.fetchone()[0] or 0.0)

        # 3) Total paid (use admission.paid; if unreliable, derive from grand_total - due)
        total_paid = float(admission.paid or 0.0)
        if admission.grand_total and admission.due is not None:
            # safer in many custom modules
            total_paid = float((admission.grand_total or 0.0) - (admission.due or 0.0))

        if total_paid < 0:
            total_paid = 0.0

        # ✅ THIS is what you must put in journal 2
        paid_after_advance = total_paid - advance_cash
        if paid_after_advance < 0:
            paid_after_advance = 0.0

        # Remaining AR after advance (kept in sales move)
        ar_after_advance = total_credit - advance_cash
        if ar_after_advance < 0:
            ar_after_advance = 0.0

        # ---- Update SALES MOVE (journal 1) ----
        # Keep cash line as advance_cash (do NOT change it here)
        self._update_receivable_debit(cr, uid, sales_move_id, ar_after_advance, context=context)

        # ---- Update DUE MOVE (journal 2) ----
        if paid_after_advance <= 0:
            # If no extra payment beyond advance, remove due move
            self._remove_due_move(cr, uid, due_move_id, context=context)
            return True

        # j2 cash debit = paid_after_advance
        self._update_cash_line(cr, uid, due_move_id, cash_account_id, paid_after_advance, context=context)

        # j2 AR credit = paid_after_advance
        self._update_receivable_credit(cr, uid, due_move_id, paid_after_advance, context=context)

        return True


    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}

        if vals.get("due") and vals.get("due") < 0:
            raise osv.except_osv(_('Warning!'), _("Check paid and grand total!"))

        trigger_fields = ('leih_admission_line_id', 'paid', 'grand_total', 'due')
        need_journal_update = any(f in vals for f in trigger_fields)

        removed_line_info = []
        has_update_cmd = False

        if vals.get('leih_admission_line_id'):
            for cmd in vals['leih_admission_line_id']:
                if cmd[0] == 2:
                    line_id = cmd[1]
                    old_line = self.pool.get('leih.admission.line').browse(cr, uid, line_id, context=context)
                    if old_line and old_line.name:
                        acc_id = old_line.name.accounts_id.id if old_line.name.accounts_id else 611
                        removed_line_info.append({
                            'line_id': line_id,
                            'account_id': acc_id,
                            'amount': old_line.total_amount,
                        })
                if cmd[0] == 1:
                    has_update_cmd = True

        res = super(leih_admission, self).write(cr, uid, ids, vals, context=context)

        if not need_journal_update:
            return res

        admission = self.browse(cr, uid, ids[0], context=context)

        cash_account_id = 6
        if admission.payment_type and admission.payment_type.account:
            cash_account_id = admission.payment_type.account.id

        move_ids = self._get_admission_moves(cr, uid, admission, context=context)
        if not move_ids:
            return res

        sales_move_id, due_move_id = self._identify_sales_and_due_moves(cr, uid, move_ids, cash_account_id, context=context)
        if not sales_move_id:
            return res

        self._cancel_moves(cr, uid, move_ids, context=context)

        if has_update_cmd:
            self._rebuild_income_lines(cr, uid, admission, sales_move_id, cash_account_id, context=context)
        else:
            self._apply_admission_line_commands(cr, uid, sales_move_id, vals, removed_line_info, context=context)

        total_credit, advance_cash = self._get_total_credit_and_advance_cash(cr, uid, sales_move_id, cash_account_id, context=context)

        if len(move_ids) > 1 and due_move_id:
            if advance_cash >= total_credit:
                self._remove_due_move(cr, uid, due_move_id, context=context)
                self._delete_receivable_line(cr, uid, sales_move_id, context=context)
                self._update_cash_line(cr, uid, sales_move_id, cash_account_id, total_credit, context=context)
                self.pool.get('account.move').button_validate(cr, uid, [sales_move_id], context=context)
                return res
            else:
                self._adjust_two_journal_case(cr, uid, sales_move_id, due_move_id, cash_account_id, admission, context=context)
                self._validate_moves(cr, uid, [sales_move_id, due_move_id], context=context)
                return res

        if len(move_ids) == 1:
            self._update_cash_line(cr, uid, sales_move_id, cash_account_id, admission.paid, context=context)
            self._update_receivable_debit(cr, uid, sales_move_id, admission.due, context=context)
            self._validate_moves(cr, uid, [sales_move_id], context=context)

        return res


    @api.onchange('leih_admission_line_id')
    def onchange_admission_line(self):
        sumalltest = 0.0
        total_without_discount = 0.0
        for item in self.leih_admission_line_id:
            sumalltest += item.total_amount
            total_without_discount += item.price

        self.total = sumalltest
        self.after_discount = 0.0
        self.grand_total = sumalltest
        self.due = sumalltest - self.paid
        self.total_without_discount = total_without_discount
        return "X"

    @api.onchange('paid')
    def onchange_paid(self):
        self.due = self.grand_total - self.paid
        if self.payment_type and self.payment_type.name == 'Visa Card':
            interest = self.payment_type.service_charge
            service_charge = (self.paid * interest) / 100.0
            self.service_charge = service_charge
            self.to_be_paid = self.paid + service_charge
        return 'x'

    @api.onchange('doctors_discounts')
    def onchange_doc_discount(self):
        discount = self.doctors_discounts
        for item in self.leih_admission_line_id:
            item.discount_percent = round((item.price * discount) / 100.0)
            item.discount = discount
            item.total_discount = item.flat_discount + item.discount_percent
            item.total_amount = item.price - item.total_discount
        return "X"

    @api.onchange('other_discount')
    def onchange_other_discount(self):
        other_discount = self.other_discount
        total = self.total_without_discount
        gd = total - other_discount
        line_total = 0.0
        if total > 0:
            discount_distribution = other_discount / total
            for item in self.leih_admission_line_id:
                item.flat_discount = 0
                item.flat_discount = round(item.price * discount_distribution)
                item.total_discount = item.flat_discount + item.discount_percent
                item.total_amount = item.price - item.total_discount
                line_total += item.total_amount
            if line_total < gd:
                item.total_amount = item.total_amount + (gd - line_total)
                item.flat_discount = item.flat_discount - (gd - line_total)
                item.total_discount = item.flat_discount + item.discount_percent
            if gd < line_total:
                item.total_amount = item.total_amount - (line_total - gd)
                item.flat_discount = item.flat_discount + (line_total - gd)
        return 'Nothing'


class test_information(osv.osv):
    _name = 'leih.admission.line'

    _columns = {
        'name': fields.many2one("examination.entry", "Item Name", ondelete='cascade'),
        'leih_admission_id': fields.many2one('leih.admission', "Information"),
        'department': fields.char("Department"),
        'price': fields.float("Price"),
        'discount': fields.float("Discount"),
        'flat_discount': fields.integer("Flat Discount"),
        'total_discount': fields.integer("Total Discount"),
        'discount_percent': fields.integer("Discount Percent"),
        'total_amount': fields.float("Total Amount")
    }

    def onchange_test(self, cr, uid, ids, name, context=None):
        tests = {'values': {}}
        dep_object = self.pool.get('examination.entry').browse(cr, uid, name, context=None)
        abc = {'department': dep_object.department.name, 'price': dep_object.rate, 'total_amount': dep_object.rate}
        tests['value'] = abc
        return tests

    def onchange_discount(self, cr, uid, ids, name, discount, context=None):
        tests = {'values': {}}
        dep_object = self.pool.get('examination.entry').browse(cr, uid, name, context=None)
        abc = {'total_amount': round(dep_object.rate - (dep_object.rate * discount / 100.0))}
        tests['value'] = abc
        return tests


class admission_bill_register(osv.osv):
    _name = 'bill.register.admission.line'

    _columns = {
        'admission_line_id': fields.many2one('leih.admission', 'admission'),
        'bill_id': fields.many2one("bill.register", "Bill ID"),
        'total': fields.float('Total')
    }

    def onchange_bill_id(self, cr, uid, ids, bill_id, context=None):
        lists = {'values': {}}
        dep_object = self.pool.get('bill.register').browse(cr, uid, bill_id, context=None)
        bill_info = {'total': dep_object.total}
        lists['value'] = bill_info
        return lists


class admission_payment_line(osv.osv):
    _name = 'admission.payment.line'

    _columns = {
        'admission_payment_line_id': fields.many2one('leih.admission', 'admission payment'),
        'date': fields.datetime("Date"),
        'amount': fields.float('amount'),
        'type': fields.char('Type'),
        'card_no': fields.char('Card Number'),
        'bank_name': fields.char('Bank Name'),
        'money_receipt_id': fields.many2one('leih.money.receipt', 'Money Receipt ID'),
    }
