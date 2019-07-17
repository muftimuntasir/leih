from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class testentry(osv.osv):
    _name = "leih.testentry"

    # def _dep(self, cr, uid, ids, field_name, arg, context=None):
    #     department={}
    #     for record in self.browse(cr, uid, ids, context=context):
    #         dep=record.group.department
    #         department[record.id]=dep
    #
    #     return department






    _columns = {

        'name': fields.char("Test Name",required=True),
        'group':fields.many2one('leih.group',"Group"),
        'department':fields.char("Department"),
        'rate':fields.integer("Rate"),
        'refarence_value':fields.char("Reference value"),
        'required_time':fields.char("Required time"),
        'entrr_parameters':fields.one2many('ss','testenry_id','Parameters',required=True)

    }
    def onchange_group(self,cr,uid,ids,group,context=None):

        test={'values':{}}
        dep_object=self.pool.get('leih.group').browse(cr,uid,group,context=None)
        abc={'department':dep_object.department.name}
        test['value']=abc
        # import pdb
        # pdb.set_trace()
        return test


# many2one('leih.doctors',"Test Names", required=True, ondelete='cascade', select=True)

class testentryparamaerte(osv.osv):
    _name = 'ss'
    _columns = {

        'name': fields.char("Name",required=True,ondelete='cascade'),
        'testenry_id': fields.many2one('leih.testentry', "Test Entry"),
        'reference_value': fields.char("Reference Value"),
        'others': fields.char("Others")
    }

    # def onchange_ll(self,cr,uid,ids,name,context=None):
    #     # raise osv.except_osv(_('ValidateError'), _('Directory name contains special characters!'))
    #     tests={'values':{}}
    #     dep_object = self.pool.get('leih.doctors').browse(cr, uid, name, context=None)
    #     abc = {'reference_value': dep_object.designation}
    #     tests['value'] = abc
    #     return tests