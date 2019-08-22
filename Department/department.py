from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class diagnostic_department(osv.osv):
    _name = "diagnosis.department"




    _columns = {

        'name': fields.char("Department Name",required=True),
        'parent':fields.selection([('a','A'),('b','B')], string='Parent', default='a')

    }