from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class leih(osv.osv):
    _name = "leih.room"




    _columns = {

        'room_no': fields.char("Room No",required=True),
        'name':fields.char('Room Name',required=True),
        'floor':fields.char('Floor'),
        'building_name':fields.char("Building Name"),

    }