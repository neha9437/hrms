# -*- coding: utf-8 -*-
import datetime
from datetime import datetime, timedelta, date
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
date_format = "%Y-%m-%d"
from odoo import models, api
from lxml import etree
import simplejson
from odoo.osv.orm import setup_modifiers
from dateutil.relativedelta import relativedelta
import calendar
import uuid
from odoo.exceptions import UserError, AccessError, ValidationError
import base64
import os
from odoo.tools.translate import _
import re
from odoo import api, fields, models, tools, _



def date_by_adding_business_days(self, from_date, add_days):
    business_days_to_add = add_days
    current_date = from_date
    while business_days_to_add > 0:
        current_date = current_date + timedelta(days=1)
        holiday_master = self.env['holiday.master'].search([('holiday_date','=',current_date)])
        if holiday_master:
            print (current_date)
            # business_days_to_add += 1
            weekday = current_date.weekday()
            print (weekday,'ppppppp')
            if weekday >= 5: # sunday = 6
                continue
        else:
            weekday = current_date.weekday()
            if weekday >= 5: # sunday = 6
                continue
            business_days_to_add -= 1
    return current_date

class HrResignation(models.Model):
    _name = 'hr.resignation'
    _inherit = ['mail.thread']
    _rec_name = 'employee_id'

    def _get_employee_id(self):
        # assigning the related employee of the logged in user
        employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        return employee_rec.id

    def _get_manager_id(self):
        # assigning the related employee of the logged in user
        hr_position = self.env['hr.job'].search([('hr_manager_bool', '=', True)], limit=1)
        employee_manager = self.env['hr.employee'].search([('job_id', '=',hr_position.id)], limit=1)
        return employee_manager.id

    def _get_reporting_manager_id(self):
        # assigning the related employee of the logged in user
        employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        manager_id = employee_rec.parent_id.id
        return manager_id

    def _get_joining_date(self):
        # assigning the related employee of the logged in user
        employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        return employee_rec.joining_date

    def _get_notice_period(self):
        employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        # print(employee_rec,'-----------')
        cur_date = str(datetime.now().date())
        resignation_type = self.resignation_type
        for rec in employee_rec:
            if str(rec.department_id.name) != 'FM':
                if rec.position_type == 'probation':
                    grade_id = rec.grade_id
                    notice_period = int(grade_id.notice_period) -1
                    approved_relieving_date = datetime.strptime(cur_date, "%Y-%m-%d")+relativedelta(days=notice_period)
                    rec.approved_relieving_date =approved_relieving_date
                    rec.notice_period =int(grade_id.notice_period)
                else:
                    grade_id = rec.grade_id
                    notice_period = int(grade_id.notice_period_after_confirmation) -1
                    print(grade_id,notice_period)
                    approved_relieving_date = datetime.strptime(cur_date, "%Y-%m-%d")+relativedelta(days=notice_period)
                    rec.approved_relieving_date =approved_relieving_date
                    rec.notice_period =int(grade_id.notice_period_after_confirmation)
                print(grade_id,notice_period,rec.approved_relieving_date,rec.notice_period)
            else:
                if rec.department_id:
                    if rec.position_type == 'probation':
                        notice_period = 29
                        approved_relieving_date = datetime.strptime(cur_date, "%Y-%m-%d")+relativedelta(days=notice_period)
                        rec.approved_relieving_date =approved_relieving_date
                        rec.notice_period =notice_period+1
                    else:
                        notice_period = 60
                        approved_relieving_date = datetime.strptime(cur_date, "%Y-%m-%d")+relativedelta(days=notice_period)
                        rec.approved_relieving_date = approved_relieving_date
                        rec.notice_period =notice_period
        if resignation_type:
            if resignation_type.allow_exit_process == False:
                rec.notice_period = 0
                rec.approved_relieving_date = cur_date
        return rec.notice_period


    def _get_relieving_date(self):
        employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        cur_date = str(datetime.now().date())
        resignation_type = self.resignation_type
        for rec in employee_rec:
            notice_period = 30
            if str(rec.department_id.name) != 'FM':
                if rec.position_type == 'probation':
                    grade_id = rec.grade_id
                    notice_period = int(grade_id.notice_period) -1
                    if notice_period <= 0:
                        notice_period = 30
                    approved_relieving_date = datetime.strptime(cur_date, "%Y-%m-%d")+relativedelta(days=notice_period)
                    # rec.approved_relieving_date =approved_relieving_date
                else:
                    grade_id = rec.grade_id
                    notice_period = int(grade_id.notice_period_after_confirmation) -1
                    if notice_period <= 0:
                        notice_period = 30
                    approved_relieving_date = datetime.strptime(cur_date, "%Y-%m-%d")+relativedelta(days=notice_period)
                    # rec.approved_relieving_date =approved_relieving_date                                                  
            else:
                if rec.department_id:
                    if rec.position_type == 'probation':
                        notice_period = 29
                        approved_relieving_date = datetime.strptime(cur_date, "%Y-%m-%d")+relativedelta(days=notice_period)
                        # rec.approved_relieving_date =approved_relieving_date
                    else:
                        notice_period = 60
                        approved_relieving_date = datetime.strptime(cur_date, "%Y-%m-%d")+relativedelta(days=notice_period)
                        # rec.approved_relieving_date =approved_relieving_date
            count=0
            new_approved_relieving_date = approved_relieving_date
            for a in range(10):
                h_day = calendar.day_name[new_approved_relieving_date.weekday()]
                if count ==0:
                    if h_day == 'Sunday':
                        new_approved_relieving_date = datetime.strptime(str(new_approved_relieving_date), "%Y-%m-%d %H:%M:%S")-relativedelta(days=2)
                    if h_day == 'Saturday':
                        new_approved_relieving_date = datetime.strptime(str(new_approved_relieving_date), "%Y-%m-%d %H:%M:%S")-relativedelta(days=1)
                    holiday_master = self.env['holiday.master'].search([('holiday_date','=',new_approved_relieving_date)])
                    if holiday_master:
                        new_approved_relieving_date = datetime.strptime(str(new_approved_relieving_date), "%Y-%m-%d %H:%M:%S")-timedelta(days=1)
                    else:
                        rec.approved_relieving_date = new_approved_relieving_date
                        count+=1
        if resignation_type:
            if resignation_type.allow_exit_process == False:
                rec.approved_relieving_date = cur_date         
        return rec.approved_relieving_date


    def _get_grade(self):
        employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        cur_date = str(datetime.now().date())
        for rec in employee_rec:
            if str(rec.department_id.name) != 'FM':
                if rec.position_type == 'probation':
                    grade_id = rec.grade_id
                else:
                    grade_id = rec.grade_id
            else:
                if rec.department_id:
                    if rec.position_type == 'probation':
                        grade_id = rec.grade_id
                    else:
                        grade_id = rec.grade_id
        return grade_id

          

    name = fields.Char(string='Reference Number', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    employee_id = fields.Many2one('hr.employee', string="Employee", default=_get_employee_id,
                                  help='Name of the employee for whom the request is creating')
    hr_manager_id = fields.Many2one('hr.employee', string="HR Manager", default=_get_manager_id,
                                  help='Name of the HR Manager')
    reporting_manager_id = fields.Many2one('hr.employee', string="Reporting Manager", default=_get_reporting_manager_id,
                                  help='Name of the Reporting Manager')
    department_id = fields.Many2one('hr.department', string="Department", related='employee_id.department_id',
                                    help='Department of the employee')
    joined_date = fields.Date(string="Join Date", required=True, default=_get_joining_date,
                              help='Joining date of the employee')
    expected_relieving_date = fields.Date(string="Resignation Date", required=True, default=str(datetime.now()),
                                          help='Date on which he is relieving from the company')
    resign_confirm_date = fields.Date(string="Resign confirm date", help='Date on which the request is confirmed')
    approved_relieving_date = fields.Date(string="Last Working Date",default=_get_relieving_date, help='The date approved for the relieving')
    reason = fields.Text(string="Reason", help='Specify reason for leaving the company')
    notice_period = fields.Char(string="Notice Period", compute='_notice_period',  default=_get_notice_period)
    # notice_period1 = fields.Char(string="Notice Period", default=_get_notice_period)
    state = fields.Selection([('draft', 'Draft'), 
                            ('confirm', 'Manager Approval'), 
                            ('approved', 'HR Approval'), 
                            ('resignation_accepted','Resignation Accepted'), 
                            ('cancel', 'Cancel'),
                            ('rejected','Rejected'),
                            ('resignation_revoked','Resignation Revoked')],
                             string='Status', default='draft')
    resignation_type = fields.Many2one('hr.employee.resignation.type',string='Resignation Type',help='Name of Resignation Type')
    allow_exit_process = fields.Boolean('Allow Exit Process', default=False)
    reason_resignation = fields.Many2one('reason.resignation','Reason Resignation')
    reason_process = fields.Boolean('Reason', default=False)
    grade = fields.Many2one('hr.employee.grade','Grade',default=_get_grade)
    button_check = fields.Boolean('button_check', compute='_get_user')

    def _get_user(self):
        button_bool = False
        employee= self.employee_id.user_id.id
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        if res_user.has_group('hr.group_hr_manager') or res_user.has_group('hr.group_hr_user') or res_user.has_group('orient_hr_resignation.group_reporting_manager'):
            if employee == self._uid:
                button_bool = True
                self.button_check = button_bool
            else:
                if self.employee_id.parent_id.user_id.id == self._uid:
                    self.button_check = button_bool
                else:
                    self.button_check = button_bool


    @api.onchange('employee_id')
    def set_join_date(self):
        self.joined_date = self.employee_id.joining_date if self.employee_id.joining_date else ''

    @api.model
    def create(self, vals):
        # assigning the sequence for the record
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.resignation') or _('New')
        vals.update({'expected_relieving_date':datetime.now()})
        res = super(HrResignation, self).create(vals)
        return res

    @api.onchange('reason_resignation')
    def _onchange_reason_resignation(self):
        if self.reason_resignation:
            comments = self.reason_resignation.comments
            if comments == True:
                self.reason_process = True
            else:
                self.reason_process = False

    @api.onchange('resignation_type')
    def _onchange_resignation_type(self):
        self.allow_exit_process = self.resignation_type.allow_exit_process
        if self.resignation_type:
            if self.resignation_type.allow_exit_process == False:
                self.employee_id = ''
                self.department_id = ''
                self.joined_date = ''
        else:
            self.allow_exit_process = True


    @api.constrains('employee_id')
    def check_employee(self):
        # Checking whether the user is creating leave request of his/her own
        for rec in self:
            if not self.env.user.has_group('hr.group_hr_user'):
                if rec.employee_id.user_id.id and rec.employee_id.user_id.id != self.env.uid:
                    pass
                    # raise ValidationError(_('You cannot create request for other employees'))

    @api.onchange('employee_id')
    @api.depends('employee_id')
    def check_request_existence(self):
        # Check whether any resignation request already exists
        for rec in self:
            if rec.employee_id:
                if rec.resignation_type:
                    if rec.resignation_type.allow_exit_process == False:
                        rec.reporting_manager_id =rec.employee_id.parent_id.id
                        rec.grade = rec.employee_id.grade_id.id
                        rec.approved_relieving_date = rec.expected_relieving_date
                resignation_request = self.env['hr.resignation'].search([('employee_id', '=', rec.employee_id.id),
                                                                         ('state', 'in', ['confirm', 'approved'])])
                if resignation_request:
                    raise ValidationError(_('There is a resignation request in confirmed or'
                                            ' approved state for this employee already !'))

    @api.multi
    def _notice_period(self):
        # calculating the notice period for the employee
        for rec in self:
            if rec.approved_relieving_date and rec.resign_confirm_date:
                if str(rec.employee_id.department_id.name) != 'FM':
                    if rec.employee_id.position_type == 'probation':
                        grade_id = rec.employee_id.grade_id
                        notice_period = int(grade_id.notice_period)
                        rec.notice_period = notice_period
                    else:
                        grade_id = rec.employee_id.grade_id
                        notice_period = int(grade_id.notice_period_after_confirmation)
                        rec.notice_period = notice_period
                else:
                    if rec.employee_id.department_id:
                        if rec.employee_id.position_type == 'probation':
                            notice_period = 30
                            rec.notice_period = notice_period
                        else:
                            notice_period = 60
                            rec.notice_period = notice_period
                if rec.resignation_type:
                    if rec.resignation_type.allow_exit_process == False:
                        rec.notice_period = 0



    @api.constrains('joined_date', 'expected_relieving_date')
    def _check_dates(self):
        # validating the entered dates
        for rec in self:
            resignation_request = self.env['hr.resignation'].search([('employee_id', '=', rec.employee_id.id),
                                                                     ('state', 'in', ['confirm', 'approved','resignation_accepted'])])
            if resignation_request:
                raise ValidationError(_('There is a resignation request in confirmed or'
                                        ' approved state for this employee already !'))
            if rec.joined_date >= rec.expected_relieving_date:
                raise ValidationError(_('Relieving date must be anterior to joining date'))

    @api.multi
    def confirm_resignation(self):
        for rec in self:
            if self.state == 'draft':
                rec.state = 'confirm'
                template_id = self.env.ref('orient_hr_resignation.email_template_for_resignation', False)
                self.env['mail.template'].browse(template_id.id).send_mail(rec.id, force_send=True)
            else:
                if rec.resignation_type:
                    allow_exit_process = rec.resignation_type.allow_exit_process
                    if allow_exit_process == False:
                        user_id = rec.employee_id.user_id.id
                        user = self.env.uid
                        if user_id == user:
                            raise ValidationError(_('You cannot apply for resignation as it does not fall under exit process'))
                if rec.resignation_type:
                    allow_exit_process = rec.resignation_type.allow_exit_process
                    if allow_exit_process == False:
                        template_id = self.env.ref('orient_hr_resignation.email_template_resignation_approval', False)
                        self.env['mail.template'].browse(template_id.id).send_mail(rec.id, force_send=True)
                        rec.approved_relieving_date = rec.expected_relieving_date
                        rec.state= 'approved'
                else:
                    rec.state = 'confirm'
                    template_id = self.env.ref('orient_hr_resignation.email_template_for_resignation', False)
                    self.env['mail.template'].browse(template_id.id).send_mail(rec.id, force_send=True)
            rec.resign_confirm_date = datetime.now()


    @api.multi
    def revoked_approval(self):
        for rec in self:
            employee_exit_id = self.env['hr.employee.exit'].search([('resignation_id', '=', rec.id)])
            if employee_exit_id:
                employee_exit_id.sudo().unlink()
            department_clearance_id = self.env['department.clearance'].search([('resignation_id','=',rec.id)])
            if department_clearance_id:
                department_clearance_id.sudo().unlink()
            rec.state = 'resignation_revoked'



    @api.multi
    def cancel_resignation(self):
        for rec in self:
            rec.state = 'cancel'

    @api.multi
    def reject_resignation(self):
        for rec in self:
            if rec.state == 'confirm':
                template_id = self.env.ref('orient_hr_resignation.email_template_resignation_reject_manager', False)
                self.env['mail.template'].browse(template_id.id).send_mail(rec.id, force_send=True)
            if rec.state == 'approved':
                template_id = self.env.ref('orient_hr_resignation.email_template_resignation_reject_hr_manager', False)
                self.env['mail.template'].browse(template_id.id).send_mail(rec.id, force_send=True)
            rec.state = 'rejected'

    @api.multi
    def reset_to_hr_approval(self):
        for rec in self:
            hr_employee_exit_confirm = self.env['hr.employee.exit'].search([('resignation_id','=',rec.id),('state','=','confirm')])
            if hr_employee_exit_confirm:
                raise ValidationError(_('The Exit Interview has been confirmed so you cannot reset to HR approval'))
            department_confirm = self.env['department.clearance'].search([('resignation_id','=',rec.id),('state','!=','draft')])
            if department_confirm:
                raise ValidationError(_('The Clearance Form has been confirmed so you cannot reset to HR approval'))
            template_id = self.env.ref('orient_hr_resignation.email_template_resignation_date_reset', False)
            self.env['mail.template'].browse(template_id.id).send_mail(rec.id, force_send=True)
            rec.state = 'approved'

    @api.multi
    def approve(self):
        for rec in self:
            template_id = self.env.ref('orient_hr_resignation.email_template_resignation_approval', False)
            self.env['mail.template'].browse(template_id.id).send_mail(rec.id, force_send=True)
            rec.state = 'approved'


    @api.multi
    def approve_resignation(self):
        for rec in self:
            if not rec.resignation_type:
                raise ValidationError(_('Please Select the Resignation Type'))
            if not rec.approved_relieving_date:
                raise ValidationError(_('Enter Approved Relieving Date'))
            if rec.approved_relieving_date and rec.resign_confirm_date:
                if rec.approved_relieving_date <= rec.resign_confirm_date:
                    pass
                    # raise ValidationError(_('Approved relieving date must be anterior to confirmed date'))
            hr_employee_exit_confirm = self.env['hr.employee.exit'].search([('resignation_id','=',rec.id),('state','=','confirm')])
            if hr_employee_exit_confirm:
                raise ValidationError(_('The Exit Interview has been confirmed so you cannot reset to HR approval'))
            department_confirm = self.env['department.clearance'].search([('resignation_id','=',rec.id),('state','!=','draft')])
            if department_confirm:
                raise ValidationError(_('The Clearance Form has been confirmed so you cannot reset to HR approval'))
            hr_employee_exit_search = self.env['hr.employee.exit'].search([('resignation_id','=',rec.id),('state','=','draft')])
            if hr_employee_exit_search:
                hr_employee_exit_browse = self.env['hr.employee.exit'].browse(hr_employee_exit_search[0])
                hr_employee_exit_browse.id.last_working_date=rec.approved_relieving_date
                department_clearance_search = self.env['department.clearance'].search([('resignation_id','=',rec.id),('state','=','draft')])
                if department_clearance_search:
                    department_clearance_browse = self.env['department.clearance'].browse(department_clearance_search[0])
                    department_clearance_browse.id.last_working_date=rec.approved_relieving_date
                template_id = self.env.ref('orient_hr_resignation.email_template_resignation_date_reset', False)
                self.env['mail.template'].browse(template_id.id).send_mail(rec.id, force_send=True)
            else:
                if rec.resignation_type.allow_exit_process == True:
                    resignation_request = self.env['hr.employee.template'].search([])
                    if not resignation_request:
                         raise ValidationError(_('Exit Template not defined!!'))
                    template_id = resignation_request.id
                    employee_id = rec.employee_id.id
                    employee_name = rec.employee_id.name
                    name = 'Clearance for Employee'+' '+str(employee_name)
                    employee_id = rec.employee_id.id
                    employee_code = rec.employee_id.emp_code
                    department_id = rec.department_id.id
                    joining_date = rec.joined_date
                    resignation_date = rec.expected_relieving_date
                    last_working_date = rec.approved_relieving_date
                    designation_id = rec.employee_id.job_id.id
                    clearance_vals = {'name':name,'employee_id':employee_id,'employee_code':employee_code,'joining_date':joining_date,'resignation_date':resignation_date,'last_working_date':last_working_date,'department_id':department_id,'designation_id':designation_id,'state':'draft','resignation_id':rec.id}
                    department_clearance = self.env['department.clearance'].create(clearance_vals)
                    clearance_master_obj = self.env['clearance.master'].search([('active','=',True)])
                    for clearance_id in clearance_master_obj:
                        points_id = clearance_id.id
                        rim_points = clearance_id.rim_points
                        finance_points = clearance_id.finance_points
                        hr_points = clearance_id.hr_points
                        if rim_points ==True:
                            rim_obj = self.env['rim.clearance'].create({'rim_clearance_id':points_id,'rim_id':department_clearance.id})
                        if finance_points == True:
                            rim_obj = self.env['finance.clearance'].create({'finance_clearance_id':points_id,'finance_id':department_clearance.id})
                        if hr_points == True:
                            rim_obj = self.env['hr.clearance'].create({'hr_clearance_id':points_id,'hr_id':department_clearance.id})
                    count=0
                    exit_interview_date = datetime.strptime(rec.approved_relieving_date, "%Y-%m-%d")-relativedelta(days=2)
                    new_approved_relieving_date = exit_interview_date
                    for a in range(10):
                        h_day = calendar.day_name[new_approved_relieving_date.weekday()]
                        if count ==0:
                            if h_day == 'Sunday':
                                new_approved_relieving_date = datetime.strptime(str(new_approved_relieving_date), "%Y-%m-%d %H:%M:%S")-relativedelta(days=2)
                            if h_day == 'Saturday':
                                new_approved_relieving_date = datetime.strptime(str(new_approved_relieving_date), "%Y-%m-%d %H:%M:%S")-relativedelta(days=1)
                            holiday_master = self.env['holiday.master'].search([('holiday_date','=',new_approved_relieving_date)])
                            if holiday_master:
                                new_approved_relieving_date = datetime.strptime(str(new_approved_relieving_date), "%Y-%m-%d %H:%M:%S")-timedelta(days=1)
                            else:
                                new_approved_relieving_date = new_approved_relieving_date
                                count+=1
                    template_name = resignation_request.name+' for '+str(employee_name)
                    exit_form_vals = {'name':template_name,'submit_hr_employee':employee_id,'exit_interview_date':new_approved_relieving_date,'last_working_date':rec.approved_relieving_date,'state':'draft','resignation_id':rec.id}
                    exit_form_creation = self.env['hr.employee.exit'].sudo().create(exit_form_vals)
                    template_line = self.env['hr.employee.template.line'].search([('template_id','=',template_id)])
                    if template_line:
                        for template_line_id in template_line:
                            template_line_name = template_line_id.name
                            exit_line_vals = {'name':template_line_name,'exit_id':exit_form_creation.id}
                            exit_line_creation = self.env['hr.employee.exit.line'].sudo().create(exit_line_vals)
                    template_id = self.env.ref('orient_hr_resignation.email_template_resignation_hr_approval', False)
                    self.env['mail.template'].browse(template_id.id).send_mail(rec.id, force_send=True)
            rec.state = 'resignation_accepted'

class Job(models.Model):
    _inherit = 'hr.job'

    hr_manager_bool = fields.Boolean(string='HR Manager')

class EmployeeExitTemplate(models.Model):

    _name = "hr.employee.template"
    _description = "Employee Exit Template"

    name = fields.Char(string="Template Name", required=True)
    template_line = fields.One2many('hr.employee.template.line', 'template_id', string='', auto_join=True)
    active = fields.Boolean('Active', default=True)

class EmployeeExitTemplateChild(models.Model):
    _name = "hr.employee.template.line"
    _description = "Employee Exit Template Child"

    name = fields.Char(string='', required=True)
    template_id = fields.Many2one('hr.employee.template', string='', ondelete='cascade', index=True, copy=False)


class EmployeeExit(models.Model):

    _name = "hr.employee.exit"
    _description = "Employee Exit Form"

    def _get_manager_id(self):
        # assigning the related employee of the logged in user
        hr_position = self.env['hr.job'].search([('hr_manager_bool', '=', True)], limit=1)
        employee_manager = self.env['hr.employee'].search([('job_id', '=',hr_position.id)], limit=1)
        return employee_manager.id

    name = fields.Char(string="Template Name", required=True)
    hr_employee_id = fields.Many2one('hr.employee', string="Employee",help='Name of the Employee',ondelete='cascade', index=True, copy=False)
    submit_hr_employee = fields.Many2one('hr.employee', string="Employee",help='Name of the Employee',ondelete='cascade', index=True, copy=False)
    hr_manager_id = fields.Many2one('hr.employee', string="HR Manager", default=_get_manager_id, help='Name of the HR Manager')
    last_working_date = fields.Date(string="Last Working Date", help='The last working day')
    exit_line = fields.One2many('hr.employee.exit.line', 'exit_id', string='', auto_join=True)
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'), ('cancel', 'Cancel')], string='Status', default='draft')
    is_expired = fields.Boolean(compute='_compute_is_expired', string="Is expired")
    assigned_to = fields.Many2one('hr.employee', string="Assigned to",help='Name of HR to which exit interview will be assigned')
    resignation_id = fields.Many2one('hr.resignation','Resignation id')
    exit_interview_date = fields.Date(string='Exit Interview Date', help='This is Exit Interview Date')

    def _compute_is_expired(self):
        now = datetime.now().date()
        for order in self:
            last_working_date = datetime.strptime(order.last_working_date, "%Y-%m-%d").date()
            exit_interview_date = datetime.strptime(order.exit_interview_date, "%Y-%m-%d").date()
            if exit_interview_date <= now <= last_working_date:
                order.is_expired = False
            else:
                order.is_expired = True

    @api.multi
    def submit(self):
        append_bool=[]
        for rec in self:
            submit_hr_employee = rec.submit_hr_employee.id
            line_id = self.env['hr.employee.exit.line'].search([('exit_id','=',rec.id)])
            for line in line_id:
                comments = line.comments
                if not comments:
                    raise ValidationError(_('You have to answer the questions without it cannot be submitted'))
                # if line.bad_bool == True:
                #     append_bool.append(line.bad_bool)
                # if line.very_bad_bool == True:
                #     append_bool.append(line.very_bad_bool)
                # if line.satisfactory_bool == True:
                #     append_bool.append(line.satisfactory_bool)
                # if line.good_bool == True:
                #     append_bool.append(line.good_bool)
                # if line.very_good_bool ==True:
                #     append_bool.append(line.very_good_bool)
                # if len(append_bool) > 1:
                #     raise ValidationError(_('You cannot check multiple options in one question'))
            self.write({'hr_employee_id':submit_hr_employee})
            rec.state = 'confirm'

    @api.multi
    def cancel(self):
        for rec in self:
            rec.state = 'cancel'

    def exit_mail_reminder(self):
        """Sending reminder mail for exit interview and for asset collection of an employee"""
        match = self.search([('state','=','draft')])
        for rec in match:
            last_working_date = datetime.strptime(rec.last_working_date, "%Y-%m-%d").date()
            date_now = datetime.now().date()
            prior_last_working_date = last_working_date - timedelta(days=2)
            previous_last_working_date = last_working_date - timedelta(days=1)
            if date_now == prior_last_working_date:
                template_id = self.env.ref('orient_hr_resignation.email_template_for_exit_interview', False)
                self.env['mail.template'].browse(template_id.id).send_mail(rec.id, force_send=True)
            if date_now == last_working_date:
                template_id = self.env.ref('orient_hr_resignation.email_template_for_exit_interview', False)
                self.env['mail.template'].browse(template_id.id).send_mail(rec.id, force_send=True)
            if date_now == previous_last_working_date:
                template_id = self.env.ref('orient_hr_resignation.email_template_for_asset_collection', False)
                self.env['mail.template'].browse(template_id.id).send_mail(rec.id, force_send=True)
        resignation_match = self.env['hr.resignation'].search([('state','=','confirm')])
        for rec1 in resignation_match:
            expected_relieving_date = datetime.strptime(rec1.expected_relieving_date, "%Y-%m-%d").date()
            date_now = datetime.now().date()
            reporting_manager_date = expected_relieving_date+timedelta(days=3)
            bu_head_date = expected_relieving_date + timedelta(days=5)
            hr_head_date = expected_relieving_date + timedelta(days=7)
            if date_now == reporting_manager_date:
                template_id = self.env.ref('orient_hr_resignation.email_template_for_reporting_manager', False)
                self.env['mail.template'].browse(template_id.id).send_mail(rec1.id, force_send=True)
            if date_now == bu_head_date:
                template_id = self.env.ref('orient_hr_resignation.email_template_for_bu_head', False)
                self.env['mail.template'].browse(template_id.id).send_mail(rec1.id, force_send=True)
            if date_now == hr_head_date:
                template_id = self.env.ref('orient_hr_resignation.email_template_for_hr_head', False)
                self.env['mail.template'].browse(template_id.id).send_mail(rec1.id, force_send=True)



    def print_relieving(self):
        return self.env.ref('orient_hr_resignation.action_report_exitreport').report_action(self)            

class EmployeeExitChild(models.Model):
    _name = "hr.employee.exit.line"
    _description = "Employee Exit Child Form"

    name = fields.Char(string='', required=True)
    comments = fields.Text(string="Comments", help='Specify answer of the question')
    # bad_bool = fields.Boolean('Bad', default=False)
    # very_bad_bool = fields.Boolean('Very Bad', default=False)
    # satisfactory_bool = fields.Boolean('Satisfactory', default=False)
    # good_bool = fields.Boolean('Good', default=False)
    # very_good_bool = fields.Boolean('Very Good', default=False)
    exit_id = fields.Many2one('hr.employee.exit', string='', ondelete='cascade', index=True, copy=False)
    

class HREmployee(models.Model):
    _inherit = 'hr.employee'

    def _get_groups_id(self):
        template_id = self.env.ref('hr.group_hr_user', False)
        return template_id

    position_type = fields.Selection([('probation', 'Probation'),('confirm','Permanent')], string='Employee Status')
    hr_employee_exit_form = fields.One2many('hr.employee.exit', 'hr_employee_id', string='', auto_join=True)
    grade_id = fields.Many2one('hr.employee.grade', string='Grade', ondelete='cascade', index=True, copy=False)
    group_id = fields.Many2one('res.groups','Groups',default=_get_groups_id)
    shift_id = fields.Many2one('hr.employee.shift.timing', string='Shift', ondelete='cascade', index=True, copy=False)

class ResignationType(models.Model):

    _name = "hr.employee.resignation.type"
    _description = "Resignation Type"

    name = fields.Char(string="Type", required=True)
    allow_exit_process = fields.Boolean('Allow Exit Process', default=False)
    active = fields.Boolean('Active', default=True)


class GradeMaster(models.Model):

    _name = "hr.employee.grade"
    _description = "Grade Master"

    name = fields.Char(string="Grade Name", required=True)
    notice_period = fields.Char(string="Notice Period (During Probation)")
    notice_period_after_confirmation = fields.Char(string="Notice Period (After Confirmation)")
    active = fields.Boolean('Active', default=True)


class ReasonResignation(models.Model):

    _name = "reason.resignation"
    _description = "Reason Resignation"

    name = fields.Char(string="Name", required=True)
    comments = fields.Boolean('Comment', default=False)
    active = fields.Boolean('Active', default=True)

class FnFCalculations(models.Model):

    _name = "fnf.form"
    _description = "FnF Form"

    name = fields.Char(string="Name", required=True)
    joining_date = fields.Date(string="Joining Date", help='The joining date of employee')
    last_working_date = fields.Date(string="Last Working Date", help='The last working date of employee')
    fnf_date = fields.Date(string="FnF Date", help='The FnF date of employee')
    is_expired = fields.Boolean(compute='_compute_is_expired', string="Is expired")
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'FnF Completed'), ('cancel', 'Cancel')], string='Status', default='draft')
    employee_id = fields.Many2one('hr.employee', string="Employee",help='Name of the Employee',ondelete='cascade', index=True, copy=False)

    def _compute_is_expired(self):
        now = datetime.now().date()
        for order in self:
            last_working_date = datetime.strptime(order.fnf_date, "%Y-%m-%d").date()
            if last_working_date == now:
                order.is_expired = False
            else:
                order.is_expired = True

    @api.multi
    def submit(self):
        for rec in self:
            employee_id = rec.employee_id
            employee_id.active = False
            res_users_obj = self.env['res.users'].search([('id','=',employee_id.user_id.id)])
            res_users_obj.sudo().write({'active':False})
            rec.state = 'confirm'



    @api.multi
    def cancel(self):
        for rec in self:
            employee_id = rec.employee_id
            rec.state = 'cancel'

class res_company(models.Model):
    _inherit = "res.company"

    def _get_logo1(self):
        return base64.b64encode(open(os.path.join(tools.config['root_path'], 'addons', 'base', 'res', 'res_company_logo1.png'), 'rb') .read())


    hr_group_email = fields.Char('HR Group Email')
    finance_email = fields.Char('Finance Group Email')
    rim_email = fields.Char('RIM Group Email')
    all_employee_email = fields.Char('All Employee Email')
    admin_user_email = fields.Char('Admin User Email')
    sdm_group_email = fields.Char('SDM Group Email')
    parent_company = fields.Many2one('res.company','Parent Company')
    logo1 = fields.Binary(default=_get_logo1, string="Company Logo1")

class ClearanceMaster(models.Model):
    _name = "clearance.master"
    _description = "Clearance Master"

    name = fields.Char(string="Name", required=True)
    rim_points = fields.Boolean('RIM', default=False)
    finance_points = fields.Boolean('Finance', default=False)
    hr_points = fields.Boolean('HR', default=False)
    active = fields.Boolean('Active', default=True)


class RIMClearanceForm(models.Model):
    _name = "rim.clearance"
    _description = "RIM Clearance Form"

    rim_clearance_id = fields.Many2one('clearance.master', string="Clearance",help='RIM Clearance Points', index=True, copy=False)
    state = fields.Selection([('submitted', 'Submitted'), ('not_submitted', 'Not Submitted'),('not_applicable', 'Not Applicable')], string='Status')
    comments = fields.Text(string="Comments", help='Specify the Comments')
    rim_date = fields.Date(string="Date")
    rim_user_id = fields.Many2one('res.users', string="User")
    rim_id = fields.Many2one('department.clearance',string="RIM ID",ondelete='cascade',index=True, copy=False)

    @api.onchange('state')
    def _onchange_state(self):
        if self.state:
            self.rim_date = datetime.now().date()
            self.rim_user_id = self.env.uid

class FinanceClearanceForm(models.Model):
    _name = "finance.clearance"
    _description = "Finance Clearance Form"

    finance_clearance_id = fields.Many2one('clearance.master', string="Clearance",help='Finance Clearance Points', index=True, copy=False)
    state = fields.Selection([('submitted', 'Submitted'), ('not_submitted', 'Not Submitted'),('not_applicable', 'Not Applicable')], string='Status')
    comments = fields.Text(string="Comments", help='Specify the Comments')
    finance_date = fields.Date(string="Date")
    finance_user_id = fields.Many2one('res.users', string="User")
    finance_id = fields.Many2one('department.clearance',string="Finance ID",ondelete='cascade',index=True, copy=False)

    @api.onchange('state')
    def _onchange_state(self):
        if self.state:
            self.finance_date = datetime.now().date()
            self.finance_user_id = self.env.uid

class HRClearanceForm(models.Model):
    _name = "hr.clearance"
    _description = "HR Clearance Form"

    hr_clearance_id = fields.Many2one('clearance.master', string="Clearance",help='HR Clearance Points', index=True, copy=False)
    state = fields.Selection([('submitted', 'Submitted'), ('not_submitted', 'Not Submitted'),('not_applicable', 'Not Applicable')], string='Status')
    comments = fields.Text(string="Comments", help='Specify the Comments')
    hr_date = fields.Date(string="Date")
    hr_user_id = fields.Many2one('res.users', string="User")
    hr_id = fields.Many2one('department.clearance',string="HR ID",ondelete='cascade',index=True, copy=False)

    @api.onchange('state')
    def _onchange_state(self):
        if self.state:
            self.hr_date = datetime.now().date()
            self.hr_user_id = self.env.uid

class ClearanceForm(models.Model):
    _name = "department.clearance"
    _description = "Clearance Form"

    def _get_manager_id(self):
        # assigning the related employee of the logged in user
        hr_position = self.env['hr.job'].search([('hr_manager_bool', '=', True)], limit=1)
        employee_manager = self.env['hr.employee'].search([('job_id', '=',hr_position.id)], limit=1)
        return employee_manager.id
    
    name = fields.Char(string="Name", required=True)
    employee_id = fields.Many2one('hr.employee', string="Employee Name",help='Name of the Employee', index=True, copy=False)
    joining_date = fields.Date(string="Date of Joining", help='Employee Joining Date')
    resignation_date = fields.Date(string="Date of Resignation", help='Employee Resignation Date')
    last_working_date = fields.Date(string="Last Working Date", help='Employee last working day')
    department_id = fields.Many2one('hr.department',string="Department",help="Employee Department")
    designation_id = fields.Many2one('hr.job',string="Designation",help="Employee Designation")
    employee_code = fields.Integer('Employee Code')
    state = fields.Selection([('draft', 'RIM Approval'), ('finance_approval', 'Finance Approval'), ('hr_approval', 'HR Approval'),('done','Done')], string='Status', default='draft')
    is_expired = fields.Boolean(compute='_compute_is_expired', string="Is expired")
    rim_line = fields.One2many('rim.clearance', 'rim_id', string='', auto_join=True)
    finance_line = fields.One2many('finance.clearance', 'finance_id', string='', auto_join=True)
    hr_line = fields.One2many('hr.clearance', 'hr_id', string='', auto_join=True)
    resignation_id = fields.Many2one('hr.resignation','Resignation id')
    hr_manager_id = fields.Many2one('hr.employee', string="HR Manager", default=_get_manager_id,
                                  help='Name of the HR Manager')
    # agree_rim = fields.Boolean('I agree that employee has submitted all the assets to RIM Department', default=False)
    # agree_finance = fields.Boolean('I agree that employee has submitted all the assets to Finance Department', default=False)
    # agree_manager = fields.Boolean('I agree that employee has submitted all the assets to HR Department', default=False)

    def print_clearance(self):
        return self.env.ref('orient_hr_resignation.action_report_clearance').report_action(self)


    def _compute_is_expired(self):
        now = datetime.now().date()
        print (now)
        for order in self:
            last_working_date = datetime.strptime(order.last_working_date, "%Y-%m-%d").date()
            print (last_working_date,'last_working_date')
            if last_working_date == now:
                order.is_expired = False
                print('xxxxxxx')
            else:
                order.is_expired = True
                print ('zzzzzzz')


    @api.multi
    def confirm_rim(self):
        for rec in self:
            line_id = self.env['rim.clearance'].search([('rim_id','=',rec.id)])
            for line in line_id:
                state = line.state
                if not state:
                    raise ValidationError(_('You have to fill the status of clearance points'))
            rec.state = 'finance_approval'


    @api.multi
    def approve(self):
        for rec in self:
            line_id = self.env['finance.clearance'].search([('finance_id','=',rec.id)])
            for line in line_id:
                state = line.state
                if not state:
                    raise ValidationError(_('You have to fill the status of clearance points'))
            rec.state = 'hr_approval'




    @api.multi
    def hr_approval(self):
        for rec in self:
            line_id = self.env['hr.clearance'].search([('hr_id','=',rec.id)])
            for line in line_id:
                state = line.state
                if not state:
                    raise ValidationError(_('You have to fill the status of clearance points'))
            submit_hr_employee = rec.employee_id.id
            employee_name = rec.employee_id.name
            resignation_id = rec.resignation_id.id
            name = 'FNF for Employee'+' '+str(employee_name)
            last_working_date = datetime.strptime(rec.last_working_date, "%Y-%m-%d").date()
            fnf_date = last_working_date + timedelta(days=46)
            new_approved_relieving_date = fnf_date
            count=0
            new_approved_relieving_date = date_by_adding_business_days(self, last_working_date, 46)
            # for a in range(44):
            #     h_day = calendar.day_name[new_approved_relieving_date.weekday()]
            #     print (h_day,'pppppppppppp')
            #     if count ==0:
            #         if h_day == 'Sunday':
            #             new_approved_relieving_date = datetime.strptime(str(new_approved_relieving_date), "%Y-%m-%d")-relativedelta(days=2)
            #         if h_day == 'Saturday':
            #             new_approved_relieving_date = datetime.strptime(str(new_approved_relieving_date), "%Y-%m-%d")-relativedelta(days=1)
            #         holiday_master = self.env['holiday.master'].search([('holiday_date','=',new_approved_relieving_date)])
            #         print (holiday_master,'lllllllllll')
            #         if holiday_master:
            #             new_approved_relieving_date = datetime.strptime(str(new_approved_relieving_date), "%Y-%m-%d")-timedelta(days=1)
            #         else:
            #             new_approved_relieving_date = new_approved_relieving_date
            #             count+=1
            joining_date = rec.employee_id.joining_date
            self.env['fnf.form'].create({'name':name,'last_working_date':last_working_date,'fnf_date':new_approved_relieving_date,'joining_date':joining_date,'state':'draft','employee_id':submit_hr_employee})
            rec.state = 'done'


class HolidayMaster(models.Model):
    _name = 'holiday.master'

    name = fields.Char('Holiday Name')
    holiday_date = fields.Date('Date')


    @api.constrains('holiday_date')
    def _holiday_date_repeat_check(self):
        existing_holiday_id = self.search([('holiday_date', '=', self.holiday_date),('id', '!=', self.id)])
        if existing_holiday_id:
            raise UserError(_('A holiday is already allocated again %s !') % (self.holiday_date))


class Users(models.Model):

    _inherit = "res.users"

    emp_code = fields.Integer('Employee Code')


class ShiftTimings(models.Model):

    _name = "hr.employee.shift.timing"
    _description = "Employee Shift Timing"
    _rec_name = 'name'

    name = fields.Char(string="Shift Grade", required=True)
    in_time = fields.Char('In Time',size=5)
    out_time = fields.Char('Out Time',size=5)
    in_time_select = fields.Selection([('am', 'AM'), ('pm', 'PM')], string='', default='am')
    out_time_select = fields.Selection([('am', 'AM'), ('pm', 'PM')], string='', default='am')
    in_shift_time = fields.Char(compute='_get_in_shift', string="In Shift Timing")
    out_shift_time = fields.Char(compute='_get_out_shift', string="Out Shift Timing")


    def _get_in_shift(self):
        for order in self:
            in_time = order.in_time
            in_time_select = order.in_time_select
            in_time_var = str(in_time)+' '+str(in_time_select)
            order.in_shift_time = str(in_time_var)


    def _get_out_shift(self):
        for order in self:
            out_time = order.out_time
            out_time_select = order.out_time_select
            out_time_var = str(out_time)+' '+str(out_time_select)
            order.out_shift_time = str(out_time_var)


class WallPostPoints(models.Model):
    _name = 'wall.post.points'
    _description = "Wall Post Points"
    _order = "id desc"

    name = fields.Text(string="Description")


class WallPost(models.Model):
    _name = 'wall.post'
    _description = "Wall Post"

    def _get_name_id(self):
        # assigning the related employee of the logged in user
        employee_note =[]
        employee_rec = self.env['wall.post.points'].search([],order='id desc')
        for employee_rec_id in employee_rec:
            user_id = employee_rec_id.create_uid.name 
            created_date = datetime.strptime(str(employee_rec_id.create_date), "%Y-%m-%d %H:%M:%S").date()
            new_create_date = created_date.strftime("%d-%m-%Y")
            # employee_note.append('<hr style="border:2px solid black;"><br/>Posted By: '+user_id+' on '+str(new_create_date)+'<br/><br/>'+str(employee_rec_id.name))
            employee_note.append(
                                '<hr style="border:2px solid black;"><br/><font size="3" color="blue">Posted By: </font>'+
                                '<font size="3" color="blue">'+user_id+'</font>'+
                                '<font size="3" color="blue"> on </font>'+
                                '<font size="3" color="blue">'+str(new_create_date)+'</font>'+
                                '<br/><br/>'+
                                str(employee_rec_id.name)
                                )
        employee_note = '\n\n'.join(employee_note)
        return employee_note

    name = fields.Text(string="Description",default=_get_name_id,)


class ExitReports(models.Model):
    _name = 'exit.reports'

    def _get_default_access_token(self):
        return str(uuid.uuid4())

    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    access_token = fields.Char('Security Token', copy=False,default=_get_default_access_token)
    site_master_id = fields.Many2one('site.master','Site')
    department_id = fields.Many2one('hr.department','Department')
    time_period = fields.Selection([('daily','Daily'),('month','Monthly'),('year','Yearly')], string="Period")

    @api.model_cr_context
    def _init_column(self, column_name):
        """ Initialize the value of the given column for existing rows.

            Overridden here because we need to generate different access tokens
            and by default _init_column calls the default method once and applies
            it for every record.
        """
        if column_name != 'access_token':
            super(ExitReports, self)._init_column(column_name)
        else:
            query = """UPDATE %(table_name)s
                          SET %(column_name)s = md5(md5(random()::varchar || id::varchar) || clock_timestamp()::varchar)::uuid::varchar
                        WHERE %(column_name)s IS NULL
                    """ % {'table_name': self._table, 'column_name': column_name}
            self.env.cr.execute(query)

    def _generate_access_token(self):
        for invoice in self:
            invoice.access_token = self._get_default_access_token()

    @api.multi
    def generate_excelreport(self,access_uid=None):
        self.get_dates()
        self.ensure_one()
        return {
        'type': 'ir.actions.act_url',
        'url': '/web/pivot/exit_report_xls/%s?access_token=%s' % (self.id, self.access_token),
        'target': 'new',
        }

    @api.multi
    def get_dates(self):
        current_date = datetime.now().date()
        # current_month = datetime.strptime(str(current_date), "%Y-%m-%d").strftime('%B')
        # current_year = datetime.strptime(str(current_date), "%Y-%m-%d").strftime('%Y')
        month = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").month
        year = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").year
        if self.time_period:
            abc = self.time_period
            print(abc,'***********88')
            if self.time_period == 'daily':
                self.from_date = datetime.now().date()
                self.to_date = datetime.now().date()
            elif self.time_period == 'month':
                date_list = []
                date_list = calendar.monthrange(year, month)
                first_day = date_list[0]
                last_day = date_list[1]
                first_date = date.today().replace(day=1)
                last_date = date.today().replace(day=last_day)
                print(first_date,last_date,'first date and last date')
                self.from_date = first_date
                self.to_date = last_date
            elif self.time_period == 'year':
                starting_day_of_current_year = datetime.now().date().replace(month=1, day=1)    
                ending_day_of_current_year = datetime.now().date().replace(month=12, day=31)
                print(starting_day_of_current_year,'wwwwww')
                print(ending_day_of_current_year,'dsds')
                self.from_date = starting_day_of_current_year
                self.to_date = ending_day_of_current_year
        return True
