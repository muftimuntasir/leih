from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class patient_info(osv.osv):
    _name = "patient.info"

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





        # for item in test_history:
        #     abcd.append(item.name)

        # bill_obj=self.pool.get('bill.register').browse(self,uid,ids,context)
        # for item in bill_obj:
        #     if item.testid:
        #         tes_id.append(item.testid)
        # tes_obj=self.pool.get('abc.model').browse(self,uid,tes_id,context)
        # biil_history={}
        # for record in bill_obj.bill_register_line_id:
        #     price=record.price
        #     biil_history[record.id]=price
        # return biil_history













    _columns = {

        'mobile': fields.char("Mobile No",required=True),
        'name': fields.char("Patient Name"),
        'age':fields.char('Age'),
        'address':fields.char('Address'),
        'sex': fields.selection([('male', 'Male'), ('female', 'Female'),('others','Others')], string='Sex', default='male'),
        'bills':fields.one2many('bill.register','patient_name','Bill History',required=False),
        'testname':fields.function(_testname,string="Test Name",type='char')
    }
    _sql_constraints = [
        ('code_mobile_uniq', 'unique (mobile)', 'The mobile number already exist !')
    ]

    def create(self, cr, uid, vals, context=None):
        mobile_number = None
        mobile_number = vals.get('mobile')
        if len(mobile_number) <11:
            raise osv.except_osv(_('Error!'), _('Mobile number should minimum 11 digit'))
        if len(mobile_number)>11:
            x=mobile_number.split()
            number=x[0]
            back=len(number)-11
            listnumber=[]
            for item in range(len(number)-1,back-1,-1):
                singlenumber=number[item]
                listnumber.append(singlenumber)
            reverse_number=''.join(listnumber)
            final_number=reverse_number[::-1]
            # import pdb
            # pdb.set_trace()


            vals['mobile'] = final_number

        return super(patient_info, self).create(cr, uid, vals, context=context)