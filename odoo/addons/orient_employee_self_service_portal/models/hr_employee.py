# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from odoo import SUPERUSER_ID
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
import uuid
import xlsxwriter as xls

class Employee(models.Model):
    _inherit = ['hr.employee']
    

    age = fields.Integer(string='Age',default=0)
    pan = fields.Char(string='PAN', translate=True, size=10)
    aadhar = fields.Char(string='Aadhar',translate=True,size=12)
    blood_group = fields.Selection([
        ('a_positive', 'A+ve'),
        ('a_negative', 'A-ve'),
        ('b_positive', 'B+ve'),
        ('b_negative', 'B-ve'),
        ('ab_positive', 'AB+ve'),
        ('ab_negative', 'AB-ve'),
        ('o_positive', 'O+ve'),
        ('o_negative', 'O-ve'),
        ('na', 'NA'),
    ])
    candidate_type1 = fields.Selection([('fresher', 'Fresher'),('experianced', 'Experianced')],default=False,string="Candidate Type")
    previous_company = fields.Char(string='Previous Company', translate=True)
    previous_designation = fields.Char(string='Previous Company Designation', translate=True)
    gross_salary = fields.Float("Gross Salary")
    current_ctc = fields.Float("Current CTC")
    experiance_id = fields.Many2one('service.experiance', string='Years of Experience', ondelete='restrict')
    highest_qualification = fields.Char(string='Highest Qualification', translate=True)
    address = fields.Text('Current Address')
    same_as_current = fields.Boolean('Same as current?',default=False)
    per_address = fields.Text('Permanent Address')
    personal_email = fields.Char(string='Email')
    first_name = fields.Char(string='First Name', translate=True)
    middle_name = fields.Char(string='Middle Name', translate=True)
    last_name = fields.Char(string='Last Name', translate=True)
    main_company_id = fields.Many2one('res.company', string='Company Name')
    title = fields.Selection([('mr', 'Mr'),('ms', 'Miss'),('mrs', 'Mrs')],string="Title")
    guardian_title = fields.Selection([('mr', 'Mr')],default='mr',string="Title")
    guardian_first_name = fields.Char(string='First Name')
    guardian_middle_name = fields.Char(string='Middle Name')
    guardian_last_name = fields.Char(string='Last Name')
    group_join_date = fields.Date(string='Group Join Date')
    cost_center_id = fields.Many2one('cost.center', string='Cost Center Name')
    rate_code = fields.Selection([('daily', 'Daily'),('monthly', 'Monthly'),('wages', 'Wages')],string="Rate Code")
    emp_category = fields.Selection([('staff', 'Staff')],string="Category",default="staff")
    bank_id = fields.Many2one('bank.name', string='Bank Name')
    branch_name = fields.Char(string='Branch Name', translate=True)
    gl_code = fields.Char(string='GL Code', translate=True)
    medical_policy_number = fields.Char(string='Medical Policy Number', translate=True)
    union_member = fields.Boolean(default=False,string='Union Member')
    probation_period = fields.Float(digits=0, default=0, string='Probation Period')
    probation_date = fields.Date(string='Probation Date')
    passport_expire_date = fields.Date(string='Passport Expire Date')
    notice_period = fields.Integer('Notice Period', translate=True)
    salary_disbursement_date = fields.Date(string='Salary Disbursement Date')
    confirmation_date = fields.Date(string='Confirmation Date')
    retirement_date = fields.Date(string='Retirement Date')
    weekly_off = fields.Selection([('sunday', 'Sunday'),
                                   ('monday', 'Monday'),
                                   ('tuesday', 'Tuesday'),
                                   ('wednesday', 'Wednesday'),
                                   ('thursday', 'Thursday'),
                                   ('friday', 'Friday'),
                                   ('saturday', 'Saturday')],
                                   string="Weekly Off")
    emergency_contact_name = fields.Char(string='Emergency Contact Person',translate=True)
    emergency_contact_number = fields.Char(string='Emergency Contact Number',translate=True)
    emergency_contact_relation = fields.Char(string='Relation',translate=True)
    applicant_id = fields.Many2one('hr.applicant', string='Application')
    portal_id = fields.Many2one('service.portal.master', string='Portal Form')

    pf_esic_holder = fields.Boolean(default=False,string='PF and ESIC account holder')
    pf_uan_no = fields.Char(string='PF UAN Number',size=12)

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

    pf_percent_total = fields.Integer(string='PF Percent Total%')
    esic_percent_total = fields.Integer(string='ESIC Percent Total%')

    cv_file = fields.Binary('CV',attachment=True)
    residence_proof = fields.Binary('Residence',attachment=True)
    pan_doc = fields.Binary('PAN',attachment=True)
    aadhar_doc = fields.Binary('Aadhar',attachment=True)
    passport_photo = fields.Binary('Photo',attachment=True)
    birth_cert = fields.Binary('Birth Certificate',attachment=True)
    appraisal_doc = fields.Binary('Appraisal Letter',attachment=True)
    appointment_doc = fields.Binary('Appointment Letter',attachment=True)
    payslip = fields.Binary('Payslip',attachment=True)
    qualification_cert = fields.Binary('Qualification Certificate',attachment=True)
    relieving_cert = fields.Binary('Relieving Letter',attachment=True)
    skill_cert = fields.Binary('Skill Certificate',attachment=True)
    year = fields.Many2one('year.master','Year')
    accept = fields.Boolean('I Accept', default=False)
    reject = fields.Boolean('I Reject', default=False)
    reason_for_rejection = fields.Text('Reason')
    freeze_records = fields.Boolean('Freeze records')
    can_edit_name = fields.Boolean(compute='_compute_can_edit_name',default=False)
    position_type = fields.Selection([('probation', 'Probation'),('confirm','Permanent')], string='Employee Status')
    emp_code = fields.Integer('Employee Code')
    father_name = fields.Char(string="Father's Name")
    mother_name = fields.Char(string="Mother's Name")
    spouse_name = fields.Char(string="Spouse Name")
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], groups=None, default="male")
    marital = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('cohabitant', 'Legal Cohabitant'),
        ('widower', 'Widower'),
        ('divorced', 'Divorced')
    ], string='Marital Status', groups=None, default='single')
    birthday = fields.Date('Date of birth', groups=None)
    country_id = fields.Many2one(
        'res.country', 'Nationality (Country)', groups=None)
    bank_account_id = fields.Many2one(
        'res.partner.bank', 'Bank Account Number',
        domain="[('partner_id', '=', address_home_id)]",
        groups=None,
        help='Employee bank salary account')
    visa_no = fields.Char('Visa No', groups=None)
    visa_expire = fields.Date('Visa Expire Date', groups=None)
    passport_id = fields.Char('Passport No', groups=None)
    employee_billing_status = fields.Selection([
        ('billable', 'Billable'),
        ('non_billable', 'Non-Billable')], string='Employee Billing Status')
    po_received = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], string='PO Received',default="no")
    po_number = fields.Char('PO Number')
    po_start_date = fields.Date('PO Start Date')
    po_end_date = fields.Date('PO End Date')
    po_attachement = fields.Binary('PO Document',attachment=True)
    bank_account_number = fields.Char(string='Bank Account Number',size=16)
    last_working_date = fields.Date('Last Working Date')
    user_id = fields.Many2one('res.users', 'User', related='resource_id.user_id',store=True)
    physically_disabled = fields.Selection([('yes','Yes'),('no','No')], default="no" ,string="Physically Disabled")
    esic_location = fields.Many2one('res.city','ESIC Location')
    site_location_id = fields.Many2one('res.city','Site Location')
    confirmation_link = fields.Text('Confirmation Link')
    pms_form_applicable = fields.Many2one('sub.department','PMS Form Applicable')


    @api.model
    def create(self, values):
        if values.get('pan'):
            pan = values.get('pan')
            existing_pan_ids = self.env['hr.employee'].search([('pan', '=', pan)])
            if existing_pan_ids:
                raise UserError(_("Pan %s already exists!") % values.get('pan'))
        if values.get('personal_mobile'):
            personal_mobile = values.get('personal_mobile')
            existing_mobile_ids = self.env['hr.employee'].search(['|',('personal_mobile', '=', personal_mobile),('mobile_phone', '=', personal_mobile)])
            if existing_mobile_ids:
                raise UserError(_("Mobile number %s already exists!") % values.get('personal_mobile'))
        if values.get('work_email'):
            work_email = values.get('work_email')
            existing_work_mail_ids = self.env['hr.employee'].search(['|',('work_email', '=', work_email),('personal_email', '=', work_email)])
            if existing_work_mail_ids:
                raise UserError(_("Email %s already exists!") % values.get('work_email'))
        if values.get('personal_email'):
            personal_email = values.get('personal_email')
            existing_personal_mail_ids = self.env['hr.employee'].search(['|',('work_email', '=', personal_email),('personal_email', '=', personal_email)])
            if existing_personal_mail_ids:
                raise UserError(_("Email %s already exists!") % values.get('personal_email'))
        return super(Employee, self).create(values)

    # @api.constrains('pan','personal_mobile')
    # def _check_existing_employee(self):
    #         print("pan",pan)
    #     # for emp in self:
    #         existing_pan_ids = self.env['hr.employee'].search([('pan', '=', pan)])
    #         existing_mobile_ids = self.env['hr.employee'].search([('personal_mobile', '=', personal_mobile)])
    #         print("existing_pan_ids",existing_pan_ids)
    #         print("existing_mobile_ids",existing_mobile_ids)
    #         asdfas
    #         if emp.pan in 0:
    #             raise UserError(_('Leaves cannot be applied for 0 days!'))


    def _compute_can_edit_name(self):
        for each in self:
            res_user = self.env['res.users'].search([('id', '=', each._uid)])
            if res_user.id!=1:
                if res_user.has_group('base.group_user') and not res_user.has_group('hr.group_hr_user') and not res_user.has_group('hr.group_hr_manager'):
                    each.can_edit_name = True
                else:
                    each.can_edit_name = False


    @api.onchange('first_name','middle_name','last_name')
    def onchange_name(self):
        data = {}
        if self.first_name:
            first_name = self.first_name.capitalize()
        else:
            first_name = ''
        if self.middle_name:
            middle_name = self.middle_name.capitalize()
        else:
            middle_name = ''
        if self.last_name:
            last_name = self.last_name.capitalize()
        else:
            last_name = ''
        data['name'] = first_name+' '+middle_name+' '+last_name
        search_shift = self.env['hr.employee.shift.timing'].search([('name','=','G')],limit=1)
        if search_shift:
            data['shift_id']=search_shift.id
        search_nationality = self.env['res.country'].search([('name','=','India')],limit=1)
        if search_nationality:
            data['country_id']=search_nationality.id
        return {'value':data}


    @api.onchange('same_as_current')
    def onchange_same_as_current(self):
        data = {}
        if self.same_as_current:
            if self.address:
                per_address = self.address
            else:
                per_address = None
        else:
            per_address = None
        data['per_address'] = per_address
        return {'value':data}


    @api.onchange('accept','reject')
    def onchange_accept_reject(self):
        data = {}
        if self.accept:
            data['reject'] = False
        if self.reject:
            data['accept'] = False
        return {'value':data}


    @api.onchange('year','freeze_records')
    def onchange_year(self):
        data = {}
        if self.year.id!=False:
            data['freeze_records'] = False
        return {'value':data}  


    @api.onchange('birthday')
    def onchange_birthday(self):
        data = {}
        age = 0
        if self.birthday:
            today = datetime.today()
            birthday = datetime.strptime(self.birthday, '%Y-%m-%d')
            difference  = today - birthday
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

    def birthday_reminder(self):
        emp_search = self.search([('id', '>', 0),('active','=','t')])
        today = datetime.now()
        today_day = today.day
        today_month = today.month
        for record in emp_search:
            count = 0
            emp_active = record.active
            if record.birthday:
                birth_date = record.birthday
                birth_date_month = int(birth_date[5:7])
                birth_date_day = int(birth_date[8:10])
                if birth_date and today_day == birth_date_day and today_month == birth_date_month:
                    search_resign = self.env['hr.resignation'].search([('employee_id','=',record.id),('state','not in',('draft','cancel','rejected','resignation_revoked'))])         
                    if search_resign:
                        if str(search_resign.approved_relieving_date) < str(today):
                            pass
                        elif str(search_resign.approved_relieving_date) >= str(today):
                            emp_record_id = record.id
                            emp_work_mail = record.work_email if record.work_email else record.email
                            if record.cost_center_id.name == 'ITES - FMS/PS':
                                template_id1 = self.env.ref('orient_employee_self_service_portal.email_template_for_bday_reminder_FMS', False)
                                self.env['mail.template'].browse(template_id1.id).send_mail(record.id, force_send=True)
                            if record.cost_center_id.name != 'ITES - FMS/PS':
                                template_id2 = self.env.ref('orient_employee_self_service_portal.email_template_for_birthday_reminder', False)
                                self.env['mail.template'].browse(template_id2.id).send_mail(record.id, force_send=True)
                    else:
                        emp_record_id = record.id
                        emp_work_mail = record.work_email if record.work_email else record.email
                        if record.cost_center_id.name == 'ITES - FMS/PS':
                            template_id1 = self.env.ref('orient_employee_self_service_portal.email_template_for_bday_reminder_FMS', False)
                            self.env['mail.template'].browse(template_id1.id).send_mail(record.id, force_send=True)
                        if record.cost_center_id.name != 'ITES - FMS/PS':
                            template_id2 = self.env.ref('orient_employee_self_service_portal.email_template_for_birthday_reminder', False)
                            self.env['mail.template'].browse(template_id2.id).send_mail(record.id, force_send=True)
                    count = count+1
        return True

    def confirmation_reminder(self):
        emp_search = self.search([('id', '>', 0),('active','=','t'),('position_type','=','probation')])
        today = datetime.now().date()
        today_day = today.day
        today_month = today.month
        for record in emp_search:
            search_resign = self.env['hr.resignation'].search([('employee_id','=',record.id),('state','not in',('draft','cancel','rejected','resignation_revoked'))])
            if not search_resign:
                if record.joining_date and record.site_master_id.name not in ('TIKONA','TIKONA-BACKUP','TIKONA-TTM-MAHAPE'):
                    confirmation_date = datetime.strptime(record.joining_date, "%Y-%m-%d")+relativedelta(months=6)
                    confirmation_date_split = str(confirmation_date).split(' ')
                    confirmation_date = confirmation_date_split[0]
                    if str(confirmation_date) == str(today):
                        create_id = self.env['employee.confirmation'].create({
                            'employee_code':record.emp_code,
                            'employee_id':record.id,
                            'joining_date':record.joining_date,
                            'state':'probation',
                            'designation':record.job_id.id,
                            'department':record.department_id.id,
                            'confirmation_date':confirmation_date,
                            'reporting_manager':record.parent_id.id,
                            })
                        # record.write({'confirmation_link':})
                        template_id = self.env.ref('orient_employee_self_service_portal.email_template_for_confirmation_reminder', False)
                        self.env['mail.template'].browse(template_id.id).send_mail(create_id.id, force_send=True)
        return True

    def assign_notice(self):
        emp_id = self.search([('active', '=', True)])
        for x in emp_id:
            if x.grade_id:
                if x.position_type=='probation':
                    self.write({'notice_period':x.grade_id.notice_period})
                if x.position_type=='confirm':
                    self.write({'notice_period':x.grade_id.notice_period_after_confirmation})
        return True

    def confirm_employee(self):
        self.write({'position_type':'confirm','confirmation_date':fields.date.today()})
        employee_id = self.id
        emp_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        if emp_id:
            approved_by = emp_id.id
        else:
            approved_by = False
        PL = self.env['hr.holidays.status'].search([('code','=','PL')])
        CL = self.env['hr.holidays.status'].search([('code','=','CL')])
        SL_CL = self.env['hr.holidays.status'].search([('code','=','SL/CL')])
        month = datetime.today().month
        if month == 1:
            current_month = 'jan'
        if month == 2:
            current_month = 'feb'
        if month == 3:
            current_month = 'march'
        if month == 4:
            current_month = 'april'
        if month == 5:
            current_month = 'may'
        if month == 6:
            current_month = 'june'
        if month == 7:
            current_month = 'july'
        if month == 8:
            current_month = 'aug'
        if month == 9:
            current_month = 'sept'
        if month == 10:
            current_month = 'oct'
        if month == 11:
            current_month = 'nov'
        if month == 12:
            current_month = 'dec'
        financial_year_id = False
        year = datetime.today().year
        year_master_ids = self.env['year.master'].search([('name','ilike',year)])
        for each_year_master_id in year_master_ids:
            if each_year_master_id.start_date:
                start_date_year = datetime.strptime(each_year_master_id.start_date,'%Y-%m-%d').year
                if start_date_year == year:
                    financial_year_id = each_year_master_id.id
        if not financial_year_id:
            raise AccessError("Financial Year not defined!")
        res_pl = self.env['hr.holidays'].create({
                                        'name':'Leave Allocation', 
                                        'code': 'PL',
                                        'holiday_type':'employee',
                                        'employee_id':employee_id,
                                        'holiday_status_id':PL.id, 
                                        'manager_id':self.parent_id.id,
                                        'total_days':1.0, 
                                        'balanced_days':1.0,
                                        'department_id':self.department_id.id,
                                        'type':'add',
                                        'state':'allocated',
                                        'approved_by':approved_by,
                                        'current_month':current_month,
                                        'financial_year_id':financial_year_id
            })
        self.env['hr.holidays'].create({
                                        'name':'Leave Allocation',
                                        'code': 'SL/CL',
                                        'holiday_type':'employee',
                                        'employee_id':employee_id,
                                        'holiday_status_id':SL_CL.id, 
                                        'manager_id':self.parent_id.id,
                                        'total_days':1, 
                                        'balanced_days':1,
                                        'department_id':self.department_id.id,
                                        'type':'add',
                                        'state':'allocated',
                                        'approved_by':approved_by,
                                        'current_month':current_month,
                                        'financial_year_id':financial_year_id
            })
        # self.env['hr.holidays'].create({
        #                                 'name':'Leave Allocation',
        #                                 'code': 'CL',
        #                                 'holiday_type':'employee',
        #                                 'employee_id':employee_id,
        #                                 'holiday_status_id':CL.id, 
        #                                 'manager_id':self.parent_id.id,
        #                                 'total_days':0.42, 
        #                                 'balanced_days':0.42,
        #                                 'department_id':self.department_id.id,
        #                                 'type':'add',
        #                                 'state':'allocated',
        #                                 'approved_by':approved_by,
        #                                 'current_month':current_month,
        #                                 'financial_year_id':financial_year_id
        #     })
        return True


# class Users(models.Model):
#     _inherit = ['res.users']
    

#     password_reset = fields.Boolean('Password Reset?',default=False)

class BirthdayReport(models.Model):
    _name = 'birthday.report.new'
    # _auto = False
    # _order = "dob asc"

    emp_id = fields.Many2one('hr.employee','Employee')
    emp_name = fields.Char('Name')
    emp_code = fields.Char('Employee Code')
    # dob = fields.Date('Birthday')
    # d_o_b = fields.Date('B-Day')
    # date_of_birth_char = fields.Char('Date of Birth')
    diff = fields.Integer('Diff')
    birthday = fields.Date('Birthday')
    dob = fields.Char('Birthday')
    job_id = fields.Char('Designation')
    total_days = fields.Integer('Total days')
    location = fields.Char('Location')


    @api.model_cr
    def init(self):
        cr = self._cr
        self.env.cr.execute("""
        select *,
        (to_char(dob,'ddd')::int-to_char(now(),'ddd')::int+total_days)%total_days as diff
        from (select he.id as emp_id, he.name as emp_name, to_char(he.birthday, 'Month dd') as birthday,
        hj.name as job_id , he.birthday as dob,
        (to_char((to_char(now(),'yyyy')||'-12-31')::date,'ddd')::int) as total_days,
        he.emp_code as emp_code,
        sm.name as location
        FROM hr_employee he
        join hr_job hj
        on hj.id = he.job_id
        join site_master sm
        on sm.id = he.site_master_id
        where he.active='t' and he.birthday is not null) birth
        where (to_char(dob,'ddd')::int-to_char(now(),'DDD')::int+total_days)%total_days between 0 and 20 order by diff,date_part('Day',dob) asc""")

        birthday = cr.fetchall()
        self.env.cr.execute('Delete from birthday_report_new')
        for x in birthday:
            self.env.cr.execute('insert into birthday_report_new(emp_id,emp_name,dob,job_id,birthday,total_days,diff,emp_code,location)\
             values (%s,%s,%s,%s,%s,%s,%s,%s,%s)',(x[0],x[1],x[2],x[3],x[4],x[5],x[8],str(x[6]),x[7]))
            self.env.cr.commit()
        return True

class PublicHolidays(models.Model):
    _name = 'public.holidays'
    # _auto = False
    # _order = "dob asc"

    # emp_id = fields.Many2one('hr.employee','Employee')
    name = fields.Char('Name')
    holiday_date = fields.Date('Date')


    @api.model_cr
    def init(self):
        cr = self._cr
        uid = self.env.uid
        print (uid,'uidkkkkkkkk')
        emp_id = self.env['hr.employee'].search([('user_id', '=', uid)])
        site_master_id = emp_id.site_master_id.id
        print (site_master_id,'site_master_id')
        self.env.cr.execute("delete from public_holidays")
        self.env.cr.execute("insert into public_holidays(name,holiday_date) values ('New Year','2019-01-01')")
        self.env.cr.commit()
        return True



class Utility(models.Model):
    _name = "utility.utility"


    def create_unlinked_users(self):
        # finds out the employees whose related user is not set
        # searches these employees in users one by one
        # in user is present, links this user with employee
        # or else creates new user and then links it with employee
        employee_obj = self.env['hr.employee']
        users_obj = self.env['res.users']
        partner_obj = self.env['res.partner']
        emp_ids = employee_obj.search([('active','=',True),('user_id','=',False)])
        for each_emp_id in emp_ids:
            print("employee----",each_emp_id.emp_code)
            # each_emp_id = employee_obj.browse(each_emp_id)
            existing_user_id = users_obj.search([('login','=',each_emp_id.emp_code)])
            if not existing_user_id:
                # creating new users
                e_mail = ''
                password = "'$pbkdf2-sha512$25000$Pef8P6f0XsuZ0/q/934PgQ$0uiemDsPZyf/ENm7zFZkx4kP90YX9nvxgTRfgy4Dpj6p1eQ4bFmiPHZaNPo7mU6scwt851CeDolg5JUWwnc1uA'"
                login = "'"+str(each_emp_id.emp_code)+"'"
                if each_emp_id.work_email:
                    e_mail = each_emp_id.work_email.lower()
                else:
                    e_mail = each_emp_id.personal_email.lower()
                vals = {
                        'active':True,
                        'name':each_emp_id.name,
                        'login':str(each_emp_id.emp_code),
                        'email':e_mail,
                        'company_id':1,
                        'share':False,
                        'notification_type':'email',
                        'emp_code':each_emp_id.emp_code,
                        'groups_id': [(6, 0, [self.env.ref('base.group_user').id, self.env.ref('hr_attendance.group_hr_attendance').id])]
                    }
                partner_id = partner_obj.search([('name','=',each_emp_id.name)])
                if partner_id:
                    fin_partner_id = False
                    if len(partner_id) > 1:
                        partner_id = partner_obj.search([('name','=',each_emp_id.name),'|',('email','=',each_emp_id.personal_email),('email','=',each_emp_id.work_email)])
                        if len(partner_id) == 1:
                            fin_partner_id = partner_id.id
                    elif len(partner_id) == 1:
                        fin_partner_id = partner_id.id
                    if fin_partner_id:
                        vals.update({'partner_id':fin_partner_id})
                res = users_obj.create(vals)
                self.env.cr.execute("update res_users set password_crypt=%s where login=%s" %(str(password),str(login)))
                self.env.cr.execute("update hr_employee set user_id=%s where emp_code=%s" %(str(res.id),str(login)))
            else:
                self.env.cr.execute("update hr_employee set user_id=%s where emp_code=%s" %(str(existing_user_id.id),str(each_emp_id.emp_code)))
        return res


    def update_user_emails(self):
        # it will update email for the users who do not have email id set.
        res = False
        employee_obj = self.env['hr.employee']
        users_obj = self.env['res.users']
        partner_obj = self.env['res.partner']
        # find out active users who email ids are null
        user_ids = users_obj.search([('active','=',True),('email','=',None)])
        for each_user_id in user_ids:
            # user should not be a service portal user
            service_portal_group_id = self.env['res.groups'].search([('name','=','Service Portal User')])
            group_id = service_portal_group_id.id
            user_id = each_user_id.id
            self.env.cr.execute("select uid from res_groups_users_rel where uid=%s and gid=%s" %(str(user_id),str(group_id)))
            result = self.env.cr.dictfetchall()
            # if user is not a service portal user, go ahead and find out the email id from employee profile and write in user obj
            if not result:
                email = None
                emp_id = employee_obj.search([('emp_code','=',each_user_id.login)], limit=1)
                print("employee",emp_id.emp_code)
                if emp_id:
                    if emp_id.work_email:
                        email = emp_id.work_email.lower()
                    elif emp_id.personal_email:
                        email = emp_id.personal_email.lower()
                each_user_id.write({'email':email})
        return res


    def lower_user_emails(self):
        employee_obj = self.env['hr.employee']
        users_obj = self.env['res.users']
        partner_obj = self.env['res.partner']
        user_ids = users_obj.search([('active','=',True)])
        for each_user_id in user_ids:
            print("user",each_user_id.login)
            if each_user_id.email:
                each_user_id.write({'email':each_user_id.email.lower()})
        emp_ids = employee_obj.search([('active','=',True)])
        for each_emp_id in emp_ids:
            work_email = None
            personal_email = None
            print("employee",each_emp_id.emp_code)
            if each_emp_id.work_email:
                work_email = each_emp_id.work_email.lower()
            if each_emp_id.personal_email:
                personal_email = each_emp_id.personal_email.lower()
            each_emp_id.write({'work_email':work_email,'personal_email':personal_email})
        return True


    def update_padwa_ph(self):
        employee_obj = self.env['hr.employee']
        attendance_obj = self.env['hr.attendance']
        holiday_obj = self.env['holiday.master']
        site_obj = self.env['site.master']
        gudi_padwa_sites = []
        # find sites having gudi padwa
        gudi_padwa_holiday_id = holiday_obj.search([('name','=','Gudi Padwa')])
        self.env.cr.execute("select site_id from site_holiday_rel where holiday_id=%s" %(str(gudi_padwa_holiday_id.id)))
        site_results = self.env.cr.dictfetchall()
        if site_results:
            for each_site_result in site_results:
                site_id = each_site_result.get('site_id')
                gudi_padwa_sites.append(site_id)
        if gudi_padwa_sites:
            for gudi_padwa_site in gudi_padwa_sites:
                site_data = site_obj.browse(gudi_padwa_site)
                # employees of each site
                gudi_site_employees = employee_obj.search([('site_master_id','=',gudi_padwa_site)])
                for gudi_site_employee in gudi_site_employees:
                    # find out the atendance entry of each employee on 6 april
                    attendance_id = attendance_obj.search([('employee_id','=',gudi_site_employee.id),('attendance_date','=','2019-04-06')])
                    # if there is PH, pass else update PH
                    if attendance_id:
                        ph_remark = attendance_id.employee_status
                        if ph_remark == 'PH':
                            pass
                        else:
                            attendance_id.write({'employee_status':'PH'})
                    else:
                        attendance_obj.create(
                            {
                                'employee_id':gudi_site_employee.id,
                                'employee_code':gudi_site_employee.emp_code,
                                'department_id_val':gudi_site_employee.department_id.id,
                                'attendance_date':'2019-04-06',
                                'employee_status':'PH',
                                'site_master_id':gudi_site_employee.site_master_id.id,
                                'shift':gudi_site_employee.shift_id.id,
                                'worked_hours':0.00,
                                'state':'done'
                            })
        return True



    def delete_redundant_attendance_records(self):
        attendance_obj = self.env['hr.attendance']
        emp_obj = self.env['hr.employee']
        self.env.cr.execute("SELECT employee_id,attendance_date, COUNT(employee_id) ,COUNT(attendance_date) FROM hr_attendance GROUP BY employee_id,attendance_date HAVING COUNT(employee_id)>1 and COUNT(attendance_date)>1;")
        double_entries = self.env.cr.dictfetchall()
        print("double_entries",double_entries)
        for each_entry in double_entries:
            employee_id = each_entry.get('employee_id')
            attendance_date = each_entry.get('attendance_date')
            emp_data = emp_obj.browse(employee_id)
            attendance_records = attendance_obj.search([('employee_id','=',employee_id),('attendance_date','=',attendance_date)])
            print("double_entry---",emp_data.name,emp_data.id,each_entry,attendance_records)
            to_be_deleted = False
            no_code_records = attendance_obj.search([('id','in',attendance_records.ids),('employee_code','=',False)])
            if len(no_code_records) == 1:
                to_be_deleted = no_code_records
            else:
                no_inout_time_records = attendance_obj.search([('id','in',attendance_records.ids),('check_in','=',False),('check_out','=',False)])
                if len(no_inout_time_records) == 1:
                    to_be_deleted = no_inout_time_records
                else:
                    no_worked_hours_records = attendance_obj.search([('id','in',attendance_records.ids),('worked_hours','=',False)])
                    if len(no_worked_hours_records) == 1:
                        to_be_deleted = no_worked_hours_records
                    else:
                        no_emp_status_records = attendance_obj.search([('id','in',attendance_records.ids),('employee_status','=',False)])
                        if len(no_emp_status_records) == 1:
                            to_be_deleted = no_emp_status_records
                        else:
                            noapproval_state_records = attendance_obj.search([('id','in',attendance_records.ids),('state','!=','approval')])
                            if len(noapproval_state_records) == 1:
                                to_be_deleted = noapproval_state_records
                            else:
                                no_shift_records = attendance_obj.search([('id','in',attendance_records.ids),('shift','=',False)])
                                if len(no_shift_records) == 1:
                                    to_be_deleted = no_shift_records
                                else:
                                    no_site_records = attendance_obj.search([('id','in',attendance_records.ids),('site_master_id','=',False)])
                                    if len(no_site_records) == 1:
                                        to_be_deleted = no_site_records
                                    else:
                                        no_dept_records = attendance_obj.search([('id','in',attendance_records.ids),('department_id_val','=',False)])
                                        if len(no_dept_records) == 1:
                                            to_be_deleted = no_dept_records
                                        else:
                                            min_id = min(attendance_records.ids)
                                            min_data = attendance_obj.browse(min_id)
                                            to_be_deleted = min_data
            print("deleting",to_be_deleted)
            self.env.cr.execute("delete from hr_attendance where id=%s" %(str(to_be_deleted.id)))
        return True


    def update_attendance_records(self):
        attendance_obj = self.env['hr.attendance']
        emp_obj = self.env['hr.employee']
        code_count = 1
        no_code_records = attendance_obj.search([('employee_code','=',False),('attendance_date','>=','2019-04-01'),('attendance_date','<=','2019-04-30')])
        for each_no_code_record in no_code_records:
            if each_no_code_record.employee_id.emp_code:
                each_no_code_record.write({'employee_code':each_no_code_record.employee_id.emp_code})
                print("code_count",code_count)
                code_count = code_count+1
        site_count = 1
        no_site_records = attendance_obj.search([('site_master_id','=',False),('attendance_date','>=','2019-04-01'),('attendance_date','<=','2019-04-30')])
        for each_no_site_record in no_site_records:
            if each_no_site_record.employee_id.site_master_id:
                each_no_site_record.write({'site_master_id':each_no_site_record.employee_id.site_master_id.id})
                print("site_count",site_count)
                site_count = site_count+1
        shift_count = 1
        no_shift_records = attendance_obj.search([('shift','=',False),('attendance_date','>=','2019-04-01'),('attendance_date','<=','2019-04-30')])
        for each_no_shift_record in no_shift_records:
            if each_no_shift_record.employee_id.shift_id:
                each_no_shift_record.write({'shift':each_no_shift_record.employee_id.shift_id.id})
                print("shift_count",shift_count)
                shift_count = shift_count+1
        department_count = 1
        no_dept_records = attendance_obj.search([('department_id_val','=',False),('attendance_date','>=','2019-04-01'),('attendance_date','<=','2019-04-30')])
        for each_no_dept_record in no_dept_records:
            if each_no_dept_record.employee_id.department_id:
                each_no_dept_record.write({'department_id_val':each_no_dept_record.employee_id.department_id.id})
                print("department_count",department_count)
                department_count = department_count+1

        # ## From 1st to 9th april
        # # make early leaving false where worked_hours are more than 8.00 and still early leaving appears
        # print("From 1st to 9th april-------------------------------------------------------------------")
        # el_att_ids = attendance_obj.search([('early_leaving','!=',False),('worked_hours','>=',8.00),('shift','=',21),('attendance_date','>=','2019-04-01'),('attendance_date','<=','2019-04-09')])
        # if el_att_ids:
        #     el_count = 1
        #     for el_att_id in el_att_ids:
        #         el_att_id.write({'early_leaving':False})
        #         print("early leaving made null",el_count)
        #         el_count = el_count+1

        # ## calculate and update early leaving for those who have not completed 8.00 hours
        # el_att_ids2 = attendance_obj.search([('worked_hours','<',8.00),('worked_hours','>',0),('shift','=',21),('attendance_date','>=','2019-04-10'),('attendance_date','<=','2019-04-09')])
        # if el_att_ids2:
        #     el_count2 = 1
        #     for el_att_id2 in el_att_ids2:
        #         early_leaving_fl = 7.60 - el_att_id2.worked_hours
        #         early_leaving_str = str(early_leaving_fl)
        #         early_leaving = early_leaving_str.replace('.',':')
        #         el_att_id2.write({'early_leaving':early_leaving})
        #         print("early leaving updated",el_count2)
        #         el_count2 = el_count2+1 

        # # calculate and update late coming for those who came after 10
        # lc_att_ids = attendance_obj.search([('late_coming','=',False),('in_time','!=',False),('worked_hours','>',0),('shift','=',21),('attendance_date','>=','2019-04-01'),('attendance_date','<=','2019-04-09')])
        # if lc_att_ids:
        #     lc_count = 1
        #     for lc_att_id in lc_att_ids:
        #         if lc_att_id.in_time:
        #             in_time = lc_att_id.in_time
        #             in_time_st = in_time.replace(':','.')
        #             in_time_fl = float(in_time_st)
        #             if in_time_fl >= 10.00:
        #                 late_coming_fl = in_time_fl - 10.00
        #                 late_coming_str = str(late_coming_fl)
        #                 late_coming = late_coming_str.replace('.',':')
        #                 lc_att_id.write({'late_coming':late_coming})
        #                 print("late coming updated",lc_count)
        #                 lc_count = lc_count+1

        # ## From 10th to 26th april
        # # make early leaving false where worked_hours are more than 9.00 and still early leaving appears
        # print("From 10th to 26th april-------------------------------------------------------------------")
        # el_att_ids3 = attendance_obj.search([('early_leaving','!=',False),('worked_hours','>=',9.00),('shift','=',21),('attendance_date','>=','2019-04-10'),('attendance_date','<=','2019-04-26')])
        # if el_att_ids3:
        #     el_count3 = 1
        #     for el_att_id3 in el_att_ids3:
        #         el_att_id3.write({'early_leaving':False})
        #         print("early leaving made null",el_count3)
        #         el_count3 = el_count3+1


        # ## calculate and update early leaving for those who have not completed 9.00 hours
        # el_att_ids4 = attendance_obj.search([('worked_hours','<',9.00),('worked_hours','>',0),('shift','=',21),('attendance_date','>=','2019-04-10'),('attendance_date','<=','2019-04-26')])
        # if el_att_ids4:
        #     el_count4 = 1
        #     for el_att_id4 in el_att_ids4:
        #         early_leaving_fl = 8.60 - el_att_id4.worked_hours
        #         early_leaving_str = str(early_leaving_fl)
        #         early_leaving = early_leaving_str.replace('.',':')
        #         el_att_id4.write({'early_leaving':early_leaving})
        #         print("early leaving updated",el_count4)
        #         el_count4 = el_count4+1 


        # # calculate and update late coming for those who came after 10
        # lc_att_ids2 = attendance_obj.search([('late_coming','=',False),('in_time','!=',False),('worked_hours','>',0),('shift','=',21),('attendance_date','>=','2019-04-01'),('attendance_date','<=','2019-04-09')])
        # if lc_att_ids2:
        #     lc_count2 = 1
        #     for lc_att_id2 in lc_att_ids2:
        #         if lc_att_id2.in_time:
        #             in_time2 = lc_att_id2.in_time
        #             in_time_st2 = in_time.replace(':','.')
        #             in_time_fl2 = float(in_time_st2)
        #             if in_time_fl2 >= 10.0:
        #                 late_coming_fl2 = in_time_fl2 - 10.00
        #                 late_coming_str2 = str(late_coming_fl2)
        #                 late_coming2 = late_coming_str2.replace('.',':')
        #                 lc_att_id.write({'late_coming':late_coming2})
        #                 print("late coming updated",lc_count2)
        #                 lc_count2 = lc_count2+1


        # ## On 29th april
        # # make early leaving false where worked_hours are more than 7.00 and still early leaving appears
        # print("On 29th april-------------------------------------------------------------------")
        # el_att_ids5 = attendance_obj.search([('early_leaving','!=',False),('worked_hours','>=',7.00),('shift','=',21),('attendance_date','=','2019-04-29')])
        # if el_att_ids5:
        #     el_count5 = 1
        #     for el_att_id5 in el_att_ids5:
        #         el_att_id5.write({'early_leaving':False})
        #         print("early leaving made null",el_count5)
        #         el_count5 = el_count5+1

        # ## calculate and update early leaving for those who have not completed 7.00 hours
        # el_att_ids6 = attendance_obj.search([('worked_hours','<',7.00),('worked_hours','>',0),('shift','=',21),('attendance_date','=','2019-04-29')])
        # if el_att_ids6:
        #     el_count6 = 1
        #     for el_att_id6 in el_att_ids6:
        #         early_leaving_fl6 = 6.60 - el_att_id6.worked_hours
        #         early_leaving_str6 = str(early_leaving_fl)
        #         early_leaving6 = early_leaving_str6.replace('.',':')
        #         el_att_id6.write({'early_leaving':early_leaving6})
        #         print("early leaving updated",el_count6)
        #         el_count6 = el_count6+1 


        # # # make late coming false for those who came before 11 still have late coming mark
        # # lc_att_ids6 = attendance_obj.search([('late_coming','!=',False),('worked_hours','>',0),('shift','=',21),('attendance_date','=','2019-04-29')])
        # # if lc_att_ids6:
        # #     lc_count6= 1
        # #     for lc_att_id6 in lc_att_ids6:
        # #         if lc_att_id6.in_time:
        # #             in_time6 = lc_att_id6.in_time
        # #             in_time_st6 = in_time6.replace(':','.')
        # #             in_time_fl6 = float(in_time_st6)
        # #             if in_time_fl6 < 11.00:
        # #                 lc_att_id6.write({'late_coming':False})
        # #                 print("late coming updated",lc_count6)
        # #                 lc_count6 = lc_count6+1


        # # # calculate and update late coming for those who came after 11.00
        # # lc_att_ids3 = attendance_obj.search([('late_coming','=',False),('in_time','!=',False),('worked_hours','>',0),('shift','=',21),('attendance_date','=','2019-04-29')])
        # # if lc_att_ids3:
        # #     lc_count3 = 1
        # #     for lc_att_id3 in lc_att_ids3:
        # #         if lc_att_id3.in_time:
        # #             in_time3 = lc_att_id3.in_time
        # #             in_time_st3 = in_time3.replace(':','.')
        # #             in_time_fl3 = float(in_time_st3)
        # #             if in_time_fl3 > 11.00:
        # #                 late_coming_fl3 = in_time_fl3 - 11.00
        # #                 late_coming_str3 = str(late_coming_fl3)
        # #                 late_coming3 = late_coming_str3.replace('.',':')
        # #                 lc_att_id3.write({'late_coming':late_coming3})
        # #                 print("late coming updated",lc_count3)
        # #                 lc_count3 = lc_count3+1

        # ## On 30th april
        # # make early leaving false where worked_hours are more than 9.00 and still early leaving appears
        # print("On 30th april-------------------------------------------------------------------")
        # el_att_ids7 = attendance_obj.search([('early_leaving','!=',False),('worked_hours','>=',9.00),('shift','=',21),('attendance_date','=','2019-04-30')])
        # if el_att_ids5:
        #     el_count7 = 1
        #     for el_att_id7 in el_att_ids7:
        #         el_att_id7.write({'early_leaving':False})
        #         print("early leaving made null",el_count7)
        #         el_count7 = el_count7+1

        # ## calculate and update early leaving for those who have not completed 9.00 hours
        # el_att_ids8 = attendance_obj.search([('worked_hours','<',9.00),('worked_hours','>',0),('shift','=',21),('attendance_date','=','2019-04-30')])
        # if el_att_ids8:
        #     el_count8 = 1
        #     for el_att_id8 in el_att_ids8:
        #         early_leaving_fl8 = 8.60 - el_att_id8.worked_hours
        #         early_leaving_str8 = str(early_leaving_fl)
        #         early_leaving8 = early_leaving_str8.replace('.',':')
        #         el_att_id8.write({'early_leaving':early_leaving8})
        #         print("early leaving updated",el_count8)
        #         el_count8 = el_count8+1 

        # # calculate and update late coming for those who came after 10.00
        # lc_att_ids4 = attendance_obj.search([('late_coming','=',False),('in_time','!=',False),('worked_hours','>',0),('shift','=',21),('attendance_date','=','2019-04-30')])
        # if lc_att_ids4:
        #     lc_count4 = 1
        #     for lc_att_id4 in lc_att_ids4:
        #         if lc_att_id4.in_time:
        #             in_time4 = lc_att_id4.in_time
        #             in_time_st4 = in_time4.replace(':','.')
        #             in_time_fl4 = float(in_time_st4)
        #             if in_time_fl4 >= 10.00:
        #                 late_coming_fl4 = in_time_fl4 - 10.00
        #                 late_coming_str4 = str(late_coming_fl4)
        #                 late_coming4 = late_coming_str4.replace('.',':')
        #                 lc_att_id4.write({'late_coming':late_coming4})
        #                 print("late coming updated",lc_count4)
        #                 lc_count4 = lc_count4+1
        return True



    def resolve_early_leaving_late_coming_issue(self):
        attendance_obj = self.env['hr.attendance']

        ## From 1st to 9th april
        # make early leaving false where worked_hours are more than 8.00 and still early leaving appears
        print("From 1st to 9th april-------------------------------------------------------------------")
        el_att_ids = attendance_obj.search([('early_leaving','!=',False),('worked_hours','>=',8.00),('shift','=',21),('attendance_date','>=','2019-04-01'),('attendance_date','<=','2019-04-09')])
        if el_att_ids:
            el_count = 1
            for el_att_id in el_att_ids:
                el_att_id.write({'early_leaving':False})
                print("early leaving made null",el_count)
                el_count = el_count+1

        ## calculate and update early leaving for those who have not completed 8.00 hours
        el_att_ids2 = attendance_obj.search([('worked_hours','<',8.00),('worked_hours','>',0),('shift','=',21),('attendance_date','>=','2019-04-10'),('attendance_date','<=','2019-04-09')])
        if el_att_ids2:
            el_count2 = 1
            for el_att_id2 in el_att_ids2:
                early_leaving_fl = 7.60 - el_att_id2.worked_hours
                early_leaving_str = str(early_leaving_fl)
                early_leaving = str('%.2f' % early_leaving_str).replace('.',':')
                el_att_id2.write({'early_leaving':early_leaving})
                print("early leaving updated",el_count2)
                el_count2 = el_count2+1 

        # calculate and update late coming for those who came after 10
        lc_att_ids = attendance_obj.search([('late_coming','=',False),('in_time','!=',False),('worked_hours','>',0),('shift','=',21),('attendance_date','>=','2019-04-01'),('attendance_date','<=','2019-04-09')])
        if lc_att_ids:
            lc_count = 1
            for lc_att_id in lc_att_ids:
                if lc_att_id.in_time:
                    in_time = lc_att_id.in_time
                    in_time_st = in_time.replace(':','.')
                    in_time_fl = float(in_time_st)
                    if in_time_fl >= 10.00:
                        late_coming_fl = in_time_fl - 10.00
                        late_coming_str = str(late_coming_fl)
                        late_coming = str('%.2f' % late_coming_str).replace('.',':')
                        lc_att_id.write({'late_coming':late_coming})
                        print("late coming updated",lc_count)
                        lc_count = lc_count+1

        ## From 10th to 26th april
        # make early leaving false where worked_hours are more than 9.00 and still early leaving appears
        print("From 10th to 26th april-------------------------------------------------------------------")
        el_att_ids3 = attendance_obj.search([('early_leaving','!=',False),('worked_hours','>=',9.00),('shift','=',21),('attendance_date','>=','2019-04-10'),('attendance_date','<=','2019-04-26')])
        if el_att_ids3:
            el_count3 = 1
            for el_att_id3 in el_att_ids3:
                el_att_id3.write({'early_leaving':False})
                print("early leaving made null",el_count3)
                el_count3 = el_count3+1


        ## calculate and update early leaving for those who have not completed 9.00 hours
        el_att_ids4 = attendance_obj.search([('worked_hours','<',9.00),('worked_hours','>',0),('shift','=',21),('attendance_date','>=','2019-04-10'),('attendance_date','<=','2019-04-26')])
        if el_att_ids4:
            el_count4 = 1
            for el_att_id4 in el_att_ids4:
                early_leaving_fl = 8.60 - el_att_id4.worked_hours
                early_leaving_str = str(early_leaving_fl)
                early_leaving = str('%.2f' % early_leaving_str).replace('.',':')
                el_att_id4.write({'early_leaving':early_leaving})
                print("early leaving updated",el_count4)
                el_count4 = el_count4+1 


        # calculate and update late coming for those who came after 10
        lc_att_ids2 = attendance_obj.search([('late_coming','=',False),('in_time','!=',False),('worked_hours','>',0),('shift','=',21),('attendance_date','>=','2019-04-01'),('attendance_date','<=','2019-04-09')])
        if lc_att_ids2:
            lc_count2 = 1
            for lc_att_id2 in lc_att_ids2:
                if lc_att_id2.in_time:
                    in_time2 = lc_att_id2.in_time
                    in_time_st2 = in_time.replace(':','.')
                    in_time_fl2 = float(in_time_st2)
                    if in_time_fl2 >= 10.0:
                        late_coming_fl2 = in_time_fl2 - 10.00
                        late_coming_str2 = str(late_coming_fl2)
                        late_coming2 = str('%.2f' % late_coming_str2).replace('.',':')
                        lc_att_id.write({'late_coming':late_coming2})
                        print("late coming updated",lc_count2)
                        lc_count2 = lc_count2+1


        ## On 29th april
        # make early leaving false where worked_hours are more than 7.00 and still early leaving appears
        print("On 29th april-------------------------------------------------------------------")
        el_att_ids5 = attendance_obj.search([('early_leaving','!=',False),('worked_hours','>=',7.00),('shift','=',21),('attendance_date','=','2019-04-29')])
        if el_att_ids5:
            el_count5 = 1
            for el_att_id5 in el_att_ids5:
                el_att_id5.write({'early_leaving':False})
                print("early leaving made null",el_count5)
                el_count5 = el_count5+1

        ## calculate and update early leaving for those who have not completed 7.00 hours
        el_att_ids6 = attendance_obj.search([('worked_hours','<',7.00),('worked_hours','>',0),('shift','=',21),('attendance_date','=','2019-04-29')])
        if el_att_ids6:
            el_count6 = 1
            for el_att_id6 in el_att_ids6:
                early_leaving_fl6 = 6.60 - el_att_id6.worked_hours
                early_leaving_str6 = str(early_leaving_fl)
                early_leaving6 = str('%.2f' % early_leaving_str6).replace('.',':')
                el_att_id6.write({'early_leaving':early_leaving6})
                print("early leaving updated",el_count6)
                el_count6 = el_count6+1 


        # # make late coming false for those who came before 11 still have late coming mark
        # lc_att_ids6 = attendance_obj.search([('late_coming','!=',False),('worked_hours','>',0),('shift','=',21),('attendance_date','=','2019-04-29')])
        # if lc_att_ids6:
        #     lc_count6= 1
        #     for lc_att_id6 in lc_att_ids6:
        #         if lc_att_id6.in_time:
        #             in_time6 = lc_att_id6.in_time
        #             in_time_st6 = in_time6.replace(':','.')
        #             in_time_fl6 = float(in_time_st6)
        #             if in_time_fl6 < 11.00:
        #                 lc_att_id6.write({'late_coming':False})
        #                 print("late coming updated",lc_count6)
        #                 lc_count6 = lc_count6+1


        # # calculate and update late coming for those who came after 11.00
        # lc_att_ids3 = attendance_obj.search([('late_coming','=',False),('in_time','!=',False),('worked_hours','>',0),('shift','=',21),('attendance_date','=','2019-04-29')])
        # if lc_att_ids3:
        #     lc_count3 = 1
        #     for lc_att_id3 in lc_att_ids3:
        #         if lc_att_id3.in_time:
        #             in_time3 = lc_att_id3.in_time
        #             in_time_st3 = in_time3.replace(':','.')
        #             in_time_fl3 = float(in_time_st3)
        #             if in_time_fl3 > 11.00:
        #                 late_coming_fl3 = in_time_fl3 - 11.00
        #                 late_coming_str3 = str(late_coming_fl3)
        #                 late_coming3 = late_coming_str3.replace('.',':')
        #                 lc_att_id3.write({'late_coming':late_coming3})
        #                 print("late coming updated",lc_count3)
        #                 lc_count3 = lc_count3+1



        ## On 30th april
        # make early leaving false where worked_hours are more than 9.00 and still early leaving appears
        print("On 30th april-------------------------------------------------------------------")
        el_att_ids7 = attendance_obj.search([('early_leaving','!=',False),('worked_hours','>=',9.00),('shift','=',21),('attendance_date','=','2019-04-30')])
        if el_att_ids5:
            el_count7 = 1
            for el_att_id7 in el_att_ids7:
                el_att_id7.write({'early_leaving':False})
                print("early leaving made null",el_count7)
                el_count7 = el_count7+1

        ## calculate and update early leaving for those who have not completed 9.00 hours
        el_att_ids8 = attendance_obj.search([('worked_hours','<',9.00),('worked_hours','>',0),('shift','=',21),('attendance_date','=','2019-04-30')])
        if el_att_ids8:
            el_count8 = 1
            for el_att_id8 in el_att_ids8:
                early_leaving_fl8 = 8.60 - el_att_id8.worked_hours
                early_leaving_str8 = str(early_leaving_fl)
                early_leaving8 = str('%.2f' % early_leaving_str8).replace('.',':')
                el_att_id8.write({'early_leaving':early_leaving8})
                print("early leaving updated",el_count8)
                el_count8 = el_count8+1 

        # calculate and update late coming for those who came after 10.00
        lc_att_ids4 = attendance_obj.search([('late_coming','=',False),('in_time','!=',False),('worked_hours','>',0),('shift','=',21),('attendance_date','=','2019-04-30')])
        if lc_att_ids4:
            lc_count4 = 1
            for lc_att_id4 in lc_att_ids4:
                if lc_att_id4.in_time:
                    in_time4 = lc_att_id4.in_time
                    in_time_st4 = in_time4.replace(':','.')
                    in_time_fl4 = float(in_time_st4)
                    if in_time_fl4 >= 10.00:
                        late_coming_fl4 = in_time_fl4 - 10.00
                        late_coming_str4 = str(late_coming_fl4)
                        late_coming4 = str('%.2f' % late_coming_str4).replace('.',':')
                        lc_att_id4.write({'late_coming':late_coming4})
                        print("late coming updated",lc_count4)
                        lc_count4 = lc_count4+1
        return True


    def update_manager_user_id_leaves(self):
        leaves_obj = self.env['hr.holidays']
        emp_obj = self.env['hr.employee']
        applied_leaves = leaves_obj.search([('type','=','remove'),('state','=','confirm')])
        for applied_leave in applied_leaves:
            if applied_leave.manager_id.user_id.id == applied_leave.manager_user_id.id:
                pass
            else:
                applied_leave.write({'manager_user_id':applied_leave.manager_id.user_id.id})
        return True

    def correct_leave_count(self):
        leaves_obj = self.env['hr.holidays']
        #find the allocated PLs
        allocated_pl_ids = leaves_obj.search([('type','=','add'),('code','=','PL')])
        print("allocated_pl_ids",len(allocated_pl_ids))
        # iterate over the allocated PL to find each employee holidays
        for each_allocated_pl_id in allocated_pl_ids:
            allocated = each_allocated_pl_id.total_days
            # find out leaves taken
            pl_ids = leaves_obj.search([('employee_id','=',each_allocated_pl_id.employee_id.id),('code','=','PL'),('type','=','remove'),('state','in',['confirm','validate'])])
            if pl_ids:
                taken = 0
                for each_pl_id in pl_ids:
                    taken = taken + each_pl_id.total_days
                balanced_pl_days = allocated - taken
            else:
                balanced_pl_days = allocated
            if balanced_pl_days > each_allocated_pl_id.total_days:
                print("Problem----: ",each_allocated_pl_id,each_allocated_pl_id.employee_code,each_allocated_pl_id.code)
            # if new calculated balance is equal to existing balanced
            if balanced_pl_days == each_allocated_pl_id.balanced_days:
                print("Correct----: ",each_allocated_pl_id.employee_code,each_allocated_pl_id.balanced_days,balanced_pl_days)
            else:
                print("Incorrect----: ",each_allocated_pl_id.employee_code,each_allocated_pl_id.balanced_days,balanced_pl_days)
                self.env.cr.execute("update hr_holidays set balanced_days=%s where id=%s" %(balanced_pl_days,str(each_allocated_pl_id.id)))
                
        # find the allocated SLs
        allocated_sl_ids = leaves_obj.search([('type','=','add'),('code','=','SL/CL')])
        print("allocated_sl_ids",len(allocated_sl_ids))
        # iterate over the allocated SLs to find each employee holidays
        for each_allocated_sl_id in allocated_sl_ids:
            allocated = each_allocated_sl_id.total_days
            # find out leaves taken
            sl_ids = leaves_obj.search([('employee_id','=',each_allocated_sl_id.employee_id.id),('code','=','SL/CL'),('type','=','remove'),('state','in',['confirm','validate'])])
            if sl_ids:
                taken = 0
                for each_sl_id in sl_ids:
                    taken = taken + each_sl_id.total_days
                balanced_sl_days = allocated - taken
            else:
                balanced_sl_days = allocated
            if balanced_sl_days > each_allocated_sl_id.total_days:
                print("Problem----: ",each_allocated_sl_id,each_allocated_sl_id.employee_code,each_allocated_sl_id.code)
            # if new calculated balance is equal to existing balanced
            if balanced_sl_days == each_allocated_sl_id.balanced_days:
                print("Correct----: ",each_allocated_sl_id.employee_code,each_allocated_sl_id.balanced_days,balanced_sl_days)
            else:
                print("Incorrect----: ",each_allocated_sl_id.employee_code,each_allocated_sl_id.balanced_days,balanced_sl_days)
                self.env.cr.execute("update hr_holidays set balanced_days=%s where id=%s" %(balanced_sl_days,str(each_allocated_sl_id.id)))
        return True

    def calculate_worked_hours(self):
        emp_obj = self.env['hr.employee']
        attendance_obj = self.env['hr.attendance']
        search_attendance = attendance_obj.search([('attendance_date','>=','2019-05-01'),('attendance_date','<=','2019-05-31')])
        todays_date = datetime.now()
        emp_recs = emp_obj.search([('active','=',True)])
        count = 0
        for hr_employee_id in emp_recs:
            employee_id = hr_employee_id.id
            employee_code = hr_employee_id.emp_code
            department_id = hr_employee_id.department_id.id
            if not department_id:
                department_id=None
            site_master_id = hr_employee_id.site_master_id.id
            if not site_master_id:
                site_master_id=None
            fms_ids = []
            mumbai_id = self.env['site.master'].search([('name','=','Mumbai HO')])
            pune_id = self.env['site.master'].search([('name','=','PUNE BRANCH')])
            ahmedabad_id = self.env['site.master'].search([('name','=','Ahmedabad Branch')])
            bangalore_id = self.env['site.master'].search([('name','=','BANGLORE BRANCH')])
            chennai_id = self.env['site.master'].search([('name','=','CHENNAI BRANCH')])
            delhi_id = self.env['site.master'].search([('name','=','Delhi Branch')])
            kolkata_id = self.env['site.master'].search([('name','=','KOLKATA BRANCH')])
            hr_id = self.env['site.master'].search([('name','=','Human Resource - Mumbai')])
            if mumbai_id:
                fms_ids.append(mumbai_id.id)
            if pune_id:
                fms_ids.append(pune_id.id)
            if ahmedabad_id:
                fms_ids.append(ahmedabad_id.id)
            if bangalore_id:
                fms_ids.append(bangalore_id.id)
            if chennai_id:
                fms_ids.append(chennai_id.id)
            if delhi_id:
                fms_ids.append(delhi_id.id)
            if kolkata_id:
                fms_ids.append(kolkata_id.id)
            if hr_id:
                fms_ids.append(hr_id.id)
            # shift_application_line = self.env['shift.application.line'].search([('employee_code','=',employee_code),('date','=',attendance_date)])
            search_attendance = attendance_obj.search([('employee_code','=',employee_code),('attendance_date','>=','2019-05-01'),('attendance_date','<=','2019-05-31')])
            for rec in search_attendance:
                actual_worked_hours = 0.0
                diff_out_time_replace = None
                diff_in_time_replace = None
                search_att = attendance_obj.search([('employee_code','=',employee_code),('attendance_date','=',str(rec.attendance_date))],limit=1)
                if search_att.in_time!='' and search_att.out_time!='':
                    update_in_time = search_att.in_time
                    update_out_time = search_att.out_time
                    in_time_split = 0.0
                    out_time_split = 0.0
                    if update_in_time:
                        in_time_split = update_in_time.replace(':','.')
                    # to keep the most out time 
                    if update_out_time:
                        out_time_split = update_out_time.replace(':','.')
                    attendance_date_split = rec.attendance_date.split('-')
                    attendance_date = attendance_date_split[0]+'-'+attendance_date_split[1]+'-'+attendance_date_split[2]
                    in_time = in_time_split
                    out_time = out_time_split
                    print (in_time_split,in_time,'llllll')
                    print (out_time_split,out_time,'jjjj')
                    if in_time != 0.0 and out_time!=0.0:
                        if in_time!=0.0:
                            in_time = in_time.replace('.',':')
                            check_in = str(attendance_date)+' '+str(in_time)
                            print (check_in,'check_in')
                        if out_time!=0.0:
                            out_time = out_time.replace('.',':')
                            check_out = str(attendance_date)+' '+str(out_time)
                        check_in_time = False
                        check_out_time = False
                        check_in_min = False
                        check_out_min = False
                        if check_in:
                            check_in_time = datetime.strptime(str(check_in), "%Y-%m-%d %H:%M") - timedelta(hours=5)
                        if check_out:
                            check_out_time = datetime.strptime(str(check_out), "%Y-%m-%d %H:%M")- timedelta(hours=5)
                        # print(check_in_time,check_out_time,'gggggg---1111')
                        if check_in_time:
                            check_in_min = check_in_time - timedelta(minutes=30)
                        if check_out_time:
                            check_out_min = check_out_time - timedelta(minutes=30)
                        tdiff =  check_out_time - check_in_time
                        tdiff_string = str(tdiff)
                        tdiff_split = tdiff_string.split(':')
                        tdiff_split_val = tdiff_split[0]+'.'+tdiff_split[1]
                        # print(tdiff_split_val,'tdiff_split_val')
                        if ',' in tdiff_split_val:
                            tdiff_split_comma = tdiff_split_val.split(',')
                            tdiff_split_comma_val = tdiff_split_comma[1]
                            tdiff_split_val = tdiff_split_comma_val
                        worked_hours = float(tdiff_split_val)
                        print(worked_hours,'worked_hours',rec.employee_code)
                        self.env.cr.execute('update hr_attendance set worked_hours=%s where id=%s' ,(worked_hours,rec.id))
                        self.env.cr.commit()
            count+=1
        print (count,'count')
        return True                    



    def resend_selection_mail(self):
        applicant_ids = self.env['hr.applicant'].search([('location','=',288)]).ids
        # sorted_applicant_ids = [32,
        # 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 
        # 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 
        # 61, 62, 63, 64, 65, 66, 67, 68, 69, 70,
        # 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 
        # 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 
        # 91, 92, 93, 94, 95, 97, 98, 99, 100, 
        # 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 
        # 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 
        # 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 
        # 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 
        # 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 
        # 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 
        # 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 
        # 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 
        # 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 
        # 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 
        # 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 
        # 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 
        # 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 
        # 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 
        # 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 
        # 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 
        # 261, 262, 263]
        # batch1
        # applicant_ids = [237,156,78,120,79]
        # batch2
        # applicant_ids = [111,112,102,263,228,224,227,220,226,223,225,110,222,219,221,218,103,101,109,100,108,99,213,74,94]
        # batch3
        # applicant_ids = [73,212,93,209,92,72,208,56,207,211,217,216,210,215,55,214,95,206,44,43,198,205,48,47,204,46,197]
        # batch4
        # applicant_ids = [42,52,53,54,68,77,80,113,114,125,126,130,131,132,137,239,144,163,240,241,167,32]
        # batch5
        # applicant_ids = [203,202,196,201,200,195,194,45,199,193,186,185,184,183,41,174,173,172,171,146,154,153,152,
        #107,151,106,147,105,104,157,155,182,138,145]
        # batch6
        # applicant_ids = [124,143,123,142,141,122,140,181,139,180,179,178,177,176,148,136,129,135,128,134,127,133,121,
        #175,170,169,119]
        # batch7
        # applicant_ids = [251,168,250,166,165,249,164,248,247,246,162,245,244,161,243,242,160,159,150,149,232,158,
        #231,230,97,51,238,50,
        # 49,236,235,234,233,98,84,91,75,90,83,89,88,87,86,85,82,81,76,118,117,116,115,192,191,190,189,188,
        # 187,229,66,65,64,63,62,61,60,59,58,57,71,70,69,67,257,256,255,254,253,252,262,261,260,259,258]
        # batch8
        # applicant_ids = [232]
        # batch9
        # applicant_ids = [95,227]
        # batch10
        # applicant_ids = [273]
        # batch11
        # applicant_ids = [181,271]
        # batch12
        # applicant_ids = [273,52,274,242,234]
        # batch13
        applicant_ids = [52]
        for each_applicant_id in applicant_ids:
            each_applicant_id = self.env['hr.applicant'].browse(each_applicant_id)
            print("each_applicant_id---",each_applicant_id,each_applicant_id.email_from)
            password = "'$pbkdf2-sha512$25000$Pef8P6f0XsuZ0/q/934PgQ$0uiemDsPZyf/ENm7zFZkx4kP90YX9nvxgTRfgy4Dpj6p1eQ4bFmiPHZaNPo7mU6scwt851CeDolg5JUWwnc1uA'"
            login = "'"+str(each_applicant_id.email_from.lower())+"'"
            self.env.cr.execute("update res_users set password_crypt=%s where login=%s" %(str(password),str(login)))
            self.env.cr.commit()
            ir_model_data = self.env['ir.model.data']
            template_id = ir_model_data.get_object_reference('orient_rms', 'resend_selection_login_email_template_quik_recruitments')[1]
            ress = self.env['mail.template'].browse(template_id).send_mail(each_applicant_id.id, force_send=True)
        return True


    def send_code_generation_mail(self):
        employee_obj = self.env['hr.employee']
        # emp_codes = [9573,9593,9551,9598,9563,9576,9553,9559,9595,9569,9587,9558,9591,9536,9579,9600,9594,9588,9554,9562,9565,9556,9539,9602,9561,9549,9557,9538,9547,9550,9546,9566,9545,9583,9581,9599,9601,9570,9543,9584,9537,9592,9552,9555,9575,9548,9590,9564,9574,9577,9589,9571,9596,9544,9540,9597,9560,9567,9572,9578,9580,9585]
        # emp_codes = [9621,9624,9632,9619,9613,9611,9620,9605,9636,9639,9610,9635,9645,9614,9615,9618,9643,9634,9631,9599,9630,9609,9622,9629,9641,9642,9628,9640,9606,9612,9625,9626,9616,9617,9604,9623,9627,9633,9638]
        emp_codes = []
        for emp_code in emp_codes:
            emp_id = employee_obj.search([('active','=','t'),('emp_code','=',emp_code)])
            if emp_id:
                print("emp_code---",emp_code)
                ir_model_data = self.env['ir.model.data']
                template_id = ir_model_data.get_object_reference('orient_rms', 'employee_code_generation_email_template')[1]
                ress = self.env['mail.template'].browse(template_id).send_mail(emp_id.id, force_send=True)
        return True


    def know_your_emp_code_mailer(self):
        applicant_ids = self.env['hr.applicant'].search([('location','=',288),('state','=','employee_created')]).ids
        for each_applicant_id in applicant_ids:
            each_applicant_id = self.env['hr.applicant'].browse(each_applicant_id)
            if each_applicant_id.emp_id:
                print("---",each_applicant_id.email_from,each_applicant_id.emp_id.emp_code)
                ir_model_data = self.env['ir.model.data']
                template_id = ir_model_data.get_object_reference('orient_rms', 'know_your_emp_code_quik_recruitments')[1]
                ress = self.env['mail.template'].browse(template_id).send_mail(each_applicant_id.id, force_send=True)
        return True


    def correct_direct_recruited_users(self):
        all_users = self.env['res.users'].search([]).ids
        print("all_users",all_users)
        # all_users = self.env['res.users'].search([('id','=',3886)])
        for each_user in all_users:
            each_user = self.env['res.users'].browse(each_user)
            if '.com' in each_user.login or 'admin' in each_user.login or 'co.in' in each_user.login:
                pass
            else:
                print("each_user----------",each_user.login)
                emp_id = self.env['hr.employee'].search([('emp_code','=',each_user.login)])
                if emp_id:
                    if each_user.email:
                        extra_user_id = self.env['res.users'].search([('login','=',each_user.email),('id','!=',each_user.id)])
                        if extra_user_id:
                            print("employee",emp_id.emp_code)
                            print("extra_user_id exists",extra_user_id)
                            # extra_user_id.partner_id.unlink()
                            extra_user_id.unlink()
                            emp_id.write({'user_id':each_user.id})
                            print("employee updated")
                            self.env.cr.commit()
                            all_users.remove(each_user.id)
        return True



class EmployeeConfirmationReport(models.Model):
    _name = "employee.confirmation.report"

    def _get_default_access_token(self):
        return str(uuid.uuid4())

    name = fields.Char('Name',default="Confirmation Due Report")
    due_report_lines = fields.One2many('employee.confirmation.report.lines','report_id', 'Report Lines')
    access_token = fields.Char('Security Token', copy=False,default=_get_default_access_token)

    @api.model_cr_context
    def _init_column(self, column_name):
        """ Initialize the value of the given column for existing rows.

            Overridden here because we need to generate different access tokens
            and by default _init_column calls the default method once and applies
            it for every record.
        """
        if column_name != 'access_token':
            super(EmployeeConfirmationReport, self)._init_column(column_name)
        else:
            query = """UPDATE %(table_name)s
                          SET %(column_name)s = md5(md5(random()::varchar || id::varchar) || clock_timestamp()::varchar)::uuid::varchar
                        WHERE %(column_name)s IS NULL
                    """ % {'table_name': self._table, 'column_name': column_name}
            self.env.cr.execute(query)

    def _generate_access_token(self):
        for invoice in self:
            invoice.access_token = self._get_default_access_token()


    def get_confirmation_due_report(self):
        res = False
        today = datetime.today()
        today = str(datetime.now().date())
        employee_obj = self.env['hr.employee']
        emp_ids = employee_obj.search([('active','=','t'),('position_type','=','probation')])
        self.env.cr.execute("delete from employee_confirmation_report_lines")
        if emp_ids:
            for each_emp_id in emp_ids:
                if each_emp_id.joining_date and each_emp_id.department_id.name not in ('FM','FM Backup'):
                    join_date = each_emp_id.joining_date
                    six_monthsss = datetime.strptime(join_date, '%Y-%m-%d')
                    later = six_monthsss + relativedelta(months=6)
                    confirmation_date = later.date()
                    if str(confirmation_date) <= str(today):
                        print ('xxxxxxxxxxxxx')
                        print(join_date, confirmation_date,'six_monthsss')
                        self.env['employee.confirmation.report.lines'].create({'emp_id':each_emp_id.id,
                        'emp_code':each_emp_id.emp_code,'joining_date':each_emp_id.joining_date,
                        'confirmation_date':confirmation_date,'location':each_emp_id.site_master_id.id,'report_id':self.id,'department':each_emp_id.department_id.id,'reporting_manager':each_emp_id.parent_id.id})
            return {
            'type': 'ir.actions.act_url',
            'url': '/web/pivot/confirmation_due_export_xls/%s?access_token=%s' % (self.id, self.access_token),
            'target': 'new',
            }

                # print (joining_date,'six_months')

class EmployeeConfirmationReportLines(models.Model):
    _name = "employee.confirmation.report.lines"

    report_id = fields.Many2one('employee.confirmation.report','Report Id')
    emp_code = fields.Char('Employee Code')
    emp_id = fields.Many2one('hr.employee','Employee')
    joining_date = fields.Date('Joining Date')
    confirmation_date = fields.Date('Confirmation Date')
    location =  fields.Many2one('site.master','Location')
    department = fields.Many2one('hr.department','Department')
    reporting_manager = fields.Many2one('hr.employee','Reporting To')


class City(models.Model):
    _name = "res.city"
    _order = "name asc"

    name = fields.Char('Site Location')
    active = fields.Boolean('Active',default=True)

class EmployeeConfirmation(models.Model):
    _name = "employee.confirmation"

    name =  fields.Char('Name',default="Employee Confirmation")
    employee_code = fields.Char('Employee Code')
    employee_id = fields.Many2one('hr.employee','Employee')
    joining_date = fields.Date('Joining Date')
    state = fields.Selection([('probation','Probation'),('confirm','Permanent'),('on_hold','On Hold')])
    reporting_manager = fields.Many2one('hr.employee','Reporting To')
    designation = fields.Many2one('hr.job','Designation')
    department = fields.Many2one('hr.department','Department')
    confirmation_date = fields.Date('Confirmation Date')
    company_id = fields.Many2one('res.company',default=1)

    @api.multi
    def employee_confirmation(self):
        for rec in self:
            template_id = self.env.ref('orient_employee_self_service_portal.email_template_for_employee_confirmation', False)
            self.env['mail.template'].browse(template_id.id).send_mail(rec.id, force_send=True)
            rec.state = 'confirm'
            employee_id = rec.employee_id
            employee_id.write({'position_type':'confirm','confirmation_date':rec.confirmation_date})
            return True

    @api.multi
    def employee_confirmation_on_hold(self):
        for rec in self:
            self.write({'state':'on_hold'})
            return True