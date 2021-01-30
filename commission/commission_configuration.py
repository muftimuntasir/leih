from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time
from openerp import api





class commissionconfiguration(osv.osv):
    _name = "commission.configuration"




    _columns = {

        'name': fields.char("Name"),
        'doctor_id': fields.many2one('doctors.profile', 'Doctor/Broker Name'),
        'start_date':fields.date('MOU Start Date'),
        'end_date':fields.date('MOU End Date'),
        'overall_commission_rate': fields.float('Overall Commission Rate (%)'),
        'overall_default_discount': fields.float('Overall Discount Rate (%)'),
        'max_default_discount': fields.float('Max Discount Rate (%)'),
        'deduct_from_discount': fields.boolean("Deduct Excess Discount From Commission"),
        'add_few_departments': fields.boolean("Add by Department"),
        'department_ids':fields.many2one('diagnosis.department','Department List'),

        'commission_configuration_line_ids':fields.one2many("commission.configuration.line",'commission_configuration_line_ids',"Commission Lines"),
        'state': fields.selection(
            [('pending', 'Pending'), ('done', 'Confirmed'), ('cancelled', 'Cancelled')],
            'Status', default='pending', readonly=True)

    }

    _defaults = {
        'state': 'pending',

    }

    _order = 'id desc'

    @api.model
    def create(self, vals):
        record = super(commissionconfiguration, self).create(vals)

        record.name = 'CA-0' + str(record.id)
        return record

    @api.onchange('overall_commission_rate')
    def add_tests_ids_in_line_with_rate(self):
        line_data =[]
        if self.overall_commission_rate:
            try:
                comm_rate = round((self.overall_commission_rate/100),2)
            except:
                comm_rate=0
            if self.commission_configuration_line_ids:
                for items in self.commission_configuration_line_ids:
                    est_comm = round((comm_rate*items.test_price),2)

                    line_data.append({

                        'department_id': items.department_id,
                        'test_id': items.test_id,
                        'applicable': items.applicable,
                        'fixed_amount': items.fixed_amount,
                        'variance_amount': comm_rate,
                        'test_price': items.test_price,
                        'est_commission_amount': est_comm,
                        'max_commission_amount': items.max_commission_amount

                    })
        self.commission_configuration_line_ids=line_data


        return 'x'


    @api.onchange('department_ids')
    def add_tests_ids_in_line(self):
        comm_rate=0
        if self.overall_commission_rate:
            try:
                comm_rate = round((self.overall_commission_rate / 100), 2)
            except:
                comm_rate=0
        if self.department_ids:
            depet_id=self.department_ids.id
            query="select id,name,department,rate from examination_entry where id=%s"
            self._cr.execute(query, ([depet_id]))

            all_data = self._cr.dictfetchall()
            configure_line=[]


            if self.commission_configuration_line_ids:
                for items in self.commission_configuration_line_ids:
                    est_comm = round((comm_rate*items.test_price),2)

                    configure_line.append({

                        'department_id': items.department_id,
                        'test_id': items.test_id,
                        'applicable': items.applicable,
                        'fixed_amount': items.fixed_amount,
                        'variance_amount': comm_rate,
                        'test_price': items.test_price,
                        'est_commission_amount': est_comm,
                        'max_commission_amount': items.max_commission_amount

                    })


            for items in all_data:
                est_amnt=round((comm_rate*items.get('rate')),2)
                configure_line.append(
                    {

                        'department_id': items.get('department'),
                        'test_id': items.get('id'),
                        'applicable':True ,
                        'fixed_amount': 0,
                        'variance_amount':0 ,
                        'test_price': items.get('rate'),
                        'est_commission_amount': est_amnt,
                        'max_commission_amount': 0

                    }
                )
            self.commission_configuration_line_ids=configure_line



        return "xXxXxXxXxX"



    def confirm_configuration(self, cr, uid, ids, context=None):

        cr.execute("update commission_configuration set state='done' where id=%s", (ids))
        cr.commit()

        config_data = self.browse(cr, uid, ids, context=context)
        doc_id = config_data.doctor_id.id

        if config_data.state == 'done':
            raise osv.except_osv(_('Already Confirmed!'),
                                 _('Already Confirmed'))


        cr.execute("update doctors_profile set cc_id=%s where id=%s", ([doc_id,ids[0]]))
        cr.commit()




        return True

    def cancel_configuration(self, cr, uid, ids, context=None):
        config_data = self.browse(cr, uid, ids, context=context)

        if config_data.state == 'done':
            raise osv.except_osv(_('Already Confirmed!'),
                                 _('Already Confirmed'))

        cr.execute("update commission_configuration set state='cancelled' where id=%s", (ids))
        cr.commit()

        return True






class commissionconfigurationline(osv.osv):
    _name = "commission.configuration.line"

    _columns = {
        'commission_configuration_line_ids': fields.many2one('commission.configuration', 'Commission Configuration ID'),
        'department_id':fields.many2one('diagnosis.department','Department'),
        'test_id':fields.many2one('examination.entry','Test Name'),
        'applicable':fields.boolean('Applicable'),
        'fixed_amount': fields.float('Fixed Amount'),
        'variance_amount': fields.float('Amount (%)'),
        'test_price': fields.float('Test Fee'),
        'est_commission_amount': fields.float('Commission Amount'),
        'max_commission_amount': fields.float('Max Commission Amount'),


    }


class doctors_profile(osv.osv):
    _inherit = "doctors.profile"
    _columns = {

        'cc_id': fields.many2one('commission.configuration', 'Commission Rule')
    }

