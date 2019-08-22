from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class patient_info(osv.osv):
    _name = "patient.info"




    _columns = {

        'mobile': fields.char("Mobile No",required=True),
        'name': fields.char("Patient Name",required=True),
        'age':fields.char('Age',required=True),
        'address':fields.char('Address',required=True),
        'sex': fields.selection([('male', 'Male'), ('female', 'Female'),('others','Others')], string='Sex', default='male')


    }