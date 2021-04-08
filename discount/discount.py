from openerp import api
from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class discount(osv.osv):
    _name = "discount"
    _order = 'id desc'
    # _rec_name = 'patient_id'


    _columns = {

        'name': fields.char("Discount Number"),
        'admission_id':fields.many2one("leih.admission","Admission ID"),
        'bill_no': fields.many2one('bill.register','Bill No'),
        'patient_name': fields.char("Patient Name",required=True),
        'mobile': fields.char("Mobile Number", required=True),
        'total_discount':fields.float('Total Discount'),
        'amount': fields.integer("Amount"),
        'state': fields.selection([
            ('pending', 'Pending'),
            ('approve', 'Approved'),
            ('cancel', 'Cancelled')],'State',default='pending',readonly=True),
        'discount_line_id': fields.one2many("discount.line",'discount_id','Discount Line',required=True),
    }

    def approve_discount(self,cr,uid,ids,context=None):
        discount_object = self.browse(cr, uid, ids, context=None)
        bill_id=discount_object.bill_no.id
        admission_id=discount_object.admission_id.id
        total_discount=discount_object.total_discount
        # import pdb
        # pdb.set_trace()

        # confirm button code
        if bill_id != False:
            # fetching data from bill_register
            query = "select grand_total,paid,due from bill_register where id=%s"
            cr.execute(query, ([bill_id]))
            all_data = cr.dictfetchall()
            # grand_total = 0
            # paid_amount = 0
            # due_amount = 0
            for item in all_data:
                grand_total = item.get('grand_total')
                paid_amount = item.get('paid')
                due_amount = item.get('due')
            if due_amount < total_discount:
                raise osv.except_osv(_('Warning!'),
                                     _('Not permissed to make discount more than due!'))
            elif due_amount >= total_discount:
                grand_total = grand_total - total_discount
                due_amount = due_amount - total_discount

            cr.execute('update bill_register set other_discount=%s,grand_total=%s,due=%s where id=%s',
                       (total_discount, grand_total, due_amount, bill_id))
            cr.commit()

        elif admission_id != False:
            query = "select grand_total,paid,due from leih_admission where id=%s"
            cr.execute(query, ([admission_id]))
            all_data = cr.dictfetchall()
            grand_total = 0
            paid_amount = 0
            due_amount = 0
            for item in all_data:
                grand_total = item.get('grand_total')
                paid_amount = item.get('paid')
                due_amount = item.get('due')
            if due_amount <= total_discount:
                total_discount = due_amount
                grand_total = grand_total - total_discount
                due_amount = due_amount - total_discount
            elif due_amount > total_discount:
                grand_total = grand_total - total_discount
                due_amount = due_amount - total_discount
            cr.execute('update leih_admission set other_discount=%s,grand_total=%s,due=%s where id=%s',
                       (total_discount, grand_total, due_amount, admission_id))
            cr.commit()

        # end confirm button code


        if ids is not None:
            cr.execute("update discount set state='approve' where id=%s", (ids))
            cr.commit()
        return True
    def cancel_discount(self,cr,uid,ids,context=None):
        if ids is not None:
            cr.execute("update discount set state='cancel' where id=%s", (ids))
            cr.commit()
        return True


    @api.onchange('discount_line_id')
    def onchange_discount_item(self):
        total_amount=self.amount
        listfixed=[]
        listpercent=[]

        for item in self.discount_line_id:
            fixed_amount=item.fixed_amount
            percent_amount=item.percent_amount
            listfixed.append(fixed_amount)
            listpercent.append(percent_amount)
        total_percent = sum(listpercent)
        total_fixed = sum(listfixed)
        percent_discounted_amount = (total_amount * total_percent) / 100
        total_discount=total_fixed+percent_discounted_amount
        self.total_discount=total_discount





        return "X"


    def onchange_bill(self,cr,uid,ids,bill_no,context=None):
        tests = {'values': {}}
        dep_object = self.pool.get('bill.register').browse(cr, uid,bill_no, context=None)
        patient_name=dep_object.patient_name.name
        mobile=dep_object.patient_name.mobile
        amount=dep_object.due
        abc = {'patient_name': patient_name,'mobile':mobile,'amount':amount}
        tests['value'] = abc
        return tests
    def onchange_admission(self,cr,uid,ids,admission_id,context=None):
        tests = {'values': {}}
        dep_object = self.pool.get('leih.admission').browse(cr, uid,admission_id, context=None)
        patient_name=dep_object.patient_name.name
        mobile=dep_object.patient_name.mobile
        amount=dep_object.grand_total
        abc = {'patient_name': patient_name,'mobile':mobile,'amount':amount}
        tests['value'] = abc
        return tests

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}

        stored = super(discount, self).create(cr, uid, vals, context)  # return ID int object

        if stored is not None:
            name_text = 'Dis-10' + str(stored)
            cr.execute('update discount set name=%s where id=%s', (name_text, stored))
            cr.commit()
        return stored

class discount_line(osv.osv):
    _name = "discount.line"
    # _rec_name = 'patient_id'


    _columns = {

        'category':fields.many2one('discount.category', 'Discount Category'),
        # 'category':fields.char('Category'),
        'ref': fields.char("Reference"),
        'accounts':fields.many2one("account.account","Account Name"),
        'fixed_amount': fields.integer("Amount(fixed)"),
        'percent_amount': fields.integer("Amount(%)"),
        'discount_id': fields.many2one("discount","discount Id")
    }

    # def onchange_type(self,cr,uid,ids,type,context=None):
    #     values={}
    #     discount_type_obj=self.pool.get('discount.core.type').browse(cr,uid,type,context=None)
    #     category_id=discount_type_obj.category_id.name
    #     amount=discount_type_obj.discount_amount
    #     accounts=discount_type_obj.account_id
    #     new_dict={'category':category_id,'percent_amount':amount,'accounts':accounts}
    #     values['value']=new_dict
    #     return values
