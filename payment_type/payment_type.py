from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time
from openerp import SUPERUSER_ID, api

class payment_type(osv.osv):
    _name = "payment.type"

    _columns = {

        'name': fields.char("Name",required=True),
        'account': fields.many2one('account.account', string='Account',required=True),
        'service_charge_account': fields.many2one('account.account', string='Service Charge Account'),
        'service_charge': fields.float("Service Charge", required=True),
        'service_charge_flat': fields.char("Service Charge(Flat)"),
        'active':fields.boolean("Active")
    }


class bill_register(osv.osv):
    _inherit = "bill.register"
    def _default_payment_type(self):
         return self.env['payment.type'].search([('name', '=', 'Cash')], limit=1).id

    # def _default_payment_type(self):
    #      return self.env['payment.type'].search([('name', '=', 'Cash')], limit=1).id

    _columns = {
        'payment_type':fields.many2one("payment.type","Payment Type", default=_default_payment_type),
        'service_charge':fields.float("Service Charge"),
        'to_be_paid':fields.float("To be Paid"),
        'account_number':fields.char("Account Number")
    }

    @api.onchange("payment_type")
    def onchnage_payment_type(self):
        if self.payment_type.active==True:
            interest=self.payment_type.service_charge
            if interest>0:
                service_charge=(self.paid*interest)/100
                self.service_charge=service_charge
                self.to_be_paid=self.paid+service_charge
            else:
                self.to_be_paid=self.paid
                self.service_charge=0
        return "X"


class leih_admission(osv.osv):
    _inherit = "leih.admission"

    def _default_payment_type(self):
         return self.env['payment.type'].search([('name', '=', 'Cash')], limit=1).id

    _columns = {
        'payment_type':fields.many2one("payment.type","Payment Type", default=_default_payment_type),
        'service_charge':fields.float("Service Charge"),
        'to_be_paid':fields.float("To be Paid"),
        'account_number':fields.char("Account Number")
    }

    @api.onchange("payment_type")
    def onchnage_payment_type(self):
        if self.payment_type.active==True:
            interest=self.payment_type.service_charge
            if interest>0:
                service_charge=(self.paid*interest)/100
                self.service_charge=service_charge
                self.to_be_paid=self.paid+service_charge
            else:
                self.to_be_paid=self.paid
                self.service_charge=0
        return "X"


class optics_sale(osv.osv):
    _inherit = "optics.sale"

    def _default_payment_type(self):
         return self.env['payment.type'].search([('name', '=', 'Cash')], limit=1).id

    _columns = {
        'payment_type':fields.many2one("payment.type","Payment Type", default=_default_payment_type),
        'service_charge':fields.float("Service Charge"),
        'to_be_paid':fields.float("To be Paid"),
        'account_number':fields.char("Account Number")
    }

    @api.onchange("payment_type")
    def onchnage_payment_type(self):
        if self.payment_type.active==True:
            interest=self.payment_type.service_charge
            if interest>0:
                service_charge=(self.paid*interest)/100
                self.service_charge=service_charge
                self.to_be_paid=self.paid+service_charge
            else:
                self.to_be_paid=self.paid
                self.service_charge=0
        return "X"






