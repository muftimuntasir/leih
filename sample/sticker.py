from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class sample(osv.osv):
    _name = "diagnosis.sticker"
    _order = 'id desc'






    _columns = {
        'name': fields.char('Name'),
        'bill_register_id':fields.many2one('bill.register','Bill register Id'),
        'department_id':fields.many2one('diagnosis.group','Department'),
        'sticker_line_id':fields.one2many('diagnosis.sticker.line','sticker_id','Record Sample')
    }


class test_sample(osv.osv):
    _name = "diagnosis.sticker.line"

    _columns = {
        'test_name': fields.char("Name"),
        'sticker_id':fields.many2one('diagnosis.sticker','ID'),
        'ref_value': fields.char('Reference Value'),
        'result': fields.char('Test ID'),
        'remarks': fields.char('Remarks')

    }




