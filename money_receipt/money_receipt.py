from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class money_receipt(osv.osv):
    _name = "leih.money.receipt"


    _columns = {
        'name':fields.char("MR ID"),
        'date':fields.date("Date"),
        'bill_id':fields.many2one("bill.register","BIll ID"),
        'admission_id':fields.many2one("leih.admission","Admission ID"),
        'amount':fields.float("amount"),
        'already_collected':fields.boolean("Collected"),
        'type':fields.selection([('bank','Bank'),('cash','Cash')],string="Type"),
        'user_id':fields.many2one('res.users','Current User', default=lambda self: self.env.user.id)
    }


    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        res = super(money_receipt, self).create(cr, uid, vals, context)
          ## Update Bill regiester Paid Value

        try:
            paid_amount=0
            bill_id = [vals.get('bill_id')]
            abc = self.pool.get('bill.register').browse(cr, uid, bill_id, context=context)[0]
            paid_amount = abc.paid + float(vals.get('amount'))
            cr.execute("update bill_register set paid=%s where id=%s", ([paid_amount,bill_id]))
            cr.commit()
        except:
            pass


        return res
