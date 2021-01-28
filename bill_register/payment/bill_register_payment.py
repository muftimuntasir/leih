from openerp.osv import osv, fields
from openerp import SUPERUSER_ID, api
from openerp.tools.translate import _
from datetime import datetime




class bill_register_payment(osv.osv):
    _name = 'bill.register.payment'
    _description = "bill register Payment"


    def button_add_payment_action(self,cr,uid,ids,context=None):

        payment_obj=self.browse(cr,uid,ids,context=None)
        bill_id=payment_obj.bill_id.id
        eve_mee_obj = self.pool.get('bill.register.payment.line')
        pay_date=payment_obj.date
        pay_amount = payment_obj.amount
        pay_type = payment_obj.type
        pay_card=payment_obj.card_no
        pay_bank=payment_obj.bank_name
        current_due =payment_obj.bill_id.due
        current_paid =payment_obj.bill_id.paid

        updated_amount = current_due-pay_amount
        updated_paid = current_paid+pay_amount
        if updated_amount <0:
            updated_amount=0







        service_dict={'date': pay_date,'amount':pay_amount,'type': pay_type,'card_no':pay_card ,'bill_register_payment_line_id': bill_id}

        service_id = eve_mee_obj.create(cr, uid, vals=service_dict, context=context)

        cr.execute("update bill_register set due=%s,paid=%s where id=%s", (updated_amount,updated_paid,bill_id))
        cr.commit()


        return service_id

    _columns = {
        'name':fields.char("Cash Collection ID", readonly=True),
        'bill_id': fields.many2one('bill.register', 'Bill ID', readoly=True),
        'date': fields.date('Date'),
        'amount': fields.float('Receive Amount', required=True),
        'type': fields.selection([('bank','Bank'),('cash','Cash')],'Type'),
        'card_no':fields.char('Card No.'),
        'bank_name':fields.char('Bank Name'),
    }

    def create(self,cr,uid,vals,context):
        stored = super(bill_register_payment, self).create(cr, uid, vals, context)  # return ID int object

        if stored is not None:
            name_text = 'CC-100' + str(stored)
            cr.execute('update bill_register_payment set name=%s where id=%s', (name_text, stored))
            cr.commit()
        value={}
        value['date']=vals['date']
        value['bill_id']=vals['bill_id']
        value['amount']=vals['amount']
        value['type']=vals['type']
        # value['user_id']=vals['user_id']

        mr_object=self.pool.get("leih.money.receipt")
        mr_id=mr_object.create(cr, uid, value, context=context)
        # import pdb
        # pdb.set_trace()
        paid_amount = 0
        # try:
        #     paid_amount=0
        #     bill_id = [vals.get('bill_id')]
        #     abc = self.pool.get('bill.register').browse(cr, uid, bill_id, context=context)[0]
        #     paid_amount = abc.paid + float(vals.get('amount'))
        #     import pdb
        #     pdb.set_trace()
        #     cr.execute("update bill_register set paid=%s where id=%s", (paid_amount,bill_id))
        #     cr.commit()
        # except:
        #     pass

        if mr_id is not None:
            mr_name='mr#' +str(mr_id)
            cr.execute('update leih_money_receipt set name=%s where id=%s',(mr_name,mr_id))
            cr.commit()
        return stored



# class inherited_admision(osv.osv):
#     _inherits = "leih.admission"
#
#     _columns = {
#         ''
#     }
#

