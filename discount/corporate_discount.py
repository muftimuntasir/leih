from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time
from openerp import api

class corporatediscount(osv.osv):
    _name = "corporate.discount"


    _columns = {

        'name': fields.char("Corporate Disocunt ID"),
        'bill_id': fields.many2one('bill.register', 'Bill ID'),
        'date':fields.date('Date'),
        'corporate_id': fields.many2one('discount.configuration', 'Corporate ID'),
        # 'debit_id': fields.many2one('account.account', 'Debit Account'),
        # 'credit_id': fields.many2one('account.account', 'Credit Account'),
        'discount_amount': fields.float('Discount Amount'),
        'total_amount': fields.float('Due Amount'),
        'period_id': fields.many2one('account.period','Period'),
        'journal_id': fields.many2one('account.move','Journal'),
        'note': fields.text("Note"),

        'state': fields.selection(
            [('pending', 'Pending'), ('done', 'Confirmed'), ('cancelled', 'Cancelled')],
            'Status', default='pending', readonly=True)

    }
    _defaults = {
        'state': 'pending',

    }

    _order = 'id desc'

class bill_register_inherit(osv.osv):
    _inherit ="bill.register"

    def btn_corporate_discount(self, cr, uid, ids, context=None):
        if not ids: return []

        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'leih','corporate_discount_form_view')
        #
        inv = self.browse(cr, uid, ids[0], context=context)
        # import pdb
        # pdb.set_trace()

        return {
            'name': _("Payment"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'corporate.discount',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'default_bill_id': inv.name
                # 'default_paid_amount': inv.total_payable_amount
            }
        }
        raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))







