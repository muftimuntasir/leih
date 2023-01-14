from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class doctors_profile(osv.osv):
    _name = "doctors.profile"

    _columns = {

        'name': fields.char("Doctor Name",required=True),
        'department':fields.char('Department'),
        'designation':fields.char('Designation'),
        'degree':fields.char('Degree'),
        'type': fields.selection([('inhouse', 'In house'), ('consoled', 'Consoled'),('prttime','Part Time'),('outsid','Out Side')], string='Type', default='inhouse'),
        'status': fields.selection([('active', 'Active'), ('inactive', 'Inactive')], string='Status', default='active'),
        'others': fields.char("Others"),
        'bill_info':fields.one2many("bill.register",'ref_doctors',"Bill Register"),
        'admission_info':fields.many2one("leih.admission",'ref_doctors',"Admission Info"),
        'commission':fields.many2one("commission",'ref_doctors',"Commission"),

        'commission_rate':fields.float("Commission Rate (%) "),
        'last_commission_calculation_date':fields.date("Last Commission Calculation Date"),
        # added for commission
        'referral_id': fields.many2one("doctors.profile", "Referral ID"),
        'is_referral': fields.boolean("Is Referral?"),
        # 'nid':fields.integer("NID")


    }