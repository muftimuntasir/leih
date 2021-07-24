from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class inventory_requisition(osv.osv):
    _name = "inventory.requisition"




    _columns = {

        'name': fields.char("Inventory Requisition"),
        'reference_no':fields.char("Reference No"),
        'warehouse_id': fields.many2one('stock.warehouse', 'Warehouse Location'),
        'partner_id': fields.many2one('res.partner', 'Receiver'),
        'challan_id': fields.many2one('stock.picking', 'Challan NO'),
        'department':fields.many2one("diagnosis.department","Department"),
        'inventory_requisition_line_ids':fields.one2many('inventory.requisition.line','inventory_requsition_id',string="Inventory Requision Items"),
        'date':fields.date('Date'),
        'state': fields.selection(
            [('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')],
            'Status', default='pending', readonly=True)

    }

    def confirm_transfer(self, cr, uid, ids, context=None):

        cc_ids = ids
        for id in cc_ids:
            ir_obj = self.browse(cr, uid, ids, context=context)
            if ir_obj.state == 'confirmed':
                raise osv.except_osv(_('Already Confirmed'), _('Sorry, it is already confirmed'))

            stock_picking_type_ids = self.pool['stock.picking.type'].search(cr, uid, [
                ('warehouse_id', '=', ir_obj.warehouse_id.id), ('code', '=', 'outgoing')],
                                                                            context=context)
            stock_picking_type_data = self.pool['stock.picking.type'].browse(cr, uid, stock_picking_type_ids,
                                                                             context=context)

            sorce_id = None
            dest_id = None
            picking_type_id = None

            for items in stock_picking_type_data:
                sorce_id = items.default_location_src_id.id
                dest_id = items.default_location_dest_id.id
                picking_type_id = items.id
            grn_vals = {
                'partner_id': ir_obj.partner_id.id,
                'date': fields.datetime.now(),
                'origin': ir_obj.name,
                'move_type': 'one',
                'invoice_state': 'none',

                'picking_type_id': picking_type_id,
                # 'priority': 1, #Normal
            }
            ids = [id]

            move_line = []
            line_ids = []

            for items in ir_obj.inventory_requisition_line_ids:
                move_line.append([0, False, {
                    'product_id': items.product_name.id,
                    'product_uom': 1,
                    'product_uom_qty': items.quantity,
                    'product_uos_qty': items.quantity,
                    'name': ir_obj.name,
                    'location_id': sorce_id,
                    'location_dest_id': dest_id,
                    'invoice_state': 'none',
                }])



            grn_vals['move_lines'] = move_line

            grn_id = self.pool.get('stock.picking').create(cr, uid, grn_vals, context=context)

            stock_picking_id = grn_id
            stock_confirm = self.pool.get('stock.picking').action_confirm(cr, uid, [grn_id], context=context)

            stock_picking = self.pool.get('stock.picking').do_enter_transfer_details(cr, uid, [stock_picking_id],
                                                                                     context=context)

            trans_obj = self.pool.get('stock.transfer_details')
            trans_search = trans_obj.search(cr, uid, [('picking_id', '=', stock_picking_id)], context=context)

            trans_search = [trans_search[len(trans_search) - 1]] if len(trans_search) > 1 else trans_search

            trans_browse = self.pool.get('stock.transfer_details').browse(cr, uid, trans_search, context=context)

            trans_browse.do_detailed_transfer()


        return True

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

