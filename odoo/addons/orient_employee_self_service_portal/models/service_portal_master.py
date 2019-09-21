# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo import SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta


class ServicePortalMaster(models.Model):
    _name = "service.portal.master"
    _description = "Self service portal master form"
    _rec_name = 'full_name'


    # @api.depends('dob')
    # def _get_age(self):
    #     if not self.dob:
    #         return 0
    #     else:
    #         age = 0.0
    #         today = datetime.today()
    #         dob = datetime.strptime(self.dob, '%Y-%m-%d')
    #         difference  = today - dob
    #         difference_in_years = (difference.days + difference.seconds/86400)/365.2425
    #         age = int(round(difference_in_years))
    #         return age

    # @api.model
    # def default_get(self, default_fields):
    #     rec = super(ServicePortalMaster, self).default_get(default_fields)
    #     rec.update({'form_name': 'Candidate Profilee'})
    #     return rec

    # @api.one
    # @api.depends('percent_father', 'percent_mother', 'percent_spouse', 'percent_child1', 'percent_child2')
    # def __calculate_percent_total(self):
    #     print(self)
    #     self.percent_total = self.percent_father + self.percent_mother + self.percent_spouse + self.percent_child1 +  self.percent_child2

    title = fields.Selection([('mr', 'Mr'),('ms', 'Ms'),('mrs', 'Mrs')],string="Title")
    full_name = fields.Char(string='Full Name', translate=True)
    first_name = fields.Char(string='First Name', required=True, translate=True)
    middle_name = fields.Char(string='Middle Name', required=True, translate=True)
    last_name = fields.Char(string='Last Name', required=True, translate=True)
    mother_name = fields.Char(string='Mother Name', required=True, translate=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], required=True)
    dob = fields.Date(string='Date of birth', required=True, index=True, copy=False)
    age = fields.Integer(string='Age',default=0)
    phone_number = fields.Char(string='Phone Number', copy=False)
    emergency_contact_number = fields.Char(string='Emergency Contact Number', copy=False)
    marital_status = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced')
    ], required=True)
    blood_group = fields.Selection([
        ('a_positive', 'A+ve'),
        ('a_negative', 'A-ve'),
        ('b_positive', 'B+ve'),
        ('b_negative', 'B-ve'),
        ('ab_positive', 'AB+ve'),
        ('ab_negative', 'AB-ve'),
        ('o_positive', 'O+ve'),
        ('o_negative', 'O-ve'),
    ], required=True)

    reference_name = fields.Char(string="Reference Name")
    reference_contact_number = fields.Char(string='Contact Number')
    reference_email_id = fields.Char(string='Email ID')
    reference_designation = fields.Char(string='Designation')
    father_name = fields.Char(string="Father's Name")
    passport_number = fields.Char(string='Passport Number')

    candidate_type = fields.Selection([('fresher', 'Fresher'),('experianced', 'Experienced')],required=True,default='fresher')
    pan = fields.Char(string='PAN', required=True, translate=True, size=10)
    aadhar = fields.Char(string='Aadhar', required=True, translate=True,size=12)
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict')
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    previous_company = fields.Char(string='Previous Company', required=True, translate=True)
    designation = fields.Char(string='Designation', required=True, translate=True)
    cv = fields.Binary(string='CV', attachment=True)
    highest_qualification = fields.Char(string='Highest Qualification', required=True, translate=True)
    experiance_id = fields.Many2one('service.experiance', string='Years of Experience', ondelete='restrict')
    domain_id = fields.Many2one('service.domain', string='Domain', ondelete='restrict')
    previous_company = fields.Char(string='Previous Company',translate=True)
    designation = fields.Char(string='Designation', translate=True)
    # c_ctc_id = fields.Many2one('service.ctc', string='Current CTC', ondelete='restrict')
    # e_ctc_id = fields.Many2one('service.ctc', string='Expected CTC', ondelete='restrict')
    # c_ctc = fields.Char(string='Current CTC', translate=True)
    # e_ctc = fields.Char(string='Expected CTC', required=True, translate=True)
    # skills = fields.Text('Skills',required=True)
    # current_ctc = fields.Integer('Current CTC', translate=True)
    # expected_ctc = fields.Integer('Expected CTC', required=True, translate=True)
    # service_doc_ids = fields.One2many('service.documents', 'portal_master_id', 'Attach Documents', copy=False)
    notes = fields.Text('Notes')
    submitted = fields.Boolean(default=False,string='Submitted')
    skill1 = fields.Char()
    skill2 = fields.Char()
    skill3 = fields.Char()
    skill4 = fields.Char()
    skill5 = fields.Char()
    skill6 = fields.Char()
    skill7 = fields.Char()
    skill8 = fields.Char()
    primary_country_code = fields.Char(translate=True)
    secondary_country_code = fields.Char(translate=True)
    pf_esic_holder = fields.Boolean(default=False,string='PF and ESIC account holder')

    pf_uan_no = fields.Char(string='PF UAN Number',size=12)

    # nominee_ids = fields.Many2many('service.pf.esic.nominee',string='Nominees')
    pf_nominee_father = fields.Boolean(default=False,string='PF Nominee Father')
    pf_nominee_mother = fields.Boolean(default=False,string='PF Nominee Mother')
    pf_nominee_spouse = fields.Boolean(default=False,string='PF Nominee Spouse')
    pf_nominee_child1 = fields.Boolean(default=False,string='PF Nominee Child1')
    pf_nominee_child2 = fields.Boolean(default=False,string='PF Nominee Child2')

    pf_father_name = fields.Char(string='PF Nominee Father Name')
    pf_mother_name = fields.Char(string='PF Nominee Mother Name')
    pf_spouse_name = fields.Char(string='PF Nominee Spouse Name')
    pf_first_child = fields.Char(string='PF Nominee Child1 Name')
    pf_second_child = fields.Char(string='PF Nominee Child2 Name')

    pf_dob_father = fields.Date(string="PF DOB Father",index=True, copy=False)
    pf_dob_mother = fields.Date(string="PF DOB Mother",index=True, copy=False)
    pf_dob_spouse = fields.Date(string="PF DOB Spouse",index=True, copy=False)
    pf_dob_child1 = fields.Date(string="PF DOB Child1",index=True, copy=False)
    pf_dob_child2 = fields.Date(string="PF DOB Child2",index=True, copy=False)

    pf_percent_father = fields.Integer(string='PF Percent Father',default=0)
    pf_percent_mother = fields.Integer(string='PF Percent Mother',default=0)
    pf_percent_spouse = fields.Integer(string='PF Percent Spouse',default=0)
    pf_percent_child1 = fields.Integer(string='PF Percent Child1',default=0)
    pf_percent_child2 = fields.Integer(string='PF Percent Child2',default=0)

    pf_gender_spouse = fields.Selection([('male', 'Male'),('female', 'Female'),('other', 'Other')],string="PF Gender Spouse")
    pf_gender_child1 = fields.Selection([('male', 'Male'),('female', 'Female'),('other', 'Other')],string="PF Gender Child1")
    pf_gender_child2 = fields.Selection([('male', 'Male'),('female', 'Female'),('other', 'Other')],string="PF Gender Child2")

    esic_uan_no = fields.Char(string='ESIC UAN Number',size=17)

    same_as_pf = fields.Boolean(default=False,string='Same as PF')

    esic_nominee_father = fields.Boolean(default=False,string='ESIC Nominee Father')
    esic_nominee_mother = fields.Boolean(default=False,string='ESIC Nominee Mother')
    esic_nominee_spouse = fields.Boolean(default=False,string='ESIC Nominee Spouse')
    esic_nominee_child1 = fields.Boolean(default=False,string='ESIC Nominee Child1')
    esic_nominee_child2 = fields.Boolean(default=False,string='ESIC Nominee Child2')

    esic_father_name = fields.Char(string='ESIC Nominee Father Name')
    esic_mother_name = fields.Char(string='ESIC Nominee Mother Name')
    esic_spouse_name = fields.Char(string='ESIC Nominee Spouse Name')
    esic_first_child = fields.Char(string='ESIC Nominee Child1 Name')
    esic_second_child = fields.Char(string='ESIC Nominee Child2 Name')

    esic_dob_father = fields.Date(string="ESIC DOB Father",index=True, copy=False)
    esic_dob_mother = fields.Date(string="ESIC DOB Mother",index=True, copy=False)
    esic_dob_spouse = fields.Date(string="ESIC DOB Spouse",index=True, copy=False)
    esic_dob_child1 = fields.Date(string="ESIC DOB Child1",index=True, copy=False)
    esic_dob_child2 = fields.Date(string="ESIC DOB Child2",index=True, copy=False)

    esic_percent_father = fields.Integer(string='ESIC Percent Father',default=0)
    esic_percent_mother = fields.Integer(string='ESIC Percent Mother',default=0)
    esic_percent_spouse = fields.Integer(string='ESIC Percent Spouse',default=0)
    esic_percent_child1 = fields.Integer(string='ESIC Percent Child1',default=0)
    esic_percent_child2 = fields.Integer(string='ESIC Percent Child2',default=0)

    esic_gender_spouse = fields.Selection([('male', 'Male'),('female', 'Female'),('other', 'Other')],string="ESIC Gender Spouse")
    esic_gender_child1 = fields.Selection([('male', 'Male'),('female', 'Female'),('other', 'Other')],string="ESIC Gender Child1")
    esic_gender_child2 = fields.Selection([('male', 'Male'),('female', 'Female'),('other', 'Other')],string="ESIC Gender Child2")

    cv_file = fields.Binary('CV file',attachment=True)
    residence_proof = fields.Binary('Residence proof file',attachment=True)
    pan_doc = fields.Binary('PAN proof file',attachment=True)
    aadhar_doc = fields.Binary('Aadhar proof file',attachment=True)
    passport_photo = fields.Binary('Passportsize photo file',attachment=True)
    birth_cert = fields.Binary('Birth certificate file',attachment=True)
    relieving_doc = fields.Binary('Relieving Letter file',attachment=True)
    appraisal_doc = fields.Binary('Appraisal letter file',attachment=True)
    appointment_doc = fields.Binary('Appointment letter file',attachment=True)
    payslip = fields.Binary('Payslip file',attachment=True)
    qualification_cert = fields.Binary('Qualification certificate file',attachment=True)
    leaving_cert = fields.Binary('Leaving certificate file',attachment=True)
    skill_cert = fields.Binary('Skill certificate file',attachment=True)

    cv_flag = fields.Boolean(default=False,string='CV')
    residence_flag = fields.Boolean(default=False,string='Residence Proof')
    pan_flag = fields.Boolean(default=False,string='PAN proof')
    aadhar_flag = fields.Boolean(default=False,string='Aadhar Proof')
    passport_flag = fields.Boolean(default=False,string='Passportsize Photo')
    birth_flag = fields.Boolean(default=False,string='Birth Certificate')
    relieving_flag = fields.Boolean(default=False,string='Relieving Letter')
    appraisal_flag = fields.Boolean(default=False,string='Appraisal Letter')
    appointment_flag = fields.Boolean(default=False,string='Appointment Letter')
    payslip_flag = fields.Boolean(default=False,string='Payslip')
    qualification_flag = fields.Boolean(default=False,string='Qualification Certificate')
    lc_flag = fields.Boolean(default=False,string='Leaving Certificate')
    skill_flag = fields.Boolean(default=False,string='Skill Certificate')

    pf_percent_total = fields.Integer(string='PF Percent Total%')
    esic_percent_total = fields.Integer(string='ESIC Percent Total%')

    skill_ids = fields.Many2many('skillset','portal_skillset_rel', 'portal_skill_id', 'skill_portal_id',copy=False, string='Skillset')


    # _sql_constraints = [
    #     ('aadhar_uniq', 'unique (aadhar)', 'A profile with this aadhar number already exists!'),
    # ]

    @api.onchange('country_id')
    def onchange_country_id(self):
        data = {}
        domain = {}
        if self.country_id:
            domain['state_id'] = [('country_id', '=', self.country_id.id)]
            if self.country_id.phone_code:
                data['primary_country_code'] = self.country_id.phone_code
                data['secondary_country_code'] = self.country_id.phone_code
            else:
                data['primary_country_code'] = False
                data['secondary_country_code'] = False
        else:
            domain['state_id'] = []
            data['primary_country_code'] = False
            data['secondary_country_code'] = False
        return {'value':data,'domain': domain}   


    @api.onchange('dob')
    def onchange_dob(self):
        data = {}
        age = 0
        if self.dob:
            today = datetime.today()
            dob = datetime.strptime(self.dob, '%Y-%m-%d')
            difference  = today - dob
            difference_in_years = (difference.days + difference.seconds/86400)/365.2425
            age = int(round(difference_in_years))
            data['age'] = age
        else:
            data['age'] = age
        return {'value':data}


    @api.onchange('pf_percent_father')
    def onchange_pf_percent_father(self):
        data = {}
        if self.pf_percent_father:
            pf_percent_total = self.pf_percent_father + self.pf_percent_mother + self.pf_percent_spouse + self.pf_percent_child1 + self.pf_percent_child2
            data['pf_percent_total'] = pf_percent_total
        else:
            pf_percent_total = self.pf_percent_mother + self.pf_percent_spouse + self.pf_percent_child1 + self.pf_percent_child2
            data['pf_percent_total'] = pf_percent_total
        return {'value':data}   

    @api.onchange('pf_percent_mother')
    def onchange_pf_percent_mother(self):
        data = {}
        if self.pf_percent_mother:
            pf_percent_total = self.pf_percent_father + self.pf_percent_mother + self.pf_percent_spouse + self.pf_percent_child1 + self.pf_percent_child2
            data['pf_percent_total'] = pf_percent_total
        else:
            pf_percent_total = self.pf_percent_father + self.pf_percent_spouse + self.pf_percent_child1 + self.pf_percent_child2
            data['pf_percent_total'] = pf_percent_total
        return {'value':data}     

    @api.onchange('pf_percent_spouse')
    def onchange_pf_percent_spouse(self):
        data = {}
        if self.pf_percent_spouse:
            pf_percent_total = self.pf_percent_father + self.pf_percent_mother + self.pf_percent_spouse + self.pf_percent_child1 + self.pf_percent_child2
            data['pf_percent_total'] = pf_percent_total
        else:
            pf_percent_total = self.pf_percent_father + self.pf_percent_mother + self.pf_percent_child1 + self.pf_percent_child2
            data['pf_percent_total'] = pf_percent_total
        return {'value':data}   

    @api.onchange('pf_percent_child1')
    def onchange_pf_percent_child1(self):
        data = {}
        if self.pf_percent_child1:
            pf_percent_total = self.pf_percent_father + self.pf_percent_mother + self.pf_percent_spouse + self.pf_percent_child1 + self.pf_percent_child2
            data['pf_percent_total'] = pf_percent_total
        else:
            pf_percent_total = self.pf_percent_father + self.pf_percent_mother + self.pf_percent_spouse + self.pf_percent_child2
            data['pf_percent_total'] = pf_percent_total
        return {'value':data}   

    @api.onchange('pf_percent_child2')
    def onchange_pf_percent_child2(self):
        data = {}
        if self.pf_percent_child2:
            pf_percent_total = self.pf_percent_father + self.pf_percent_mother + self.pf_percent_spouse + self.pf_percent_child1 + self.pf_percent_child2
            data['pf_percent_total'] = pf_percent_total
        else:
            pf_percent_total = self.pf_percent_father + self.pf_percent_mother + self.pf_percent_spouse + self.pf_percent_child1
            data['pf_percent_total'] = pf_percent_total
        return {'value':data}   

    @api.onchange('pf_nominee_father')
    def onchange_pf_nominee_father(self):
        data = {}
        if self.pf_nominee_father:
            if self.pf_nominee_mother and self.pf_nominee_spouse and self.pf_nominee_child1 and self.pf_nominee_child2:
                data['pf_nominee_father'] = False
                raise UserError(_('Maximum 4 nominees allowed!'))
        else:
            data['pf_father_name'] = False
            data['pf_dob_father'] = False
            data['pf_percent_father'] = 0
        return {'value':data}

    @api.onchange('pf_nominee_mother')
    def onchange_pf_nominee_mother(self):
        data = {}
        if self.pf_nominee_mother:
            if self.pf_nominee_father and self.pf_nominee_spouse and self.pf_nominee_child1 and self.pf_nominee_child2:
                data['nominee_mother'] = False
                raise UserError(_('Maximum 4 nominees allowed!'))
        else:
            data['mother_name'] = False
            data['dob_mother'] = False
            data['percent_mother'] = 0
        return {'value':data}

    @api.onchange('pf_nominee_spouse')
    def onchange_pf_nominee_spouse(self):
        data = {}
        if self.pf_nominee_spouse:
            if self.pf_nominee_mother and self.pf_nominee_father and self.pf_nominee_child1 and self.pf_nominee_child2:
                data['pf_nominee_spouse'] = False
                raise UserError(_('Maximum 4 nominees allowed!'))
        else:
            data['pf_spouse_name'] = False
            data['pf_dob_spouse'] = False
            data['pf_percent_spouse'] = 0
            data['pf_gender_spouse'] = False
        return {'value':data}

    @api.onchange('pf_nominee_child1')
    def onchange_pf_nominee_child1(self):
        data = {}
        if self.pf_nominee_child1:
            if self.pf_nominee_mother and self.pf_nominee_spouse and self.pf_nominee_father and self.pf_nominee_child2:
                data['pf_nominee_child1'] = False
                raise UserError(_('Maximum 4 nominees allowed!'))
        else:
            data['pf_first_child'] = False
            data['pf_dob_child1'] = False
            data['pf_percent_child1'] = 0
            data['pf_gender_child1'] = False
        return {'value':data}

    @api.onchange('pf_nominee_child2')
    def onchange_pf_nominee_child2(self):
        data = {}
        if self.pf_nominee_child2:
            if self.pf_nominee_mother and self.pf_nominee_spouse and self.pf_nominee_child1 and self.pf_nominee_father:
                data['pf_nominee_child2'] = False
                raise UserError(_('Maximum 4 nominees allowed!'))
        else:
            data['pf_second_child'] = False
            data['pf_dob_child2'] = False
            data['pf_percent_child2'] = 0
            data['pf_gender_child2'] = False
        return {'value':data}

    @api.onchange('same_as_pf')
    def onchange_same_as_pf(self):
        data = {}
        if self.same_as_pf:
            if self.pf_nominee_father:
                data['esic_nominee_father'] = True
                data['esic_father_name'] = self.pf_father_name
                data['esic_dob_father'] = self.pf_dob_father
                data['esic_percent_father'] = self.pf_percent_father
            if self.pf_nominee_mother:
                data['esic_nominee_mother'] = True
                data['esic_mother_name'] = self.pf_mother_name
                data['esic_dob_mother'] = self.pf_dob_mother
                data['esic_percent_mother'] = self.pf_percent_mother              
            if self.pf_nominee_spouse:
                data['esic_nominee_spouse'] = True
                data['esic_spouse_name'] = self.pf_spouse_name
                data['esic_dob_spouse'] = self.pf_dob_spouse
                data['esic_percent_spouse'] = self.pf_percent_spouse  
                data['esic_gender_spouse'] = self.pf_gender_spouse  
            if self.pf_nominee_child1:
                data['esic_nominee_child1'] = True
                data['esic_first_child'] = self.pf_first_child
                data['esic_dob_child1'] = self.pf_dob_child1
                data['esic_percent_child1'] = self.pf_percent_child1  
                data['esic_gender_child1'] = self.pf_gender_child1              
            if self.pf_nominee_child2:
                data['esic_nominee_child2'] = True
                data['esic_first_child2'] = self.pf_second_child
                data['esic_dob_child2'] = self.pf_dob_child2
                data['esic_percent_child2'] = self.pf_percent_child2  
                data['esic_gender_child2'] = self.pf_gender_child2    
        else:
                data['esic_nominee_father'] = False
                data['esic_father_name'] = False
                data['esic_dob_father'] = False
                data['esic_percent_father'] = False
                data['esic_nominee_mother'] = False
                data['esic_mother_name'] = False
                data['esic_dob_mother'] = False
                data['esic_percent_mother'] = False
                data['esic_nominee_spouse'] = False
                data['esic_spouse_name'] = False
                data['esic_dob_spouse'] = False
                data['esic_percent_spouse'] = False
                data['esic_gender_spouse'] = False
                data['esic_nominee_child1'] = False
                data['esic_first_child'] = False
                data['esic_dob_child1'] = False
                data['esic_percent_child1'] = False
                data['esic_gender_child1'] = False
                data['esic_nominee_child2'] = False
                data['esic_first_child2'] = False
                data['esic_dob_child2'] = False
                data['esic_percent_child2'] = False
                data['esic_gender_child2'] = False                
        return {'value':data}

    @api.onchange('esic_percent_father')
    def onchange_esic_percent_father(self):
        data = {}
        if self.esic_percent_father:
            esic_percent_total = self.esic_percent_father + self.esic_percent_mother + self.esic_percent_spouse + self.esic_percent_child1 + self.esic_percent_child2
            data['esic_percent_total'] = esic_percent_total
        else:
            esic_percent_total = self.pf_percent_mother + self.pf_percent_spouse + self.pf_percent_child1 + self.pf_percent_child2
            data['esic_percent_total'] = esic_percent_total
        return {'value':data}   

    @api.onchange('esic_percent_mother')
    def onchange_esic_percent_mother(self):
        data = {}
        if self.esic_percent_mother:
            esic_percent_total = self.esic_percent_father + self.esic_percent_mother + self.esic_percent_spouse + self.esic_percent_child1 + self.esic_percent_child2
            data['esic_percent_total'] = esic_percent_total
        else:
            esic_percent_total = self.esic_percent_father + self.esic_percent_spouse + self.esic_percent_child1 + self.esic_percent_child2
            data['esic_percent_total'] = esic_percent_total
        return {'value':data}     

    @api.onchange('esic_percent_spouse')
    def onchange_esic_percent_spouse(self):
        data = {}
        if self.esic_percent_spouse:
            esic_percent_total = self.esic_percent_father + self.esic_percent_mother + self.esic_percent_spouse + self.esic_percent_child1 + self.esic_percent_child2
            data['esic_percent_total'] = esic_percent_total
        else:
            esic_percent_total = self.esic_percent_father + self.esic_percent_mother + self.esic_percent_child1 + self.esic_percent_child2
            data['esic_percent_total'] = esic_percent_total
        return {'value':data}   

    @api.onchange('esic_percent_child1')
    def onchange_esic_percent_child1(self):
        data = {}
        if self.esic_percent_child1:
            esic_percent_total = self.esic_percent_father + self.esic_percent_mother + self.esic_percent_spouse + self.esic_percent_child1 + self.esic_percent_child2
            data['esic_percent_total'] = esic_percent_total
        else:
            esic_percent_total = self.esic_percent_father + self.esic_percent_mother + self.esic_percent_spouse + self.esic_percent_child2
            data['esic_percent_total'] = esic_percent_total
        return {'value':data}   

    @api.onchange('esic_percent_child2')
    def onchange_esic_percent_child2(self):
        data = {}
        if self.esic_percent_child2:
            esic_percent_total = self.esic_percent_father + self.esic_percent_mother + self.esic_percent_spouse + self.esic_percent_child1 + self.esic_percent_child2
            data['esic_percent_total'] = esic_percent_total
        else:
            esic_percent_total = self.esic_percent_father + self.esic_percent_mother + self.esic_percent_spouse + self.esic_percent_child1
            data['esic_percent_total'] = esic_percent_total
        return {'value':data}   

    @api.onchange('esic_nominee_father')
    def onchange_esic_nominee_father(self):
        data = {}
        if self.esic_nominee_father:
            if self.esic_nominee_mother and self.esic_nominee_spouse and self.esic_nominee_child1 and self.esic_nominee_child2:
                data['esic_nominee_father'] = False
                raise UserError(_('Maximum 4 nominees allowed!'))
        else:
            data['esic_father_name'] = False
            data['esic_dob_father'] = False
            data['esic_percent_father'] = 0
        return {'value':data}

    @api.onchange('esic_nominee_mother')
    def onchange_esic_nominee_mother(self):
        data = {}
        if self.esic_nominee_mother:
            if self.esic_nominee_father and self.esic_nominee_spouse and self.esic_nominee_child1 and self.esic_nominee_child2:
                data['esic_nominee_mother'] = False
                raise UserError(_('Maximum 4 nominees allowed!'))
        else:
            data['esic_mother_name'] = False
            data['esic_dob_mother'] = False
            data['esic_percent_mother'] = 0
        return {'value':data}

    @api.onchange('esic_nominee_spouse')
    def onchange_esic_nominee_spouse(self):
        data = {}
        if self.esic_nominee_spouse:
            if self.esic_nominee_mother and self.esic_nominee_father and self.esic_nominee_child1 and self.esic_nominee_child2:
                data['esic_nominee_spouse'] = False
                raise UserError(_('Maximum 4 nominees allowed!'))
        else:
            data['esic_spouse_name'] = False
            data['esic_dob_spouse'] = False
            data['esic_percent_spouse'] = 0
            data['esic_gender_spouse'] = False
        return {'value':data}

    @api.onchange('esic_nominee_child1')
    def onchange_esic_nominee_child1(self):
        data = {}
        if self.esic_nominee_child1:
            if self.esic_nominee_mother and self.esic_nominee_spouse and self.esic_nominee_father and self.esic_nominee_child2:
                data['esic_nominee_child1'] = False
                raise UserError(_('Maximum 4 nominees allowed!'))
        else:
            data['esic_first_child'] = False
            data['esic_dob_child1'] = False
            data['esic_percent_child1'] = 0
            data['esic_gender_child1'] = False
        return {'value':data}

    @api.onchange('esic_nominee_child2')
    def onchange_esic_nominee_child2(self):
        data = {}
        if self.esic_nominee_child2:
            if self.esic_nominee_mother and self.esic_nominee_spouse and self.esic_nominee_child1 and self.esic_nominee_father:
                data['esic_nominee_child2'] = False
                raise UserError(_('Maximum 4 nominees allowed!'))
        else:
            data['esic_second_child'] = False
            data['esic_dob_child2'] = False
            data['esic_percent_child2'] = 0
            data['esic_gender_child2'] = False
        return {'value':data}



    def submit_portal_form(self):
        existing_aadhar_ids = self.search([('aadhar', '=', self.aadhar),('id', '!=', self.id)])
        for each_existing_id in existing_aadhar_ids:
            self.env.cr.execute("delete from service_portal_master where id=%s" %(str(each_existing_id.id)))
        if self.age < 18:
            raise UserError(_("Sorry. You cannot submit your profile as you are minor. Candidates only above 18 can apply!"))
        try:
            int(self.phone_number)
        except:
            raise UserError(_("Mobile number cannot contain special characters!"))
        try:
            int(self.emergency_contact_number)
        except:
            raise UserError(_("Emergency contact number cannot contain special characters!")) 
        if self.phone_number.strip() == self.emergency_contact_number.strip():
            raise UserError(_("Mobile and Emergency contact number cannot be same!")) 
        try:
            int(self.aadhar)
        except:
            raise UserError(_("Aadhar number cannot contain special characters!"))
        try:
            int(self.zip)
        except:
            raise UserError(_("Zip cannot contain special characters!"))  
        if len(self.pan) < 10:
            raise UserError(_("PAN number cannot be less than 10 characters!"))
        if len(str(self.aadhar)) < 12:
            raise UserError(_("Aadhar number cannot be less than 12 digits!")) 
        if len(self.skill_ids) < 3:
            raise UserError(_("Please enter atleast 3 skills!"))
        if self.pf_esic_holder:
            if self.pf_uan_no and not self.pf_nominee_father and not self.pf_nominee_mother and not self.pf_nominee_spouse and not self.pf_nominee_child1 and not self.pf_nominee_child2:
                raise UserError(_("Select PF nominees(atleast one)!"))
            if self.pf_uan_no and self.pf_percent_total > 100:
                raise UserError(_("PF nominees percentage cannot exceed 100!"))
            if self.pf_uan_no and self.pf_percent_total < 100:
                raise UserError(_("Total percent distributed in the nominees should sum up to 100!"))
            if self.esic_uan_no and not self.esic_nominee_father and not self.esic_nominee_mother and not self.esic_nominee_spouse and not self.esic_nominee_child1 and not self.esic_nominee_child2:
                raise UserError(_("Select ESIC nominees(atleast one)!"))
            if self.esic_uan_no and self.esic_percent_total > 100:
                raise UserError(_("ESIC nominees percentage cannot exceed 100!"))
            if self.esic_uan_no and self.esic_percent_total < 100:
                raise UserError(_("Total percent distributed in the nominees should sum up to 100!"))
        first_name = self.first_name.capitalize()
        middle_name = self.middle_name.capitalize()
        last_name = self.last_name.capitalize()
        full_name = first_name+' '+middle_name+' '+last_name
        city = self.city.capitalize()
        cv_flag = False
        residence_flag = False
        pan_flag = False
        aadhar_flag = False
        passport_flag = False
        birth_flag = False
        appraisal_flag = False
        appointment_flag = False
        payslip_flag = False
        qualification_flag = False
        lc_flag = False
        skill_flag = False
        if self.cv_file:
            cv_flag = True
        if self.residence_proof:
            residence_flag = True
        if self.pan_doc:
            pan_flag = True
        if self.aadhar_doc:
            aadhar_flag = True
        if self.passport_photo:
            passport_flag = True
        if self.birth_cert:
            birth_flag = True
        if self.appraisal_doc:
            appraisal_flag = True
        if self.appointment_doc:
            appointment_flag = True
        if self.payslip:
            payslip_flag = True
        if self.qualification_cert:
            qualification_flag = True
        if self.leaving_cert:
            lc_flag = True
        if self.skill_cert:
            skill_flag = True
        res = self.write(
            {
                'submitted':True,
                'first_name':first_name,
                'middle_name':middle_name,
                'last_name':last_name,
                'full_name':full_name,
                'city':city,
                'pan':self.pan.upper(),
                'pf_uan_no':self.pf_uan_no.upper() if self.pf_uan_no else False,
                'esic_uan_no':self.esic_uan_no.upper() if self.esic_uan_no else False,
                'cv_flag': cv_flag,
                'residence_flag': residence_flag,
                'pan_flag': pan_flag,
                'aadhar_flag': aadhar_flag,
                'passport_flag': passport_flag,
                'birth_flag': birth_flag,
                'appraisal_flag': appraisal_flag,
                'appointment_flag': appointment_flag,
                'payslip_flag': payslip_flag,
                'qualification_flag': qualification_flag,
                'lc_flag': lc_flag,
                'skill_flag': skill_flag,
            })
        applicant_id = self.env['hr.applicant'].search([('email_from','=',self.env.user.login)],limit=1)
        self.env.cr.execute("update hr_applicant set portal_id=%s where id=%s" %(str(self.id),str(applicant_id.id)))
        return res