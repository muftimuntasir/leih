from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class inventory_product_entry(osv.osv):
    _name = "inventory.product.entry"




    _columns = {

        'name': fields.char("Inventory Product entry"),
        'reference_no':fields.char("Reference No"),
        'order_no':fields.char("Reference No"),
        'department':fields.many2one("diagnosis.department","Department"),
        'warehouse_id': fields.many2one('stock.warehouse', 'Warehouse Location'),
        'inventory_product_entry_line_ids':fields.one2many('inventory.product.entry.line','inventory_product_entry_id',string="Inventory Requision Items"),
        'date':fields.date('Date'),
        'state': fields.selection(
            [('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')],
            'Status', default='pending', readonly=True)

    }


    def confirm_transfer(self):


        return "X"


    def create(self, cr, uid, vals, context=None):

        if context is None:
            context = {}

        stored = super(inventory_product_entry, self).create(cr, uid, vals, context) # return ID int object


        if stored is not None:
            name_text = 'IR-0' + str(stored)
            cr.execute('update inventory_product_entry set name=%s where id=%s', (name_text, stored))
            cr.commit()



        return stored


class inventory_product_entry_line(osv.osv):
    _name="inventory.product.entry.line"


    _columns = {
        'name':fields.char("Inventory Requisition Line Id"),
        'inventory_product_entry_id':fields.many2one("inventory.product.entry","Inventory Entry ID"),
        'product_name':fields.many2one('product.product','Product Name'),
        'quantity':fields.integer("Quantity")
    }

