from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time
from openerp import api

class commissionconfiguration(osv.osv):
    _name = "commission.configuration"




    _columns = {

        'name': fields.char("Name"),
        'doctor_id': fields.many2one('doctors.profile', 'Doctor/Broker Name'),
        'start_date':fields.date('MOU Start Date'),
        'end_date':fields.date('MOU End Date'),
        'overall_commission_rate': fields.float('Overall Commission Rate (%)'),
        'overall_default_discount': fields.float('Overall Discount Rate (%)'),
        'max_default_discount': fields.float('Max Discount Rate (%)'),
        'deduct_from_discount': fields.boolean("Deduct Excess Discount From Commission"),
        'department_ids':fields.many2one('diagnosis.department','Department List'),

        'commission_configuration_line_ids':fields.one2many("commission.configuration.line",'commission_configuration_line_ids',"Commission Lines"),
        'state': fields.selection(
            [('pending', 'Pending'), ('done', 'Confirmed'), ('cancelled', 'Cancelled')],
            'Status', default='pending', readonly=True)

    }

    _defaults = {
        'state': 'pending',

    }

    _order = 'id desc'



class commissionconfigurationline(osv.osv):
    _name = "commission.configuration.line"

    _columns = {
        'commission_configuration_line_ids': fields.many2one('commission.configuration', 'Commission Configuration ID'),
        'department_id':fields.many2one('diagnosis.department','Department'),
        'test_id':fields.many2one('examination.entry','Test Name'),
        'applicable':fields.boolean('Applicable'),
        'fixed_amount': fields.float('Fixed Amount'),
        'variance_amount': fields.float('Amount (%)'),
        'test_price': fields.float('Test Fee'),
        'est_commission_amount': fields.float('Commission Amount'),
        'max_commission_amount': fields.float('Max Commission Amount'),


    }


