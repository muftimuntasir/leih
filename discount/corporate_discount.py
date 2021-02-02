from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time
from openerp import api

class corporatediscount(osv.osv):
    _name = "corporate.discount"


    _columns = {

        'name': fields.char("Corporate Disocunt ID"),
        'bill_id': fields.many2one('bill.register', 'Bill ID'),
        'date':fields.date('Date'),
        'corporate_id':fields.many2one('discount.configuration', 'Corporate ID'),
        # 'debit_id': fields.many2one('account.account', 'Debit Account'),
        # 'credit_id': fields.many2one('account.account', 'Credit Account'),
        'discount_amount': fields.float('Discount Amount'),
        'total_amount': fields.float('Due Amount'),
        'period_id': fields.many2one('account.period','Period'),
        'journal_id': fields.many2one('account.move','Journal'),
        'note': fields.text("Note"),

        'state': fields.selection(
            [('pending', 'Pending'), ('done', 'Confirmed'), ('cancelled', 'Cancelled')],
            'Status', default='pending', readonly=True)

    }
    _defaults = {
        'state': 'pending',

    }

    _order = 'id desc'


    # @api.onchange('corporate_id')
    def onchange_corporate_client(self,cr,uid,ids,corporate_id,bill_id,context=None):
        if corporate_id:
        # import pdb
        # pdb.set_trace()
        # bill_ids=bill_id['default_bill_id']
            bill_object=self.pool.get('bill.register').browse(cr, uid, bill_id, context=context)
            # self.bill_id.bill_register_line_id.name
            testdict=[item.name for item in bill_object.bill_register_line_id]
            # corporate_id=self.corporate_id


            #query for discount configuration
            query = "select discount_configuration_line.test_id,discount_configuration_line.after_discount,discount_configuration_line.applicable from discount_configuration,discount_configuration_line where discount_configuration_line.discount_donfiguration_line_ids=discount_configuration.id and discount_configuration_line.applicable = True and discount_configuration.id =%s"
            cr.execute(query, ([corporate_id]))

            all_data = cr.dictfetchall()

            total_discount=0
            for bill_item in testdict:
                for discount_item in all_data:

                    if discount_item.get('test_id') == bill_item.id and discount_item.get('applicable') == True:
                        # import pdb
                        # pdb.set_trace()
                        total_discount = total_discount + discount_item.get('after_discount')
                        break

            tests = {'values': {}}
            abc = {'discount_amount': total_discount}
            tests['value'] = abc
            return tests


class bill_register_inherit(osv.osv):
    _inherit ="bill.register"

    def btn_corporate_discount(self, cr, uid, ids, context=None):
        if not ids: return []

        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'leih','corporate_discount_form_view')
        #
        inv = self.browse(cr, uid, ids[0], context=context)
        # import pdb
        # pdb.set_trace()

        return {
            'name': _("Payment"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'corporate.discount',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'default_bill_id': ids[0]
                # 'default_paid_amount': inv.total_payable_amount
            }
        }
        raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))







