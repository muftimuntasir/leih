from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class sample(osv.osv):
    _name = "leih.sample"






    _columns = {
        'sample_id':fields.integer("ID"),
        'investigation_id':fields.integer('investigation'),
        'tests_id':fields.integer('Test ID'),
        'department_id':fields.char('Department'),
        'testsampleid':fields.one2many('leih.testsample','sample_ide','Record Sample')


    }


class test_sample(osv.osv):
    _name = "leih.testsample"

    _columns = {
        'test_name': fields.char("Name"),
        'sample_ide':fields.many2one('leih.sample','ID'),
        'ref_value': fields.char('Reference Value'),
        'result': fields.char('Test ID'),
        'remarks': fields.char('Remarks')

    }




