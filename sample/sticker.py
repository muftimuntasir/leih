from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class sample(osv.osv):
    _name = "diagnosis.sticker"
    _order = 'id desc'


    def print_sticker(self,cr,uid,ids,context=None):
        statue='lab'


        for id in ids:
            report_obj = self.browse(cr, uid, id, context=context)
            if report_obj.state == 'lab' or report_obj.state == 'done':
                raise osv.except_osv(_('Warning!'),
                                     _('Already it is sample collected.'))
            cr.execute('update diagnosis_sticker set state=%s where id=%s', (statue, id))
            cr.commit()
        return self.pool['report'].get_action(cr, uid, ids, 'leih.report_sample_report', context=context)
        # return True

    def print_lab_report(self,cr,uid,ids,context=None):
        status='done'

        for id in ids:
            report_obj = self.browse(cr, uid, id, context=context)
            if report_obj.state == 'done':
                raise osv.except_osv(_('Warning!'),
                                     _('Already it is Completed.'))
            cr.execute('update diagnosis_sticker set state=%s where id=%s', (status, id))
            cr.commit()
        return True


    def set_to_lab(self,cr,uid,ids,context=None):
        status = 'lab'

        for id in ids:
            # report_obj = self.browse(cr, uid, id, context=context)
            # if report_obj.state == 'done':
            #     raise osv.except_osv(_('Warning!'),
            #                          _('Already it is Completed.'))
            cr.execute('update diagnosis_sticker set state=%s where id=%s', (status, id))
            cr.commit()
        return True





    _columns = {
        'name': fields.char('Name'),
        'bill_register_id':fields.many2one('bill.register','Bill register Id'),
        'department_id':fields.char('Department'),
        'sticker_line_id':fields.one2many('diagnosis.sticker.line','sticker_id','Record Sample'),
        'state': fields.selection(
            [('cancel', 'Cancelled'), ('sample', 'Sample'), ('lab', 'Lab'),('done', 'Done')],
            'Status', required=True, readonly=True, copy=False,
            ),

    }


class test_sample(osv.osv):
    _name = "diagnosis.sticker.line"

    _columns = {
        'test_name': fields.char("Name"),
        'sticker_id':fields.many2one('diagnosis.sticker','ID'),
        'ref_value': fields.char('Reference Value'),
        'result': fields.char('Test ID'),
        'remarks': fields.char('Remarks')

    }




