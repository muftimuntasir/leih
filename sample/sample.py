from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class sample(osv.osv):
    _name = "leih.sample"






    _columns = {

        'patient_id': fields.char("Patient ID",required=True),
        'mobile': fields.char("Mobile", required=True),
        'name': fields.many2one('leih.patients', "Name", required=True),


    }

