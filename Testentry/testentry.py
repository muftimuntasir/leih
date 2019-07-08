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
        'required_time':fields.char("Required time")




    }
    def onchange_group(self,cr,uid,ids,group,context=None):

        test={'values':{}}
        dep_object=self.pool.get('leih.group').browse(cr,uid,group,context=None)
        abc={'department':dep_object.department}
        test['value']=abc
        # import pdb
        # pdb.set_trace()
        return test


