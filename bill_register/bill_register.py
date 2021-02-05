from openerp import api
from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time, timedelta, datetime




class bill_register(osv.osv):
    _name = "bill.register"
    _order = 'id desc'
    # pdf=PDF()

    # pdf.lines()
    # pdf.titles()

    def _totalpayable(self, cr, uid, ids, field_name, arg, context=None):
        Percentance_calculation = {}
        sum = 0
        for items in self.pool.get("bill.register").browse(cr,uid,ids,context=None):
            total_list=[]
            for amount in items.bill_register_line_id:
                total_list.append(amount.total_amount)

            for item in total_list:
                sum=item+sum


                for record in self.browse(cr, uid, ids, context=context):
                    Percentance_calculation[record.id] = sum

        return Percentance_calculation
    def _delivery_dates(self, cr, uid, ids, field_name, arg, context=None):
        delivery_date={}
        test_delivery_date=[]
        max_day=0
        for items in self.pool.get("bill.register").browse(cr,uid,ids,context=None):
            total_list=[]
            for amount in items.bill_register_line_id:
                for test in amount.name:

                    test_delivery_date.append(test.required_time)

        if len(test_delivery_date):
            max_day=max(test_delivery_date)
        #
        # import pdb
        # pdb.set_trace()

            # for item in total_list:
            #     sum=item+sum
        for record in self.browse(cr,uid,ids,context=context):
            delivery_date[record.id]=date.today()+timedelta(days=max_day)
        return delivery_date


    _columns = {

        # 'patient_id': fields.char("Patient ID"),
        'name':fields.char("Name"),
        'mobile': fields.char(string="Mobile",readonly=True,store=False),
        'patient_id': fields.char(related='patient_name.patient_id',string="Patient Id",readonly=True),
        'patient_name': fields.many2one('patient.info', "Patient Name"),
        'address': fields.char("Address",store=False),
        'age': fields.char("Age",store=False),
        'sex':fields.char("Sex",store=False),
        'ref_doctors': fields.many2one('doctors.profile','Reffered by'),
        'delivery_date': fields.function(_delivery_dates,string="Delivery Date",type='date',store=True),
        'bill_register_line_id': fields.one2many('bill.register.line', 'bill_register_id', 'Investigations'),
        'bill_register_payment_line_id': fields.one2many("bill.register.payment.line", "bill_register_payment_line_id","Bill Register Payment"),
        # 'footer_connection': fields.one2many('leih.footer', 'relation', 'Parameters', required=True),
        # 'relation': fields.many2one("leih.investigation"),
        # 'total': fields.float(_totalpayable,string="Total",type='float',store=True),
        'total': fields.float(string="Total"),
        'doctors_discounts': fields.float("Discount(%)"),
        'after_discount': fields.float("Discount Amount"),
        'other_discount': fields.float("Other Discount"),
        'grand_total': fields.float("Grand Total"),
        'paid': fields.float(string="Paid",required=True),
        'type': fields.selection([('cash', 'Cash'),('bank', 'Bank')], 'Payment Type'),
        'card_no': fields.char('Card No.'),
        'bank_name': fields.char('Bank Name'),
        'due': fields.float("Due"),
        'date':fields.date("Date",default=datetime.now().strftime('%Y-%m-%d'),readonly=True),
        'state': fields.selection(
            [('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')],
            'Status', default='pending', readonly=True)
    }


    def bill_confirm(self, cr, uid, ids, context=None):
        ## Bill Status Will Change

        cr.execute("update bill_register set state='confirmed' where id=%s", (ids))
        cr.commit()

        stored_obj = self.browse(cr, uid, [ids[0]], context=context)
        stored = int(ids[0])

        for items in stored_obj.bill_register_line_id:
            state = 'sample'
            if items.name.sample_req == False or items.name.sample_req == None:
                state='lab'
            child_list = []
            value = {
                'bill_register_id':int(stored),
                'test_id':int(items.name.id),
                'department_id':items.name.department.name,
                'state':state,
            }



            for test_item in items.name.examination_entry_line:
                tmp_dict = {}
                tmp_dict['test_name'] = test_item.name
                tmp_dict['ref_value'] = test_item.reference_value
                child_list.append([0, False, tmp_dict])
            value['sticker_line_id']=child_list


            sample_obj = self.pool.get('diagnosis.sticker')
            sample_id = sample_obj.create(cr, uid, value, context=context)

            if sample_id is not None:
                sample_text = 'Lab-0' + str(sample_id)
                cr.execute('update diagnosis_sticker set name=%s where id=%s', (sample_text, sample_id))
                # cr.commit()


        if stored_obj.paid !=False:
            for bills_vals in stored_obj:
                # import pdb
                # pdb.set_trace()
                mr_value={
                    'date':stored_obj.date,
                    'bill_id':int(stored),
                    'amount':stored_obj.paid,
                    'type':stored_obj.type,
                }
            mr_obj = self.pool.get('leih.money.receipt')
            mr_id = mr_obj.create(cr, uid, mr_value, context=context)
            if mr_id is not None:
                mr_name = 'MR#' + str(mr_id)
                cr.execute('update leih_money_receipt set name=%s where id=%s', (mr_name, mr_id))
                cr.commit()
            # if mr_id is not None:
            #     try:
            #         mr_name = 'MR#' + str(mr_id)
            #         cr.execute('update leih_money_receipt set name=%s where id=%s', (mr_name, mr_id))
            #         cr.commit()
            #     except:
            #         pass


        return True




    def onchange_total(self,cr,uid,ids,name,context=None):
        tests = {'values': {}}
        dep_object = self.pool.get('leih.tests').browse(cr, uid, name, context=None)
        abc = {'total': dep_object.rate}
        tests['value'] = abc
        return tests

    def onchange_patient(self,cr,uid,ids,name,context=None):
        tests={}
        dep_object = self.pool.get('patient.info').browse(cr, uid, name, context=None)
        abc={'mobile':dep_object.mobile,'address':dep_object.address,'age':dep_object.age,'sex':dep_object.sex}
        tests['value']=abc
        return tests

    def add_new_test(self, cr, uid, ids, context=None):
        if not ids: return []

        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'leih', 'add_bill_view')
        #
        inv = self.browse(cr, uid, ids[0], context=context)
        # import pdb
        # pdb.set_trace()
        return {
            'name':_("Pay Invoice"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'add.bill',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'bill_id':ids[0],
                'default_price':500,
                # 'default_name':context.get('name', False),
                'default_total_amount':200,
            }
        }
        raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
    def button_dummy(self, cr, uid, ids, context=None):


        return True

    def bill_cancel(self, cr, uid, ids, context=None):
        ## Bill Status Will Change

        cr.execute("update bill_register set state='cancelled' where id=%s", (ids))
        cr.commit()
        ## Lab WIll be Deleted

        cr.execute("update diagnosis_sticker set state='cancel' where bill_register_id=%s", (ids))
        cr.commit()
        return True

    def btn_pay_bill(self, cr, uid, ids, context=None):
        if not ids: return []

        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'leih','bill_register_payment_form_view')
        #
        inv = self.browse(cr, uid, ids[0], context=context)

        # total=inv.total
        # import pdb
        # pdb.set_trace()
        return {
            'name': _("Pay Invoice"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'bill.register.payment',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'default_bill_id': ids[0],
                'default_amount': inv.due
            }
        }
        raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))


    def add_discount(self,cr,uid,ids,context=None):
        # import pdb
        # pdb.set_trace()
        if not ids: return []

        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'leih', 'discount_view')
        #
        inv = self.browse(cr, uid, ids[0], context=context)
        # import pdb
        # pdb.set_trace()
        return {
            'name': _("Pay Invoice"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'discount',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'pi_id':ids[0]
            }
        }
        raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))

  
    def create(self, cr, uid, vals, context=None):

        if context is None:
            context = {}

        stored = super(bill_register, self).create(cr, uid, vals, context) # return ID int object


        if stored is not None:
            name_text = 'Bill-0' + str(stored)
            cr.execute('update bill_register set name=%s where id=%s', (name_text, stored))
            cr.commit()



        return stored

    def write(self, cr, uid, ids, vals, context=None):


        return super(bill_register, self).write(cr, uid, ids, vals, context=context)

    @api.onchange('bill_register_line_id')
    def onchange_test_bill(self):
        sumalltest=0
        for item in self.bill_register_line_id:
            sumalltest=sumalltest+item.total_amount

        self.total=sumalltest
        after_dis = (sumalltest* (self.doctors_discounts/100))
        self.after_discount = after_dis
        self.grand_total=sumalltest -  self.other_discount - after_dis
        self.due=sumalltest - after_dis -  self.other_discount- self.paid

        return "X"

    @api.onchange('paid')
    def onchange_paid(self):
        self.due = self.grand_total - self.paid
        return 'x'



    @api.onchange('doctors_discounts')
    def onchange_doc_discount(self):
        aft_discount=(self.total*(self.doctors_discounts/100))
        self.after_discount=aft_discount
        self.grand_total = self.total - aft_discount - self.other_discount
        self.due=self.total - aft_discount - self.other_discount- self.paid

        return "X"

    @api.onchange('other_discount')
    def onchange_other_discount(self):
        self.grand_total = self.total - self.after_discount - self.other_discount
        self.due=self.total - self.after_discount - self.other_discount- self.paid
        return 'True'






class test_information(osv.osv):
    _name = 'bill.register.line'



    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('bill.register')
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            rate=record.price
            discount=record.discount
            interst_amount=int(discount)*int(rate)/100
            total_amount=int(rate)-interst_amount
            res[record.id]=total_amount
            # import pdb
            # pdb.set_trace()
        return res




    _columns = {

        'name': fields.many2one("examination.entry","Item Name",ondelete='cascade'),
        'bill_register_id': fields.many2one('bill.register', "Information"),
        'department':fields.char("Department"),
        # 'currency_id': fields.related('pricelist_id', 'currency_id', type="many2one", relation="res.currency",
        #                               string="Currency", readonly=True, required=True),
        # 'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute=dp.get_precision('Account')),
        'price': fields.integer("Price"),
        'discount': fields.integer("Discount"),
        'total_amount': fields.integer("Total Amount"),
        'commission_paid': fields.boolean("Commission Paid"),

    }

    def onchange_test(self,cr,uid,ids,name,context=None):
        tests = {'values': {}}
        dep_object = self.pool.get('examination.entry').browse(cr, uid, name, context=None)
        abc = {'department':dep_object.department.name,'price': dep_object.rate,'total_amount':dep_object.rate,'bill_register_id.paid':dep_object.rate}
        tests['value'] = abc
        # import pdb
        # pdb.set_trace()
        return tests

    def onchange_discount(self,cr,uid,ids,name,discount,context=None):
        tests = {'values': {}}
        dep_object = self.pool.get('examination.entry').browse(cr, uid, name, context=None)
        abc = {'total_amount':round(dep_object.rate-(dep_object.rate* discount/100))}
        tests['value'] = abc
        # import pdb
        # pdb.set_trace()
        return tests
    # def create(self, cr, uid, vals, context=None):
    #     import pdb
    #     pdb.set_trace()
    #     return 0
class admission_payment_line(osv.osv):
    _name = 'bill.register.payment.line'

    _columns = {
        'bill_register_payment_line_id': fields.many2one('bill.register', 'bill register payment'),
        'date':fields.datetime("Date"),
        'amount':fields.float('amount'),
        'type':fields.selection([('bank','Bank'),('cash','Cash')],'Type'),
        'card_no':fields.char('Card Number'),
        'bank_name':fields.char('Bank Name'),
        'money_receipt_id': fields.many2one('leih.money.receipt', 'Money Receipt ID'),

    }




