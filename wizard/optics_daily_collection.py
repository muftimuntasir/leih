
import time
from openerp.osv import osv, fields


class optics_daily_collection(osv.osv_memory):
    _name = 'optics.daily.collection'
    _description = 'Daily Optics Collection Report '

    _columns = {
        'date_start': fields.datetime('Date',required=True),
        'date_end': fields.datetime('Date End',required=True),
    }


    def print_optics_report(self, cr, uid, ids, context=None):

        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        res = self.read(cr, uid, ids, ['date_start', 'date_end',], context=context)
        res = res and res[0] or {}
        datas['form'] = res
        if res.get('id',False):
            datas['ids']=[res['id']]

        return self.pool['report'].get_action(cr, uid, [], 'leih.report_optics_collection', data=datas, context=context)
