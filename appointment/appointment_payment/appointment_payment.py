from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time
from openerp import api

class appointment_payment(osv.osv):
    _name = "appointment.payment"




    _columns = {

        'cal_st_date': fields.date('Calculation Start Date'),
        'cal_end_date': fields.date('Calculation End Date'),
        'ref_doctors': fields.many2one('doctors.profile', 'Doctor Name'),
        'total_payable_amount': fields.float('Total Payable Amount'),
        'appointment_payment_line_ids':fields.one2many('appointment.payment.line','appointment_payment_line_ids','Payment Line')
    }

    @api.onchange('ref_doctors')
    def doctor_change(self):
        if self.cal_st_date == False or self.cal_end_date == False:
            raise osv.except_osv(_('Select'), _('Please select Start and End Date od Calculation'))

        st_date = self.cal_st_date
        end_date = self.cal_end_date
        commissioner_id = self.ref_doctors.id

        ## Get all Commission Configuration List



        query = "select patient_name,patient_status,amount from appointment_booking where doctor_name=%s"
        self._cr.execute(query, ([commissioner_id]))
        all_data = self._cr.dictfetchall()

        appointment_payment_line = list()


        # total_amount = 0
        # total_billing_amount = 0
        # total_test_count = 0

        for bill_items in all_data:

           patient_name=bill_items.get("patient_name")
           patient_status=bill_items.get("patient_status")
           amount=bill_items.get("amount")

           appointment_payment_line.append({
               'patient_name':patient_name,
               'patient_status':patient_status,
               'amount':amount

           })

           # import pdb
           # pdb.set_trace()


        self.appointment_payment_line_ids = appointment_payment_line

        return "xXxXxXxXxX"



class appointment_payment_line(osv.osv):
        _name="appointment.payment.line"

        _columns = {
            'appointment_payment_line_ids':fields.many2one('appointment.payment','Admission Payment'),
            'patient_name':fields.char("Patient Name"),
            'patient_status':fields.char("Patient Status"),
            'date':fields.date(string="Date"),
            'amount':fields.float('Amount')

        }





