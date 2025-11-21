from openerp import api
from openerp.osv import osv, fields

class ProductTemplate(osv.osv):
    _inherit = 'product.template'

    _columns = {
        'valuation': fields.property(type='selection', selection=[('manual_periodic', 'Periodical (manual)'),
                                                                  ('real_time', 'Real Time (automated)')],
                                     string='Inventory Valuation',
                                     help="If real-time valuation is enabled for a product, the system will automatically write journal entries corresponding to stock moves, with product price as specified by the 'Costing Method'" \
                                          "The inventory variation account set on the product category will represent the current inventory value, and the stock input and stock output account will hold the counterpart moves for incoming and outgoing products."
                                     , required=True, copy=True, default='real_time'),
        'cost_method': fields.property(type='selection',
                                       selection=[('standard', 'Standard Price'), ('average', 'Average Price'),
                                                  ('real', 'Real Price')],
                                       help="""Standard Price: The cost price is manually updated at the end of a specific period (usually every year).
                        Average Price: The cost price is recomputed at each incoming shipment and used for the product valuation.
                        Real Price: The cost price displayed is the price of the last outgoing product (will be use in case of inventory loss for example).""",
                                       string="Costing Method", required=True, copy=True,default='real'),
    }