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

        if stored is not None:
            name_text = 'Dis-10' + str(stored)
            cr.execute('update discount set name=%s where id=%s', (name_text, stored))
            cr.commit()
        return stored

class discount_line(osv.osv):
    _name = "discount.line"
    # _rec_name = 'patient_id'


    _columns = {

        'type':fields.selection([('blf','BLF'),('staff','Staff'),('zakat','Zakat'),('others','Others')], 'Discount Type',default='blf'),
        'ref': fields.char("Reference"),
        'account_id': fields.many2one("account.account","Account"),
        'fixed_amount': fields.integer("Amount(fixed)"),
        'percent_amount': fields.integer("Amount(%)"),
        'discount_id': fields.many2one("discount","discount Id"),
    }