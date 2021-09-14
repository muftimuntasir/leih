import datetime
import pytz
import time
from openerp import tools
from openerp.osv import osv
from openerp.report import report_sxw


class collcetion_details(report_sxw.rml_parse):

    def _get_user_names(self, t_dat=None, end_date=None):
        st_dat=t_dat
        end_date= end_date
        result = []

        bill_q = "select sum(amount) as totla_collection, create_uid from leih_money_receipt where bill_id is not Null " \
                 "and state='confirm' and diagonostic_bill=TRUE and (create_date <= '%s') and (create_date >= '%s') group by create_uid"


        bill_others = "select sum(amount) as totla_collection, create_uid from leih_money_receipt where bill_id is not Null " \
                 "and state='confirm' and (diagonostic_bill=FALSE OR diagonostic_bill IS NULL) and (create_date <= '%s') and (create_date >= '%s') group by create_uid"

        add_q= "select sum(amount) as totla_collection, create_uid from leih_money_receipt where admission_id is not Null" \
               " and state='confirm' and (create_date <= '%s') and (create_date >= '%s') group by create_uid"

        optic_q = "select sum(amount) as totla_collection, create_uid from leih_money_receipt where optics_sale_id is not Null" \
                  " and state='confirm' and (create_date <= '%s') and (create_date >= '%s') group by create_uid"


        ## It sis For BIll Data Collction
        self.cr.execute(bill_q % (end_date,st_dat))
        participant_ids = []
        bill_info = {}
        for items in self.cr.fetchall():
            if items[1] is not participant_ids:
                participant_ids.append(items[1])
            bill_info[items[1]]=items[0]

        self.cr.execute(bill_others % (end_date,st_dat))
        participant_ids = []
        bill_other_info = {}
        for items in self.cr.fetchall():
            if items[1] is not participant_ids:
                participant_ids.append(items[1])
            bill_other_info[items[1]]=items[0]


        ## Bill Collction Ends Here

        ## It sis For Addmission Data Collction

        self.cr.execute(add_q % (end_date, st_dat))

        adm_info = {}
        for items in self.cr.fetchall():
            if items[1] is not participant_ids:
                participant_ids.append(items[1])
            adm_info[items[1]] = items[0]

        ## Addmission Collction Ends Here

        ## It sis For Addmission Data Collction
        self.cr.execute(optic_q % (end_date,st_dat))

        optic_info = {}
        for items in self.cr.fetchall():
            if items[1] is not participant_ids:
                participant_ids.append(items[1])
            optic_info[items[1]] = items[0]

        ## Addmission Collction Ends Here

        ## OPD Data Query
        opd_q = "select sum(total) as total_b, create_uid from opd_ticket " \
                "where (create_date <='%s') and (create_date >='%s') group by create_uid"



        self.cr.execute(opd_q % (end_date, st_dat))

        opd_info = {}
        for items in self.cr.fetchall():
            if items[1] is not participant_ids:
                participant_ids.append(items[1])
            opd_info[items[1]] = items[0]


        ## Optics Ends Here


        participant_ids = list(set(participant_ids))


        ## Users Name Get

        user_q = "select res_partner.name,res_users.id from res_users, res_partner where res_users.partner_id=res_partner.id and res_users.id in %s"

        self.cr.execute(user_q , (tuple(participant_ids),))
        user_info = {}

        for items in self.cr.fetchall():
            user_info[items[1]]=items[0]


        ### Ends Here

        for user_id in participant_ids:
            b_amnt = bill_info.get(user_id) if bill_info.get(user_id) else 0
            b_other_amnt=bill_other_info.get(user_id) if bill_other_info.get(user_id) else 0
            adm_amnt = adm_info.get(user_id) if adm_info.get(user_id) else 0
            opt_amnt= optic_info.get(user_id) if optic_info.get(user_id) else 0
            opd_amnt= opd_info.get(user_id) if opd_info.get(user_id) else 0

            total = b_amnt + b_other_amnt+ adm_amnt + opt_amnt + opd_amnt
            result.append({
                'user_name':user_info.get(user_id),
                'bill_collection': b_amnt,
                'bill_other_collection':b_other_amnt,
                'admission_collection': adm_amnt,
                'optics_collection': opt_amnt,
                'opd_collection':opd_amnt,
                'total_collection':total,
            })


        return result

    def _get_context_text(self, t_dat=None, end_date=None):
        txt = "Start Date " + str(t_dat)  + " End Date " + str(end_date)
        return txt

    def __init__(self, cr, uid, name, context):



        super(collcetion_details, self).__init__(cr, uid, name, context=context)

        self.localcontext.update({
            'get_user_names': self._get_user_names,
            'get_user_context': self._get_context_text,
        })


class report_cc_collection(osv.AbstractModel):
    _name = 'report.leih.report_cc_collection'
    _inherit = 'report.abstract_report'
    _template = 'leih.report_cc_collection'
    _wrapped_report_class = collcetion_details
