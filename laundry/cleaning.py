from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class laundry_clean(osv.osv):
    _name = "laundry.clean"




    _columns = {

        'name': fields.char("Name",required=True),
        'send_date':fields.date("Send Date"),
        'laundry_name':fields.many2one('laundry.laundry',"Laundry Name",required=True),
        'back_date': fields.date("Delivered Date"),
        'product_line':fields.one2many("laundry.clean.line","laundry_clean_id","Clean Product List")
        # 'nid':fields.integer("NID")


    }

class clean_line(osv.osv):
    _name = 'laundry.clean.line'


    _columns = {

        'laundry_clean_id': fields.many2one('laundry.clean', "Clean"),
        'linen_item': fields.many2one("laundry.product","Linen Item"),
        'quantity': fields.integer("Quantity"),
        'color': fields.char("Color")
    }




class laundry_receive(osv.osv):
    _name = "laundry.receive"




    _columns = {

        'laundry_name': fields.many2one('laundry.laundry', "Laundry Name", required=True),
        'name': fields.char("Cloth Type",required=True),
        'color':fields.char('Color',required=True),
        'quantity':fields.integer('Quantity',required=True),
        'receive_date':fields.date("Receive Date"),

        # 'nid':fields.integer("NID")


    }