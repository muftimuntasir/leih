
from openerp import api
from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class cash_collection(osv.osv):
    _name = "cash.collection"



    @api.onchange('type')
    def _onchange_tpe(self):
        import pdb
        pdb.set_trace()
        if self.type:
           self.total = 1234
           self.cash_collection_lines = [{
                'mr_no':1,
                'bill_admission_opd_id':1,
                'amount':13
            }]


    _columns = {

        'date': fields.date("Date"),
        'type': fields.selection([('bill','Bill'),('opd','OPD'),('admission','Admission')], 'Type'),
        'total': fields.float("Total"),
        'cash_collection_lines': fields.one2many("cash.collection.line","cash_collection_line_id",'cash collection', required=True),
    }



class cash_collection_line(osv.osv):
    _name="cash.collection.line"

    _columns = {
        'cash_collection_line_id':fields.many2one("cash.collection","Cash Collection"),
        'mr_no':fields.many2one("leih.money.receipt","Mr No."),
        'bill_admission_opd_id':fields.char("Bill/Admission/OPD Number"),
        'amount':fields.float("Amount")
    }