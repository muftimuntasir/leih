from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class sample(osv.osv):
    _name = "leih.sample"






    _columns = {
        'sample_id':fields.integer("ID"),
        'investigation_id':fields.integer('investigation'),
        'tests_id':fields.integer('Test ID'),
        'department_id':fields.char('Department')


    }

