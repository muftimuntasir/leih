from openerp.osv import osv, fields
from openerp import SUPERUSER_ID, api
from openerp.tools.translate import _
from datetime import datetime




class optics_sale_payment(osv.osv):
    _name = 'optics.sale.payment'
    _description = "optics sale Payment"


    def button_add_payment_action(self,cr,uid,ids,context=None):

        payment_obj=self.browse(cr,uid,ids,context=None)
        optics_sale_id=payment_obj.optics_sale_id.id
        eve_mee_obj = self.pool.get('optics.sale.payment.line')
        pay_date=payment_obj.date
        pay_amount = payment_obj.amount
        pay_type = payment_obj.type
        pay_card=payment_obj.card_no
        pay_bank=payment_obj.bank_name
        current_due =payment_obj.optics_sale_id.due
        current_paid =payment_obj.optics_sale_id.paid
        money_receipt_id =payment_obj.money_receipt_id.id

        updated_amount = current_due-pay_amount
        updated_paid = current_paid+pay_amount
        if updated_amount <0:
            updated_amount=0







        service_dict={'date': pay_date,'amount':pay_amount,'type': pay_type,'card_no':pay_card ,'optics_sale_payment_line_id': optics_sale_id,'money_receipt_id':money_receipt_id}

        service_id = eve_mee_obj.create(cr, uid, vals=service_dict, context=context)

        cr.execute("update optics_sale set due=%s,paid=%s where id=%s", (updated_amount,updated_paid,optics_sale_id))
        cr.commit()


        return service_id

    _columns = {
        'name':fields.char("Cash Collection ID", readonly=True),
        'optics_sale_id': fields.many2one('optics.sale', 'Optics Bill ID', readoly=True),
        'date': fields.date('Date',required=True),
        'amount': fields.float('Receive Amount', required=True),
        'type': fields.selection([('bank','Bank'),('cash','Cash')],'Type', required=True),
        'card_no':fields.char('Card No.'),
        'bank_name':fields.char('Bank Name'),
        'money_receipt_id': fields.many2one('leih.money.receipt', 'Money Receipt ID'),
    }

    def create(self,cr,uid,vals,context):
        storedpayment = super(optics_sale_payment, self).create(cr, uid, vals, context)  # return ID int object

        if storedpayment is not None:
            name_text = 'CC-100' + str(storedpayment)
            cr.execute('update optics_sale_payment set name=%s where id=%s', (name_text, storedpayment))
            cr.commit()
        value={}
        value['date']=vals['date']
        value['optics_sale_id']=vals['optics_sale_id']
        value['amount']=vals['amount']
        value['type']=vals['type']
        value['p_type']='due_payment'
        # value['user_id']=vals['user_id']

        mr_object=self.pool.get("leih.money.receipt")
        mr_id=mr_object.create(cr, uid, value, context=context)

        stored_obj = self.pool.get("optics.sale").browse(cr, uid, vals['optics_sale_id'], context=None)

        ## Bill Status Will Change

        # if stored_obj.state == 'confirmed':
        #     raise osv.except_osv(_('Warning!'),
        #                          _('Already this Bill is Confirmed.'))
        grand_total = stored_obj.grand_total
        if grand_total != 0:
            cr.execute("update optics_sale set state='confirmed' where id=%s", ([vals['optics_sale_id']]))
            cr.commit()

            stored = int(vals['optics_sale_id'])

            ### check and merged with Lab report





        if mr_id is not None:
            mr_name='MR#' +str(mr_id)
            cr.execute('update leih_money_receipt set name=%s where id=%s',(mr_name,mr_id))
            cr.execute('update optics_sale_payment set money_receipt_id=%s where id=%s',(mr_id,storedpayment))
            cr.commit()

        #confirm on paid





        return storedpayment
