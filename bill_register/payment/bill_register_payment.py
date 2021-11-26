from openerp.osv import osv, fields
from openerp import SUPERUSER_ID, api
from openerp.tools.translate import _
from datetime import datetime




class bill_register_payment(osv.osv):
    _name = 'bill.register.payment'
    _description = "bill register Payment"


    def button_add_payment_action(self,cr,uid,ids,context=None):

        payment_obj=self.browse(cr,uid,ids,context=None)
        bill_id=payment_obj.bill_id.id
        bill_register_id=payment_obj.bill_id.name
        eve_mee_obj = self.pool.get('bill.register.payment.line')
        pay_date=payment_obj.date
        pay_amount = payment_obj.amount
        pay_type = payment_obj.type
        pay_card=payment_obj.card_no
        pay_bank=payment_obj.bank_name
        current_due =payment_obj.bill_id.due
        current_paid =payment_obj.bill_id.paid
        money_receipt_id =payment_obj.money_receipt_id.id

        updated_amount = current_due-pay_amount
        updated_paid = current_paid+pay_amount
        if updated_amount <0:
            updated_amount=0

        service_dict={'date': pay_date,'amount':pay_amount,'type': pay_type,'card_no':pay_card ,'bill_register_payment_line_id': bill_id,'money_receipt_id':money_receipt_id}

        service_id = eve_mee_obj.create(cr, uid, vals=service_dict, context=context)

        cr.execute("update bill_register set due=%s,paid=%s where id=%s", (updated_amount,updated_paid,bill_id))
        cr.commit()
        # ###journal_entry
        # line_ids = []
        #
        # if context is None: context = {}
        # if context.get('period_id', False):
        #     return context.get('period_id')
        # periods = self.pool.get('account.period').find(cr, uid, context=context)
        # period_id = periods and periods[0] or False
        #
        # if current_paid > 0:
        #
        #     line_ids.append((0, 0, {
        #         'analytic_account_id': False,
        #         'tax_code_id': False,
        #         'tax_amount': 0,
        #         'name': bill_register_id,
        #         'currency_id': False,
        #         'credit': 0,
        #         'date_maturity': False,
        #         'account_id': 6,  ### Cash ID
        #         'debit': current_paid,
        #         'amount_currency': 0,
        #         'partner_id': False,
        #     }))
        #     if context is None:
        #         context = {}
        #
        #     line_ids.append((0, 0, {
        #         'analytic_account_id': False,
        #         'tax_code_id': False,
        #         'tax_amount': 0,
        #         'name': bill_register_id,
        #         'currency_id': False,
        #         'credit': current_paid,
        #         'date_maturity': False,
        #         'account_id': 6010,  ### Accounts Receivable ID
        #         'debit': 0,
        #         'amount_currency': 0,
        #         'partner_id': False,
        #     }))
        #
        #
        #
        #
        #
        #
        # jv_entry = self.pool.get('account.move')
        #
        # j_vals = {'name': '/',
        #           'journal_id': 8,  ## Sales Journal
        #           'date': fields.date.today(),
        #           'period_id': period_id,
        #           'ref': bill_register_id,
        #           'line_id': line_ids
        #
        #           }
        #
        # # import pdb
        # # pdb.set_trace()
        # saved_jv_id = jv_entry.create(cr, uid, j_vals, context=context)
        #
        # if saved_jv_id > 0:
        #     journal_id = saved_jv_id
        # jv_entry.button_validate(cr, uid, [saved_jv_id], context)


        ###end journal






        return service_id

    _columns = {
        'name':fields.char("Cash Collection ID", readonly=True),
        'bill_id': fields.many2one('bill.register', 'Bill ID', readoly=True),
        'date': fields.date('Date',required=True),
        'amount': fields.float('Receive Amount', required=True),
        'type': fields.selection([('bank','Bank'),('cash','Cash')],'Type'),
        'card_no':fields.char('Card No.'),
        'bank_name':fields.char('Bank Name'),
        'money_receipt_id': fields.many2one('leih.money.receipt', 'Money Receipt ID'),
    }

    def create(self,cr,uid,vals,context):
        storedpayment = super(bill_register_payment, self).create(cr, uid, vals, context)  # return ID int object

        if storedpayment is not None:
            name_text = 'CC-100' + str(storedpayment)
            cr.execute('update bill_register_payment set name=%s where id=%s', (name_text, storedpayment))
            cr.commit()
        value={}
        value['date']=vals['date']
        value['bill_id']=vals['bill_id']
        value['amount']=vals['amount']
        value['type']=vals['type']
        value['p_type'] = 'due_payment'

        # value['user_id']=vals['user_id']
        stored_obj = self.pool.get("bill.register").browse(cr, uid, vals['bill_id'], context=None)
        diagonostic_bill = stored_obj.diagonostic_bill
        value['diagonostic_bill'] = diagonostic_bill

        mr_object=self.pool.get("leih.money.receipt")
        mr_id=mr_object.create(cr, uid, value, context=context)



        ## Bill Status Will Change

        # if stored_obj.state == 'confirmed':
        #     raise osv.except_osv(_('Warning!'),
        #                          _('Already this Bill is Confirmed.'))
        grand_total = stored_obj.grand_total
        if grand_total != 0:
            cr.execute("update bill_register set state='confirmed' where id=%s", ([vals['bill_id']]))
            cr.commit()

            stored = int(vals['bill_id'])

            ### check and merged with Lab report

            get_all_tested_ids = []

            for items in stored_obj.bill_register_line_id:
                get_all_tested_ids.append(items.name.id)

            ### Ends here merged Section

            already_merged = []
            custom_name = ''

            for items in stored_obj.bill_register_line_id:
                custom_name = ''
                state = 'sample'
                ### Create LAB/SAMPLE From Here
                if items.name.sample_req == False or items.name.sample_req == None:
                    state = 'lab'

                if items.name.manual != True or items.name.lab_not_required != True:

                    custom_name = custom_name + ' ' + str(items.name.name)

                    if items.name.id not in already_merged:

                        child_list = []
                        value = {
                            'bill_register_id': int(stored),
                            'test_id': int(items.name.id),
                            'department_id': items.name.department.name,
                            'state': state
                        }

                        for test_item in items.name.examination_entry_line:
                            tmp_dict = {}
                            tmp_dict['test_name'] = test_item.name
                            tmp_dict['ref_value'] = test_item.reference_value
                            tmp_dict['bold'] = test_item.bold
                            tmp_dict['group_by'] = test_item.group_by
                            child_list.append([0, False, tmp_dict])

                        if items.name.merge == True:

                            for entry in items.name.merge_ids:
                                test_id = entry.examinationentry_id.id

                                if test_id in get_all_tested_ids:
                                    custom_name = custom_name + ', ' + str(entry.examinationentry_id.name)
                                    already_merged.append(test_id)
                                    for m_test_line in entry.examinationentry_id.examination_entry_line:
                                        tmp_dict = {}
                                        tmp_dict['test_name'] = m_test_line.name
                                        tmp_dict['ref_value'] = m_test_line.reference_value
                                        tmp_dict['bold'] = m_test_line.bold
                                        tmp_dict['group_by'] = m_test_line.group_by
                                        child_list.append([0, False, tmp_dict])

                        value['sticker_line_id'] = child_list

                        value['full_name'] = custom_name

                        sample_obj = self.pool.get('diagnosis.sticker')
                        sample_id = sample_obj.create(cr, uid, value, context=context)

                    ### Ends Here LAB/SAMPLE From Here

                    if sample_id is not None:
                        sample_text = 'Lab-0' + str(sample_id)
                        cr.execute('update diagnosis_sticker set name=%s where id=%s', (sample_text, sample_id))
                        cr.commit()



        if mr_id is not None:
            mr_name='MR#' +str(mr_id)
            cr.execute('update leih_money_receipt set name=%s where id=%s',(mr_name,mr_id))
            cr.execute('update bill_register_payment set money_receipt_id=%s where id=%s',(mr_id,storedpayment))
            cr.commit()

        #confirm on paid





        return storedpayment
