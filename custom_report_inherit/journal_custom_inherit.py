from openerp import api
from openerp.osv import osv, fields


class account_move(osv.osv):
    _inherit = "account.move"

    _columns = {
        'invoice_bill_no': fields.char('Invoice No.'),
        'chalan_no': fields.char('Chalan No.'),

    }

    def default_get(self, cr, uid, fields_list, context=None):
        defaults = super(account_move, self).default_get(cr, uid, fields_list, context=context)

        # Get the context to check if we have a purchase order id
        purchase_order_id = context.get('default_purchase_order_id')
        if purchase_order_id:
            purchase_order = self.pool.get('purchase.order').browse(cr, uid, purchase_order_id, context=context)

            # Set the default values for invoice_bill_no and chalan_no fields
            defaults.update({
                'invoice_bill_no': purchase_order.invoice_bill_no,
                'chalan_no': purchase_order.chalan_no,
            })

        return defaults
