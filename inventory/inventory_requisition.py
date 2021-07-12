from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class inventory_requisition(osv.osv):
    _name = "inventory.requisition"




    _columns = {

        'name': fields.char("Inventory Requisition"),
        'reference_no':fields.char("Reference No"),
        'department':fields.many2one("diagnosis.department","Department"),
        'inventory_requisition_line_ids':fields.one2many('inventory.requisition.line','inventory_requsition_id',string="Inventory Requision Items"),
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

        stored = super(inventory_requisition, self).create(cr, uid, vals, context) # return ID int object


        if stored is not None:
            name_text = 'IR-0' + str(stored)
            cr.execute('update inventory_requisition set name=%s where id=%s', (name_text, stored))
            cr.commit()



        return stored


class inventory_requisition_line(osv.osv):
    _name="inventory.requisition.line"


    _columns = {
        'name':fields.char("Inventory Requisition Line Id"),
        'inventory_requsition_id':fields.many2one("inventory.requisition","Inventory Requision ID"),
        'product_name':fields.many2one('product.product','Product Name'),
        'quantity':fields.integer("Quantity")
    }

