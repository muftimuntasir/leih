from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class doctors_profile(osv.osv):
    _name = "doctors.profile"




    _columns = {

        'name': fields.char("Doctor Name",required=True),
        'department':fields.char('Department',required=True),
        'designation':fields.char('Designation',required=True),
        'type': fields.selection([('inhouse', 'In house'), ('consoled', 'Consoled'),('prttime','Part Time'),('outsid','Out Side')], string='Type', default='inhouse'),
        'status': fields.selection([('active', 'Active'), ('inactive', 'Inactive')], string='Status', default='active'),
        'others': fields.char("Others"),
        'bill_info':fields.one2many("bill.register",'ref_doctors',"Bill Register"),
        'admission_info':fields.many2one("leih.admission","Admission Info"),
        'commission':fields.char("Commission")
        # 'nid':fields.integer("NID")


    }