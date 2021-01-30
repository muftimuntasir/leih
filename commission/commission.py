from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time
from openerp import api

class commission(osv.osv):
    _name = "commission"


    _columns = {

        'name': fields.char("Doctor Name"),
        'ref_doctors': fields.many2one('doctors.profile', 'Doctor/Broker Name'),
        'commission_configuration_id': fields.many2one('commission.configuration', 'Commission Rule'),
        'commission_rate': fields.float('Commission Rate'),
        'cal_st_date': fields.date("Calculation Start Date", required=True),
        'cal_end_date': fields.date("Calculation End Date", required=True),
        'total_amount': fields.float('Total Commission Amount'),
        'given_discount_amount': fields.float('Total Discount'),
        'total_payable_amount': fields.float('Total Payable Amount'),
        'total_patient': fields.float('Total Patients'),
        'total_bill': fields.float('Total Billing Amount'),
        'total_tests': fields.float('Total Tests in All Billing'),
        'commission_line_ids':fields.one2many("commission.line",'commission_line_ids',"Commission Lines"),
        'state': fields.selection(
            [('pending', 'Pending'), ('done', 'Confirmed'), ('cancelled', 'Cancelled')],
            'Status', default='pending', readonly=True)

    }

    _defaults = {
        'state': 'pending',

    }

    _order = 'id desc'

    def make_confirm(self, cr, uid, ids, context=None):

        id_list = ids
        stock_packing_ids = []

        for element in id_list:
            ids = [element]



            if ids is not None:
                cr.execute("update commission set state='done' where id=%s", (ids))
                cr.commit()




        return 'True'


    @api.model
    def create(self, vals):
        record = super(commission, self).create(vals)
        return record

    @api.onchange('ref_doctors')
    def customer_on_select(self):

        if self.ref_doctors:
            commissioner_id=self.ref_doctors.id
            commission_rate = 0
            c_query = "select commission_rate from doctors_profile where id=%s"
            self._cr.execute(c_query, ([commissioner_id]))
            com_data=self._cr.dictfetchall()
            for itm in com_data:
                commission_rate_raw = itm.get('commission_rate')
                break
            try:
                commission_rate = round((commission_rate_raw/100),2)
            except:
                commission_rate=0




            query = "select bill_register_line.name,bill_register_line.total_amount,bill_register.ref_doctors from bill_register_line,bill_register where bill_register_line.bill_register_id=bill_register.id and (bill_register_line.commission_paid = FALSE or bill_register_line.commission_paid is NULL)and bill_register.ref_doctors =%s"


            self._cr.execute(query, ([commissioner_id]))

            all_data = self._cr.dictfetchall()



            order_payment_line = list()

            total_amount = 0


            for bill_items in all_data:
                try:
                    pay_amount = round((commission_rate * bill_items.get('total_amount')),2)
                except:
                    pay_amount=0

                total_amount = total_amount + pay_amount

                order_payment_line.append({


                    'name': bill_items.get('name'),
                    'amount': bill_items.get('total_amount'),
                    'commission_rate': commission_rate_raw,
                    'payable_amount': pay_amount,

                })

            self.commission_line_ids = order_payment_line
            self.total_amount=total_amount
            self.commission_rate=commission_rate_raw

        return "xXxXxXxXxX"

    @api.onchange('commission_line_ids')
    def commission_line_ids_code(self):
        total_sum = 0
        for line_item in self.commission_line_ids:
            total_sum = total_sum + line_item.payable_amount
        self.total_amount = total_sum
        return 'ss'


class commission_line(osv.osv):
    _name = "commission.line"

    _columns = {
        'commission_line_ids': fields.many2one('commission', 'commission'),
        'department_id': fields.many2one("diagnosis.department", "Department"),
        'name': fields.many2one("examination.entry", "Test Name"),
        'discount_amount': fields.float('Discount Amount'),
        'test_amount': fields.float('Test Amount'),
        'mou_payable_comm_var': fields.float('MOU Payable Commission Amount (%)'),
        'mou_payable_comm_fixed': fields.float('MOU Payable Commission Fixed'),
        'mou_payable_comm_max_cap': fields.float('MOU Max CAP Amount'),
        'after_discount': fields.float('After Discount Amount'),
        'payable_amount': fields.float('Payable Amount'),


        'bill_line_id': fields.many2one("bill.register.line",'Bill Register Line ID'),
    }

    @api.onchange('commission_rate')
    def commission_rate_change(self):
        try:
            if self.commission_rate:
                self.payable_amount = round((self.amount * round((self.commission_rate/100),2)),2)
            else:
                self.payable_amount = 0
        except:
            self.payable_amount=0

        return 'xxx'
