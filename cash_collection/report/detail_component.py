import datetime
import pytz
import time
from openerp import tools
from openerp.osv import osv
from openerp.report import report_sxw


class detail_collcetion_details(report_sxw.rml_parse):

    def _get_user_names(self, t_dat=None, end_date=None):
        st_dat=t_dat
        end_date= end_date
        result = []

        opd_component_q = "select sum(opd_ticket_line.total_amount) as t_amnt,count(opd_ticket_line.total_amount) as t_count, " \
                          "(select opd_ticket_entry.name from opd_ticket_entry where opd_ticket_entry.id=opd_ticket_line.name) as name ,opd_ticket_line.department " \
                          "from opd_ticket_line,opd_ticket where opd_ticket_line.opd_ticket_id=opd_ticket.id and (opd_ticket.create_date <= '%s')" \
                          " and (opd_ticket.create_date >= '%s') " \
                          "group by opd_ticket_line.name, opd_ticket_line.department order by opd_ticket_line.department asc"


        bill_q = "select sum(bill_register_line.total_amount),count(bill_register_line.total_amount) as tl," \
                 " (select examination_entry.name from examination_entry where examination_entry.id=bill_register_line.name) as name,bill_register_line.department " \
                 "from bill_register_line,bill_register where bill_register_line.bill_register_id=bill_register.id and " \
                 "(bill_register.create_date <= '%s') and (bill_register.create_date >= '%s') " \
                 "group by bill_register_line.name, bill_register_line.department order by bill_register_line.department"

        admission_query = "select sum(leih_admission_line.total_amount) as tm,count(leih_admission_line.total_amount) as tv, " \
                          "(select examination_entry.name from examination_entry where examination_entry.id=leih_admission_line.name) as name " \
                          "from leih_admission_line,leih_admission where leih_admission_line.leih_admission_id=leih_admission.id " \
                          "and (leih_admission.create_date <='%s') and (leih_admission.create_date >='%s') " \
                          "group by leih_admission_line.name"

        ## It sis For BIll Data Collction
        self.cr.execute(opd_component_q % (end_date,st_dat))
        participant_ids = []
        opd_info = []
        for items in self.cr.fetchall():
            opd_info.append({
                'test_name':items[2],
                'test_count':items[1],
                'test_amnt':items[0],
                'test_dept':'OPD',
            })


        ## Bill Collction Ends Here

        ## It sis For Addmission Data Collction

        self.cr.execute(bill_q % (end_date, st_dat))
        for items in self.cr.fetchall():
            opd_info.append({
                'test_name': items[2],
                'test_count': items[1],
                'test_amnt': items[0],
                'test_dept': items[3],
            })

        ## Addmission Collction Ends Here

        ## It sis For Addmission Data Collction
        self.cr.execute(admission_query % (end_date,st_dat))

        for items in self.cr.fetchall():
            opd_info.append({
                'test_name': items[2],
                'test_count': items[1],
                'test_amnt': items[0],
                'test_dept': "",
            })
        ## Addmission Collction Ends Here


        return opd_info

    def _get_context_text(self, t_dat=None, end_date=None):
        txt = "Start Date " + str(t_dat)  + " End Date " + str(end_date)
        return txt

    def __init__(self, cr, uid, name, context):



        super(detail_collcetion_details, self).__init__(cr, uid, name, context=context)

        self.localcontext.update({
            'get_user_names': self._get_user_names,
            'get_user_context': self._get_context_text,
        })


class report_detail_component(osv.AbstractModel):
    _name = 'report.leih.report_detail_component'
    _inherit = 'report.abstract_report'
    _template = 'leih.report_detail_component'
    _wrapped_report_class = detail_collcetion_details
