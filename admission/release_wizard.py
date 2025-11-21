from openerp.osv import osv, fields

class leih_admission_release_wizard(osv.osv_memory):
    _name = 'leih.admission.release.wizard'
    _description = 'Wizard to confirm release of selected admissions'

    _columns = {
        'note': fields.text('Note (optional)'),
    }

    def action_confirm_release(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        active_ids = context.get('active_ids', []) or []
        if not active_ids:
            return {'type': 'ir.actions.act_window_close'}

        # perform the release on leih.admission
        self.pool.get('leih.admission').write(cr, uid, active_ids, {'state': 'released'}, context=context)

        # close the wizard
        return {'type': 'ir.actions.act_window_close'}

leih_admission_release_wizard()
