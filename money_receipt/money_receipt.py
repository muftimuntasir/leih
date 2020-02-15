from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class money_receipt(osv.osv):
    _name = "leih.money.receipt"


    _columns = {
        'name':fields.char("MR ID"),
        'date':fields.datetime("Date"),
        'bill_id':fields.many2one("bill.register","BIll ID"),
        'admission_id':fields.many2one("leih.admission","Admission ID"),
        'amount':fields.float("amount"),
        'type':fields.selection([('bank','Bank'),('cash','Cash')],string="Type"),
        'user_id':fields.many2one('res.users','Current User', default=lambda self: self.env.user.id)
    }
