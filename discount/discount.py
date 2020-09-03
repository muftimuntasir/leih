from openerp import api
from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class discount(osv.osv):
    _name = "discount"
    # _rec_name = 'patient_id'


    _columns = {

        'bill_no': fields.many2one('bill.register','Bill No'),
        'patient_name': fields.char("Patient Name",required=True),
        'name': fields.char("Discount Number"),
        'mobile': fields.char("Mobile Number", required=True),
        'total_discount':fields.float('Total Discount'),
        'amount': fields.integer("Amount"),
        'state': fields.selection([
            ('pending', 'Pending'),
            ('approve', 'Approved'),
            ('cancel', 'Cancelled')],'State',default='pending',readonly=True),
        'discount_line_id': fields.one2many("discount.line",'discount_id','Discount Line    ',required=True),
    }

    def approve_discount(self,cr,uid,ids,context=None):
        if ids is not None:
            cr.execute("update discount set state='approve' where id=%s", (ids))
            cr.commit()
        return True
    def cancel_discount(self,cr,uid,ids,context=None):
        if ids is not None:
            cr.execute("update discount set state='cancel' where id=%s", (ids))
            cr.commit()
        return True


    def onchange_bill(self,cr,uid,ids,bill_no,context=None):
        tests = {'values': {}}
        dep_object = self.pool.get('bill.register').browse(cr, uid,bill_no, context=None)
        patient_name=dep_object.patient_name.name
        mobile=dep_object.patient_name.mobile
        amount=dep_object.total
        abc = {'patient_name': patient_name,'mobile':mobile,'amount':amount}
        tests['value'] = abc
        return tests

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}

        stored = super(discount, self).create(cr, uid, vals, context)  # return ID int object
        bill_id=vals.get('bill_no')
        bill_object=self.pool.get('bill.register').browse(cr,uid,bill_id,context=None)
        stored_obj = self.browse(cr, uid, [stored], context=context)
        discount_values=[]
        discount_fixed_amount=[]
        for item in stored_obj.discount_line_id:
            discount_amount_percent=int(item.percent_amount)
            discount_fixed=item.fixed_amount
            discount_values.append(discount_amount_percent)
            discount_fixed_amount.append(discount_fixed)
        total_percent=sum(discount_values)
        total_fixed=sum(discount_fixed_amount)
        total_amount=stored_obj.amount
        percent_discounted_amount=(total_amount*total_percent)/100
        total_discount=percent_discounted_amount+total_fixed

        cr.execute('update discount set total_discount=%s where id=%s', (total_discount, stored))
        cr.execute('update bill_register set other_discount=%s where id=%s', (total_discount, bill_id))
        cr.commit()


        # if stored is not None:
        #     discount_line_obj = vals.get('discount_line_id')
        #     discount_line_id=discount_line_obj[0][2]['type']
        #     discount_lines=self.pool.get('discount.core.type').browse(cr,uid,discount_line_id,context=None)
        #     discount_type=discount_lines.name
        #     discount_amount=discount_lines.discount_amount
        # import pdb
        # pdb.set_trace()

            #
            # cr.execute('update bill_register set discount_type=%s,discounts=%s where id=%s', (discount_type,discount_amount, bill_id))
            # cr.commit()

        # import pdb
        # pdb.set_trace()


        if stored is not None:
            name_text = 'Dis-10' + str(stored)
            cr.execute('update discount set name=%s where id=%s', (name_text, stored))
            cr.commit()
        return stored

class discount_line(osv.osv):
    _name = "discount.line"
    # _rec_name = 'patient_id'


    _columns = {

        'type':fields.many2one('discount.core.type', 'Discount Type'),
        'category':fields.char('Category'),
        'ref': fields.char("Reference"),
        'accounts':fields.char("Account Name"),
        'fixed_amount': fields.integer("Amount(fixed)"),
        'percent_amount': fields.integer("Amount(%)"),
        'discount_id': fields.many2one("discount","discount Id"),
    }

    def onchange_type(self,cr,uid,ids,type,context=None):
        values={}
        discount_type_obj=self.pool.get('discount.core.type').browse(cr,uid,type,context=None)
        category_id=discount_type_obj.category_id.name
        amount=discount_type_obj.discount_amount
        accounts=discount_type_obj.account_id
        new_dict={'category':category_id,'percent_amount':amount,'accounts':accounts}
        values['value']=new_dict
        return values
