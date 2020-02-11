from openerp.osv import osv, fields
from openerp import SUPERUSER_ID, api
from openerp.tools.translate import _
from datetime import datetime




class admission_payment(osv.osv):
    _name = 'admission.payment'
    _description = "admission Payment"


    # def button_add_payment_action(self,cr,uid,ids,context=None):
    #
    #     payment_obj=self.browse(cr,uid,ids,context=None)
    #     pi_id=context.get('pi_id')
    #     eve_mee_obj = self.pool.get('pi.payment.line')
    #     pay_date=payment_obj.date
    #     pay_type = payment_obj.type
    #     pay_amount = payment_obj.amount
    #     pay_usd_amount=payment_obj.usd_amount
    #
    #     service_dict={'date': pay_date, 'type': pay_type,'amount':pay_amount,'pi_id': pi_id}
    #
    #     service_id = eve_mee_obj.create(cr, uid, vals=service_dict, context=context)
    #
    #     proforma_id = self.pool.get('proforma.invoice').search(cr, uid, [('id', '=', pi_id)], context=None)
    #     proforma_object = self.pool.get('proforma.invoice').browse(cr, uid, proforma_id, context)
    #     total=proforma_object.total
    #     due_amount=total-payment_obj.amount
    #
    #     cr.execute('update proforma_invoice set due_amount=%s where id=%s',
    #                    (due_amount,pi_id))
    #     cr.commit()
    #     # import pdb
    #     # pdb.set_trace()
    #     return service_id




    _columns = {
        'amount': fields.float('Amount', required=True),
        'date': fields.datetime('Date'),
        'type': fields.char('Type'),
        'usd_amount':fields.float('USD'),
        'pi_id': fields.many2one('proforma.invoice', 'PI ID'),

    }


