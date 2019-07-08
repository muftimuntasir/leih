from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class testentry(osv.osv):
    _name = "leih.testentry"




    _columns = {

        'name': fields.char("Test Name",required=True),
        'group':fields.many2one('leih.group',"Group"),
        'department':fields.many2one('leih.department',"Department"),
        'rate':fields.integer("Rate"),
        'refarence_value':fields.char("Reference value"),
        'required_time':fields.char("Required time")




    }