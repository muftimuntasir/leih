from openerp import api
from openerp.exceptions import ValidationError
from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time
from datetime import datetime


class patient_info(osv.osv):
    _name = "patient.info"
    # _rec_name = 'patient_id'

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        res = []
        for elmt in self.browse(cr, uid, ids, context=context):
            name = elmt.name
            try:
                name = name + ' ' + str(elmt.patient_id) if elmt.patient_id is not False else '---'
                res.append((elmt.id, name))
            except ValueError:
                pass
        return res

    # def name_search(self, name, args=None, operator='ilike', limit=100):
    #     import pdb
    #     pdb.set_trace()

        # args = args or []
        # recs = self.browse()
        # if not recs:
        #     recs = self.search([('patient_id', operator, name)] + args, limit=limit)
        # return 1

    def _testname(self,cr,uid,ids,field_name, arg, context=None):
        result={}
        tes_id =[]
        abc=[]
        patient_id=self.browse(cr,uid,ids,context=None)
        for items in patient_id:
            abc.append(items.id)



        bill_id=self.pool.get('bill.register').search(cr,uid,[('patient_name', '=', abc)],context=None)
        test_history = self.pool.get('bill.register').browse(cr, uid, bill_id, context=None)
        xyz=[]
        for testname in test_history:
            for datas in testname.bill_register_line_id.name:
                xyz.append(datas)
        abcd = []
        for item in xyz:
            for items in self.browse(cr,uid,ids,context=None):
            # import pdb
            # pdb.set_trace()
                abcd.append(item.name)
                result[items.id]=abcd

        return result

    @api.multi
    @api.constrains('mobile')
    def _check_mobile(self):

        for rec in self:

            if rec.mobile and len(rec.mobile) != 11:

                raise ValidationError(_("Mobile Number Should be 11 digit"))

        return True

    # def _compute_age(self, cr, uid, ids, field_name, arg, context=None):
    #     res = {}
    #     today = date.today()

    #     for rec in self.browse(cr, uid, ids, context=context):
    #         age = 0

    #         if rec.date_of_birth:
    #             try:
    #                 dob = datetime.strptime(rec.date_of_birth, "%Y-%m-%d").date()
    #                 age = today.year - dob.year - (
    #                     (today.month, today.day) < (dob.month, dob.day)
    #                 )
    #             except:
    #                 age = 0

    #         res[rec.id] = str(age)

    #     return res



    

    _columns = {

        'mobile': fields.char("Mobile No"),
        'patient_id': fields.char("Patient Id", readonly=True),
        'name':fields.char("Name"),
        # 'date_of_birth': fields.date("Date of Birth"),
        # 'birth_year': fields.char("Birth Year"),
        # 'manual_age': fields.integer("Manual Age"),

        # # Auto calculated age
        'age':fields.char('Age'),
        # 'age': fields.function(_compute_age,string="Age",type='char',store=False),
        'address':fields.char('Address'),
        'sex': fields.selection([('male', 'Male'), ('female', 'Female'),('others','Others')], string='Sex', default='male'),
        'bills':fields.one2many('bill.register','patient_name','Bill History',required=False),
        'testname':fields.function(_testname,string="Test Name",type='char'),
        'state': fields.selection(
            [('created', 'Created'), ('notcreated', 'Notcreated')],
            'Status', default='notcreated', readonly=True),
        # 'is_patient':fields.function(_ispatient,string="Is Patient",type='boolean')
    }
    _sql_constraints = [
        ('code_mobile_uniq', 'Check(1=1)', 'The mobile number already exist !')
    ]

    def create(self, cr, uid, vals, context=None):
 
        stored_id=super(patient_info, self).create(cr, uid, vals, context=context)
        if stored_id is not None:
            name_text = 'P-0' + str(stored_id)
            cr.execute('update patient_info set patient_id=%s where id=%s', (name_text, stored_id))
            cr.execute('update patient_info set state=%s where id=%s', ('created', stored_id))
            # cr.commit()

        return stored_id


    

    def write(self, cr, uid, ids, vals, context=None):
        change_patient= self.browse(cr, uid, ids, context)
        if "age" in vals:
            newage=vals['age']
        # query="select name from opd_ticket where patient_id=%"
        # cr.execute(query, (ids))
        # import pdb
        # pdb.set_trace()

        return super(patient_info, self).write(cr, uid, ids, vals, context=context)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        # test_val=self.search([])

        if name:
            recs = self.search([('patient_id', '=', name)] + args, limit=limit)

        # import pdb
        # pdb.set_trace()
        if not recs:
            recs = self.search([('patient_id', operator, name)] + args, limit=limit)
        if not recs:
            recs = self.search([('name', operator, name)] + args, limit=limit)
        if not recs:
            recs = self.search([('mobile', operator,name)] + args, limit=limit)

        return recs.name_get()
