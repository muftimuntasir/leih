from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class add_bill(osv.osv):
    _name = "add.bill"


    def button_add_action(self,cr,uid,ids,context=None):

        bill_register_line=self.pool.get('bill.register.line')
        bill_id=context.get("bill_id")
        add_test_object=self.browse(cr,uid,ids,context=None)
        test_name=add_test_object.name.id
        test_price=add_test_object.price
        test_discount=add_test_object.discount
        test_amount=add_test_object.total_amount


        vals_dict = {'discount': test_discount, 'price': test_price, 'bill_register_id': bill_id, 'name': test_name, 'total_amount': test_amount}
        # import pdb
        # pdb.set_trace()
        bill_id_confirm=bill_register_line.create(cr,uid,vals=vals_dict,context=None)





        return bill_id_confirm
        #


    _columns = {

        'name': fields.many2one("examination.entry", "Test Name", required=True, ondelete='cascade'),
        # 'bill_register_id': fields.many2one('bill.register', "Information"),
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
