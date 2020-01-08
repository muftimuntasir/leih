from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class blood_donar(osv.osv):
    _name = "blood.donar"


    _columns = {
        'name':fields.char('Name'),
        'doner_name':fields.char('Donar Name',required=True),
        'mobile_no':fields.char('Mobile No',required=True),
        'receive_date':fields.date('Received Date',required=True),
        'date':fields.date('Received Date',required=True),
        'description':fields.text('Description'),
        'group':fields.char('Blood Group'),
        'cost':fields.float('Cost'),
        'active': fields.boolean('Available'),
            }



class blood_receiver(osv.osv):
    _name = "blood.receiver"


    _columns = {
        'name':fields.char('Name'),
        'buyer_name':fields.char('Buyer Name',required=True),
        'receive_date':fields.date('Date',required=True),
        'mobile_no':fields.char('Mobile No',required=True),
        'patient_id': fields.many2one('patient.info', "Patient Name"),
        'description':fields.text('Description'),
        'group':fields.char('Blood Group'),
        'price':fields.float('Price'),
        'paid_amount':fields.float('Paid Amount'),
        'unpaid_amount':fields.float('Unpaid Amount'),

            }







