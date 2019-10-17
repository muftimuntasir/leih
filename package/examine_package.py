from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class examine_package(osv.osv):
    _name = "examine.package"
    _columns = {

        # 'patient_id': fields.char("Patient ID"),
        'name':fields.char("Package name"),
        'price': fields.float(string="Price"),
        'start_date': fields.date(string="Start Date"),
        'end_date': fields.date(string="End Date"),
        'active': fields.boolean("Active"),
        'examine_package_line_id':fields.one2many('examine.package.line', 'examine_package_id', 'Add test', required=True),
    }


class examine_package_line(osv.osv):
    _name = 'examine.package.line'

    _columns = {

        'name': fields.many2one("examination.entry","Test Name", required=True, ondelete='cascade'),
        'examine_package_id': fields.many2one('examine.package', "Information"),
    }




