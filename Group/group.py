from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class group(osv.osv):
    _name = "leih.group"




    _columns = {

        'name': fields.char("Group Name",required=True),
        'department':fields.many2one('leih.department',"Department"),
        'year':fields.integer("Year")



    }