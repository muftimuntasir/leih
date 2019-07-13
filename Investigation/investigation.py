from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class investigation(osv.osv):
    _name = "leih.investigation"






    _columns = {

        'patient_id': fields.char("Patient ID",required=True),
        'mobile': fields.char("Mobile", required=True),
        'name': fields.char("Test Name", required=True),
        'address': fields.char("Address",),
        'age': fields.char("Age"),
        'sex':fields.char("Sex"),
        'ref_doctors': fields.selection([('shafi', 'Dr. Md. Shafi Khan'), ('ssg', 'Dr. S S Gazi'),('sabrina','Dr. Sabrina Rahmatullah'),('Bibek','Dr. Bibek Ananda')], string='Ref. Doctorss', default='shafi'),
        'delivery_date': fields.char("Delivery Date"),
        'entrr_test_information': fields.one2many('leih.tests', 'test_info', 'Parameters', required=True)
    }


class test_information(osv.osv):
    _name = 'leih.tests'


    def _price_update(self, cr, uid, ids, name, arg, context=None):



    _columns = {

        'name': fields.many2one("leih.testentry", required=True, ondelete='cascade'),
        'test_info': fields.many2one('leih.investigation', "Information"),
        'price': fields.char("Price"),
        'discount': fields.char("Discount"),
        'total_amount': fields.function(_price_update,type='char', string="Total")
    }

    def onchange_test(self,cr,uid,ids,name,context=None):
        tests = {'values': {}}
        dep_object = self.pool.get('leih.testentry').browse(cr, uid, name, context=None)
        abc = {'price': dep_object.rate}
        tests['value'] = abc
        # import pdb
        # pdb.set_trace()
        return tests



