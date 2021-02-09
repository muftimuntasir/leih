from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import api
from datetime import date, time
PACKAGE_FIELDS=('name','price')

class leih_admission(osv.osv):
    _name = "leih.admission"
    _order = 'id desc'




    def _totalpayable(self, cr, uid, ids, field_name, arg, context=None):
        Percentance_calculation = {}
        sum = 0
        for items in self.pool.get("leih.admission").browse(cr,uid,ids,context=None):
            total_list=[]
            for amount in items.leih_admission_line_id:
                total_list.append(amount.total_amount)

            for item in total_list:
                sum=item+sum


                for record in self.browse(cr, uid, ids, context=context):
                    Percentance_calculation[record.id] = sum
                    # import pdb
                    # pdb.set_trace()
        return Percentance_calculation


    _columns = {

        # 'patient_id': fields.char("Patient ID"),
        'name':fields.char("Name"),
        'mobile': fields.char(string="Mobile",readonly=True,store=False),
        'patient_id': fields.char(related='patient_name.patient_id',string="Patient Id"),
        'patient_name': fields.many2one('patient.info', "Patient Name"),
        'address': fields.char("Address",store=False),
        'age': fields.char("Age",store=False),
        'sex':fields.char("Sex",store=False),
        'ref_doctors': fields.many2one('doctors.profile','Reffered by'),
        'delivery_date': fields.char("Delivery Date"),
        'release_note': fields.text("Release Note"),
        'package_name': fields.many2one("examine.package", string="Package"),
        'leih_admission_line_id': fields.one2many('leih.admission.line', 'leih_admission_id', 'Investigations'),
        'guarantor_line_id':fields.one2many("patient.guarantor","admission_id","Guarantor Name"),
        'bill_register_admission_line_id': fields.one2many("bill.register.admission.line","admission_line_id","Bill Register"),
        'admission_payment_line_id': fields.one2many("admission.payment.line","admission_payment_line_id","Admission Payment"),
        # 'footer_connection': fields.one2many('leih.footer', 'relation', 'Parameters', required=True),
        # 'relation': fields.many2one("leih.investigation"),
        'total': fields.function(_totalpayable,string="Total",type='float',store=True),
        'doctors_discounts': fields.float("Discount(%)"),
        'after_discount': fields.float("Discount Amount"),
        'other_discount': fields.float("Other Discount"),
        'grand_total': fields.float("Grand Total"),
        'paid': fields.float("Paid"),
        'due': fields.float("Due"),
        'state': fields.selection(
            [('pending', 'Pending'),('activated', 'Admitted'), ('released', 'Released'), ('cancelled', 'Cancelled')],
            'Status',default='pending', readonly=True,
        ),
    }

    def onchange_total(self,cr,uid,ids,name,context=None):
        tests = {'values': {}}
        dep_object = self.pool.get('leih.tests').browse(cr, uid, name, context=None)
        abc = {'total': dep_object.rate}
        tests['value'] = abc
        # import pdb
        # pdb.set_trace()
        return tests

    # def print_bill_register(self, cr, uid, ids, context=None):
    #     '''
    #     This function prints the sales order and mark it as sent, so that we can see more easily the next step of the workflow
    #     '''
    #     assert len(ids) == 1, 'This option should only be used for a single id at a time'
    #
    #     return self.pool['report'].get_action(cr, uid, ids, 'sale.report_saleorder', context=context)

    def onchange_patient(self,cr,uid,ids,name,context=None):
        tests={}
        dep_object = self.pool.get('patient.info').browse(cr, uid, name, context=None)
        abc={'mobile':dep_object.mobile,'address':dep_object.address,'age':dep_object.age,'sex':dep_object.sex}
        tests['value']=abc
        return tests

    def _package_fields(self, cr, uid, context=None):
        return list(PACKAGE_FIELDS)

    # def onchange_mobile(self,cr,uid,ids,mobile,context=None):
    #     tests={'values':{}}
    #     patient_id=self.pool.get('patient.info').search(cr,uid,[('mobile', '=', mobile)],context=None)
    #     dep_object=self.pool.get('patient.info').browse(cr,uid,patient_id,context)
    #     abc = {'patient': dep_object.name, 'address': dep_object.address, 'age': dep_object.age, 'sex': dep_object.sex}
    #     tests['value']=abc
    #     return tests

        #
        # import pdb
        # pdb.set_trace()

    def onchange_package(self,cr,uid,ids,package_name,vals,context=None):
        values={}
        if not package_name:
            return {}
        total_amount = 0.0
        abc={'leih_admission_line_id':[]}
        package_object=self.pool.get('examine.package').browse(cr,uid,package_name,context=None)

        for item in package_object.examine_package_line_id:
            items=item.name.id

            total_amount = total_amount + item.total_amount


            abc['leih_admission_line_id'].append([0, False, {'name':item.name.id,'total_amount':item.total_amount}])
        values['value']=abc

        return values


    def change_status(self, cr, uid, ids, context=None):
        values = {}

        stored_obj = self.browse(cr, uid, [ids[0]], context=context)
        ## Bill Status Will Change

        if stored_obj.state == 'activated':
            raise osv.except_osv(_('Warning!'),
                                 _('Already this Bill is Confirmed.'))
        cr.execute("update leih_admission set state='activated' where id=%s", (ids))
        cr.commit()

        stored = int(ids[0])

        ### check and merged with Lab report

        get_all_tested_ids = []

        for items in stored_obj.leih_admission_line_id:
            get_all_tested_ids.append(items.name.id)

        ### Ends here merged Section

        already_merged = []
        custom_name = ''

        for items in stored_obj.leih_admission_line_id:
            state = 'sample'
            if items.name.sample_req == False or items.name.sample_req == None:
                state = 'lab'

            custom_name = custom_name + str(items.name.name)

            if items.name.id not in already_merged:

                child_list = []
                value = {
                    'admission_id': int(stored),
                    'test_id': int(items.name.id),
                    'department_id': items.name.department.name,
                    'state': state,
                }

                for test_item in items.name.examination_entry_line:
                    tmp_dict = {}
                    tmp_dict['test_name'] = test_item.name
                    tmp_dict['ref_value'] = test_item.reference_value
                    child_list.append([0, False, tmp_dict])

                if items.name.merge == True:

                    for entry in items.name.merge_ids:
                        test_id = entry.examinationentry_id.id
                        custom_name = custom_name + str(entry.examinationentry_id.name)
                        if test_id in get_all_tested_ids:
                            already_merged.append(test_id)
                            for m_test_line in entry.examinationentry_id.examination_entry_line:
                                tmp_dict = {}
                                tmp_dict['test_name'] = m_test_line.name
                                tmp_dict['ref_value'] = m_test_line.reference_value
                                child_list.append([0, False, tmp_dict])

                value['sticker_line_id'] = child_list

                value['full_name'] = custom_name

                sample_obj = self.pool.get('diagnosis.sticker')
                sample_id = sample_obj.create(cr, uid, value, context=context)

                if sample_id is not None:
                    sample_text = 'Lab-0' + str(sample_id)
                    cr.execute('update diagnosis_sticker set name=%s where id=%s', (sample_text, sample_id))
                    cr.commit()

        if stored_obj.paid != False:


            ad_vals = {
                'date':'2021-01-01',
                'admission_id':stored_obj.id,
                'amount':stored_obj.paid,
                'type':'cash',
            }
            ad_obj = self.pool.get('admission.payment')
            ad_payment_id = ad_obj.create(cr, uid, ad_vals, context=context)

            assign_payment_line = self.pool.get('admission.payment').button_add_payment_action(cr, uid, [ad_payment_id], context=context)





        return values


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

                # 'default_partner_id': self.pool.get('res.partner')._find_accounting_partner(inv.partner_id).id,
                # 'default_amount': inv.type in ('out_refund', 'in_refund') and -inv.residual or inv.residual,
                # 'default_reference': inv.name,
                # 'close_after_process': True,
                # 'invoice_type': inv.type,
                # 'invoice_id': inv.id,
                # 'default_type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment',
                # 'type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment'
            }
        }
        raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))

    def btn_final_settlement(self, cr, uid, ids, context=None):
        if not ids: return []

        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'leih', 'admission_release_view')
        #
        inv = self.browse(cr, uid, ids[0], context=context)
        total=inv.total
        # import pdb
        # pdb.set_trace()
        return {
            'name':_("Pay Invoice"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'admission.release',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'default_total':total,
                'default_admission_id': ids[0]

            }
        }
        raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))


    def btn_pay(self, cr, uid, ids, context=None):
        if not ids: return []

        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'leih', 'admission_payment_form_view')
        #
        inv = self.browse(cr, uid, ids[0], context=context)
        # total=inv.total
        # import pdb
        # pdb.set_trace()
        return {
            'name':_("Pay Invoice"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'admission.payment',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'default_admission_id': ids[0],
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
                # 'default_price': 500,
                # # 'default_name':context.get('name', False),
                # 'default_total_amount': 200,
                # 'default_partner_id': self.pool.get('res.partner')._find_accounting_partner(inv.partner_id).id,
                # 'default_amount': inv.type in ('out_refund', 'in_refund') and -inv.residual or inv.residual,
                # 'default_reference': inv.name,
                # 'close_after_process': True,
                # 'invoice_type': inv.type,
                # 'invoice_id': inv.id,
                # 'default_type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment',
                # 'type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment'
            }
        }
        raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))


    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}

        stored = super(leih_admission, self).create(cr, uid, vals, context) # return ID int object

        if stored is not None:
            name_text = 'A-1000' + str(stored)
            cr.execute('update leih_admission set name=%s where id=%s', (name_text, stored))
            cr.commit()


        return stored

    @api.onchange('leih_admission_line_id')
    def onchange_admission_line(self):
        sumalltest=0
        for item in self.leih_admission_line_id:
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
    _name = 'leih.admission.line'



    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('leih.admission')
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
        'leih_admission_id': fields.many2one('leih.admission', "Information"),
        # 'currency_id': fields.related('pricelist_id', 'currency_id', type="many2one", relation="res.currency",
        #                               string="Currency", readonly=True, required=True),
        # 'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute=dp.get_precision('Account')),
        'price': fields.integer("Price"),
        'discount': fields.integer("Discount"),
        'total_amount': fields.integer("Total Amount")

    }

    def onchange_test(self,cr,uid,ids,name,context=None):
        tests = {'values': {}}
        dep_object = self.pool.get('examination.entry').browse(cr, uid, name, context=None)
        abc = {'price': dep_object.rate,'total_amount':dep_object.rate}
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
class admission_bill_register(osv.osv):
    _name = 'bill.register.admission.line'

    _columns = {
        'admission_line_id': fields.many2one('leih.admission', 'admission'),
        'bill_id':fields.many2one("bill.register","Bill ID"),
        'total':fields.float('Total')
    }

    def onchange_bill_id(self,cr,uid,ids,bill_id,context=None):
        lists={'values':{}}
        dep_object = self.pool.get('bill.register').browse(cr, uid, bill_id, context=None)
        bill_info={'total':dep_object.total}
        lists['value']=bill_info
        return lists

class admission_payment_line(osv.osv):
    _name = 'admission.payment.line'

    _columns = {
        'admission_payment_line_id': fields.many2one('leih.admission', 'admission payment'),
        'date':fields.datetime("Date"),
        'amount':fields.float('amount'),
        'type':fields.selection([('bank','Bank'),('cash','Cash')],'Type'),
        'card_no':fields.char('Card Number'),
        'bank_name':fields.char('Bank Name')

    }