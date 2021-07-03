from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time, datetime
from openerp import api


class bill_register(osv.osv):
    _name = "opd.ticket"
    _order = 'id desc'




    def _totalpayable(self, cr, uid, ids, field_name, arg, context=None):
        Percentance_calculation = {}
        sum = 0
        for items in self.pool.get("opd.ticket").browse(cr,uid,ids,context=None):
            total_list=[]
            for amount in items.opd_ticket_line_id:
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
        'mobile': fields.char(string="Mobile",store=False),
        'patient_id': fields.char(related='patient_name.patient_id',string="Patient Id",readonly=True),
        'patient_name': fields.many2one('patient.info', "Patient Name"),
        'address': fields.char("Address",store=False),
        'age': fields.char("Age",store=False),
        'sex':fields.char("Sex",store=False),
        'already_collected':fields.boolean("Money Collected",default=False),
        # 'date':fields.datetime("Date", readonly=True,default=lambda self: fields.datetime.now()),
        'date':fields.date("Date", readonly=True,default=lambda self: fields.datetime.now()),
        'ref_doctors': fields.many2one('doctors.profile','Reffered by'),
        'opd_ticket_line_id': fields.one2many('opd.ticket.line', 'opd_ticket_id', 'Investigations',required=True),
        # 'total': fields.function(_totalpayable,string="Total",type='float',store=True),
        'total': fields.float(string="Total")
    }
    _defaults = {
        # 'opd_ticket_line_id':[[0, False, {'department': 'Medicine', 'price': 100, 'name': 1, 'total_amount': 100}]],
    }


    def onchange_total(self,cr,uid,ids,name,context=None):
        tests = {'values': {}}
        dep_object = self.pool.get('leih.tests').browse(cr, uid, name, context=None)
        abc = {'total': dep_object.rate}
        tests['value'] = abc
        # import pdb
        # pdb.set_trace()
        return tests

    def onchange_patient(self,cr,uid,ids,name,context=None):
        tests={}
        dep_object = self.pool.get('patient.info').browse(cr, uid, name, context=None)
        abc={'mobile':dep_object.mobile,'address':dep_object.address,'age':dep_object.age,'sex':dep_object.sex}
        tests['value']=abc
        return tests





    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}

        stored = super(bill_register, self).create(cr, uid, vals, context) # return ID int object

        if stored is not None:

            name_text = 'OPD-1000' + str(stored)
            cr.execute('update opd_ticket set name=%s where id=%s', (name_text, stored))
            cr.commit()
        return stored

    @api.onchange('opd_ticket_line_id')
    def onchange_total(self):
        total=0
        for item in self.opd_ticket_line_id:
            total=total+item.total_amount
        self.total=total
        return 'O'







class test_information(osv.osv):
    _name = 'opd.ticket.line'

    _columns = {

        'name': fields.many2one("opd.ticket.entry","Item Name",ondelete='cascade'),
        'opd_ticket_id': fields.many2one('opd.ticket', "Information"),
        # 'currency_id': fields.related('pricelist_id', 'currency_id', type="many2one", relation="res.currency",
        #                               string="Currency", readonly=True, required=True),
        # 'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute=dp.get_precision('Account')),
        'price': fields.integer("Price"),
        'department':fields.char('Department'),
        'total_amount': fields.integer("Total Amount")

    }



    # @api.onchange('total_amount')
    # def change_item_price(self):
    #     opd_ticket_line_id=list()
    #     opd_ticket_line_id.append({
    #         'total':500
    #     })
    #
    #     ticket_id=self.opd_ticket_id
    #     return "Nothing"


    def onchange_item(self,cr,uid,ids,name,context=None):
        tests = {'values': {}}
        dep_object = self.pool.get('opd.ticket.entry').browse(cr, uid, name, context=None)
        abc = {'price': dep_object.fee,'department':dep_object.department.name,'total_amount':dep_object.fee}
        tests['value'] = abc
        # import pdb
        # pdb.set_trace()
        return tests



