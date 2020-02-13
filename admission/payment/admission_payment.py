from openerp.osv import osv, fields
from openerp import SUPERUSER_ID, api
from openerp.tools.translate import _
from datetime import datetime




class admission_payment(osv.osv):
    _name = 'admission.payment'
    _description = "admission Payment"


    def button_add_payment_action(self,cr,uid,ids,context=None):

        payment_obj=self.browse(cr,uid,ids,context=None)
        admission_id=context.get('admission_id')
        eve_mee_obj = self.pool.get('admission.payment.line')
        pay_date=payment_obj.date
        pay_amount = payment_obj.amount
        pay_type = payment_obj.type
        pay_card=payment_obj.card_no
        pay_bank=payment_obj.bank_name

        service_dict={'date': pay_date,'amount':pay_amount,'type': pay_type,'card_no':pay_card ,'admission_payment_line_id': admission_id}

        service_id = eve_mee_obj.create(cr, uid, vals=service_dict, context=context)

        return service_id

    _columns = {
        'name':fields.char("Cash COllection ID", readonly=True),
        'date': fields.datetime('Date'),
        'amount': fields.float('Receive Amount', required=True),
        'type': fields.selection([('bank','Bank'),('cash','Cash')],'Type'),
        'card_no':fields.char('Card No.'),
        'bank_name':fields.char('Bank Name'),
        'admission_id': fields.many2one('leih.admission', 'Admission ID',readonly=True)

    }

    def create(self,cr,uid,vals,context):
        stored = super(admission_payment, self).create(cr, uid, vals, context)  # return ID int object

        if stored is not None:
            name_text = 'CC-100' + str(stored)
            cr.execute('update admission_payment set name=%s where id=%s', (name_text, stored))
            cr.commit()
        return stored

# class inherited_admision(osv.osv):
#     _inherits = "leih.admission"
#
#     _columns = {
#         ''
#     }
#

