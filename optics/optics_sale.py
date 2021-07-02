from openerp import api
from openerp.exceptions import ValidationError
from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time, timedelta, datetime


class optics_sale(osv.osv):
    _name = "optics.sale"
    _order = 'id desc'



    def _totalpayable(self, cr, uid, ids, field_name, arg, context=None):
        Percentance_calculation = {}
        sum = 0
        for items in self.pool.get("optics.sale").browse(cr, uid, ids, context=None):
            total_list = []
            for amount in items.optics_sale_line_id:
                total_list.append(amount.total_amount)

            for item in total_list:
                sum = item + sum

                for record in self.browse(cr, uid, ids, context=context):
                    Percentance_calculation[record.id] = sum

        return Percentance_calculation


    _columns = {

        # 'patient_id': fields.char("Patient ID"),
        'name': fields.char("Name"),
        'mobile': fields.char(string="Mobile", readonly=True, store=False),
        'patient_id': fields.char(related='patient_name.patient_id', string="Patient Id", readonly=True),
        'patient_name': fields.many2one('patient.info', "Patient Name"),
        'address': fields.char("Address", store=False),
        'age': fields.char("Age", store=False),
        'sex': fields.char("Sex", store=False),
        'right_eye_sph': fields.char('Right Eye SPH'),
        'right_eye_cyl': fields.char('Right Eye CYL'),
        'right_eye_axis': fields.char('Right Eye AXIS'),
        'right_eye_sph_n': fields.char('Right Eye SPH -N'),
        'right_eye_cyl_n': fields.char('Right Eye CYL -N'),
        'right_eye_axis_n': fields.char('Right Eye AXIS -N'),
        'left_eye_sph': fields.char('Left Eye SPH'),
        'left_eye_cyl': fields.char('Left Eye CYL'),
        'left_eye_axis': fields.char('Left Eye AXIS'),
        'left_eye_sph_n': fields.char('Left Eye SPH -N'),
        'left_eye_cyl_n': fields.char('Left Eye CYL -N'),
        'left_eye_axis_n': fields.char('Left Eye AXIS -N'),
        'delivery_date': fields.date(string="Delivery Date"),
        'hard_cover':fields.boolean("Cover",default=True),
        'cell_pad':fields.boolean("Cell Pad",default=True),
        'frame_id':fields.many2one('product.product','Frame'),
        'delivery_id':fields.many2one('stock.picking','Delivery Challan'),
        'price':fields.float('Price'),
        'optics_lens_sale_line_id': fields.one2many('optics.lens.sale.line', 'optics_sale_id', 'Lens Entry', required=True),
        'optics_sale_payment_line_id': fields.one2many("optics.sale.payment.line", "optics_sale_payment_line_id",
                                                         "Bill Register Payment"),
        # 'footer_connection': fields.one2many('leih.footer', 'relation', 'Parameters', required=True),
        # 'relation': fields.many2one("leih.investigation"),
        # 'total': fields.float(_totalpayable,string="Total",type='float',store=True),
        'total': fields.float(string="Total"),
        'doctors_discounts': fields.float("Discount(%)"),
        'after_discount': fields.float("Discount Amount"),
        'other_discount': fields.float("Other Discount"),
        'grand_total': fields.float("Grand Total"),
        'paid': fields.float(string="Paid", required=True),
        'type': fields.selection([('cash', 'Cash'), ('bank', 'Bank')], 'Payment Type'),
        'card_no': fields.char('Card No.'),
        'bank_name': fields.char('Bank Name'),
        'due': fields.float("Due"),
        'date': fields.datetime("Date", readonly=True, default=lambda self: fields.datetime.now()),
        'state': fields.selection(
            [('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')],
            'Status', default='pending', readonly=True)
    }

    # if same item exist in line

    def create_picking(self, cr, uid, ids, context=None):
        """Create a picking for each order and validate it."""
        picking_obj = self.pool.get('stock.picking')
        partner_obj = self.pool.get('res.partner')
        move_obj = self.pool.get('stock.move')

        for order in self.browse(cr, uid, ids, context=context):
            if all(t == 'service' for t in order.lines.mapped('product_id.type')):
                continue

            picking_type = order.picking_type_id
            picking_id = False
            if picking_type:
                picking_id = picking_obj.create(cr, uid, {
                    'origin': order.name,
                    'partner_id': False,
                    'date_done': order.date_order,
                    'picking_type_id': picking_type.id,
                    'company_id': order.company_id.id,
                    'move_type': 'direct',
                    'note': order.note or "",
                    'invoice_state': 'none',
                }, context=context)
                self.write(cr, uid, [order.id], {'picking_id': picking_id}, context=context)
            location_id = order.location_id.id
            if order.partner_id:
                destination_id = order.partner_id.property_stock_customer.id
            elif picking_type:
                if not picking_type.default_location_dest_id:
                    raise osv.except_osv(_('Error!'),
                                         _('Missing source or destination location for picking type %s. Please configure those fields and try again.' % (
                                         picking_type.name,)))
                destination_id = picking_type.default_location_dest_id.id
            else:
                destination_id = partner_obj.default_get(cr, uid, ['property_stock_customer'], context=context)[
                    'property_stock_customer']

            move_list = []
            

            move_list.append(move_obj.create(cr, uid, {
                'name': order.name,
                'product_uom': order.frame_id.uom_id.id,
                'product_uos': order.frame_id.uom_id.id,
                'picking_id': picking_id,
                'picking_type_id': picking_type.id,
                'product_id': order.frame_id.id,
                'product_uos_qty': abs(1),
                'product_uom_qty': abs(1),
                'state': 'draft',
                'location_id': location_id if order.qty >= 0 else destination_id,
                'location_dest_id': destination_id if order.qty >= 0 else location_id,
            }, context=context))


            if picking_id:
                picking_obj.action_confirm(cr, uid, [picking_id], context=context)
                picking_obj.force_assign(cr, uid, [picking_id], context=context)
                picking_obj.action_done(cr, uid, [picking_id], context=context)

        return True

    def bill_confirm(self, cr, uid, ids, context=None):

        stored_obj = self.browse(cr, uid, [ids[0]], context=context)
        ## Bill Status Will Change


        stored = int(ids[0])
        if stored_obj.state == 'confirmed':
            raise osv.except_osv(_('Warning!'),
                                 _('Already it is  Confirmed. Yuo can not change.'))

        if stored_obj.paid != False:
            for bills_vals in stored_obj:

                mr_value = {
                    'date': stored_obj.date,
                    'optics_sale_id': int(stored),
                    'amount': stored_obj.paid,
                    'type': stored_obj.type,
                }
            mr_obj = self.pool.get('leih.money.receipt')
            mr_id = mr_obj.create(cr, uid, mr_value, context=context)
            if mr_id is not None:
                mr_name = 'MR#' + str(mr_id)
                cr.execute('update leih_money_receipt set name=%s where id=%s', (mr_name, mr_id))
                cr.commit()


            #### Create a challan

            picking_obj = self.pool.get('stock.picking')
            partner_obj = self.pool.get('res.partner')
            move_obj = self.pool.get('stock.move')

            for order in self.browse(cr, uid, ids, context=context):


                picking_id = picking_obj.create(cr, uid, {
                    'origin': order.name,
                    'partner_id': False,
                    'date_done': stored_obj.date,
                    'picking_type_id': 13, ## Hard Coded
                    # 'company_id': order.company_id.id,
                    'move_type': 'direct',
                    'note': "",
                    'invoice_state': 'none',
                }, context=context)
                self.write(cr, uid, [order.id], {'picking_id': picking_id}, context=context)
                location_id = 25 # Source Location from where stock will reduce

                destination_id = 9 ## Customer location


                move_list = []

                move_list.append(move_obj.create(cr, uid, {
                    'name': order.name,
                    'product_uom': order.frame_id.uom_id.id,
                    'product_uos': order.frame_id.uom_id.id,
                    'picking_id': picking_id,
                    'picking_type_id': 13,
                    'product_id': order.frame_id.id,
                    'product_uos_qty': abs(1),
                    'product_uom_qty': abs(1),
                    'state': 'draft',
                    'location_id': location_id,
                    'location_dest_id': destination_id,
                }, context=context))


                for opt_line in order.optics_lens_sale_line_id:
                    move_list.append(move_obj.create(cr, uid, {
                        'name': order.name,
                        'product_uom': opt_line.product_id.uom_id.id,
                        'product_uos': opt_line.product_id.uom_id.id,
                        'picking_id': picking_id,
                        'picking_type_id': 13,
                        'product_id': opt_line.product_id.id,
                        'product_uos_qty': abs(opt_line.qty),
                        'product_uom_qty': abs(opt_line.qty),
                        'state': 'draft',
                        'location_id': location_id,
                        'location_dest_id': destination_id,
                    }, context=context))


                if picking_id:
                    picking_obj.action_confirm(cr, uid, [picking_id], context=context)
                    picking_obj.force_assign(cr, uid, [picking_id], context=context)
                    picking_obj.action_done(cr, uid, [picking_id], context=context)
                    cr.execute("update optics_sale set delivery_id=%s where id=%s", (picking_id,ids[0]))
                    cr.commit()

            ### Ends Here

            cr.execute("update optics_sale set state='confirmed' where id=%s", (ids))
            cr.commit()
        else:
            raise osv.except_osv(_('Warning!'),
                                 _('Minimum Payment is Required'))

        return self.pool['report'].get_action(cr, uid, ids, 'leih.report_optics_sale', context=context)



    def onchange_patient(self, cr, uid, ids, name, context=None):
        tests = {}
        dep_object = self.pool.get('patient.info').browse(cr, uid, name, context=None)
        abc = {'mobile': dep_object.mobile, 'address': dep_object.address, 'age': dep_object.age, 'sex': dep_object.sex}
        tests['value'] = abc
        return tests


    def bill_cancel(self, cr, uid, ids, context=None):
        ## Bill Status Will Change

        cr.execute("update optics_sale set state='cancelled' where id=%s", (ids))
        cr.commit()

        return True

    def btn_pay_bill(self, cr, uid, ids, context=None):
        if not ids: return []

        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'leih',
                                                                             'optics_sale_payment_form_view')
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
            'res_model': 'optics.sale.payment',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'default_optics_sale_id': ids[0],
                'default_amount': inv.due
            }
        }
        raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))


    def create(self, cr, uid, vals, context=None):

        if context is None:
            context = {}

        stored = super(optics_sale, self).create(cr, uid, vals, context)  # return ID int object

        if stored is not None:
            name_text = 'Opt-0' + str(stored)
            cr.execute('update optics_sale set name=%s where id=%s', (name_text, stored))
            cr.commit()

        return stored

    def write(self, cr, uid, ids, vals, context=None):
        return super(optics_sale, self).write(cr, uid, ids, vals, context=context)


    @api.onchange('optics_lens_sale_line_id')
    def onchange_lens_bill(self):
        sumalltest = self.total
        for item in self.optics_lens_sale_line_id:
            sumalltest = sumalltest + item.total_amount

        self.total = sumalltest
        after_dis = (sumalltest * (self.doctors_discounts / 100))
        self.after_discount = after_dis
        self.grand_total = sumalltest - self.other_discount - after_dis
        self.due = sumalltest - after_dis - self.other_discount - self.paid

        return "X"




    @api.onchange('paid')
    def onchange_paid(self):
        self.due = self.grand_total - self.paid
        return 'x'

    # @api.onchange('doctors_discounts')
    # def onchange_doc_discount(self):
    #     aft_discount = (self.total * (self.doctors_discounts / 100))
    #     self.after_discount = aft_discount
    #     self.grand_total = self.total - aft_discount - self.other_discount
    #     self.due = self.total - aft_discount - self.other_discount - self.paid
    #
    #     return "X"

    @api.onchange('other_discount')
    def onchange_other_discount(self):
        self.grand_total = self.total - self.after_discount - self.other_discount
        self.due = self.total - self.after_discount - self.other_discount - self.paid
        return 'True'


# class optics_information(osv.osv):
#     _name = 'optics.sale.line'
#
#     def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
#         cur_obj = self.pool.get('optics.sale')
#         res = {}
#         for record in self.browse(cr, uid, ids, context=context):
#             rate = record.price
#             discount = record.discount
#             interst_amount = int(discount) * int(rate) / 100
#             total_amount = int(rate) - interst_amount
#             res[record.id] = total_amount
#             # import pdb
#             # pdb.set_trace()
#         return res
#
#     _columns = {
#
#         'name': fields.many2one("product.product", "Item Name", ondelete='cascade'),
#         'optics_sale_id': fields.many2one('optics.sale', "Information"),
#         'department': fields.char("Department"),
#         'delivery_date': fields.date("Delivery Date"),
#         'date': fields.datetime("Date", readonly=True, default=lambda self: fields.datetime.now()),
#         # 'currency_id': fields.related('pricelist_id', 'currency_id', type="many2one", relation="res.currency",
#         #                               string="Currency", readonly=True, required=True),
#         # 'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute=dp.get_precision('Account')),
#         'price': fields.integer("Price"),
#         'qty': fields.integer("Quantity"),
#         'total_amount': fields.integer("Total Amount"),
#         'assign_doctors': fields.many2one('doctors.profile', 'Doctor'),
#         'commission_paid': fields.boolean("Commission Paid"),
#
#     }

    # def onchange_test(self, cr, uid, ids, name, context=None):
    #     tests = {'values': {}}
    #     dep_object = self.pool.get('product.product').browse(cr, uid, name, context=None)
    #
    #     abc = {'price': dep_object.list_price, 'total_amount': dep_object.list_price,
    #            'optics_sale_id.paid': dep_object.list_price}
    #     tests['value'] = abc
    #     # import pdb
    #     # pdb.set_trace()
    #     return tests

    # def onchange_discount(self, cr, uid, ids, name, discount, context=None):
    #     tests = {'values': {}}
    #     dep_object = self.pool.get('examination.entry').browse(cr, uid, name, context=None)
    #     abc = {'total_amount': round(dep_object.rate - (dep_object.rate * discount / 100))}
    #     tests['value'] = abc
    #     # import pdb
    #     # pdb.set_trace()
    #     return tests

    # def create(self, cr, uid, vals, context=None):
    #     # deliry_min_time
    #     stored = super(optics_information, self).create(cr, uid, vals, context)
    #
    #
    #     # today = datetime.datetime.strftime(datetime.datetime.today(), '%d/%m/%Y-%Hh/%Mm')
    #
    #     return 0

    # def write(self, cr, uid, vals, context=None):
    #     import pdb
    #     pdb.set_trace()


#starting the process of frame

class optics_lens_information(osv.osv):
    _name = 'optics.lens.sale.line'


    _columns = {

        'name': fields.many2one("product.lens", "Lens Name", ondelete='cascade'),
        'product_id': fields.many2one('product.product', "Lens Name"),
        'optics_sale_id': fields.many2one('optics.sale', "Information", required=True),
        'price': fields.integer("Unit Price"),
        'qty': fields.integer("Quantity"),
        'total_amount': fields.integer("Total Amount"),


    }

    def onchange_lens(self, cr, uid, ids, name, context=None):
        tests = {'values': {}}
        # dep_object = self.pool.get('product.product').browse(cr, uid, name, context=None)
        # abc = {'price': dep_object.sell_price,'qty':1, 'total_amount': dep_object.sell_price,
        #        'optics_sale_id.paid': dep_object.sell_price}
        # tests['value'] = abc
        #
        # import pdb
        # pdb.set_trace()
        return tests

    def onchange_price(self, cr, uid, ids, name,price, context=None):
        tests = {'values': {}}
        dep_object = self.pool.get('product.lens').browse(cr, uid, name, context=None)
        abc = {'price': price, 'total_amount': price}
        tests['value'] = abc
        #
        # import pdb
        # pdb.set_trace()
        return tests

    def onchange_qty(self, cr, uid, ids, name,qty,price, context=None):
        tests = {'values': {}}
        # import pdb
        # pdb.set_trace()
        total_line=price*qty
        abc = {'qty': qty,'total_amount':total_line}
        tests['value'] = abc
        #
        # import pdb
        # pdb.set_trace()
        return tests

    # def onchange_discount(self, cr, uid, ids, name, discount, context=None):
    #     tests = {'values': {}}
    #     dep_object = self.pool.get('examination.entry').browse(cr, uid, name, context=None)
    #     abc = {'total_amount': round(dep_object.rate - (dep_object.rate * discount / 100))}
    #     tests['value'] = abc
    #     # import pdb
    #     # pdb.set_trace()
    #     return tests

    # def create(self, cr, uid, vals, context=None):
    #     # deliry_min_time
    #     stored = super(optics_lens_information, self).create(cr, uid, vals, context)
    #     optics_sale_line_object = self.browse(cr, uid, stored, context=context)
    #     test_name = optics_sale_line_object.name
    #     required_time = test_name.required_time
    #     today = date.today()
    #     delivery_date = today + timedelta(days=required_time)
    #     cr.execute("update optics_sale_line set delivery_date=%s where id=%s", (delivery_date, stored))
    #     cr.commit()
    #
    #     # today = datetime.datetime.strftime(datetime.datetime.today(), '%d/%m/%Y-%Hh/%Mm')
    #
    #     return 0

    # def write(self, cr, uid, vals, context=None):
    #     import pdb
    #     pdb.set_trace()

#end of the process of lance






class admission_payment_line(osv.osv):
    _name = 'optics.sale.payment.line'

    _columns = {
        'optics_sale_payment_line_id': fields.many2one('optics.sale', 'bill register payment'),
        'date': fields.datetime("Date"),
        'amount': fields.float('Amount'),
        'type': fields.selection([('bank', 'Bank'), ('cash', 'Cash')], 'Type'),
        'card_no': fields.char('Card Number'),
        'bank_name': fields.char('Bank Name'),
        'money_receipt_id': fields.many2one('leih.money.receipt', 'Money Receipt ID'),

    }




