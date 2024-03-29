from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class opd_ticket_config(osv.osv):
    _name = "opd.ticket.entry"
    _order = 'id desc'
    _columns = {
        'name':fields.char("Name"),
        'department':fields.many2one("diagnosis.department","Department"),
        'fee': fields.float("Fee"),
        'accounts_id':fields.many2one('account.account',"Account ID",required=True),
        'total_cash':fields.float("Total Cash")

    }

