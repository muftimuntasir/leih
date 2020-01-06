from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class ambulance_registration(osv.osv):
    _name = "ambulance.registration"


    _columns = {

        'vehicle_type': fields.char("Vehicle Type",required=True),
        'name':fields.char('Vehicle Number',required=True),
        'vehicle_name':fields.char('Vehicle Name',required=True),
        'active': fields.boolean('In Service'),
            }


class ambulance_booking(osv.osv):
    _name = "ambulance.booking"


    _columns = {

        'booking_type': fields.char("Booking Type",required=True),
        'name':fields.char('Name',required=True),
        'patient_id':fields.char('Patient Name',required=True),
        'mobile_no': fields.char('Mobile No', required=True),
        'start_from': fields.char('Start From', required=True),
        'destination': fields.char('Destination', required=True),
        'amount': fields.float('Amount', required=True),
        'advance_amount': fields.float('Advance Amount', required=True),
        'paid_amount': fields.float('Paid Amount'),
        'unpaid_amount': fields.float('Unpaid Amount'),
        'grace_time': fields.float('Expected Completion Time', required=True),
        'date': fields.datetime('Booking/Request Date and Time', required=True),

            }

class ambulance_expense(osv.osv):
    _name = "ambulance.expense"



