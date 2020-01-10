from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class ward(osv.osv):
    _name = "ward.managment"




    _columns = {

        'wname': fields.char("Ward Name",required=True),
        'bed': fields.char("Bed No", required=True),
        'name': fields.char("Patient Name", required=True),
        'pid': fields.char("Patient ID", required=True),
        'Date': fields.datetime("Recived Date", required=True),
        'precived': fields.char("Recived By", required=True),


    }