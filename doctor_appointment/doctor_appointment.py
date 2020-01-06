from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class doctor_appointment(osv.osv):
    _name = "doctor.appointment"




    _columns = {

        'mobile_no': fields.char("Mobile No",required=True),
        'name':fields.char('Patient Name',required=True),
        'appointment_date':fields.datetime('Date and Time',required=True),
        'doctor_id':fields.many2one('doctors.profile','Doctor',required=True),

    }