from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time
from openerp import api

class commissionpayment(osv.osv):
    _name = "commission.payment"




    _columns = {

        'name': fields.char("Name"),
        'doctor_id': fields.many2one('doctors.profile', 'Name'),
        'date':fields.date('Payment Date'),
        'cc_id': fields.many2one('commission', 'Commission'),
        'debit_id': fields.many2one('account.account', 'Debit Account'),
        'credit_id': fields.many2one('account.account', 'Credit Account'),
        'paid_amount': fields.float('Paid Amount'),
        'due_amount': fields.float('Due Amount'),
        'period_id': fields.many2one('account.period','Period'),
        'note': fields.text("Note"),

        'state': fields.selection(
            [('pending', 'Pending'), ('done', 'Confirmed'), ('cancelled', 'Cancelled')],
            'Status', default='pending', readonly=True)

    }
    _defaults = {
        'state': 'pending',

    }

    _order = 'id desc'
