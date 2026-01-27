# -*- coding: utf-8 -*-
from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp import api
from datetime import datetime


class admission_payment(osv.osv):
    _name = 'admission.payment'
    _description = "admission Payment"

    # -----------------------
    # ACTION: add payment (NO COMMIT, atomic)
    # -----------------------
    def button_add_payment_action(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return True

        try:
            cr.execute("SAVEPOINT admission_payment_add")

            payment_obj = self.browse(cr, uid, ids[0], context=context)

            if not payment_obj.admission_id:
                raise osv.except_osv(_('Error!'), _('Admission is missing on this payment.'))

            admission_id = payment_obj.admission_id.id
            admission_ref = payment_obj.admission_id.name  # used as account.move.ref / line name

            pay_date = payment_obj.date
            pay_amount = payment_obj.amount
            pay_type_name = payment_obj.payment_type.name if payment_obj.payment_type else False
            pay_card = payment_obj.account_number

            current_due = payment_obj.admission_id.due
            current_paid = payment_obj.admission_id.paid

            money_receipt_id = payment_obj.money_receipt_id.id if payment_obj.money_receipt_id else False
            if not money_receipt_id:
                raise osv.except_osv(_('Error!'), _('Money receipt is missing for this cash collection.'))

            updated_amount = current_due - pay_amount
            updated_paid = current_paid + pay_amount
            if updated_amount < 0:
                updated_amount = 0

            # 1) Create admission.payment.line
            eve_mee_obj = self.pool.get('admission.payment.line')
            service_dict = {
                'date': pay_date,
                'amount': pay_amount,
                'type': pay_type_name,
                'card_no': pay_card,
                'admission_payment_line_id': admission_id,
                'money_receipt_id': money_receipt_id
            }
            service_id = eve_mee_obj.create(cr, uid, vals=service_dict, context=context)
            if not service_id:
                raise osv.except_osv(_('Error!'), _('Failed to create admission payment line.'))

            # 2) Update admission due/paid (NO COMMIT)
            cr.execute(
                "UPDATE leih_admission SET due=%s, paid=%s WHERE id=%s",
                (updated_amount, updated_paid, admission_id)
            )

            # 3) Journal entry (NO COMMIT)
            journal_object = self.pool.get("bill.journal.relation")
            line_ids = []

            periods = self.pool.get('account.period').find(cr, uid, context=context)
            period_id = periods and periods[0] or False

            # Cash
            if pay_amount > 0 and pay_type_name == 'Cash':
                # Dr Cash
                line_ids.append((0, 0, {
                    'analytic_account_id': False,
                    'tax_code_id': False,
                    'tax_amount': 0,
                    'name': admission_ref,
                    'currency_id': False,
                    'credit': 0.0,
                    'date_maturity': False,
                    'account_id': 6,
                    'debit': pay_amount,
                    'amount_currency': 0.0,
                    'partner_id': False,
                }))
                # Cr AR
                line_ids.append((0, 0, {
                    'analytic_account_id': False,
                    'tax_code_id': False,
                    'tax_amount': 0,
                    'name': admission_ref,
                    'currency_id': False,
                    'credit': pay_amount,
                    'date_maturity': False,
                    'account_id': 195,
                    'debit': 0.0,
                    'amount_currency': 0.0,
                    'partner_id': False,
                }))

            # Visa Card
            if pay_amount > 0 and pay_type_name == 'Visa Card':
                other_method_pay = payment_obj.to_be_paid
                service_charge = payment_obj.service_charge

                # Dr Bank/Card account
                line_ids.append((0, 0, {
                    'analytic_account_id': False,
                    'tax_code_id': False,
                    'tax_amount': 0,
                    'name': admission_ref,
                    'currency_id': False,
                    'credit': 0.0,
                    'date_maturity': False,
                    'account_id': payment_obj.payment_type.account.id,
                    'debit': other_method_pay,
                    'amount_currency': 0.0,
                    'partner_id': False,
                }))
                # Cr AR (paid amount only)
                line_ids.append((0, 0, {
                    'analytic_account_id': False,
                    'tax_code_id': False,
                    'tax_amount': 0,
                    'name': admission_ref,
                    'currency_id': False,
                    'credit': pay_amount,
                    'date_maturity': False,
                    'account_id': 195,
                    'debit': 0.0,
                    'amount_currency': 0.0,
                    'partner_id': False,
                }))
                # Cr service charge
                if service_charge and service_charge > 0:
                    line_ids.append((0, 0, {
                        'analytic_account_id': False,
                        'tax_code_id': False,
                        'tax_amount': 0,
                        'name': admission_ref,
                        'currency_id': False,
                        'credit': service_charge,
                        'date_maturity': False,
                        'account_id': payment_obj.payment_type.service_charge_account.id,
                        'debit': 0.0,
                        'amount_currency': 0.0,
                        'partner_id': False,
                    }))

            if not line_ids:
                raise osv.except_osv(_('Error!'), _('No journal lines generated for this payment type/amount.'))

            jv_entry = self.pool.get('account.move')
            j_vals = {
                'name': '/',
                'journal_id': 2,
                'date': fields.date.today(),
                'period_id': period_id,
                'ref': admission_ref,
                'line_id': line_ids
            }

            saved_jv_id = jv_entry.create(cr, uid, j_vals, context=context)
            if not saved_jv_id:
                raise osv.except_osv(_('Error!'), _('Failed to create journal entry.'))

            # Post it
            jv_entry.button_validate(cr, uid, [saved_jv_id], context=context)

            # Relation
            journal_object.create(cr, uid, vals={
                'journal_id': saved_jv_id,
                'admission_journal_relation_id': admission_id
            }, context=context)

            cr.execute("RELEASE SAVEPOINT admission_payment_add")
            return service_id

        except Exception as e:
            try:
                cr.execute("ROLLBACK TO SAVEPOINT admission_payment_add")
            except:
                pass
            raise osv.except_osv(_('Error!'), _('Admission payment failed and rolled back: %s') % (str(e),))

    def _default_payment_type(self):
        return self.env['payment.type'].search([('name', '=', 'Cash')], limit=1).id

    _columns = {
        'name': fields.char("Cash COllection ID", readonly=True),
        'admission_id': fields.many2one('leih.admission', 'Admission ID', readoly=True),
        'date': fields.date('Date',default=datetime.today()),
        'amount': fields.float('Receive Amount', required=True),
        'payment_type': fields.many2one('payment.type', 'Payment Type', default=_default_payment_type),
        'service_charge': fields.float("Service Charge"),
        'to_be_paid': fields.float("To be Paid"),
        'account_number': fields.char('Account No.'),
        'money_receipt_id': fields.many2one('leih.money.receipt', 'Money Receipt ID'),
    }

    # -----------------------
    # CREATE (NO COMMIT, atomic)
    # -----------------------
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}

        try:
            cr.execute("SAVEPOINT admission_payment_create")

            stored = super(admission_payment, self).create(cr, uid, vals, context=context)
            if not stored:
                raise osv.except_osv(_('Error!'), _('Failed to create admission cash collection.'))

            # Set name (NO COMMIT)
            name_text = 'CC-100' + str(stored)
            cr.execute('UPDATE admission_payment SET name=%s WHERE id=%s', (name_text, stored))

            # Create Money Receipt (NO COMMIT)
            if not vals.get('admission_id'):
                raise osv.except_osv(_('Error!'), _('Admission is required to create a money receipt.'))

            value = {
                'date': vals.get('date'),
                'admission_id': vals.get('admission_id'),
                'amount': vals.get('amount', 0.0),
                'type': vals.get('payment_type'),
                'p_type': 'due_payment',
            }

            mr_object = self.pool.get("leih.money.receipt")
            mr_id = mr_object.create(cr, uid, value, context=context)
            if not mr_id:
                raise osv.except_osv(_('Error!'), _('Money receipt creation failed.'))

            mr_name = 'MR#' + str(mr_id)
            cr.execute('UPDATE leih_money_receipt SET name=%s WHERE id=%s', (mr_name, mr_id))
            cr.execute('UPDATE admission_payment SET money_receipt_id=%s WHERE id=%s', (mr_id, stored))

            cr.execute("RELEASE SAVEPOINT admission_payment_create")
            return stored

        except Exception as e:
            try:
                cr.execute("ROLLBACK TO SAVEPOINT admission_payment_create")
            except:
                pass
            raise osv.except_osv(_('Error!'), _('Admission cash collection create failed and rolled back: %s') % (str(e),))

    @api.onchange("payment_type")
    def onchnage_payment_type(self):
        if self.payment_type and self.payment_type.active is True:
            interest = self.payment_type.service_charge
            if interest and interest > 0:
                service_charge = (self.amount * interest) / 100.0
                self.service_charge = service_charge
                self.to_be_paid = self.amount + service_charge
            else:
                self.to_be_paid = self.amount
                self.service_charge = 0.0
        return "X"
