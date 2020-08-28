from openerp import api
from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class discount_core_type(osv.osv):
    _name = "discount.core.type"
    # _rec_name = 'patient_id'


    _columns = {

        'name': fields.char("Discount type"),
        'category_id': fields.many2one('discount.category','Discount Category'),
        'discount_amount': fields.float("Discount Amount(%)",required=True),

    }

