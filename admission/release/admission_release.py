from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class admission_release(osv.osv):
    _name = "admission.release"


    _columns = {

        'total':fields.float("Total"),
        'paid': fields.float("Paid"),
        'unpaid':fields.float("Unpaid"),
        'pay': fields.float("Pay"),
        'release_note':fields.text("Release Note")

    }
