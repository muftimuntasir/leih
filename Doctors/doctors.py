from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class leih(osv.osv):
    _name = "leih.doctors"




    _columns = {

        'name': fields.char("Doctor Name",required=True),
        'department':fields.char('Department',required=True),
        'designation':fields.char('Designation',required=True),
        'status': fields.selection([('a', 'In house'), ('b', 'Consoled'),('c','Prt_time'),('d','Out_side')], string='Status', default='a'),
        'nid':fields.integer("NID")


    }