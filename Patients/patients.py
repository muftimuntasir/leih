from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class leih(osv.osv):
    _name = "leih.patients"




    _columns = {

        'mobile': fields.char("Mobile No",required=True),
        'name': fields.char("Patient Name",required=True),
        'age':fields.char('Age',required=True),
        'address':fields.char('Address',required=True),
        'sex': fields.selection([('a', 'Male'), ('b', 'Female'),('c','Others/Al-Amin')], string='Sex', default='a')


    }