from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class investigation(osv.osv):
    _name = "leih.investigation"






    _columns = {

        'patient_id': fields.char("Patient ID",required=True),
        'mobile': fields.char("Mobile", required=True),
        'name': fields.many2one('leih.patients', "Name", required=True),
        'address': fields.char("Address",),
        'age': fields.char("Age"),
        'sex':fields.char("Sex"),
        'ref_doctors': fields.selection([('shafi', 'Dr. Md. Shafi Khan'), ('ssg', 'Dr. S S Gazi'),('sabrina','Dr. Sabrina Rahmatullah'),('Bibek','Dr. Bibek Ananda')], string='Ref. Doctorss', default='shafi'),
        'delivery_date': fields.char("Delivery Date"),
        'entrr_test_information': fields.one2many('leih.tests', 'test_info', 'Parameters', required=True),
        # 'footer_connection': fields.one2many('leih.footer', 'relation', 'Parameters', required=True),
        # 'relation': fields.many2one("leih.investigation"),
        'total': fields.float("Total", required=True),
        'discounts': fields.float("Discount(%)", required=True),
        'flat_discount': fields.float("Flat Discount"),
        'grand_total': fields.float("Grand Total"),
        'paid': fields.float("Paid"),
        'due': fields.float("Due"),


    }
    # def onchange_pation_info(self,cr,uid,ids,name,context=None):
    #     testss = {'values': {}}
    #     dep_object = self.pool.get('leih.patients').browse(cr, uid, name, context=None)
    #     abcd = {'name': dep_object.name, 'address':dep_object.address}
    #     testss['value'] = abcd
    #     # import pdb
    #     # pdb.set_trace()
    #     return testssstash

class test_information(osv.osv):
    _name = 'leih.tests'

<<<<<<< HEAD





    # def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
    #     cur_obj = self.pool.get('leih.investigation')
    #     res = {}
    #     for record in self.browse(cr, uid, ids, context=context):
    #         rate=record.price
    #         discount=record.discount
    #         interst_amount=int(discount)*int(rate)/100
    #         total_amount=int(rate)-interst_amount
    #         res[record.id]=total_amount
    #     return res
=======
    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('leih.investigation')
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            rate=record.price
            discount=record.discount
            interst_amount=int(discount)*int(rate)/100
            total_amount=int(rate)-interst_amount
            res[record.id]=total_amount
        return res
>>>>>>> 25a05ec2c5ecb45b223c05ef4b26ec153a0455d4



    _columns = {

        'name': fields.many2one("leih.testentry","Test Name", required=True, ondelete='cascade'),
        'test_info': fields.many2one('leih.investigation', "Information"),
        # 'currency_id': fields.related('pricelist_id', 'currency_id', type="many2one", relation="res.currency",
        #                               string="Currency", readonly=True, required=True),
        # 'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute=dp.get_precision('Account')),
        'price': fields.integer("Price"),
        'discount': fields.integer("Discount"),
        'total_amount': fields.integer("Total Amount"),

    }

    def onchange_test(self,cr,uid,ids,name,context=None):
        tests = {'values': {}}
        dep_object = self.pool.get('leih.testentry').browse(cr, uid, name, context=None)
        abc = {'price': dep_object.rate,'total_amount':dep_object.rate}
        tests['value'] = abc
        # import pdb
        # pdb.set_trace()
        return tests

    def onchange_discount(self,cr,uid,ids,name,discount,context=None):
        tests = {'values': {}}
        dep_object = self.pool.get('leih.testentry').browse(cr, uid, name, context=None)
        abc = {'total_amount':round(dep_object.rate-(dep_object.rate* discount/100))}
        tests['value'] = abc
        # import pdb
        # pdb.set_trace()
        return tests



    # def onchange_tamount(self,cr,uid,ids,name,context=None):
    #     testss = {'values': {}}
    #     dep_object = self.pool.get('leih.testentry').browse(cr, uid, name, context=None)
    #     abcd = {'total_amount': dep_object.rate}
    #     testss['value'] = abcd
    #     # import pdb
    #     # pdb.set_trace()
    #     return testss


class footer(osv.osv):
    _name = "leih.footer"






    _columns = {

        'relation':fields.many2one("leih.investigation"),
        'total': fields.float("Total",required=True),
        'discount': fields.float("Discount(%)", required=True),
        'flat_discount': fields.float("Flat Discount"),
        'grand_total': fields.float("Grand Total"),
        'paid':fields.float("Paid"),
        'due': fields.char("Due"),

    }
    # def onchange_pation_info(self,cr,uid,ids,name,context=None):
    #     testss = {'values': {}}
    #     dep_object = self.pool.get('leih.patients').browse(cr, uid, name, context=None)
    #     abcd = {'name': dep_object.name, 'address':dep_object.address}
    #     testss['value'] = abcd
    #     # import pdb
    #     # pdb.set_trace()
    #     return testss