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
        'entrr_test_information': fields.one2many('ti', 'test_info', 'Parameters', required=True)
    }


class test_information(osv.osv):
    _name = 'ti'
    _columns = {

        'name': fields.char("Name", required=True, ondelete='cascade', select=True),
        'test_info': fields.many2one('leih.investigation', "Information"),
        'price': fields.char("Price"),
        'discount': fields.char("Discount"),
        'total_amount': fields.char("Total Amount"),
    }



