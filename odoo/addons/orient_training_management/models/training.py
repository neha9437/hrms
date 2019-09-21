from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import xlsxwriter
try:
    import xlwt
except ImportError:
    xlwt = None
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)
import xlsxwriter as xls
# import cStringIO
import os
import base64, urllib
from io import StringIO,BytesIO
import uuid
from dateutil.relativedelta import relativedelta
from lxml import etree
from openerp.osv.orm import setup_modifiers

class TrainingName(models.Model):
    _name = "training.name"


    name = fields.Many2one('hr.employee','Trainer Name')
    highest_qualification = fields.Char('Qualification')
    mobile_phone = fields.Char('Mobile Number')
    active = fields.Boolean('Active', default=True)
    work_email = fields.Char('Work Email')
    facilitator = fields.Char('Facilitator')
    select = fields.Boolean('Select', default=False)

    @api.onchange('name')
    def onchange_name(self):
        if self.name:
            name = self.name.id
            print(name,'**********')
            self.highest_qualification = self.name.highest_qualification
            self.mobile_phone = self.name.mobile_phone
            self.work_email= self.name.work_email
        else:
            pass

class TrainingType(models.Model):
    _name = "training.type"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Training Type')
    select = fields.Boolean('Select', default=False)
    active = fields.Boolean('Active', default=True)

class TrainingLocation(models.Model):
    _name = "training.location"

    name = fields.Char('Training Location')
    address = fields.Text('Address')
    select = fields.Boolean('Select', default=False)
    active = fields.Boolean('Active', default=True)

class TrainingMaster(models.Model):
    _name = "training.master"


    company_id = fields.Many2one('res.company','Company', default=lambda self: self.env['res.company']._company_default_get('account.invoice'))
    location = fields.Many2one('training.location','Location')
    financial_year = fields.Many2one('year.master','Financial Year')
    month = fields.Selection([('January', 'January'),('February', 'February'),
                                ('March', 'March'),('April', 'April'),
                                ('May', 'May'),('June','June'),
                                ('July','July'),('August','August'),
                                ('September','September'),('October','October'),
                                ('November','November'),('December','December')],default='January',string='Month')
    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    trainer_name = fields.Many2one('training.name','Trainer Name')
    budget = fields.Float('Budget')
    training_type = fields.Many2one('training.type','Training Type')
    supervisor = fields.Many2one('hr.employee')
    site_location = fields.Many2one('site.master','Location')
    # department = fields.Many2one('hr.department','Department')
    department_id = fields.Many2many('hr.department','request_department_rel','department_training_rel','request_department_id', string="Department")
    employee = fields.Many2many('hr.employee','training_emp_rel','employee_training_rel','training_emp_id',string='Employee')
    # application_year = fields.Many2one('year.master.annual','Year')
    state = fields.Selection([('new','New'),('complete','Completed')], default='new',string="Status")
    name = fields.Char('Training Name')
    training_id = fields.Many2one('training.request','')
    main_user_id = fields.Many2one('res.users')
    employee_details_master = fields.One2many('training.master.child','master_id','Employee Details')
    training_comp_date = fields.Date('Training Completed On')


    def get_partner_ids(self, cr, uid, user_ids) :
        return str([emp.id for emp in employee]).replace('[', '').replace(']', '') 


# class TrainingMaster(models.Model):
#     _inherit = ['training.master']

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(TrainingMaster, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        uid = self._context.get('uid')
        doc = etree.XML(res['arch'])
        temp_var = []
        user_data = self.env['res.users'].browse(uid)
        if uid and uid != 1:
            self.env.cr.execute("select name from res_groups where id in (select gid from res_groups_users_rel where uid ="+str(uid)+" and name ilike '%Portal User%')")
            temp_var = self.env.cr.fetchall()
            if temp_var:
                raise UserError(_('Sorry, You are not allowed to access these documents!'))
            if user_data.password_reset == False:
                raise UserError(_('YOU HAVE NOT CHANGED YOUR PASSWORD YET ! \n'
                                  'Please click on your username on upper right hand corner, click on "change password" and follow the instructions. You wont be able to continue using the system unless you change your current default password.'))       
        return res

    @api.multi
    def training_completed(self):
        feedback_type = self.env['feedback.type']
        feedback_type_line = self.env['feedback.type.line']
        feedback_type_template = self.env['feedback.type.template']
        feedback_type_template_line = self.env['feedback.type.template.line']

        effective_type = self.env['effective.type']
        effective_type_line = self.env['effective.type.line']
        effective_type_template = self.env['effective.type.template']
        effective_type_template_line = self.env['effective.type.template.line']

        to_date = self.to_date
        approved_to_date = datetime.strptime(to_date, "%Y-%m-%d")+relativedelta(days=30)

        for each in self.employee_details_master:
            print(each,'===')

            ft = feedback_type.create({'name':'Training FeedBack for Employee : ' + each.employee.name + ' against ' + self.name + ' training', 'state':'new','employee':each.employee.id,'training':self.id})
            print(ft,'fttttttttttt')
            ftt = feedback_type_template.search([('id','>',0)])
            for i in ftt:
                for line in i.template_line:
                    print(line,'lineeeeeeeeeeee')
                    feedback_type_line.create({'feedback_id':ft.id,'category':i.id,'name':line.name})           

            # effective for employee
            et = effective_type.create({'name': 'Training Effective for Employee : '+ each.employee.name + ' against ' + self.name + ' training','state':'new','employee':each.employee.id,'training':self.id,'date':approved_to_date})
            ett = effective_type_template.search([('id','>',0)])
            for e in ett:
                effective_type_line.create({'name':e.name,'effective_id':et.id})

            # effective for reporting manager of employee
            etr = effective_type.create({'name': 'Training Effective for Employee : '+ each.employee.name + ' against ' + self.name + ' training','state':'new','employee':each.employee.parent_id.id,'training':self.id,'date':approved_to_date})
            ettr = effective_type_template.search([('id','>',0)])
            for er in ettr:
                effective_type_line.create({'name':er.name,'effective_id':etr.id})

            self.write({'state':'complete','training_comp_date':datetime.now().date()})

            template_id = self.env.ref('orient_training_management.email_template_feedback_form', False)
            print(template_id,each.id,'======template_id')
            self.env['mail.template'].browse(template_id.id).send_mail(each.employee.id, force_send=True)
        return True

    def training_mail_reminder(self):
        """Sending reminder mail for exit interview and for asset collection of an employee"""
        match = self.search([('state','=','new')])
        for rec in match:
            to_date = datetime.strptime(rec.to_date, "%Y-%m-%d").date()
            date_now = datetime.now().date()
            prior_to_date = to_date - timedelta(days=2)
            previous_to_date = to_date - timedelta(days=1)
            if date_now == prior_to_date:
                template_id = self.env.ref('orient_training_management.reminder_email_training_mail_template', False)
                self.env['mail.template'].browse(template_id.id).send_mail(rec.id, force_send=True)
            if date_now == to_date:
                template_id = self.env.ref('orient_training_management.reminder_email_training_mail_template', False)
                self.env['mail.template'].browse(template_id.id).send_mail(rec.id, force_send=True)
            if date_now == previous_to_date:
                template_id = self.env.ref('orient_training_management.reminder_email_training_mail_template', False)
                self.env['mail.template'].browse(template_id.id).send_mail(rec.id, force_send=True)
       


    @api.multi
    def send_mail_training(self):
        # if self.employee:
        training_details= ''
        training_date = ''
        trainer_name =''
        for each in self.employee_details_master:
            template_id = self.env.ref('orient_training_management.email_training_mail_template', False)
            print(template_id,each.id,'======template_id')
            web_url = self.env['ir.config_parameter'].sudo().search([('key','=','web.base.url')])
            web_link = web_url.value

            training_name = self.name
            training_details = self.location.name
            training_date = self.from_date
            trainer_name = self.trainer_name.name.name

            web_link = web_link + '#id=%s&view_type=form&model=training.master' %(self.id)
            print(web_link,'web_link')
            context = ({'link':web_link,'training_name':training_name,'training_details':training_details,'training_date':training_date,'trainer_name':trainer_name})
            print(context,'******')
            self.env['mail.template'].browse(template_id.id).with_context(context).send_mail(each.employee.id, force_send=True)
        return True
        #   self.env.cr.execute('SELECT training_emp_id from training_emp_rel where employee_training_rel= %s' % self.id)
        #   result = self.env.cr.fetchall()
        #   list_val = [o[0] for o in result]
        #   self.env.cr.execute('SELECT user_id from resource_resource where id in (select resource_id from hr_employee where id in %s)',(tuple(list_val),))
        #   user_id = self.env.cr.fetchall()
        #   user_id_val = [i[0] for i in user_id]
        #   self.env.cr.execute('SELECT partner_id from res_users where id in %s',(tuple(user_id_val),))
        #   partner_ids_val = self.env.cr.fetchall()
        #   partner_id_list = [p[0] for p in partner_ids_val]
        #   self.env.cr.execute('SELECT id from ir_mail_server limit 1')
        #   mail_server = self.env.cr.fetchall()
        #   schedule_name = 'Training Scheduled from'+str(self.from_date)+' to '+str(self.to_date)+'. Please Kindly check the HRMS portal.'
        #   mail_server_id = [t[0] for t in mail_server]
        #   mail_compose_message = self.env['mail.compose.message'].create({'composition_mode':'mass_mail','subject':str(schedule_name),'mail_server_id':mail_server_id[0]})
        #   for t in partner_id_list:
        #       self.env.cr.execute('INSERT into mail_compose_message_res_partner_rel(wizard_id,partner_id) values(%s,%s)' % (mail_compose_message.id,t))
        #       self.env.cr.commit()
        # compose_form = self.env.ref('orient_training_management.view_training_mail_wizard_form', False)
        # ctx = dict(
        #   default_model='training.master',
        #   default_res_id=self.id,
        #   default_use_template=True,
        #   default_template_id= False,
        #   default_composition_mode='mass_mail',
        #   mark_invoice_as_sent=True,
        #   custom_layout='',
        #   force_email=True
        # )
        # return {
        #   'name': _('Compose Email'),
        #   'type': 'ir.actions.act_window',
        #   'view_type': 'form',
        #   'view_mode': 'form',
        #   'res_model': 'training.mail.wizard',
        #   # 'res_id':self.id,
        #   # 'views': [(compose_form.id, 'form')],
        #   # 'view_id': compose_form.id,
        #   'target': 'new',
        # }

class TrainingMasterChild(models.Model):
    _name = "training.master.child"

    master_id = fields.Many2one('training.master','')
    employee = fields.Many2one('hr.employee','Employee Name')
    emp_code = fields.Char('Employee Code')
    designation = fields.Many2one('hr.job','Designation')
    department_id = fields.Many2one('hr.department','Department')
    site = fields.Many2one('site.master','Site')

    @api.onchange('employee')
    def onchange_employee_master_details(self):
        res = {}
        if not self.employee or not self.employee:
            return
        else:
            self.emp_code = self.employee.emp_code
            self.designation = self.employee.job_id.id
            self.department_id = self.employee.department_id.id
            self.site = self.employee.site_master_id.id

class TrainingRequest(models.Model):
    _name = "training.request"
    # _inherit = ['ir.needaction_mixin']


    name = fields.Char('Training Name')
    # department = fields.Many2one('hr.department','Department')
    training_type = fields.Many2one('training.type','Training Type')
    department_id = fields.Many2many('hr.department','request_dep_rel','dep_training_rel','request_dep_id', string="Department")
    employee = fields.Many2many('hr.employee','request_emp_rel','emp_training_rel','request_emp_id', string="Employee")
    state = fields.Selection([('new','New'),('approved','Approved'),('reject','Rejected'),('postpone','Postponed'),('created','Training Completed')], string="Status", default="new")
    purpose = fields.Text("Purpose of Training")
    requested_by = fields.Many2one('hr.employee','Requested By',default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1))
    employee_details = fields.One2many('training.request.child','request_id','Employees')


    @api.model
    def _needaction_domain_get(self):
        domain = [('state','=','new')]
        return domain

    @api.multi
    def training_approved(self):
        for each in self.employee_details:
            if not each.employee:
                raise ValidationError(_("Kindly add attendees!"))
        self.state = 'approved'
        return True

    @api.multi
    def training_reject(self):
        self.state = 'reject'
        return True

    @api.multi
    def training_postpone(self):
        self.state = 'postpone'
        return True

    @api.multi
    def create_training(self):
        emp_training_rel = request_emp_id = ''
        name = self.name
        # department = self.department.id
        training_type = self.training_type.id

        create_id = None
        check_record = self.env['training.master'].search([('training_id','=',self.id),('training_type','=',training_type)])

        if check_record:
            create_id = check_record.id
        else:
            create_id = self.env['training.master'].create({'name':name,
                                                            # 'department':department,
                                                            'main_user_id': self.env.uid,
                                                            'training_type':training_type,
                                                            'training_id':self.id}).id

        if create_id:
            for each in self.employee_details:
                print(each,'each')
                self.env['training.master.child'].create({
                                        'master_id':create_id,
                                        'employee':each.employee.id,
                                        'emp_code':each.emp_code,
                                        'designation':each.designation.id,
                                        'department_id':each.department_id.id,
                                        'site':each.site.id
                    })

        self.write({'state':'created'})

        training_form = self.env.ref('orient_training_management.view_trainingmaster_form', False)
        return {
            'name': _('Training Master'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'training.master',
            'res_id': create_id,
            'views': [(training_form.id, 'form')],
            'view_id': self.id,
            'target': 'current',
        }


class TrainingRequestChild(models.Model):
    _name = "training.request.child"

    request_id = fields.Many2one('training.request','')
    employee = fields.Many2one('hr.employee','Employee Name')
    emp_code = fields.Char('Employee Code')
    designation = fields.Many2one('hr.job','Designation')
    department_id = fields.Many2one('hr.department','Department')
    site = fields.Many2one('site.master','Site')

    @api.onchange('employee')
    def onchange_employee_details(self):
        res = {}
        if not self.employee or not self.employee:
            return
        else:
            self.emp_code = self.employee.emp_code
            self.designation = self.employee.job_id.id
            self.department_id = self.employee.department_id.id
            self.site = self.employee.site_master_id.id

class FeedBackTypeTemplate(models.Model):

    _name = "feedback.type.template"
    _description = "FeedBack Type Template"

    name = fields.Char(string="Name", required=True)
    template_line = fields.One2many('feedback.type.template.line', 'template_id', string='', auto_join=True)
    active = fields.Boolean('Active', default=True)
    category = fields.Many2one('feedback.type.template','FT template')

class FeedBackTemplateChild(models.Model):
    _name = "feedback.type.template.line"
    _description = "FeedBack Type Template Child"

    name = fields.Char(string='', required=True)
    template_id = fields.Many2one('feedback.type.template', string='', ondelete='cascade', index=True, copy=False)



class EffectiveTypeTemplate(models.Model):

    _name = "effective.type.template"
    _description = "Effective Type Template"

    name = fields.Char(string="Name", required=True)
    effective_template_line = fields.One2many('effective.type.template.line', 'effective_template_id', string='', auto_join=True)
    active = fields.Boolean('Active', default=True)

class EffectiveTemplateChild(models.Model):
    _name = "effective.type.template.line"
    _description = "Effective Type Template Child"

    name = fields.Char(string='', required=True)
    effective_template_id = fields.Many2one('effective.type.template', string='', ondelete='cascade', index=True, copy=False)


class FeedBackTypeList(models.Model):

    _name = "feedback.type"
    _description = "FeedBack Type List"

    name = fields.Char(string="Template Name", required=True)
    feedback_line = fields.One2many('feedback.type.line', 'feedback_id', string='', auto_join=True)
    state = fields.Selection([('new', 'New'), ('done', 'Done')], string='Status', default='new')
    employee = fields.Many2one('hr.employee','Employee')
    training = fields.Many2one('training.master','Training')


    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(FeedBackTypeList, self).fields_view_get(
        view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        uid = self._context.get('uid')
        doc = etree.XML(res['arch'])
        temp_var = []
        user_data = self.env['res.users'].browse(uid)
        if uid and uid != 1:
            self.env.cr.execute("select name from res_groups where id in (select gid from res_groups_users_rel where uid ="+str(uid)+" and name ilike '%Portal User%')")
            temp_var = self.env.cr.fetchall()
            if temp_var:
                raise UserError(_('Sorry, You are not allowed to access these documents!'))
            if user_data.password_reset == False:
                raise UserError(_('YOU HAVE NOT CHANGED YOUR PASSWORD YET ! \n'
                                  'Please click on your username on upper right hand corner, click on "change password" and follow the instructions. You wont be able to continue using the system unless you change your current default password.'))       
        return res


    @api.multi
    def submit(self):
        for each in self:
            for line_id in self.feedback_line:
                poor = line_id.poor
                bad = line_id.bad
                satisfactory = line_id.satisfactory
                very_good = line_id.very_good
                excellent =line_id.excellent
                if not poor and not bad and not satisfactory and not very_good and not excellent:
                    raise ValidationError(_('Please Select atleast one option for the points given below'))
            each.state = 'done'
        return True


class FeedBackTypeListChild(models.Model):
    _name = "feedback.type.line"
    _description = "FeedBack Type Line"

    name = fields.Char(string='', required=True)
    # comments = fields.Text(string="Comments", help='Specify answer of the question')
    feedback_id = fields.Many2one('feedback.type', string='', ondelete='cascade', index=True, copy=False)
    poor = fields.Boolean('Poor', default=False)
    bad = fields.Boolean('Bad', default=False)
    satisfactory = fields.Boolean('Satisfactory', default=False)
    very_good = fields.Boolean('Good', default=False)
    excellent = fields.Boolean('Excellent', default=False)
    category = fields.Many2one('feedback.type.template','Category')


    @api.onchange('poor')
    def onchange_poor(self):
        if self.poor:
            self.bad = False
            self.satisfactory = False
            self.very_good= False
            self.excellent = False


    @api.onchange('bad')
    def onchange_bad(self):
        if self.bad:
            self.poor = False
            self.satisfactory = False
            self.very_good= False
            self.excellent = False

    @api.onchange('satisfactory')
    def onchange_satisfactory(self):
        if self.satisfactory:
            self.poor = False
            self.bad = False
            self.very_good= False
            self.excellent = False

    @api.onchange('very_good')
    def onchange_very_good(self):
        if self.very_good:
            self.poor = False
            self.bad = False
            self.satisfactory= False
            self.excellent = False

    @api.onchange('excellent')
    def onchange_excellent(self):
        if self.excellent:
            self.poor = False
            self.bad = False
            self.satisfactory= False
            self.very_good = False


class EffectiveTypeList(models.Model):

    _name = "effective.type"
    _description = "Effective Type List"

    name = fields.Char(string="Template Name", required=True)
    effective_line = fields.One2many('effective.type.line', 'effective_id', string='', auto_join=True)
    state = fields.Selection([('new', 'New'), ('done', 'Done')], string='Status', default='new')
    employee = fields.Many2one('hr.employee','Employee')
    training = fields.Many2one('training.master','Training')
    date = fields.Date('Date')


    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(EffectiveTypeList, self).fields_view_get(
        view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        uid = self._context.get('uid')
        doc = etree.XML(res['arch'])
        temp_var = []
        user_data = self.env['res.users'].browse(uid)
        if uid and uid != 1:
            self.env.cr.execute("select name from res_groups where id in (select gid from res_groups_users_rel where uid ="+str(uid)+" and name ilike '%Portal User%')")
            temp_var = self.env.cr.fetchall()
            if temp_var:
                raise UserError(_('Sorry, You are not allowed to access these documents!'))
            if user_data.password_reset == False:
                raise UserError(_('YOU HAVE NOT CHANGED YOUR PASSWORD YET ! \n'
                                  'Please click on your username on upper right hand corner, click on "change password" and follow the instructions. You wont be able to continue using the system unless you change your current default password.'))       
        return res

    @api.multi
    def submit(self):
        for each in self:
            for line_id in self.effective_line:
                poor = line_id.poor
                bad = line_id.bad
                satisfactory = line_id.satisfactory
                very_good = line_id.very_good
                excellent =line_id.excellent
                if not poor and not bad and not satisfactory and not very_good and not excellent:
                    raise ValidationError(_('Please Select atleast one option for the points given below'))
            each.state = 'done'
        return True
    
class EffectiveTypeListChild(models.Model):
    _name = "effective.type.line"
    _description = "Effective Type Line"

    name = fields.Char(string='', required=True)
    # comments = fields.Text(string="Comments", help='Specify answer of the question')
    effective_id = fields.Many2one('effective.type', string='', ondelete='cascade', index=True, copy=False)
    poor = fields.Boolean('Poor', default=False)
    bad = fields.Boolean('Bad', default=False)
    satisfactory = fields.Boolean('Satisfactory', default=False)
    very_good = fields.Boolean('Good', default=False)
    excellent = fields.Boolean('Excellent', default=False)


    @api.onchange('poor')
    def onchange_poor(self):
        if self.poor:
            self.bad = False
            self.satisfactory = False
            self.very_good= False
            self.excellent = False


    @api.onchange('bad')
    def onchange_bad(self):
        if self.bad:
            self.poor = False
            self.satisfactory = False
            self.very_good= False
            self.excellent = False

    @api.onchange('satisfactory')
    def onchange_satisfactory(self):
        if self.satisfactory:
            self.poor = False
            self.bad = False
            self.very_good= False
            self.excellent = False

    @api.onchange('very_good')
    def onchange_very_good(self):
        if self.very_good:
            self.poor = False
            self.bad = False
            self.satisfactory= False
            self.excellent = False

    @api.onchange('excellent')
    def onchange_excellent(self):
        if self.excellent:
            self.poor = False
            self.bad = False
            self.satisfactory= False
            self.very_good = False

class TrainingExcel(models.Model):
    _name = "training.excel"


    def _get_default_access_token(self):
        return str(uuid.uuid4())

    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    # financial_year = fields.Many2one('year.master','Financial Year')
    access_token = fields.Char('Security Token', copy=False,default=_get_default_access_token)
    training_one2many = fields.One2many('training.child','training','Training Details')

    def training_details(self):
        from_date = self.from_date
        to_date = self.to_date
        print(from_date,to_date,'%%%%%%%%33333333333333333333333%%')

        if self.training_one2many:
            for i in self.training_one2many:
                i.unlink()

        training_data = self.env['training.master'].search([('from_date','>=',from_date),('to_date','<=',to_date)])
        print(training_data,'&&&&&&7')
        if training_data:
            for x in training_data:
                print(x)
                self.env['training.child'].create({'training_id':x.id,
                                                    'training':self.id,
                                                    })
        else:
            raise ValidationError(_('No records found!!!'))
        # ssss
        return True

    @api.multi
    def export_training_xls(self,access_uid=None):
        self.training_details()
        self.ensure_one()
        return {
        'type': 'ir.actions.act_url',
        'url': '/web/pivot/export_training_xls/%s?access_token=%s' % (self.id, self.access_token),
        'target': 'new',
        }

class TrainingChild(models.Model):
    _name = "training.child"

    training_id = fields.Many2one('training.master','Training')
    training = fields.Many2one('training.excel','ID')
