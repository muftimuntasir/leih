from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class doctors_profile(osv.osv):
    _name = "doctors.profile"




    _columns = {

        'name': fields.char("Doctor Name",required=True),
        'department':fields.char('Department',required=True),
        'designation':fields.char('Designation',required=True),
        'type': fields.selection([('inhouse', 'In house'), ('consoled', 'Consoled'),('prttime','Prt_time'),('outsid','Out_side')], string='Type', default='inhouse'),
        'status': fields.selection([('active', 'Active'), ('inactive', 'Inactive')], string='Status', default='active'),
        'others': fields.text("About Dr. "),
        # 'nid':fields.integer("NID")


    }