from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class bill_register(osv.osv):
    _name = "bill.register"


    _columns = {

        'patient_id': fields.char("Patient ID"),
        'name':fields.char("Name"),
        'mobile': fields.char("Mobile"),
        'patient_name': fields.many2one('patient.info', "Patient Name"),
        'address': fields.char("Address",),
        'age': fields.char("Age"),
        'sex':fields.char("Sex"),
        'ref_doctors': fields.selection([('shafi', 'Dr. Md. Shafi Khan'), ('ssg', 'Dr. S S Gazi'),('sabrina','Dr. Sabrina Rahmatullah'),('Bibek','Dr. Bibek Ananda')], string='Ref. Doctorss', default='shafi'),
        'delivery_date': fields.char("Delivery Date"),
        'bill_register_line_id': fields.one2many('bill.register.line', 'bill_register_id', 'Investigations', required=True),
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

    def onchange_patient(self,cr,uid,ids,name,context=None):
        tests={'values':{}}
        dep_object = self.pool.get('patient.info').browse(cr, uid, name, context=None)
        abc={'mobile':dep_object.mobile}
        tests['value']=abc
        return tests




    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}

        stored = super(bill_register, self).create(cr, uid, vals, context) # retunr ID nt object

        stored_obj = self.browse(cr, uid, [stored], context=context)
                        # Self means model
                        # brouse means select query proepare




        for items in stored_obj.bill_register_line_id:
            child_list = []
            value = {
                'bill_register_id':int(stored),
                'tests_id':int(items.id),
                'department_id':items.name.department,
            }

            tmp_dict = {}
            for test_item in items.name.examination_entry_line:
                tmp_dict['test_name'] = test_item.name
                tmp_dict['ref_value'] = test_item.reference_value
                child_list.append([0, False, tmp_dict])
            value['sticker_line_id']=child_list
            # import pdb
            # pdb.set_trace()

            sample_obj = self.pool.get('diagnosis.sticker')
            sample_id = sample_obj.create(cr, uid, value, context=context)


        return 1








class test_information(osv.osv):
    _name = 'bill.register.line'



    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('bill.register')
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

        'name': fields.many2one("examination.entry","Test Name", required=True, ondelete='cascade'),
        'bill_register_id': fields.many2one('bill.register', "Information"),
        # 'currency_id': fields.related('pricelist_id', 'currency_id', type="many2one", relation="res.currency",
        #                               string="Currency", readonly=True, required=True),
        # 'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute=dp.get_precision('Account')),
        'price': fields.integer("Price"),
        'discount': fields.integer("Discount"),
        'total_amount': fields.integer("Total Amount"),

    }

    def onchange_test(self,cr,uid,ids,name,context=None):
        tests = {'values': {}}
        dep_object = self.pool.get('examination.entry').browse(cr, uid, name, context=None)
        abc = {'price': dep_object.rate,'total_amount':dep_object.rate}
        tests['value'] = abc
        # import pdb
        # pdb.set_trace()
        return tests

    def onchange_discount(self,cr,uid,ids,name,discount,context=None):
        tests = {'values': {}}
        dep_object = self.pool.get('examination.entry').browse(cr, uid, name, context=None)
        abc = {'total_amount':round(dep_object.rate-(dep_object.rate* discount/100))}
        tests['value'] = abc
        # import pdb
        # pdb.set_trace()
        return tests

