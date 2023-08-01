from openerp import api
from openerp.osv import osv, fields

class purchase_order_(osv.osv):
    _inherit = 'purchase.order'

    _columns = {
        'invoice_bill_no': fields.char('Invoice/Bill No.'),
        'chalan_no': fields.char('Chalan No'),
        'invoice_date': fields.date("Invoice/Bill Date"),
        'chalan_date': fields.date("Chalan Date"),
    }


