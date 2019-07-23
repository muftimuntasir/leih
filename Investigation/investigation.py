from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class investigation(osv.osv):
    _name = "leih.investigation"


    # def total_amount_all(self, cr, uid, ids, field_name, arg, context=None):
    #     cur_obj = self.pool.get('leih.investigation')
    #     res = {}
    #     for record in self.browse(cr, uid, ids, context=context):
    #         rate=record.price
    #         discount=record.discount
    #         interst_amount=int(discount)*int(rate)/100
    #         total=int(rate)-interst_amount
    #         res[record.id]=total
    #     return res



    _columns = {

        'patient_id': fields.char("Patient ID"),
        'mobile': fields.char("Mobile"),
        'name': fields.many2one('leih.patients', "Name"),
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

    def onchange_total(self,cr,uid,ids,name,context=None):
        tests = {'values': {}}
        dep_object = self.pool.get('leih.tests').browse(cr, uid, name, context=None)
        abc = {'total': dep_object.rate}
        tests['value'] = abc
        # import pdb
        # pdb.set_trace()
        return tests



    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}

        stored = super(investigation, self).create(cr, uid, vals, context) # retunr ID nt object

        stored_obj = self.browse(cr, uid, [stored], context=context)
                        # Self means model
                        # brouse means select query proepare






        for items in stored_obj.entrr_test_information:
            value = {
                'investigation_id':int(stored),
                'tests_id':int(items.id),
                'department_id':items.name.department
            }
            # import pdb
            # pdb.set_trace()

            sample_obj = self.pool.get('leih.sample')
            sample_obj.create(cr, uid, value, context=context)
        for item in stored_obj.entrr_test_information.name:

            values = {
                'test_name':item.name,
                'ref_value': item.department,
                'result': item.required_time
            }



            samples_obj = self.pool.get('leih.testsample')
            samples_obj.create(cr, uid, values, context=context)
            # import pdb
            # pdb.set_trace()
        return 1








class test_information(osv.osv):
    _name = 'leih.tests'







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

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('leih.investigation')
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            rate=record.price
            discount=record.discount
            interst_amount=int(discount)*int(rate)/100
            total_amount=int(rate)-interst_amount
            res[record.id]=total_amount
            # import pdb
            # pdb.set_trace()
        return res




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




# class footer(osv.osv):
#     _name = 'leih.footer'
#
#     _columns = {
#
#         'relation':fields.many2one("leih.investigation"),
#         'total': fields.float("Total",required=True),
#         'discount': fields.float("Discount(%)", required=True),
#         'flat_discount': fields.float("Flat Discount"),
#         'grand_total': fields.float("Grand Total"),
#         'paid':fields.float("Paid"),
#         'due': fields.char("Due"),
#
#     }


    # def onchange_tamount(self,cr,uid,ids,name,context=None):
    #     testss = {'values': {}}
    #     dep_object = self.pool.get('leih.testentry').browse(cr, uid, name, context=None)
    #     abcd = {'total_amount': dep_object.rate}
    #     testss['value'] = abcd
    #     # import pdb
    #     # pdb.set_trace()
    #     return testss



# class footer(osv.osv):
#     _name = "leih.footer"
#
#
#
#
#
#
#     _columns = {
#
#         'relation':fields.many2one("leih.investigation"),
#         'total': fields.float("Total",required=True),
#         'discount': fields.float("Discount(%)", required=True),
#         'flat_discount': fields.float("Flat Discount"),
#         'grand_total': fields.float("Grand Total"),
#         'paid':fields.float("Paid"),
#         'due': fields.char("Due"),
#
#     }

    # def onchange_pation_info(self,cr,uid,ids,name,context=None):
    #     testss = {'values': {}}
    #     dep_object = self.pool.get('leih.patients').browse(cr, uid, name, context=None)
    #     abcd = {'name': dep_object.name, 'address':dep_object.address}
    #     testss['value'] = abcd
    #     # import pdb
    #     # pdb.set_trace()
    #     return testss