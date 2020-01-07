from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class laundry_clean(osv.osv):
    _name = "laundry.clean"




    _columns = {

        'name': fields.char("Name",required=True),
        'color':fields.char('Color',required=True),
        'quantity':fields.integer('Quantity',required=True),
        'send_date':fields.date("Send Date"),
        'laundry_name':fields.many2one('laundry.laundry',"Laundry Name",required=True),
        'back_date': fields.date("Delivered Date")
        # 'nid':fields.integer("NID")


    }