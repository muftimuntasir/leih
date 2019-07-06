from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class leih(osv.osv):
    _name = "leih.department"




    _columns = {

        'department_name': fields.char("Department Name",required=True),
        'parent':fields.selection([('a','A'),('b','B')], string='Parent', default='a')

    }