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
import os
import base64, urllib
from io import StringIO,BytesIO
import uuid
from dateutil.relativedelta import relativedelta
from lxml import etree
from openerp.osv.orm import setup_modifiers
import csv
import uuid
from odoo.tools import config, human_size, ustr, html_escape
from odoo.tools.mimetypes import guess_mimetype
import shutil
from xlrd import open_workbook

def get_appraisal_scale(self,total_man_rating):
	if total_man_rating == 0.0:
		return 0
	else:
		search_scale = self.env['appraisal.scale'].search([('minimum','<=',float(total_man_rating)),('maximum','>=',float(total_man_rating))])
		return search_scale.scale

def get_current_financial_year(self):
	current_date = current_month = current_year = ''
	current_date =  datetime.now().date()
	current_month = datetime.strptime(str(current_date), "%Y-%m-%d").strftime('%B')
	current_year = datetime.strptime(str(current_date), "%Y-%m-%d").strftime('%Y')
	today_date = datetime.now().date()
	year = current_date.year
	year1=current_date.strftime('%y')
	start_year =  end_year = ''
	year = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").year
	month = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").month
	if month > 3:
		start_year = year
		end_year = year+1
		year1 = int(year1)+1
	else:
		start_year = year-1
		end_year = year
		year1 = int(year1)
	financial_start_date = str(start_year)+'-04-01'
	financial_end_date = str(end_year)+'-03-31'
	search_year = self.env['year.master'].search([('start_date','=',financial_start_date),('end_date','=',financial_end_date)])
	if search_year:
		return search_year[0].name
	else:
		return False

class AnnualReview(models.Model):
	_name = "annual.review"
	_rec_name = 'employee'

	appraisal_cycle = fields.Selection([('January','January'),('July','July')],string="Appraisal Cycle")
	average_quarter_rating = fields.Float('Quarter Average Rating')
	final_rating = fields.Float('Rating',store=True)
	hr_rating = fields.Float('HR Rating')
	manager_rating = fields.Float('Manager Rating')
	kra_year = fields.Many2one('year.master','Year')
	employee = fields.Many2one('hr.employee','Employee',default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1))
	company_id = fields.Many2one('res.company','Company')
	designation = fields.Many2one('hr.job','Designation')
	employee_code = fields.Char('Employee Code')
	department = fields.Many2one('hr.department','Department')
	location = fields.Many2one('res.company','Location')
	kra = fields.Many2one('kra.master','KRA')
	annual_goalsheet_details = fields.One2many('goalsheet.details','goalsheet_id','Goalsheet')
	annual_appraisal_details = fields.One2many('annual.appraisal.details','appraisal_detail_id','Appraisal')
	annual_appraisal_lines = fields.One2many('annual.appraisal','annual_appraisal_id','Appraisal')
	annual_behavioural_lines = fields.One2many('annual.behaviour','annual_behavioural_id','Behaviour')
	annual_kra_details = fields.One2many('annual.kra.details','annual_kra_id','')
	all_quarter_lines = fields.One2many('all.quarter.kra','all_kra_id','')
	state = fields.Selection([('draft','Draft'),('manager','Manager'),('hr','HR'),
								 ('done','Approved'),('cancel','Rejected')
								], string="State", default='draft')
	sr_no = fields.Char('Sr. No.')
	check1 = fields.Boolean(string="check field")
	active = fields.Boolean('Active',default=True)
	review_start_date = fields.Date("Review Start Date")
	review_end_date = fields.Date("Review End Date")
	pip_applicable = fields.Boolean('PIP Applicable?',default=False)
	approved_date = fields.Date('Approved Date')
	application_date = fields.Date('Application Date')
	review_summary = fields.Text('Review Summary')
	name = fields.Many2one('hr.employee','Employee Name')
	approved_status = fields.Selection([('approved','Approved'),('rejected','Rejected'),('pending','Pending')],string="Approved Status",default="pending")

	def search_annual_form(self):

		employee = self.env['hr.employee'].search([('user_id','=',self._uid)])
		review_month = self.appraisal_cycle
		domain = []		
		if self.kra_year:
			domain.append(('year','=',self.kra_year.id))
		if self.appraisal_cycle:
			domain.append(('review_cycle','=',self.appraisal_cycle))
		domain.append(('status','!=',''))
		domain.append(('employee','=',employee.id))
		goalsheet_dets = self.env['goalsheet.details'].search(domain)		
		print(goalsheet_dets,'----')

		appraisal_dets = self.env['annual.appraisal.details'].search(domain)		
		print(appraisal_dets)

		kra_dets = self.env['annual.kra.details'].search(domain)
		for i in self:
			if self.annual_goalsheet_details:
				for gs in self.annual_goalsheet_details:
					gs.write({'goalsheet_id':None,'select':False})
			if self.annual_appraisal_details:
				for gs in self.annual_appraisal_details:
					gs.write({'appraisal_detail_id':None,'select':False})
			if self.annual_kra_details:
				for gs in self.annual_kra_details:
					gs.write({'annual_kra_id':None,'select':False})
			if goalsheet_dets:
				for gs in goalsheet_dets:
					gs.write({'goalsheet_id':self.id,'select':False})
			if appraisal_dets:
				for a in appraisal_dets:
					a.write({'appraisal_detail_id':self.id,'select':False})
			if kra_dets:
				for k in kra_dets:
					k.write({'annual_kra_id':self.id,'select':False})
		return True

	def search_annualauth_form(self):
		if self._uid not in (1,1570,681):
			emp_list = []
			employee = self.env['hr.employee'].search([('user_id','=',self._uid)])
			search_emp =  self.env['hr.employee'].search([('parent_id','=',employee.id)])
			search_emp1 =  self.env['hr.employee'].search([('hr_executive_id','=',employee.id)])
			if employee:
				search_emp_hierarchy = self.env['employee.reporting.hierarchy'].search([('reportee_2','=',employee.id)])
				search_emp_hierarchy1 = self.env['employee.reporting.hierarchy'].search([('reportee_3','=',employee.id)])
				if search_emp_hierarchy:
					for p in search_emp_hierarchy:
						emp_list.append(p.name.id)
				if search_emp_hierarchy1:
					for q in search_emp_hierarchy1:
						emp_list.append(q.name.id)
			if search_emp:
				for x in search_emp:
					emp_list.append(x.id)
			if search_emp1:
				for y in search_emp1:
					emp_list.append(y.id)
			emp_list = list(set(emp_list))
			domain = []
			if self.name:
				domain.append(('employee','=',self.name.id))
			if self.approved_status:
				domain.append(('status','=',self.approved_status))
			if self.kra_year:
				domain.append(('year','=',self.kra_year.id))
			if domain == []:
				domain.append(('status','in',('pending','rejected','approved')))
			domain.append(('employee','in',emp_list))
			print (domain,'domain')

			goalsheet_dets = self.env['goalsheet.details'].search(domain)
			print(goalsheet_dets,'----')

			appraisal_dets = self.env['annual.appraisal.details'].search(domain)
			print(appraisal_dets)

			kra_dets = self.env['annual.kra.details'].search(domain)
			for i in self:
				if self.annual_goalsheet_details:
					for gs in self.annual_goalsheet_details:
						gs.write({'goalsheet_id':None,'select':False})
				if self.annual_appraisal_details:
					for gs in self.annual_appraisal_details:
						gs.write({'appraisal_detail_id':None,'select':False})
				if self.annual_kra_details:
					for gs in self.annual_kra_details:
						gs.write({'annual_kra_id':None,'select':False})
				if goalsheet_dets:
					for gs in goalsheet_dets:
						gs.write({'goalsheet_id':self.id,'select':False})
				if appraisal_dets:
					for a in appraisal_dets:
						a.write({'appraisal_detail_id':self.id,'select':False})
				if kra_dets:
					for k in kra_dets:
						k.write({'annual_kra_id':self.id,'select':False})
		else:
			domain = []
			if self.name:
				domain.append(('employee','=',self.name.id))
			if self.approved_status:
				domain.append(('status','=',self.approved_status))
			if self.kra_year:
				domain.append(('year','=',self.kra_year.id))
			if domain == []:
				domain.append(('status','in',('pending','approved')))
			print (domain,'domain')

			goalsheet_dets = self.env['goalsheet.details'].search(domain)
			print(goalsheet_dets,'----')

			appraisal_dets = self.env['annual.appraisal.details'].search(domain)
			print(appraisal_dets)

			kra_dets = self.env['annual.kra.details'].search(domain)
			for i in self:
				if self.annual_goalsheet_details:
					for gs in self.annual_goalsheet_details:
						gs.write({'goalsheet_id':None,'select':False})
				if self.annual_appraisal_details:
					for gs in self.annual_appraisal_details:
						gs.write({'appraisal_detail_id':None,'select':False})
				if self.annual_kra_details:
					for gs in self.annual_kra_details:
						gs.write({'annual_kra_id':None,'select':False})
				if goalsheet_dets:
					for gs in goalsheet_dets:
						gs.write({'goalsheet_id':self.id,'select':False})
				if appraisal_dets:
					for a in appraisal_dets:
						a.write({'appraisal_detail_id':self.id,'select':False})
				if kra_dets:
					for k in kra_dets:
						k.write({'annual_kra_id':self.id,'select':False})
		return True

	@api.multi
	def open_annual_review_form(self):
		self.ensure_one()
		kra_form = self.env.ref('orient_pms.view_annual_kra_form', False)
		return {
			'name': _('Annual Review'),
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'annual.review',
			'res_id': self.id,
			'views': [(kra_form.id, 'form')],
			'view_id': self.id,
			'target': 'new',
		}

	def print_review(self):
		return self.env.ref('orient_pms.action_report_reviewform').report_action(self)

	@api.multi
	def submit_to_manager(self):
		for rec in self:
			rec.state="manager"

	@api.multi
	def submit_to_hr(self):
		total_man_rating = 0.0
		for rec in self:
			for kpi in rec.annual_kra_lines:
				if kpi.man_rating >kpi.weightage:
					raise ValidationError(_("Manager Rating cannot be greater than the weightage"))
				total_man_rating+=kpi.man_rating
			search_scale = self.env['appraisal.scale'].search([('minimum','<=',float(total_man_rating)),('maximum','>=',float(total_man_rating))])
			rec.manager_rating = search_scale.scale
			rec.state="hr"


	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(AnnualReview, self).fields_view_get(
			view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		doc = etree.XML(res['arch'])
		if self._context.get('uid'):
			uid = self._context.get('uid')
			res_user = self.env['res.users'].search([('id','=',uid)])
			print(res_user)
			if not res_user.has_group('hr.group_hr_manager') and not res_user.has_group('hr.group_hr_user') and not res_user.has_group('orient_hr_resignation.group_reporting_manager'):
				for node in doc.xpath("//field[@name='annual_kra_lines']"):
					node.set('readonly',('1'))
					setup_modifiers(node)
			res['arch'] = etree.tostring(doc)
		return res

	@api.multi
	def approve(self):
		total_hr_rating = 0.0
		for rec in self:
			for kpi in rec.annual_kra_lines:
				if kpi.hr_rating >kpi.weightage:
					raise ValidationError(_("HR Rating cannot be greater than the weightage"))
				total_hr_rating+=kpi.hr_rating
			print (total_hr_rating,'total_hr_rating')
			search_scale = self.env['appraisal.scale'].search([('minimum','<=',float(total_hr_rating)),('maximum','>=',float(total_hr_rating))])
			print (search_scale,'llllssssssssss')
			rec.hr_rating = search_scale.scale
			if rec.manager_rating!=0.0 and rec.hr_rating!=0.0:
				final_rating = (rec.manager_rating + rec.hr_rating + rec.average_quarter_rating)/3
				rec.final_rating = final_rating
			if rec.manager_rating!=0.0 and rec.hr_rating==0.0:
				final_rating = (rec.manager_rating + rec.average_quarter_rating)/2
				rec.final_rating = final_rating
			if rec.manager_rating==0.0 and rec.hr_rating!=0.0:
				final_rating = (rec.hr_rating + rec.average_quarter_rating)/2
			if rec.manager_rating==0.0 and rec.hr_rating==0.0:
				final_rating = rec.average_quarter_rating
			rec.state="done"

	@api.multi
	def add_goalsheet(self):
		print (self.id)
		year = None
		self.ensure_one()
		goalsheet_obj = self.env['annual.goalsheet']
		goalsheet_details = self.env['goalsheet.details']
		kra_form = self.env.ref('orient_pms.view_annual_goalsheet_form', False)
		get_year = get_current_financial_year(self)
		get_year =  get_year.split('-')
		get_year1 = int(get_year[0])
		get_year2 = int(get_year[1])
		get_year3 = str(get_year1) + "-" + str(get_year2)

		goalsheet_recs = self.env['goalsheet.details'].search([('year','=',get_year3),('status','in',(('approved','pending'))),('employee','=',self.employee.id)])
		print(goalsheet_recs)
		if goalsheet_recs:
			raise ValidationError(_("Goalsheet form is already filled!"))
		search_year = self.env['year.master'].search([('name','=',str(get_year3))])
		if search_year:
			year = search_year.id
		approve1_char = ''
		approve2_char = ''
		approve3_char = ''
		approve4_char = ''
		search_recs = self.env['employee.reporting.hierarchy'].search([('name','=',self.employee.id)])
		if search_recs:
			count=0
			for c in search_recs:
				if c.reportee_1.id != False:
					count+=1
					approve1_char = 'Pending By '+c.reportee_1.name 
				if c.reportee_2.id != False:
					count+=1
					approve2_char = 'Pending By '+c.reportee_2.name
				if c.reportee_3.id != False:
					count+=1
					approve3_char = 'Pending By '+c.reportee_3.name
				if c.hr_reportee.id != False:
					count+=1
					approve4_char = 'Pending By '+c.hr_reportee.name
		gs_id = goalsheet_details.create({'employee_code':self.employee.emp_code,'year':year,'employee':self.employee.id,
				'designation':self.employee.job_id.id,'department':self.employee.department_id.id,'review_cycle':self.employee.appraisal_cycle,
				'location':self.employee.company_id.id,'application_date':datetime.now().date(),'site_id':self.employee.site_master_id.id,
				'joining_date':self.employee.joining_date,'main_id':self.id,'goalsheet_id':None,
				'approve1_char':approve1_char,'approve2_char':approve2_char,
				'approve3_char':approve3_char,'approve4_char':approve4_char})
		search_goalsheet = self.env['kra.templates'].search([('name','=','Goalsheet')])
		if search_goalsheet:
			for goalsheet in search_goalsheet.question_one2many:
				print (goalsheet.questions,'ppppppppp')
				create_id = goalsheet_obj.create({
								'questions':goalsheet.questions,
								'annual_goalsheet_id':gs_id.id,
								})
		else:
			raise ValidationError(_("Goalsheet is not mapped!"))
		return {
			'name': _('Goalsheet'),
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'goalsheet.details',
			'res_id': gs_id.id,
			'views': [(kra_form.id, 'form')],
			'view_id': self.id,
			'target': 'new',
		}

	@api.multi
	def view_goalsheet(self):
		print (self.id)
		self.ensure_one()
		if not self.annual_goalsheet_details:
			raise ValidationError(_("No record to view!!"))
		elif self.annual_goalsheet_details:
			for rec in self.annual_goalsheet_details:
				rec.write({'readonly_chk':False})
				if rec.select:
					kra_form = self.env.ref('orient_pms.view_annual_goalsheet_form', False)
					return {
						'name': _('Goalsheet'),
						'type': 'ir.actions.act_window',
						'view_type': 'form',
						'view_mode': 'form',
						'res_model': 'goalsheet.details',
						'res_id': rec.id,
						'views': [(kra_form.id, 'form')],
						'view_id': self.id,
						'target': 'new',
					}
		else:
			raise ValidationError(_("No record selected!!"))

	@api.multi
	def modify_goalsheet(self):
		print (self.id)
		self.ensure_one()
		if not self.annual_goalsheet_details:
			raise ValidationError(_("No record to modify!!"))
		else:
			for rec in self.annual_goalsheet_details:
				if rec.status == 'approved':
					raise ValidationError(_("You cannot modify Approved record!!"))
				if not rec.select:
					raise ValidationError(_("Kindly select record!!"))
				else:
					for d in self.annual_goalsheet_details:
						d.write({'readonly_chk':False})
					kra_form = self.env.ref('orient_pms.view_annual_goalsheet_form', False)
					return {
						'name': _('Goalsheet'),
						'type': 'ir.actions.act_window',
						'view_type': 'form',
						'view_mode': 'form',
						'res_model': 'goalsheet.details',
						'res_id': rec.id,
						'views': [(kra_form.id, 'form')],
						'view_id': self.id,
						'target': 'new',
					}
	@api.multi
	def view_all_goalsheet(self):
		print (self.id)
		self.ensure_one()
		raise ValidationError(_("No records to view!"))

	@api.multi
	def add_annualappraisal(self):
		department = self.employee.department_id.id
		if not self.employee.pms_form_applicable:
			raise ValidationError(_("Annual Appraisal Form is not mapped!"))
		sub_department = self.employee.pms_form_applicable.id
		year = None
		name = "Performance Appraisal"
		get_year = get_current_financial_year(self)
		get_year = 16
		appraisal_recs = self.env['annual.appraisal.details'].search([('year','=',get_year),('status','in',(('approved','pending'))),('employee','=',self.employee.id)])
		if appraisal_recs:
			raise ValidationError(_("Annual Appraisal form is already filled"))

		self.env.cr.execute("SELECT id from kra_templates where name='%s' and sub_department= %s" % (name,sub_department))
		tmp_exist = self.env.cr.fetchone()

		if tmp_exist ==None:
			raise ValidationError(_("Annual Appraisal Form is not mapped!!"))
		else:
			employee = self.employee.id
			employee_code = self.employee.emp_code
			designation = self.employee.job_id.id
			department = self.employee.department_id.id
			location = self.employee.company_id.id
			joining_date = self.employee.joining_date
			appraisal_detail_id = self.id
			review_start_date = ''
			review_end_date = ''
			get_year = get_current_financial_year(self)
			print (get_year)
			split_year = get_year.split('-')
			year1 = str(split_year[0])
			year2 = str(split_year[1])
			print (year1,year2)
			get_year1 = str(int(year1)-1)+'-'+str(int(year1))
			if self.employee.appraisal_cycle == 'January':
				review_start_date = str(int(year1)-2)+'-10-01'
				review_end_date = str(int(year1)-1)+'-09-30'
			if self.employee.appraisal_cycle == 'July':
				review_start_date = str(int(year1)-1)+'-04-01'
				review_end_date = year1+'-03-31'
			search_year = self.env['year.master'].search([('name','=',str(get_year1))])
			if search_year:
				year = search_year.id
			approve1_char = ''
			approve2_char = ''
			approve3_char = ''
			approve4_char = ''
			search_recs = self.env['employee.reporting.hierarchy'].search([('name','=',employee)])
			if search_recs:
				count=0
				for c in search_recs:
					if c.reportee_1.id != False:
						count+=1
						approve1_char = 'Pending By '+c.reportee_1.name 
					if c.reportee_2.id != False:
						count+=1
						approve2_char = 'Pending By '+c.reportee_2.name
					if c.reportee_3.id != False:
						count+=1
						approve3_char = 'Pending By '+c.reportee_3.name
					if c.hr_reportee.id != False:
						count+=1
						approve4_char = 'Pending By '+c.hr_reportee.name
			main_id = self.env['annual.appraisal.details'].create({'employee':employee ,'year':year, 'employee_code':employee_code,
														'designation':designation,'department':department,
														'location':location,'joining_date':joining_date,
														'appraisal_detail_id':None,'main_id':self.id,
														'review_cycle':self.employee.appraisal_cycle,
														'reporting_head':self.employee.parent_id.id,
														'application_date':datetime.now().date(),
														'site_id':self.employee.site_master_id.id,
														'review_start_date':review_start_date,
														'review_end_date':review_end_date,
														'approve1_char':approve1_char,'approve2_char':approve2_char,
														'approve3_char':approve3_char,'approve4_char':approve4_char})

			department = self.employee.department_id.id
			tmp_exist1 = self.env['kra.templates'].search([('name','=','Performance Appraisal'),('sub_department','=',sub_department)])
			print (tmp_exist1)
			for each in tmp_exist1.question_one2many:
					self.env['annual.appraisal.questions'].create({'annual_appraisalline_id':main_id.id,
																	'questions':each.questions,
																	'questions_id':each.id})
			if tmp_exist1.behavioural_attributes_one2many:
				for each1 in tmp_exist1.behavioural_attributes_one2many:
					self.env['annual.attributes'].create({'annual_attribute_id':main_id.id,
															'attributes':each1.attributes,
															'attributes_id':each1.id})										
				main_id.write({'show': True})

			self.ensure_one()

			kra_form = self.env.ref('orient_pms.view_annual_appraisal_form', False)
			return {
				'name': _('Annual Appraisal'),
				'type': 'ir.actions.act_window',
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'annual.appraisal.details',
				'res_id': main_id.id,
				'views': [(kra_form.id, 'form')],
				'view_id': self.id,
				'target': 'new',
			}


	@api.multi
	def view_annualappraisal(self):
		print (self.id)
		self.ensure_one()
		if not self.annual_appraisal_details:
			raise ValidationError(_("No record to view!!"))
		elif self.annual_appraisal_details:
			for rec in self.annual_appraisal_details:
				if rec.select:
					kra_form = self.env.ref('orient_pms.view_annual_appraisal_form', False)
					return {
						'name': _('Annual Appraisal'),
						'type': 'ir.actions.act_window',
						'view_type': 'form',
						'view_mode': 'form',
						'res_model': 'annual.appraisal.details',
						'res_id': rec.id,
						'views': [(kra_form.id, 'form')],
						'view_id': self.id,
						'target': 'new',
					}
		else:
			raise ValidationError(_("No record selected!"))

	@api.multi
	def view_all_appraisal(self):
		print (self.id)
		self.ensure_one()
		raise ValidationError(_("No records to view!"))

	@api.multi
	def modify_annual_kra(self):
		print (self.id)
		self.ensure_one()
		raise ValidationError(_("No records to modify!"))

	@api.multi
	def view_all_kra(self):
		print (self.id)
		self.ensure_one()
		raise ValidationError(_("No records to view!"))

	@api.multi
	def add_annual_kra(self):
		print (self.id)
		self.ensure_one()
		year = None
		annual_kra_obj = self.env['annual.kra']
		kra_master_obj = self.env['kra.master']
		emp_obj = self.env['hr.employee']
		kra_rating_obj = self.env['kra.rating']
		kpi_master_obj = self.env['kpi.master']
		emp_kra_kpi = self.env['employee.kra.kpi']
		review_cycle = ['January','July','June']
		if not self.employee.kra_one2many:
			raise ValidationError(_("Kindly Map KRA to the Employee!!"))
		kra_obj = self.env['annual.kra.details']
		kra_form = self.env.ref('orient_pms.view_annual_kra_details_form', False)
		employee = self.employee.id
		employee_code = self.employee.emp_code
		designation = self.employee.job_id.id
		department = self.employee.department_id.id
		location = self.employee.company_id.id
		joining_date = self.employee.joining_date
		appraisal_detail_id = self.id
		get_year = get_current_financial_year(self)
		print (get_year)
		split_year = get_year.split('-')
		year1 = str(split_year[0])
		year2 = str(split_year[1])
		print (year1,year2)
		get_year1 = str(int(year1)-1)+'-'+str(int(year1))
		kra_recs = self.env['annual.kra.details'].search([('year','=',get_year1),('status','in',(('approved','pending'))),('employee','=',self.employee.id)])
		print (kra_recs,'kra_recs','pppppppppp')
		if kra_recs:
			raise ValidationError(_("Annual KRA form is already filled!!"))
		approve1_char = ''
		approve2_char = ''
		approve3_char = ''
		approve4_char = ''
		search_recs = self.env['employee.reporting.hierarchy'].search([('name','=',self.employee.id)])
		count=0
		approve1 = ''
		approve2 = ''
		approve3 = ''
		approve4 = ''
		if search_recs:
			for c in search_recs:
				if c.reportee_1.id != False:
					count+=1
					approve1_char = 'Pending By '+c.reportee_1.name 
					approve1 = 'Reportee1 : '+c.reportee_1.name 
				if c.reportee_2.id != False:
					count+=1
					approve2_char = 'Pending By '+c.reportee_2.name
					approve2 = 'Reportee2 : '+c.reportee_2.name 
				if c.reportee_3.id != False:
					count+=1
					approve3_char = 'Pending By '+c.reportee_3.name
					approve3 = 'Reportee3 : '+c.reportee_3.name 
				if c.hr_reportee.id != False:
					count+=1
					approve4_char = 'Pending By '+c.hr_reportee.name
					approve4 = 'HR Reportee : '+c.hr_reportee.name 
		print (approve1,approve2,approve3,approve4)
		review_start_date = ''
		review_end_date = ''
		search_year = self.env['year.master'].search([('name','=',str(get_year))])
		if search_year:
			year = search_year.id
		split_year = get_year.split('-')
		year1 = str(split_year[0])
		year2 = str(split_year[1])
		print (year1,year2)
		get_year1 = str(int(year1)-1)+'-'+str(int(year1))
		search_year = self.env['year.master'].search([('name','=',str(get_year1))])
		if search_year:
			year = search_year.id
		if self.employee.appraisal_cycle == 'January':
			review_start_date = str(int(year1)-2)+'-10-01'
			review_end_date = str(int(year1)-1)+'-09-30'
		if self.employee.appraisal_cycle == 'July':
			review_start_date = str(int(year1)-1)+'-04-01'
			review_end_date = year1+'-03-31'
		main_id = kra_obj.create({'employee':employee,'year':year,'employee_code':employee_code,
								'designation':designation,'department':department,
								'location':location,'joining_date':joining_date,
								'appraisal_detail_id':None,'main_id':self.id,
								'review_cycle':self.employee.appraisal_cycle,
								'reporting_head':self.employee.parent_id.id,
								'application_date':datetime.now().date(),
								'current_gross':self.employee.gross_salary,
								'current_ctc':self.employee.current_ctc,
								'reporting_levels':count,'site_id':self.employee.site_master_id.id,
								'review_start_date':review_start_date,
								'review_end_date':review_end_date,
								'approve1_char':approve1_char,'approve2_char':approve2_char,
								'approve3_char':approve3_char,'approve4_char':approve4_char,
								'reportee1_name':approve1,'reportee2_name':approve2,
								'reportee3_name':approve3, 'reportee4_name':approve4})
		split_year = get_year.split('-')
		year1 = str(split_year[0])
		year2 = str(split_year[1])
		print (year1,year2)
		current_date =  datetime.now().date()
		print (current_date,'current_date',year1,year2)
		# if str(current_date) == year1+'-07-01' or str(current_date) == year2+'-01-01':
		current_month = datetime.strptime(str(current_date), "%Y-%m-%d").strftime('%B')
		print (current_month,'mmmmmm')
		emp_obj=self.env['hr.employee']
		kra_obj=self.env['kra.main']
		if current_month in review_cycle:
			rec = emp_obj.search([('id', '=',self.employee.id)])
			print (rec)
			count1=1
			final_rating=0.0
			for emp in rec:				
				joining_date = emp.joining_date
				date_dt= datetime.strptime(joining_date, "%Y-%m-%d").date()
				current_date= datetime.strptime(str(current_date), "%Y-%m-%d").date()
				tenure = relativedelta(current_date, date_dt)
				if tenure.years >= 1 or tenure.months>=9:
					if current_month in ('June','July'):
						get_year = get_current_financial_year(self)
						split_year = get_year.split('-')
						year1 = str(int(split_year[0])-1)
						year2 = str(int(split_year[1])-1)
						print (year1,year2,'review_start')
						review_start_date1=year1+'-04-01'
						review_end_date1=year1+'-06-30'
						review_start_date2=year1+'-07-01'
						review_end_date2=year1+'-09-30'
						review_start_date3=year1+'-10-01'
						review_end_date3=year1+'-12-31'
						review_start_date4=year2+'-01-01'
						review_end_date4=year2+'-03-31'
						search_quarter2=kra_obj.search([('review_start_date','=',review_start_date2),('review_end_date','=',review_end_date2),('employee','=',emp.id),('state','=','done')])
						search_quarter3=kra_obj.search([('review_start_date','=',review_start_date3),('review_end_date','=',review_end_date3),('employee','=',emp.id),('state','=','done')])
						search_quarter4=kra_obj.search([('review_start_date','=',review_start_date4),('review_end_date','=',review_end_date4),('employee','=',emp.id),('state','=','done')])
						search_quarter1=kra_obj.search([('review_start_date','=',review_start_date1),('review_end_date','=',review_end_date1),('employee','=',emp.id),('state','=','done')])
						print (review_start_date1,review_end_date1,review_start_date2,review_end_date2,review_start_date3,review_end_date3,review_start_date4,review_end_date4)
						print (search_quarter1,search_quarter2,search_quarter3,search_quarter4,emp.name,'records')
						# if not (search_quarter2.id != False and search_quarter3.id != False and search_quarter4.id != False and search_quarter1.id != False):
						# 	raise ValidationError(_("Kindly Fill all Quarterly KRA forms!!"))
						# else:
						average_quarter_rating=(search_quarter2.final_rating+search_quarter3.final_rating+search_quarter1.final_rating+search_quarter4.final_rating)/4
						main_id.write({'average_quarter_rating':average_quarter_rating})
						search_quarter2.write({'all_kra_id':main_id.id})
						search_quarter3.write({'all_kra_id':main_id.id})
						search_quarter4.write({'all_kra_id':main_id.id})
						search_quarter1.write({'all_kra_id':main_id.id})
						kra_ids = emp_obj.browse(emp.kra_one2many)
						count=1
						kpi_ids=[]
						check_record = self.env['kra.main'].search([('employee_code','=',employee_code),('kra_year','=',16),('quarter','=','Fourth'),('state','!=','cancel')])
						if check_record:
							if check_record.kra_one2many:
								for x in check_record.kra_one2many:
									create_id = annual_kra_obj.create({
									'sr_no':x.sr_no,
									'kra_name':x.kra_name,
									'kpi':x.description,
									'weightage':x.weightage,
									'annual_kra_id':main_id.id,
									'self_rating':x.emp_rating,
									'reportee1_rating':x.man_rating,
									'readonly_flag':True if x.emp_rating else False,
									'readonly_flag1':True if x.man_rating else False
									})
						else:
							if kra_ids:
								for kra in kra_ids:
									create_id = annual_kra_obj.create({
										'sr_no':count,
										'kra':kra.id.kra_master_id.id,
										'kpi':kra.id.kpi,
										'weightage':kra.id.weightage,
										'annual_kra_id':main_id.id,
										'kra_name':kra.id.name,
										})
					rating_list = []
					if main_id.all_quarter_details:
						for x in main_id.all_quarter_details:
							rating_list.append(x.final_rating)
						length = len(rating_list)
						final_rating = round(sum(rating_list)/length,2)
					main_id.write({'average_quarter_rating': final_rating})
					if current_month == 'January':
						get_year = get_current_financial_year(self)
						split_year = get_year.split('-')
						year1 = str(int(split_year[0])-1)
						year2 = str(int(split_year[1])-1)
						print (year1,year2)
						review_start_date1=year2+'-04-01'
						review_end_date1=year2+'-06-30'
						review_start_date2=year2+'-07-01'
						review_end_date2=year2+'-09-30'
						review_start_date3=year2+'-10-01'
						review_end_date3=year2+'-12-31'
						review_start_date4=year2+'-01-01'
						review_end_date4=year2+'-03-31'
						search_quarter4=kra_obj.search([('review_start_date','=',review_start_date4),('review_end_date','=',review_end_date4),('employee','=',emp.id),('state','=','done')])
						search_quarter1=kra_obj.search([('review_start_date','=',review_start_date1),('review_end_date','=',review_end_date1),('employee','=',emp.id),('state','=','done')])							
						search_quarter2=kra_obj.search([('review_start_date','=',review_start_date2),('review_end_date','=',review_end_date2),('employee','=',emp.id),('state','=','done')])
						search_quarter3=kra_obj.search([('review_start_date','=',review_start_date3),('review_end_date','=',review_end_date3),('employee','=',emp.id),('state','=','done')])
						print (review_start_date1,review_end_date1,review_start_date2,review_end_date2,review_start_date3,review_end_date3,review_start_date4,review_end_date4)
						print (search_quarter1,search_quarter2,search_quarter3,search_quarter4,emp.name,'records')
						if not (search_quarter4.id != False and search_quarter1.id != False and search_quarter2.id != False and search_quarter3.id != False):
							raise ValidationError(_("Kindly Fill all Quarterly KRA forms!!"))
						else:	
							average_quarter_rating=(search_quarter2.final_rating+search_quarter3.final_rating+search_quarter1.final_rating+search_quarter4.final_rating)/4
							main_id.write({'average_quarter_rating':average_quarter_rating})
							search_quarter4.write({'all_kra_id':main_id.id})
							search_quarter1.write({'all_kra_id':main_id.id})
							search_quarter2.write({'all_kra_id':main_id.id})
							search_quarter3.write({'all_kra_id':main_id.id})
							kra_ids = emp_obj.browse(emp.kra_one2many)
							count=1
							kpi_ids=[]
							if kra_ids:
								for kra in kra_ids:
									create_id = annual_kra_obj.create({
										'sr_no':count,
										'kra':kra.id.kra_master_id.id,
										'kpi':kra.id.kpi,
										'weightage':kra.id.weightage,
										'annual_kra_id':main_id.id,
										'kra_name':kra.id.name,
										})
					if main_id.cba_details:
						for line in main_id.cba_details:
							line.unlink()
					if main_id.cba_lines:
						for line in main_id.cba_lines:
							line.unlink()
					self.env['critical.behaviour.lines'].create({'cbl_id':main_id.id,'description':'Communication Skills'})
					self.env['critical.behaviour.lines'].create({'cbl_id':main_id.id,'description':'Relationship Maintaining & Building'})
					self.env['critical.behaviour.lines'].create({'cbl_id':main_id.id,'description':'Time Management'})
					self.env['critical.behaviour.lines'].create({'cbl_id':main_id.id,'description':'Client Orientation'})
					self.env['critical.behaviour.lines'].create({'cbl_id':main_id.id,'description':'Result Orientation'})						
					self.env['critical.behaviour.lines'].create({'cbl_id':main_id.id,'description':'Team Work'})

		return {
			'name': _('Annual KRA Details'),
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'annual.kra.details',
			'res_id': main_id.id,
			'views': [(kra_form.id, 'form')],
			'view_id': self.id,
			'target': 'new',
		}

	@api.multi
	def view_annual_kra(self):
		print (self.id)
		self.ensure_one()
		if not self.annual_kra_details:
			raise ValidationError(_("No record to view!!"))
		else:
			for rec in self.annual_kra_details:
				if rec.select:
					kra_form = self.env.ref('orient_pms.view_annual_kra_details_form', False)
					return {
						'name': _('Annual Appraisal'),
						'type': 'ir.actions.act_window',
						'view_type': 'form',
						'view_mode': 'form',
						'res_model': 'annual.kra.details',
						'res_id': rec.id,
						'views': [(kra_form.id, 'form')],
						'view_id': self.id,
						'target': 'new',
					}

class AnnualGoalsheet(models.Model):
	_name = "annual.goalsheet"

	annual_goalsheet_id = fields.Many2one('goalsheet.details','Annual KRA')
	questions = fields.Text('Questions')
	answers = fields.Text('Answers')

class GoalsheetDetails(models.Model):
	_name = 'goalsheet.details'

	goalsheet_id = fields.Many2one('annual.review','Annual KRA')
	select = fields.Boolean('Select')
	year = fields.Many2one('year.master','Year')
	review_start_date = fields.Date('Review Start Date')
	review_cycle = fields.Selection([('January','January'),('July','July')], string="Review Cycle")
	review_end_date = fields.Date('Review End Date')
	status = fields.Selection([('pending','Pending'),('approved','Approved'),('rejected','Rejected')],'Status')
	status_char = fields.Char('Status')
	employee_code = fields.Char('Employee Code')
	employee = fields.Many2one('hr.employee','Employee Name')
	site_id = fields.Many2one('site.master','Site')
	location = fields.Many2one('res.company','Location')
	designation = fields.Many2one('hr.job', 'Designation')
	department = fields.Many2one('hr.department','Department')
	joining_date = fields.Date('Joining Date')
	main_id = fields.Char('Main ID')
	readonly_chk = fields.Boolean('Readonly')
	annual_goalsheet_lines = fields.One2many('annual.goalsheet','annual_goalsheet_id','Goalsheet')
	approved_date = fields.Date('Approved Date')
	application_date = fields.Date('Application Date')
	rejected_date = fields.Date('Rejected Date')
	button_check = fields.Boolean('button_check', compute='_get_user')
	approve1_char = fields.Char('Approve1 Char')
	approve2_char = fields.Char('Approve2 Char')
	approve3_char = fields.Char('Approve3 Char')
	approve4_char = fields.Char('Approve4 Char')
	approve2 = fields.Boolean('Approve2', default=False)
	approve3 = fields.Boolean('Approve3', default=False)
	approve_hr = fields.Boolean('Approve HR', default=False)
	comments = fields.Text("Approvers/Management's Comments")

	def _get_user(self):
		button_bool = False
		employee= self.employee.user_id.id
		res_user = self.env['res.users'].search([('id', '=', self._uid)])
		if res_user.has_group('hr.group_hr_manager') or res_user.has_group('hr.group_hr_user') or res_user.has_group('orient_hr_resignation.group_reporting_manager'):
			if employee == self._uid:
				button_bool = True
				self.button_check = button_bool
			else:
				if self.employee.parent_id.user_id.id == self._uid:
					self.button_check = button_bool
				else:
					self.button_check = button_bool 

	@api.multi
	def save_exit(self):
		for recs in self:
			for rec in recs.annual_goalsheet_lines:
				if rec.answers == '' or rec.answers == False:
					raise ValidationError(_("Kindly fill Goalsheet!"))
			self.write({'review_start_date':self.year.start_date,'review_end_date':self.year.end_date,'goalsheet_id':self.main_id,'readonly_chk':True,'application_date':datetime.now().date()})
		self.status = 'pending'
		self.status_char = 'Pending'

	@api.multi
	def approve(self):
		for recs in self:
			res_user = self.env['res.users'].search([('id', '=', self._uid)])
			if recs.employee.user_id.id==res_user.id:
				raise ValidationError(_("Access Denied to approve your own Goalsheet!"))
		search_hierarchy = self.env['employee.reporting.hierarchy'].search([('name','=',self.employee.id)])
		employee = self.env['hr.employee'].search([('user_id','=',self._uid)])
		status_char = 'Approved By '+employee.name
		if search_hierarchy.reportee_2.id!=False:
			self.status = 'pending'
			self.approve2 = True
			self.status_char = status_char
			self.write({'review_start_date':self.year.start_date,'review_end_date':self.year.end_date,'approved_date':datetime.now().date(),'approve1_char':status_char,'select':False})
		elif search_hierarchy.reportee_3.id!=False:
			self.status = 'pending'
			self.approve3 = True
			self.status_char = status_char
			self.write({'review_start_date':self.year.start_date,'review_end_date':self.year.end_date,'approved_date':datetime.now().date(),'approve1_char':status_char,'select':False})
		elif search_hierarchy.hr_reportee.id!=False:
			self.status = 'pending'
			self.approve_hr = True
			self.status_char = status_char
			self.write({'review_start_date':self.year.start_date,'review_end_date':self.year.end_date,'approved_date':datetime.now().date(),'approve1_char':status_char,'select':False})
		else:
			self.status = 'approved'			
			self.write({'review_start_date':self.year.start_date,'review_end_date':self.year.end_date,'approved_date':datetime.now().date(),'select':False,'status_char':'Approved','approve1_char':status_char})
		# self.status = 'approved'

	@api.multi
	def approve_2(self):
		search_hierarchy = self.env['employee.reporting.hierarchy'].search([('name','=',self.employee.id)])
		employee = self.env['hr.employee'].search([('user_id','=',self._uid)])
		status_char = 'Approved By '+employee.name
		if search_hierarchy.reportee_3.id!=False:
			self.approve3 = True
			self.status = 'pending'
			self.status_char = status_char
			self.write({'approve2_char':status_char,'select':False})
		elif search_hierarchy.hr_reportee.id!=False:
			self.approve_hr = True
			self.status = 'pending'
			self.status_char = status_char
			self.write({'approve2_char':status_char,'select':False})
		else:
			self.status = 'approved'
			self.write({'approved_date':datetime.now().date(),'select':False,'status_char':'Approved','approve2_char':status_char})

	@api.multi
	def approve_3(self):	
		search_hierarchy = self.env['employee.reporting.hierarchy'].search([('name','=',self.employee.id)])
		employee = self.env['hr.employee'].search([('user_id','=',self._uid)])
		status_char = 'Approved By '+employee.name
		if search_hierarchy.hr_reportee.id!=False:
			self.status = 'pending'
			self.approve_hr = True
			self.status_char = status_char
			self.write({'approve3_char':status_char,'select':False})
		else:
			self.status = 'approved'
			self.write({'approved_date':datetime.now().date(),'select':False,'status_char':'Approved','approve3_char':status_char})

	@api.multi
	def hr_approve(self):
		self.status = 'approved'
		employee = self.env['hr.employee'].search([('user_id','=',self._uid)])
		status_char = 'Approved By '+employee.name
		self.write({'approved_date':datetime.now().date(),'select':False,'status_char':'Approved','approve4_char':status_char})


	@api.multi
	def reject(self):
		for recs in self:
			res_user = self.env['res.users'].search([('id', '=', self._uid)])
			if recs.employee.user_id.id==res_user.id:
				raise ValidationError(_("Access Denied to reject your own Goalsheet!"))
			self.write({'rejected_date':datetime.now().date(),'select':False})
		self.status = 'rejected'
		self.status_char = 'Rejected'

class AnnualAppraisalQuestions(models.Model):
	_name = "annual.appraisal.questions"

	annual_appraisalline_id = fields.Many2one('annual.appraisal.details','Annual Questions')
	questions = fields.Text('Questions')
	answers = fields.Text('Answers')
	questions_id = fields.Many2one('kra.questions','KRA questions')

class AnnualAttributes(models.Model):
	_name = "annual.attributes"

	annual_attribute_id = fields.Many2one('annual.appraisal.details','Annual Attributes')
	attributes = fields.Char('Attributes')
	self_rating = fields.Float('Self Rating')
	team_leader_rating = fields.Float('Team Leader Rating')
	comments = fields.Char('Comments')
	attributes_id = fields.Many2one('behavioural.attributes','Attributes')
	check1 = fields.Boolean('',compute="get_user")
	check2 = fields.Boolean('',compute="get_user")
	status = fields.Selection([('pending','Pending'),('approved','Approved'),('rejected','Rejected')],'Status')

	def get_user(self):
		for each in self:
			employee = each.annual_attribute_id.employee.user_id.id
			res_user = self.env['res.users'].search([('id', '=', each._uid)])
			if res_user.has_group('hr.group_hr_manager') or res_user.has_group('hr.group_hr_user') or res_user.has_group('orient_hr_resignation.group_reporting_manager'):
				if employee == res_user.id:
					each.check1 = True
					each.check2 = False
				else:
					if each.annual_attribute_id.employee.parent_id.user_id.id == res_user.id:
						each.check1 = False
						each.check2 = True
					else:
						each.check1 = True
						each.check2 = False
			else:
				each.check1 = True
				each.check2 = False

class AnnualAppraisalDetails(models.Model):
	_name = 'annual.appraisal.details'

	appraisal_detail_id = fields.Many2one('annual.review','Annual Appraisal')
	select = fields.Boolean('Select')
	year = fields.Many2one('year.master','Year')
	review_start_date = fields.Date('Review Start Date')
	review_end_date = fields.Date('Review End Date')
	status = fields.Selection([('pending','Pending'),('approved','Approved'),('rejected','Rejected')],'Status')
	status_char = fields.Char('Status')
	employee_code = fields.Char('Employee Code')
	employee = fields.Many2one('hr.employee','Employee Name')
	location = fields.Many2one('res.company','Location')
	designation = fields.Many2one('hr.job', 'Designation')
	department = fields.Many2one('hr.department','Department')
	joining_date = fields.Date('Joining Date')
	main_id = fields.Char('Main ID')
	reporting_head = fields.Many2one('hr.employee','Reporting Head')
	review_cycle = fields.Selection([('January','January'),('July','July')],'Review Cycle')
	readonly_chk = fields.Boolean('Readonly')
	annual_appraisalsheet_lines = fields.One2many('annual.appraisal.questions','annual_appraisalline_id','Annual Appraisal')
	annual_attributes_lines = fields.One2many('annual.attributes','annual_attribute_id','Annual Attributes')
	increment = fields.Boolean('Increment')
	recognition = fields.Boolean('Recognition')
	sec_emp = fields.Boolean('Secure Employment')
	creative_work = fields.Boolean('Creative and Challenging Work')
	designation_choice = fields.Boolean('Designation')
	role_exp = fields.Boolean('Role Expansion')
	promotion = fields.Boolean('Promotion')
	training = fields.Boolean('Training and Development')
	last_year = fields.Char('',default="2019")
	current_year = fields.Char('',default="2020")
	next_year = fields.Char('',default="2021")
	designation_last = fields.Char('')
	designation_current = fields.Char('')
	designation_next = fields.Char('')
	salary_last = fields.Char('')
	salary_current = fields.Char('')
	salary_next = fields.Char('')	
	excellent = fields.Boolean('Excellent')
	good = fields.Boolean('Good')
	scope = fields.Boolean('No Scope')
	approved_date = fields.Date('Approved Date')
	application_date = fields.Date('Application Date')
	rejected_date = fields.Date('Rejected Date')
	site_id = fields.Many2one('site.master','Site')
	comments = fields.Text('Comments')
	approve2 = fields.Boolean('Approve2', default=False)
	approve3 = fields.Boolean('Approve3', default=False)
	approve_hr = fields.Boolean('Approve HR', default=False)
	approve1_char = fields.Char('Approve1 Char')
	approve2_char = fields.Char('Approve2 Char')
	approve3_char = fields.Char('Approve3 Char')
	approve4_char = fields.Char('Approve4 Char')
	button_check = fields.Boolean('button_check', compute='_get_user')
	show = fields.Boolean('Show?',default=False)

	def _get_user(self):
		button_bool = False
		employee= self.employee.user_id.id
		res_user = self.env['res.users'].search([('id', '=', self._uid)])
		if res_user.has_group('hr.group_hr_manager') or res_user.has_group('hr.group_hr_user') or res_user.has_group('orient_hr_resignation.group_reporting_manager'):
			if employee == self._uid:
				button_bool = True
				self.button_check = button_bool
			else:
				if self.employee.parent_id.user_id.id == self._uid:
					self.button_check = button_bool
				else:
					self.button_check = button_bool

	@api.multi
	def save_exit(self):
		for recs in self:
			for rec in recs.annual_appraisalsheet_lines:
				if rec.answers == '' or rec.answers == False:
					raise ValidationError(_("Kindly fill Answers in the Appraisal Form!"))
			for rec in recs.annual_attributes_lines:
				if rec.self_rating == 0.0 or rec.self_rating > 4.0:
					raise ValidationError(_("Kindly give proper Self Rating!"))
				rec.write({'status':'pending'})
			self.write({'application_date':datetime.now().date(),'appraisal_detail_id':self.main_id,'readonly_chk':True})
		self.status = 'pending'
		self.status_char = 'Pending'

	@api.multi
	def approve(self):
		for recs in self:
			for rec in recs.annual_attributes_lines:
				# if rec.status=='pending':
				if rec.team_leader_rating == 0.0 or rec.team_leader_rating > 4.0: 
					raise ValidationError(_("Kindly give proper Team Leader Rating!"))

		search_hierarchy = self.env['employee.reporting.hierarchy'].search([('name','=',self.employee.id)])
		employee = self.env['hr.employee'].search([('user_id','=',self._uid)])
		status_char = 'Approved By '+employee.name
		if search_hierarchy.reportee_2.id!=False:
			self.status = 'pending'
			self.approve2 = True
			self.status_char = status_char
			self.write({'approve1_char':status_char,'select':False})
		elif search_hierarchy.reportee_3.id!=False:
			self.status = 'pending'
			self.approve3 = True
			self.status_char = status_char
			self.write({'approve1_char':status_char,'select':False})
		elif search_hierarchy.hr_reportee.id!=False:
			self.status = 'pending'
			self.approve_hr = True
			self.status_char = status_char
			self.write({'approve1_char':status_char,'select':False})
		else:
			self.status = 'approved'			
			for rec in self.annual_attributes_lines:
				rec.status='approved'
			self.write({'approved_date':datetime.now().date(),'select':False,'status_char':'Approved','approve1_char':status_char})

	@api.multi
	def approve_2(self):
		search_hierarchy = self.env['employee.reporting.hierarchy'].search([('name','=',self.employee.id)])
		employee = self.env['hr.employee'].search([('user_id','=',self._uid)])
		status_char = 'Approved By '+employee.name
		if search_hierarchy.reportee_3.id!=False:
			self.approve3 = True
			self.status = 'pending'
			self.status_char = status_char
			self.write({'approve2_char':status_char,'select':False})
		elif search_hierarchy.hr_reportee.id!=False:
			self.approve_hr = True
			self.status = 'pending'
			self.status_char = status_char
			self.write({'approve2_char':status_char,'select':False})
		else:
			self.status = 'approved'
			for rec in self.annual_attributes_lines:
				rec.status='approved'
			self.write({'approved_date':datetime.now().date(),'select':False,'status_char':'Approved','approve2_char':status_char})

	@api.multi
	def approve_3(self):	
		search_hierarchy = self.env['employee.reporting.hierarchy'].search([('name','=',self.employee.id)])
		employee = self.env['hr.employee'].search([('user_id','=',self._uid)])
		status_char = 'Approved By '+employee.name
		if search_hierarchy.hr_reportee.id!=False:
			self.status = 'pending'
			self.approve_hr = True
			self.status_char = status_char
			self.write({'approve3_char':status_char,'select':False})
		else:
			self.status = 'approved'
			for rec in self.annual_attributes_lines:
				rec.status='approved'
			self.write({'approved_date':datetime.now().date(),'select':False,'status_char':'Approved','approve3_char':status_char})

	@api.multi
	def hr_approve(self):
		self.status = 'approved'
		employee = self.env['hr.employee'].search([('user_id','=',self._uid)])
		status_char = 'Approved By '+employee.name
		for rec in self.annual_attributes_lines:
			rec.status='approved'
		self.write({'approved_date':datetime.now().date(),'select':False,'status_char':'Approved','approve4_char':status_char})


	@api.multi
	def reject(self):
		for recs in self:
			self.write({'rejected_date':datetime.now().date(),'select':False})
		self.status = 'rejected'
		self.status_char = 'Rejected'

class AnnualKraDetails(models.Model):
	_name = 'annual.kra.details'

	annual_kra_id = fields.Many2one('annual.review','Annual Appraisal')
	select = fields.Boolean('Select')
	year = fields.Many2one('year.master','Year')
	review_start_date = fields.Date('Review Start Date')
	review_end_date = fields.Date('Review End Date')
	status = fields.Selection([('pending','Pending'),('approved','Approved'),('rejected','Rejected')],'Status')
	status_char = fields.Char('Status')
	employee_code = fields.Char('Employee Code')
	employee = fields.Many2one('hr.employee','Employee Name')
	location = fields.Many2one('res.company','Location')
	designation = fields.Many2one('hr.job', 'Designation')
	department = fields.Many2one('hr.department','Department')
	joining_date = fields.Date('Joining Date')
	main_id = fields.Char('Main ID')
	reporting_head = fields.Many2one('hr.employee','Reporting Head')
	review_cycle = fields.Selection([('January','January'),('July','July')],'Review Cycle')
	readonly_chk = fields.Boolean('Readonly')
	annual_kra_lines = fields.One2many('annual.kra','annual_kra_id','')
	all_quarter_details = fields.One2many('kra.main','all_kra_id','')
	cba_details = fields.One2many('critical.behaviour.attributes','cba_id','')
	cba_lines = fields.One2many('critical.behaviour.lines','cbl_id','')
	assist_managers_bool = fields.Boolean('Asst. Managers and Above')
	average_quarter_rating = fields.Float('Quarter Average Rating')
	final_rating = fields.Float('Rating',store=True)
	hr_rating = fields.Float('HR Rating')
	manager_rating = fields.Float('Manager Rating')
	approved_date = fields.Date('Approved Date')
	application_date = fields.Date('Application Date')
	rejected_date = fields.Date('Rejected Date')
	approve2 = fields.Boolean('Approve2', default=False)
	approve3 = fields.Boolean('Approve3', default=False)
	approve_hr = fields.Boolean('Approve HR', default=False)
	hr_total_rating = fields.Float('HR Rating')
	reportee1_total_rating = fields.Float('Reportee1 Rating')
	reportee2_total_rating = fields.Float('Reportee2 Rating')
	reportee3_total_rating = fields.Float('Reportee3 Rating')
	hr_total_cb = fields.Float('HR CB')
	reportee1_total_cb = fields.Float('R1 CB')
	reportee2_total_cb = fields.Float('R2 CB')
	reportee3_total_cb = fields.Float('R3 CB')
	sum_ikra = fields.Float('Sum IKRA')
	sum_iar = fields.Float('Sum IAR')
	final_weightage = fields.Float('Final Weightage')
	site_id = fields.Many2one('site.master','Site')
	proposed_increment = fields.Char('Proposed Increment')
	actual_increment = fields.Float('Actual Increment')
	increment_status = fields.Selection([('not_updated','Not Updated'),('updated','Updated')],'Increment Status',default='not_updated')
	reporting_levels = fields.Integer('No of Reporting Levels')
	current_gross = fields.Float('Current Gross Salary')
	current_ctc = fields.Float('Current CTC')
	inc_child_list_id1 = fields.Many2one('increment.child.list','')
	comments = fields.Text('Comments')
	approve1_char = fields.Char('Approve1 Char')
	approve2_char = fields.Char('Approve2 Char')
	approve3_char = fields.Char('Approve3 Char')
	approve4_char = fields.Char('Approve4 Char')
	reportee1_name = fields.Char('Reportee1')
	reportee2_name = fields.Char('Reportee2')
	reportee3_name = fields.Char('Reportee3')
	reportee4_name = fields.Char('Reportee4')
	button_check = fields.Boolean('button_check', compute='_get_user')
	check1 = fields.Boolean('self check', compute='get_user')
	check2 = fields.Boolean('hr check', compute='get_user')
	rp2_check = fields.Boolean('reportee2 check', compute='get_user')
	rp3_check = fields.Boolean('reportee3 check', compute='get_user')
	tl_check = fields.Boolean('tl check', compute='get_user')

	def get_user(self):
		for each in self:
			employee = each.annual_kra_id.employee.user_id.id
			print(employee)
			res_user = self.env['res.users'].search([('id', '=', each._uid)])
			print(res_user.id, employee,'iddddddddddddd')
			check2 = False
			check1 = False
			tl_check = False
			rp2_check= False
			rp3_check = False
			
			each.check2 = False
			each.check1 = False
			each.tl_check = False
			each.rp2_check= False
			each.rp3_check = False
			if res_user.has_group('hr.group_hr_manager') or res_user.has_group('hr.group_hr_user'):
				print("hr checkkkkkkkkkkkkkkkk")
				if employee == res_user.id:
					check1 = True
				elif each.annual_kra_id.employee.parent_id.user_id.id == res_user.id:
					tl_check = True
				elif each.annual_kra_id.employee.parent_id.parent_id.user_id.id == res_user.id:
					rp2_check = True
				elif each.annual_kra_id.employee.parent_id.parent_id.parent_id.user_id.id == res_user.id:
					rp3_check = True
				else:
					if each.annual_kra_id.employee.hr_executive_id.user_id.id == res_user.id:
						check2 = True
					else:
						check2 = False

			elif res_user.has_group('orient_hr_resignation.group_reporting_manager'):
				if employee == res_user.id:
					check1 = True
				else:
					if each.annual_kra_id.employee.parent_id.user_id.id == res_user.id:
						print("tl checkkkkkkkkkkkkkkkk")
						tl_check = True
					else:
						tl_check = False

				if employee == res_user.id:
					check1 = True
				else:
					if each.annual_kra_id.employee.parent_id.parent_id.user_id.id == res_user.id:
						print("rp2_check checkkkkkkkkkkkkkkkk")
						rp2_check = True
					else:
						rp2_check = False

				if employee == res_user.id:
					check1 = True
				else:
					if each.annual_kra_id.employee.parent_id.parent_id.parent_id.user_id.id == res_user.id:
						print("rp3_check checkkkkkkkkkkkkkkkk")
						rp3_check = True
					else:
						rp3_check = False	
			else:
				if employee == res_user.id:
					print("self checkkkkkkkkkkkkkkkk")
					check1 = True
				else:
					check1 = False
			
			if check1 == True and tl_check == False and rp2_check == False and rp3_check == False and check2 == False :
				each.check1 = True
			elif check1 == False and tl_check == True and rp2_check == False and rp3_check == False and check2 == False:
				each.tl_check = True
			elif check1 == False and tl_check == False and rp2_check == True and rp3_check == False and check2 == False:
				each.rp2_check = True
			elif check1 == False and tl_check == False and rp2_check == False and rp3_check == True and check2 == False:
				each.rp3_check = True
			elif check1 == False and tl_check == False and rp2_check == False and rp3_check == False and check2 == True:
				each.check2 = True
			print(each.check1,each.tl_check,each.rp2_check,each.rp3_check,each.check2,'checkssss')


	def _get_user(self):
		button_bool = False
		employee= self.employee.user_id.id
		res_user = self.env['res.users'].search([('id', '=', self._uid)])
		if res_user.has_group('hr.group_hr_manager') or res_user.has_group('hr.group_hr_user') or res_user.has_group('orient_hr_resignation.group_reporting_manager'):
			if employee == self._uid:
				button_bool = True
				self.button_check = button_bool
			else:
				if self.employee.parent_id.user_id.id == self._uid:
					self.button_check = button_bool
				else:
					self.button_check = button_bool

	@api.onchange('assist_managers_bool')
	def onchange_assist_managers_bool(self):
		res = {'cba_lines':self.cba_lines}
		if self.assist_managers_bool:
			if self.cba_lines:
				for x in self.cba_lines:
					self.update({'cba_lines':[(0,0,{'cbl_id':self._origin.id,'description':'Communication Skills'}),
						(0,0,{'cbl_id':self._origin.id,'description':'Relationship Maintaining & Building'}),
						(0,0,{'cbl_id':self._origin.id,'description':'Time Management'}),
						(0,0,{'cbl_id':self._origin.id,'description':'Client Orientation'}),
						(0,0,{'cbl_id':self._origin.id,'description':'Result Orientation'}),
						(0,0,{'cbl_id':self._origin.id,'description':'Team Work'}),
						(0,0,{'cbl_id':self._origin.id,'description':'Leadership*'}),
						(0,0,{'cbl_id':self._origin.id,'description':'Business Acumen*'})]})
		if not self.assist_managers_bool:
			if self.cba_lines:
				for x in self.cba_lines:
					self.update({'cba_lines':[(0,0,{'cbl_id':self._origin.id,'description':'Communication Skills'}),
						(0,0,{'cbl_id':self._origin.id,'description':'Relationship Maintaining & Building'}),
						(0,0,{'cbl_id':self._origin.id,'description':'Time Management'}),
						(0,0,{'cbl_id':self._origin.id,'description':'Client Orientation'}),
						(0,0,{'cbl_id':self._origin.id,'description':'Result Orientation'}),
						(0,0,{'cbl_id':self._origin.id,'description':'Team Work'})]})
		return res

	@api.multi
	def save_exit(self):
		for recs in self:
			if recs.year.id == '' or recs.year.id == None or recs.year.id == False:
				raise ValidationError(_("Kindly select Year!"))
			self.write({'application_date':datetime.now().date(),'annual_kra_id':self.main_id,'readonly_chk':True})
			cba_ids = []
			for cba in recs.cba_lines:
				cba_ids.append(cba.id)
			if recs.cba_lines:
				if not recs.assist_managers_bool:
					cbl_rec0 = self.env['critical.behaviour.lines'].browse(cba_ids[0])
					cbl_rec1 = self.env['critical.behaviour.lines'].browse(cba_ids[1])
					cbl_rec2 = self.env['critical.behaviour.lines'].browse(cba_ids[2])
					cbl_rec3 = self.env['critical.behaviour.lines'].browse(cba_ids[3])
					cbl_rec4 = self.env['critical.behaviour.lines'].browse(cba_ids[4])
					cbl_rec5 = self.env['critical.behaviour.lines'].browse(cba_ids[5])
					cbl_rec0.write({'description':'Communication Skills'})
					cbl_rec1.write({'description':'Relationship Maintaining & Building'})
					cbl_rec3.write({'description':'Time Management'})
					cbl_rec2.write({'description':'Client Orientation'})					
					cbl_rec4.write({'description':'Result Orientation'})
					cbl_rec5.write({'description':'Team Work'})
				if recs.assist_managers_bool:
					cbl_rec0 = self.env['critical.behaviour.lines'].browse(cba_ids[0])
					cbl_rec1 = self.env['critical.behaviour.lines'].browse(cba_ids[1])
					cbl_rec2 = self.env['critical.behaviour.lines'].browse(cba_ids[2])
					cbl_rec3 = self.env['critical.behaviour.lines'].browse(cba_ids[3])
					cbl_rec4 = self.env['critical.behaviour.lines'].browse(cba_ids[4])
					cbl_rec5 = self.env['critical.behaviour.lines'].browse(cba_ids[5])
					cbl_rec6 = self.env['critical.behaviour.lines'].browse(cba_ids[6])
					cbl_rec7 = self.env['critical.behaviour.lines'].browse(cba_ids[7])
					cbl_rec0.write({'description':'Communication Skills'})
					cbl_rec1.write({'description':'Relationship Maintaining & Building'})
					cbl_rec3.write({'description':'Time Management'})
					cbl_rec2.write({'description':'Client Orientation'})					
					cbl_rec4.write({'description':'Result Orientation'})
					cbl_rec5.write({'description':'Team Work'})
					cbl_rec6.write({'description':'Leadership*'})
					cbl_rec7.write({'description':'Business Acumen*'})
			for cba in recs.cba_lines:
				if cba.self_rating == 0.0 or cba.self_rating > 5.0:
					raise ValidationError(_("Kindly give proper Self Rating in Critical Behaviour Attributes!"))
			for kpi in recs.annual_kra_lines:
				# if kpi.emp_rating<=0:
				# 	raise ValidationError(_("Self Rating cannot be 0"))
				if kpi.self_rating >kpi.weightage:
					raise ValidationError(_("Self Rating cannot be greater than the weightage in KRA/KPI form"))
			check = False
			for kpi in recs.annual_kra_lines:
				if kpi.self_rating>0:
					check = True
					break
			if check == False:
				raise ValidationError(_("Self Rating cannot be 0 for all KRA's in KRA/KPI form"))
			rating_list = []
			final_rating=0.0
			if recs.all_quarter_details:
				for x in recs.all_quarter_details:
					rating_list.append(x.final_rating)
			length = len(rating_list)
			if length != 0:
				final_rating = round(sum(rating_list)/length,2)
		self.write({'average_quarter_rating': final_rating})
		self.status = 'pending'
		self.status_char = 'Pending'

	@api.multi
	def approve1(self):
		kra_rating_obj = self.env['kra.rating']
		reportee1_total_rating = 0.0
		reportee1_total_cb = 0.0
		assist_managers_bool = False
		cba_count = 6
		if self.assist_managers_bool:
			assist_managers_bool = True
			cba_count = 8
		employee = self.env['hr.employee'].search([('user_id','=',self._uid)])
		status_char = 'Approved By '+employee.name
		for recs in self:
			if recs.cba_lines:
				for cba in recs.cba_lines:
					if cba.tl_rating <= 0.0:
						raise ValidationError(_("Kindly give Reportee1 Rating in Critical Behaviour Attributes!"))
					if cba.tl_rating > 5.0:
						raise ValidationError(_("Kindly give Reportee1 Rating in a scale of 1 to 5!"))
					reportee1_total_cb += cba.tl_rating
		for kpi in self.annual_kra_lines:
				# if kpi.emp_rating<=0:
				# 	raise ValidationError(_("Self Rating cannot be 0"))
			if kpi.reportee1_rating >kpi.weightage:
				raise ValidationError(_("TL Rating cannot be greater than the weightage in KRA/KPI form"))
		check = False
		for kpi in self.annual_kra_lines:
			if kpi.reportee1_rating>0:
				check = True
				break
		if check == False:
			raise ValidationError(_("TL Rating cannot be 0 for all KRA's in KRA/KPI form"))
		total_reportee1_rating = 0.0
		if check:
			for kpi in self.annual_kra_lines:
				total_reportee1_rating+=float(kpi.reportee1_rating)
		check_record = self.env['kra.main'].search([('employee_code','=',self.employee_code),('kra_year','=',16),('quarter','=','Fourth'),('state','!=','cancel')])
		total_weightage = 0.0
		if check_record:
			scale_new= self.env['appraisal.scale'].search([('minimum','<=',float(total_reportee1_rating)),('maximum','>=',float(total_reportee1_rating))])
			check_record.write({'final_rating':scale_new.scale,'pip_applicable':scale_new.pip_applicable,'all_kra_id':self.id,'state':'done'})
		else:
			emp_kra = self.env['kra.main'].create({
						'employee':self.employee.id,
						'company_id':1,
						'employee_code':self.employee_code,
						'designation':self.designation.id,
						'department':self.department.id,
						'location':self.employee.company_id.id,
						'kra_year':16,
						'quarter':'Fourth',
						'active':True,
						'review_start_date':'2019-01-01',
						'review_end_date':'2019-03-31',
						'check1': False,
						'state': 'done',
						'application_date': str(datetime.now().date()),	
						'kra_month': 'June',						
						})
			total_weightage = 0.0
			for kpi in self.annual_kra_lines:
				create_id = kra_rating_obj.create({
									'kra_name':kpi.kra_name,
									'description':kpi.kpi,
									'weightage':kpi.weightage,
									'man_rating':kpi.reportee1_rating,
									'emp_rating':kpi.self_rating,
									'kra_id':self.env['kra.main'].browse(emp_kra.id).id,
									'check1':False,
									})
				total_weightage+=float(kpi.reportee1_rating)
			total_weightage = round(total_weightage)
			print (total_weightage,'total_weightagemmmmmmmmmmmmm')
			scale_new= self.env['appraisal.scale'].search([('minimum','<=',float(total_weightage)),('maximum','>=',float(total_weightage))])
			emp_kra.write({'final_rating':scale_new.scale,'pip_applicable':scale_new.pip_applicable,'all_kra_id':self.id})
		rating_list = []
		if self.all_quarter_details:
			for x in self.all_quarter_details:
				rating_list.append(x.final_rating)
		length = len(rating_list)
		final_rating = round(sum(rating_list)/length,2)
		self.write({'average_quarter_rating': final_rating})
		search_hierarchy = self.env['employee.reporting.hierarchy'].search([('name','=',self.employee.id)])
		if search_hierarchy.reportee_2.id!=False:
			self.status = 'pending'
			self.approve2 = True
			self.status_char = status_char
			self.write({'approve1_char':status_char,'select':False})
		elif search_hierarchy.reportee_3.id!=False:
			self.status = 'pending'
			self.approve3 = True
			self.status_char = status_char
			self.write({'approve1_char':status_char,'select':False})
		elif search_hierarchy.hr_reportee.id!=False:
			self.status = 'pending'
			self.approve_hr = True
			self.status_char = status_char
			self.write({'approve1_char':status_char,'select':False})
		else:
			self.write({
			'reportee1_total_rating':self.average_quarter_rating,
			'reportee1_total_cb':round(reportee1_total_cb/cba_count,2)})
			count=0
			if self.average_quarter_rating!=0.0:
				count+=1
			sum_ikra = round(self.average_quarter_rating/count,2)
			count1=0
			if reportee1_total_cb!=0.0:
				count1+=1
			sum_iar = round(self.reportee1_total_cb/count1,2)
			search_hierarchy = self.env['employee.reporting.hierarchy'].search([('name','=',self.employee.id)])
			final_weightage = round(((sum_ikra*0.8) + (sum_iar*0.2)),2)
			search_scale = self.env['increment.scale'].search([('minimum_weightage','<=',float(final_weightage)),('maximum_weightage','>=',float(final_weightage))])
			proposed_increment = str(search_scale.minimum_increment) + ' - ' + str(search_scale.maximum_increment) + '%'
			self.status = 'approved'
			self.write({'status_char':'Approved','select':False,'approve1_char':status_char,'approved_date':datetime.now().date(),'sum_ikra':sum_ikra,'sum_iar':sum_iar,'final_weightage':final_weightage,'proposed_increment':proposed_increment})

	@api.multi
	def approve_2(self):
		reportee1_total_rating = 0.0
		reportee2_total_rating = 0.0
		reportee1_total_cb = 0.0
		reportee2_total_cb = 0.0
		assist_managers_bool = False
		cba_count = 6
		if self.assist_managers_bool:
			assist_managers_bool = True
			cba_count = 8
		employee = self.env['hr.employee'].search([('user_id','=',self._uid)])
		status_char = 'Approved By '+employee.name
		for recs in self:			
			if recs.cba_lines:
				for cba in recs.cba_lines:
					if cba.reportee2_rating <= 0.0:
						raise ValidationError(_("Kindly give Reportee2 Rating in Critical Behaviour Attributes!"))
					if cba.reportee2_rating > 5.0:
						raise ValidationError(_("Kindly give Reportee2 Rating in a scale of 1 to 5!"))
					reportee1_total_cb += cba.tl_rating
					reportee2_total_cb += cba.reportee2_rating
				for kra in recs.annual_kra_lines:
					if kra.reportee2_rating == 0.0:
						raise ValidationError(_("Kindly give Reportee2 Rating for Employee's KRA!"))
					reportee2_total_rating += kra.reportee2_rating
		search_hierarchy = self.env['employee.reporting.hierarchy'].search([('name','=',self.employee.id)])
		reportee2_weightage = get_appraisal_scale(self,reportee2_total_rating)
		if search_hierarchy.reportee_3.id!=False:
			self.approve3 = True
			self.status = 'pending'
			self.status_char = status_char
			self.write({'approve2_char':status_char,'select':False})
		elif search_hierarchy.hr_reportee.id!=False:
			self.approve_hr = True
			self.status = 'pending'
			self.status_char = status_char
			self.write({'approve2_char':status_char,'select':False})
		else:
			self.write({
			'reportee1_total_rating':self.average_quarter_rating,
			'reportee1_total_cb':round(reportee1_total_cb/cba_count,2),
			'reportee2_total_rating':reportee2_weightage,
			'reportee2_total_cb':round(reportee2_total_cb/cba_count,2)})
			count=0
			if self.average_quarter_rating!=0.0:
				count+=1
			if reportee2_total_rating!=0.0:
				count+=1
			sum_ikra = round((self.average_quarter_rating+self.reportee2_total_rating)/count,2)
			count1=0
			if reportee1_total_cb!=0.0:
				count1+=1
			if reportee2_total_cb!=0.0:
				count1+=1
			sum_iar = round((self.reportee1_total_cb+self.reportee2_total_cb)/count1,2)
			search_hierarchy = self.env['employee.reporting.hierarchy'].search([('name','=',self.employee.id)])
			final_weightage = round(((sum_ikra*0.8) + (sum_iar*0.2)),2)
			print (final_weightage)
			search_scale = self.env['increment.scale'].search([('minimum_weightage','<=',float(final_weightage)),('maximum_weightage','>=',float(final_weightage))])
			print (search_scale,'ppp')
			proposed_increment = str(search_scale.minimum_increment) + ' - ' + str(search_scale.maximum_increment) + '%'
			self.write({'status_char':'Approved','select':False,'approve2_char':status_char,'approved_date':datetime.now().date(),'sum_ikra':sum_ikra,'sum_iar':sum_iar,'final_weightage':final_weightage,'proposed_increment':proposed_increment})

	@api.multi
	def approve_3(self):
		reportee1_total_rating = 0.0
		reportee2_total_rating = 0.0
		reportee3_total_rating = 0.0
		reportee1_total_cb = 0.0
		reportee2_total_cb = 0.0
		reportee3_total_cb = 0.0
		assist_managers_bool = False
		cba_count = 6
		if self.assist_managers_bool:
			assist_managers_bool = True
			cba_count = 8
		employee = self.env['hr.employee'].search([('user_id','=',self._uid)])
		status_char = 'Approved By '+employee.name
		for recs in self:
			if recs.cba_lines:
				for cba in recs.cba_lines:
					if cba.reportee3_rating <= 0.0:
						raise ValidationError(_("Kindly give Reportee3 Rating in Critical Behaviour Attributes!"))
					if cba.reportee3_rating > 5.0:
						raise ValidationError(_("Kindly give Reportee3 Rating in a scale of 1 to 5!"))
					reportee1_total_cb += cba.tl_rating
					reportee2_total_cb += cba.reportee2_rating
					reportee3_total_cb += cba.reportee3_rating
				for kra in recs.annual_kra_lines:
					if kra.reportee3_rating == 0.0:
						raise ValidationError(_("Kindly give Reportee3 Rating for Employee's KRA!"))
					reportee2_total_rating += kra.reportee2_rating
					reportee3_total_rating += kra.reportee3_rating
		search_hierarchy = self.env['employee.reporting.hierarchy'].search([('name','=',self.employee.id)])
		reportee2_weightage = get_appraisal_scale(self,reportee2_total_rating)
		reportee3_weightage = get_appraisal_scale(self,reportee3_total_rating)
		if search_hierarchy.hr_reportee.id!=False:
			self.status = 'pending'
			self.approve_hr = True
			self.status_char = status_char
			self.write({'approve3_char':status_char,'select':False})
		else:
			self.write({
			'reportee1_total_rating':self.average_quarter_rating,
			'reportee1_total_cb':round(reportee1_total_cb/cba_count,2),
			'reportee2_total_rating':reportee2_weightage,
			'reportee2_total_cb':round(reportee2_total_cb/cba_count,2),
			'reportee3_total_rating':reportee3_weightage,
			'reportee3_total_cb':round(reportee3_total_cb/cba_count,2)})
			count=0
			if self.average_quarter_rating!=0.0:
				count+=1
			if reportee2_total_rating!=0.0:
				count+=1
			if reportee3_total_rating!=0.0:
				count+=1
			sum_ikra = round((self.average_quarter_rating+self.reportee2_total_rating+self.reportee3_total_rating)/count,2)
			count1=0
			if reportee1_total_cb!=0.0:
				count1+=1
			if reportee2_total_cb!=0.0:
				count1+=1
			if reportee3_total_cb!=0.0:
				count1+=1
			sum_iar = round((self.reportee1_total_cb+self.reportee2_total_cb+self.reportee3_total_cb)/count1,2)
			search_hierarchy = self.env['employee.reporting.hierarchy'].search([('name','=',self.employee.id)])
			final_weightage = round(((sum_ikra*0.8) + (sum_iar*0.2)),2)
			print (final_weightage)
			search_scale = self.env['increment.scale'].search([('minimum_weightage','<=',float(final_weightage)),('maximum_weightage','>=',float(final_weightage))])
			print (search_scale,'ppp')
			proposed_increment = str(search_scale.minimum_increment) + ' - ' + str(search_scale.maximum_increment) + '%'
			self.status = 'approved'
			employee = self.env['hr.employee'].search([('user_id','=',self._uid)])
			status_char = 'Approved By '+employee.name
			self.write({'status_char':'Approved','select':False,'approve3_char':status_char,'approved_date':datetime.now().date(),'sum_ikra':sum_ikra,'sum_iar':sum_iar,'final_weightage':final_weightage,'proposed_increment':proposed_increment})

	@api.multi
	def hr_approve(self):
		hr_total_rating = 0.0
		reportee1_total_rating = 0.0
		reportee2_total_rating = 0.0
		reportee3_total_rating = 0.0
		hr_total_cb = 0.0
		reportee1_total_cb = 0.0
		reportee2_total_cb = 0.0
		reportee3_total_cb = 0.0
		assist_managers_bool = False
		cba_count = 6
		if self.assist_managers_bool:
			assist_managers_bool = True
			cba_count = 8
		employee = self.env['hr.employee'].search([('user_id','=',self._uid)])
		status_char = 'Approved By '+employee.name
		for recs in self:
			if recs.cba_lines:
				for cba in recs.cba_lines:
					if cba.hr_rating == 0.0:
						raise ValidationError(_("Kindly give HR Rating in Critical Behaviour Attributes!"))
					if cba.hr_rating > 5.0:
						raise ValidationError(_("Kindly give HR Rating in a scale of 1 to 5!"))
					hr_total_cb += cba.hr_rating
					reportee1_total_cb += cba.tl_rating
					reportee2_total_cb += cba.reportee2_rating
					reportee3_total_cb += cba.reportee3_rating
				for kra in recs.annual_kra_lines:
					if kra.hr_rating == 0.0:
						raise ValidationError(_("Kindly give HR Rating for Employee's KRA!"))
					hr_total_rating += kra.hr_rating
					reportee2_total_rating += kra.reportee2_rating
					reportee3_total_rating += kra.reportee3_rating
		hr_weightage = get_appraisal_scale(self,hr_total_rating)
		reportee2_weightage = get_appraisal_scale(self,reportee2_total_rating)
		reportee3_weightage = get_appraisal_scale(self,reportee3_total_rating)
		self.write({'hr_total_rating':hr_weightage,'select':False,
					'reportee1_total_rating':self.average_quarter_rating,
					'reportee2_total_rating':reportee2_weightage,
					'reportee3_total_rating':reportee3_weightage,
					'hr_total_cb':round(hr_total_cb/cba_count,2),
					'reportee1_total_cb':round(reportee1_total_cb/cba_count,2),
					'reportee2_total_cb':round(reportee2_total_cb/cba_count,2),'reportee3_total_cb':round(reportee3_total_cb/cba_count,2)})
		count=0
		if hr_weightage!=0.0:
			count+=1
		if self.average_quarter_rating!=0.0:
			count+=1
		if reportee2_weightage!=0.0:
			count+=1
		if reportee3_weightage!=0.0:
			count+=1
		sum_ikra = round((hr_weightage+self.average_quarter_rating+reportee2_weightage+reportee3_weightage)/count,2)
		count1=0
		if hr_total_cb!=0.0:
			count1+=1
		if reportee1_total_cb!=0.0:
			count1+=1
		if reportee2_total_cb!=0.0:
			count1+=1
		if reportee3_total_cb!=0.0:
			count1+=1
		sum_iar = round((self.hr_total_cb+self.reportee1_total_cb+self.reportee2_total_cb+self.reportee3_total_cb)/count1,2)
		search_hierarchy = self.env['employee.reporting.hierarchy'].search([('name','=',self.employee.id)])
		final_weightage = round(((sum_ikra*0.8) + (sum_iar*0.2)),2)
		print (final_weightage)
		search_scale = self.env['increment.scale'].search([('minimum_weightage','<=',float(final_weightage)),('maximum_weightage','>=',float(final_weightage))])
		print (search_scale,'ppp')
		proposed_increment = str(search_scale.minimum_increment) + ' - ' + str(search_scale.maximum_increment) + '%'
		self.status = 'approved'
		employee = self.env['hr.employee'].search([('user_id','=',self._uid)])
		status_char = 'Approved By '+employee.name
		self.write({'status_char':'Approved','select':False,'approve4_char':status_char,'approved_date':datetime.now().date(),'sum_ikra':sum_ikra,'sum_iar':sum_iar,'final_weightage':final_weightage,'proposed_increment':proposed_increment})

	@api.multi
	def reject(self):
		for recs in self:
			self.write({'rejected_date':datetime.now().date(),'select':False})
		self.status = 'rejected'
		self.status_char = 'Rejected'

	@api.multi
	def admin_approve(self):
		hr_total_rating = 0.0
		reportee1_total_rating = 0.0
		reportee2_total_rating = 0.0
		reportee3_total_rating = 0.0
		hr_total_cb = 0.0
		reportee1_total_cb = 0.0
		reportee2_total_cb = 0.0
		reportee3_total_cb = 0.0
		assist_managers_bool = False
		cba_count = 6
		if self.assist_managers_bool:
			assist_managers_bool = True
			cba_count = 8
		employee = self.env['hr.employee'].search([('user_id','=',self._uid)])
		status_char = 'Approved By '+employee.name
		for recs in self:
			if recs.cba_lines:
				for cba in recs.cba_lines:
					if cba.hr_rating == 0.0:
						raise ValidationError(_("Kindly give HR Rating in Critical Behaviour Attributes!"))
					if cba.hr_rating > 5.0:
						raise ValidationError(_("Kindly give HR Rating in a scale of 1 to 5!"))
					hr_total_cb += cba.hr_rating
					reportee1_total_cb += cba.tl_rating
					reportee2_total_cb += cba.reportee2_rating
					reportee3_total_cb += cba.reportee3_rating
				for kra in recs.annual_kra_lines:
					if kra.hr_rating == 0.0:
						raise ValidationError(_("Kindly give HR Rating for Employee's KRA!"))
					hr_total_rating += kra.hr_rating
					reportee2_total_rating += kra.reportee2_rating
					reportee3_total_rating += kra.reportee3_rating
		hr_weightage = get_appraisal_scale(self,hr_total_rating)
		reportee2_weightage = get_appraisal_scale(self,reportee2_total_rating)
		reportee3_weightage = get_appraisal_scale(self,reportee3_total_rating)
		self.write({'hr_total_rating':hr_weightage,'select':False,
					'reportee1_total_rating':self.average_quarter_rating,
					'reportee2_total_rating':reportee2_weightage,
					'reportee3_total_rating':reportee3_weightage,
					'hr_total_cb':round(hr_total_cb/cba_count,2),
					'reportee1_total_cb':round(reportee1_total_cb/cba_count,2),
					'reportee2_total_cb':round(reportee2_total_cb/cba_count,2),'reportee3_total_cb':round(reportee3_total_cb/cba_count,2)})
		count=0
		if hr_weightage!=0.0:
			count+=1
		if self.average_quarter_rating!=0.0:
			count+=1
		if reportee2_weightage!=0.0:
			count+=1
		if reportee3_weightage!=0.0:
			count+=1
		sum_ikra = round((hr_weightage+self.average_quarter_rating+reportee2_weightage+reportee3_weightage)/count,2)
		count1=0
		if hr_total_cb!=0.0:
			count1+=1
		if reportee1_total_cb!=0.0:
			count1+=1
		if reportee2_total_cb!=0.0:
			count1+=1
		if reportee3_total_cb!=0.0:
			count1+=1
		sum_iar = round((self.hr_total_cb+self.reportee1_total_cb+self.reportee2_total_cb+self.reportee3_total_cb)/count1,2)
		search_hierarchy = self.env['employee.reporting.hierarchy'].search([('name','=',self.employee.id)])
		final_weightage = round(((sum_ikra*0.8) + (sum_iar*0.2)),2)
		print (final_weightage)
		search_scale = self.env['increment.scale'].search([('minimum_weightage','<=',float(final_weightage)),('maximum_weightage','>=',float(final_weightage))])
		print (search_scale,'ppp')
		proposed_increment = str(search_scale.minimum_increment) + ' - ' + str(search_scale.maximum_increment) + '%'
		self.status = 'approved'
		employee = self.env['hr.employee'].search([('user_id','=',self._uid)])
		status_char = 'Approved By '+employee.name
		self.write({'status_char':'Approved','select':False,'approve4_char':status_char,'approved_date':datetime.now().date(),'sum_ikra':sum_ikra,'sum_iar':sum_iar,'final_weightage':final_weightage,'proposed_increment':proposed_increment})


class AnnualAppraisal(models.Model):
	_name = "annual.appraisal"

	annual_appraisal_id = fields.Many2one('annual.review','Annual KRA')
	questions = fields.Text('Questions')
	answers = fields.Text('Answers')

class AnnualBehaviour(models.Model):
	_name = "annual.behaviour"

	annual_behavioural_id = fields.Many2one('annual.review','Annual KRA')
	attributes = fields.Char('Attributes')
	self_rating = fields.Float('Self Rating')
	team_leader_rating = fields.Float('Team Leader Rating')
	comments = fields.Char('Comments')
	check1 = fields.Boolean('check1', compute='get_user')
	check2 = fields.Boolean('check2', compute='get_user')

	def get_user(self):
		for each in self:
			employee = each.annual_behavioural_id.employee.user_id.id
			res_user = self.env['res.users'].search([('id', '=', each._uid)])
			if res_user.has_group('hr.group_hr_manager') or res_user.has_group('hr.group_hr_user') or res_user.has_group('orient_hr_resignation.group_reporting_manager'):
				if employee == res_user.id:
					each.check1 = True
					each.check2 = False
				else:
					if each.annual_behavioural_id.employee.parent_id.user_id.id == res_user.id:
						each.check1 = False
						each.check2 = True
					else:
						each.check1 = True
						each.check2 = False
			else:
				each.check1 = True
				each.check2 = False

class AnnualKra(models.Model):
	_name = "annual.kra"

	annual_kra_id = fields.Many2one('annual.kra.details','Annual KRA')
	kra = fields.Many2one('kra.master','Question')
	kra_name = fields.Char('KRA')
	kpi = fields.Char('KPI')
	weightage = fields.Float('Weightage')
	self_rating = fields.Float('Self Rating')
	hr_rating = fields.Float('HR Rating')
	reportee1_rating = fields.Float('Reportee1 Rating')
	reportee2_rating = fields.Float('Reportee2 Rating')
	reportee3_rating = fields.Float('Reportee3 Rating')
	hr_check = fields.Boolean('HR check', compute = 'get_user')
	rep_check = fields.Boolean('Rep Check', compute = 'get_user')
	check1 = fields.Boolean('self check', compute='get_user')
	check2 = fields.Boolean('hr check', compute='get_user')
	rp2_check = fields.Boolean('reportee2 check', compute='get_user')
	rp3_check = fields.Boolean('reportee3 check', compute='get_user')
	tl_check = fields.Boolean('tl check', compute='get_user')
	readonly_flag =  fields.Boolean('Readonly for Emp',default=False)
	readonly_flag1 = fields.Boolean('Readonly for TL',default=False)

	def get_user(self):
		for each in self:
			employee = each.annual_kra_id.employee.user_id.id
			print(employee)
			res_user = self.env['res.users'].search([('id', '=', each._uid)])
			print(res_user.id, employee,'iddddddddddddd')
			check2 = False
			check1 = False
			tl_check = False
			rp2_check= False
			rp3_check = False
			
			each.check2 = False
			each.check1 = False
			each.tl_check = False
			each.rp2_check= False
			each.rp3_check = False
			if res_user.has_group('hr.group_hr_manager') or res_user.has_group('hr.group_hr_user'):
				print("hr checkkkkkkkkkkkkkkkk")
				if employee == res_user.id:
					check1 = True
				elif each.annual_kra_id.employee.parent_id.user_id.id == res_user.id:
					tl_check = True
				elif each.annual_kra_id.employee.parent_id.parent_id.user_id.id == res_user.id:
					rp2_check = True
				elif each.annual_kra_id.employee.parent_id.parent_id.parent_id.user_id.id == res_user.id:
					rp3_check = True
				else:
					if each.annual_kra_id.employee.hr_executive_id.user_id.id == res_user.id:
						check2 = True
					else:
						check2 = False

			elif res_user.has_group('orient_hr_resignation.group_reporting_manager'):
				if employee == res_user.id:
					check1 = True
				else:
					if each.annual_kra_id.employee.parent_id.user_id.id == res_user.id:
						print("tl checkkkkkkkkkkkkkkkk")
						tl_check = True
					else:
						tl_check = False

				if employee == res_user.id:
					check1 = True
				else:
					if each.annual_kra_id.employee.parent_id.parent_id.user_id.id == res_user.id:
						print("rp2_check checkkkkkkkkkkkkkkkk")
						rp2_check = True
					else:
						rp2_check = False

				if employee == res_user.id:
					check1 = True
				else:
					if each.annual_kra_id.employee.parent_id.parent_id.parent_id.user_id.id == res_user.id:
						print("rp3_check checkkkkkkkkkkkkkkkk")
						rp3_check = True
					else:
						rp3_check = False	
			else:
				if employee == res_user.id:
					print("self checkkkkkkkkkkkkkkkk")
					check1 = True
				else:
					check1 = False
			
			if check1 == True and tl_check == False and rp2_check == False and rp3_check == False and check2 == False :
				each.check1 = True
			elif check1 == False and tl_check == True and rp2_check == False and rp3_check == False and check2 == False:
				each.tl_check = True
			elif check1 == False and tl_check == False and rp2_check == True and rp3_check == False and check2 == False:
				each.rp2_check = True
			elif check1 == False and tl_check == False and rp2_check == False and rp3_check == True and check2 == False:
				each.rp3_check = True
			elif check1 == False and tl_check == False and rp2_check == False and rp3_check == False and check2 == True:
				each.check2 = True
			print(each.check1,each.tl_check,each.rp2_check,each.rp3_check,each.check2,'checkssss')


class AllQuarterKra(models.Model):
	_name = "all.quarter.kra"

	all_kra_id = fields.Many2one('annual.review','Annual KRA')
	kra_main_id = fields.Many2one('kra.main','KRA')
	review_month = fields.Char('Review Month')
	year = fields.Many2one('year.master','Year')
	quarter_rating = fields.Float('Ratings')
	review_start_date = fields.Date('Review Start Date')
	review_end_date = fields.Date('Review End Date')
	state = fields.Char('Status')

class KraMain(models.Model):
	_inherit = "kra.main"

	all_kra_id = fields.Many2one('annual.kra.details','Annual KRA')

class Employee(models.Model):
	_inherit = "hr.employee"

	appraisal_history = fields.One2many('annual.review','employee','Appraisal')

class AnnualReviewStatusReport(models.Model):
	_name = "annual.review.status.report"

	def _get_default_access_token(self):
		return str(uuid.uuid4())

	company_id = fields.Many2one('res.company','Company', default=lambda self: self.env['res.company']._company_default_get('account.invoice'))
	location = fields.Many2one('res.company','Location')
	form_type = fields.Selection([('Goalsheet','Goalsheet Form'),('Appraisal','Appraisal'),('Annual KRA','Annual KRA')],string='Form Sheet',default="Goalsheet")
	financial_year = fields.Many2one('year.master','Financial Year')
	year_of_application = fields.Many2one('year.master.annual','Year Of Application')
	review_cycle = fields.Selection([('January','January'),('July','July')], string="Review Cycle")
	site_id = fields.Many2many('site.master','site_emp_rel', 'emp_site_id', 'site_master_id',string='Location')
	annual_review_one2many = fields.One2many('annual.status.child','review_id','Annual Review Status')
	access_token = fields.Char('Security Token', copy=False,default=_get_default_access_token)

	@api.multi
	def generate_status_excel(self,access_uid=None):
		self.ensure_one()
		return {
		'type': 'ir.actions.act_url',
		'url': '/web/pivot/export_status_xls/%s?access_token=%s' % (self.id, self.access_token),
		'target': 'new',
		}

	@api.onchange('form_type','annual_review_one2many')
	def onchange_form_type(self):
		res = {'annual_review_one2many':None}
		self.write({'annual_review_one2many':[(6, 0, None)]})
		return res

	def search_records(self):

		main_site_id = self.site_id
		form_type = self.form_type
		financial_year = self.financial_year.id
		year_of_application = self.year_of_application
		review_cycle = self.review_cycle
		site_list = []
		print(main_site_id,form_type,financial_year,year_of_application)
		self.env.cr.execute("delete from annual_status_child")
		for x in main_site_id:
			site_list.append(x.id)
		print (site_list)
		if form_type == 'Goalsheet':
			goalsheet_dets = self.env['goalsheet.details'].search([('year','=',financial_year),('site_id','in',site_list),('status','!=','')])
			print(goalsheet_dets,'----')
			for i in self:
				if goalsheet_dets:
					for gs in goalsheet_dets:
						status = ''
						if gs.status=='pending':
							status="Pending"
						if gs.status=='approved':
							status='Approved'
						if gs.status=='rejected':
							status="Rejected"
					
						self.env['annual.status.child'].create({
							'employee_code':gs.employee_code,
							'employee':gs.employee.id,
							'department':gs.department.id,
							'reporting_to':gs.employee.parent_id.id,
							'application_date':gs.application_date,
							'approved_date':gs.approved_date,
							'financial_year':gs.year.id,
							'status':status,
							'review_id':self.id,
							'site_id':gs.employee.site_master_id.id
							})

		if form_type == 'Appraisal':
			appraisal_dets = self.env['annual.appraisal.details'].search([('year','=',financial_year),('site_id','in',site_list),('status','!=',''),('review_cycle','=',review_cycle)])#,
			if appraisal_dets:
				for a in appraisal_dets:
					status = ''
					if a.approve1_char!='':
						status = a.approve1_char
					if a.approve2_char!='':
						status = status +'\n' +a.approve2_char
					if a.approve3_char!='':
						status = status +'\n' +a.approve3_char
					if a.approve4_char!='':
						status = status +'\n' +a.approve4_char
					self.env['annual.status.child'].create({
						'employee_code':a.employee_code,
						'employee':a.employee.id,
						'department':a.department.id,
						'reporting_to':a.employee.parent_id.id,
						'application_date':a.application_date,
						'approved_date':a.approved_date,
						'financial_year':a.year.id,
						'status':status,
						'review_id':self.id,
						'site_id':a.employee.site_master_id.id
						})

		if form_type == 'Annual KRA':
			kra_dets = self.env['annual.kra.details'].search([('year','=',financial_year),('site_id','in',site_list),('status','!=',''),('review_cycle','=',review_cycle)])
			if kra_dets:
				for k in kra_dets:
					status = ''
					if k.approve1_char!='':
						status = k.approve1_char
					if k.approve2_char!='':
						status = status +'\n' +k.approve2_char
					if k.approve3_char!='':
						status = status +'\n' +k.approve3_char
					if k.approve4_char!='':
						status = status +'\n' +k.approve4_char
					self.env['annual.status.child'].create({
						'employee_code':k.employee_code,
						'employee':k.employee.id,
						'department':k.department.id,
						'reporting_to':k.employee.parent_id.id,
						'application_date':k.application_date,
						'approved_date':k.approved_date,
						'financial_year':k.year.id,
						'status':status,
						'review_id':self.id,
						'site_id':k.employee.site_master_id.id
						})
		return True


class AnnualStatusChild(models.Model):
	_name = "annual.status.child"

	company_id = fields.Many2one('res.company','Company')
	site_id = fields.Many2one('site.master')
	financial_year = fields.Many2one('year.master')
	year_of_application = fields.Many2one('year.master.annual','Year Of Application')
	review_cycle = fields.Char('Review Cycle')
	review_id = fields.Many2one('annual.review.status.report','Annual Status')
	employee_code = fields.Char('Employee Code')
	employee = fields.Many2one('hr.employee','Employee Name')
	reporting_to = fields.Many2one('hr.employee','Reporting To')
	location = fields.Many2one('res.company','Location')
	designation = fields.Many2one('hr.job', 'Designation')
	department = fields.Many2one('hr.department','Department')
	status = fields.Char('Status')
	approved_date = fields.Date('Approved Date')
	application_date = fields.Date('Application Date')

class YearMasterAnnual(models.Model):
	_name = "year.master.annual"

	name = fields.Char('Year')

class IncrementStatusReport(models.Model):
	_name = "increment.status.report"

	def _get_default_access_token(self):
		return str(uuid.uuid4())

	year = fields.Many2one('year.master', 'Year')
	review_month = fields.Selection([('July','July'),('January','January')], string='Review Month')
	status = fields.Selection([('Yes','Updated'),('No','Not Updated'),('Both','Both')], string="Status", default='Yes')
	report_type = fields.Selection([('tl','TL Wise'),('emp','Employee Wise')], 'Report Type',default="emp")
	no_of_records = fields.Integer('No of Records')
	check_exists = fields.Boolean('Check Exists', default=False)
	increment_status_one2many_tl = fields.One2many('increment.status.report.child','increment_status_tl_id','Increment Status Details')
	increment_status_one2many_emp = fields.One2many('increment.status.report.child','increment_status_emp_id','Increment Status Details')
	access_token = fields.Char('Security Token', copy=False,default=_get_default_access_token)

	@api.multi
	def generate_increment_excel(self,access_uid=None):
		self.ensure_one()
		print(self.access_token)
		return {
		'type': 'ir.actions.act_url',
		'url': '/web/pivot/export_increment_status_xls/%s?access_token=%s' % (self.id, self.access_token),
		'target': 'new',
		}


	def get_increment_status_report(self):
		financial_year = self.year.id
		review_cycle = self.review_month
		status = self.status
		report_type = self.report_type
		increment_status = ''
		kra_dets = ''
		self.env.cr.execute("delete from increment_status_report_child")
		if report_type == 'emp':
			if status == 'Yes':
				increment_status = 'updated'
				kra_dets = self.env['annual.kra.details'].search([('year','=',financial_year),('review_cycle','=',review_cycle),('increment_status','=',increment_status),('status','=','approved')])
			elif status == 'No':
				increment_status = 'not_updated'
				kra_dets = self.env['annual.kra.details'].search([('year','=',financial_year),('review_cycle','=',review_cycle),('increment_status','=',increment_status),('status','=','approved')])
			else:
				increment_status = ['not_updated','updated']
				kra_dets = self.env['annual.kra.details'].search([('year','=',financial_year),('review_cycle','=',review_cycle),('increment_status','in',increment_status),('status','=','approved')])
			if kra_dets:
				for k in kra_dets:
					self.env['increment.status.report.child'].create({
						'employee_code':k.employee_code,
						'employee':k.employee.id,
						'tl_code':k.employee.parent_id.emp_code,
						'tl_name':k.employee.parent_id.id,
						'increment_status_emp_id':self.id,
						'department':k.department.id,
						'increment_status':k.increment_status,
						})
		tl_list = []
		if report_type == 'tl':
			search_emp = self.env['hr.employee'].search([('parent_id','!=',False)])
			if search_emp:
				for emp in search_emp:
					print (emp.parent_id.id,'pppppppppp')
					if status == 'Yes':
						increment_status = 'updated'
						kra_dets = self.env['annual.kra.details'].search([('year','=',financial_year),('review_cycle','=',review_cycle),('increment_status','=',increment_status),('employee','=',emp.parent_id.id),('status','=','approved')])
						if kra_dets not in tl_list:
							tl_list.append(kra_dets)
					elif status == 'No':
						increment_status = 'not_updated'
						kra_dets = self.env['annual.kra.details'].search([('year','=',financial_year),('review_cycle','=',review_cycle),('increment_status','=',increment_status),('employee','=',emp.parent_id.id),('status','=','approved')])
						if kra_dets not in tl_list:
							tl_list.append(kra_dets)
					else:
						increment_status = ['not_updated','updated']
						kra_dets = self.env['annual.kra.details'].search([('year','=',financial_year),('review_cycle','=',review_cycle),('increment_status','in',increment_status),('employee','=',emp.parent_id.id),('status','=','approved')])
						if kra_dets not in tl_list:
							tl_list.append(kra_dets)
				tl_list = list(set(tl_list))	
				if tl_list:					
					for k in tl_list:
						self.env['increment.status.report.child'].create({
							'tl_code':k.employee_code,
							'tl_name':k.employee.id,
							'increment_status_tl_id':self.id,
							'department':k.department.id,
							'increment_status':k.increment_status,
							})
		self.write({'check_exists':True})
		return True

class IncrementStatusReportChild(models.Model):
	_name = 'increment.status.report.child'

	increment_status_tl_id = fields.Many2one('increment.status.report','')
	increment_status_emp_id = fields.Many2one('increment.status.report','')
	tl_code = fields.Char('TL Code')
	tl_name = fields.Many2one('hr.employee','TL Name')
	employee_code = fields.Char('Employee Code')
	employee = fields.Many2one('hr.employee','Employee Name')
	department = fields.Many2one('hr.department','Department')
	increment_status = fields.Selection([('updated','Updated'),('not_updated','Not Updated')], string="Increment Status")

class IncrementReport(models.Model):
	_name = "increment.report"

	def _get_default_access_token(self):
		return str(uuid.uuid4())

	year = fields.Many2one('year.master', 'Year')
	review_month = fields.Selection([('July','July'),('January','January')], string='Review Month')	
	increment_one2many = fields.One2many('increment.report.child','increment_id','Increment Details')
	access_token = fields.Char('Security Token', copy=False,default=_get_default_access_token)

	@api.multi
	def generate_increment_excel(self,access_uid=None):
		self.ensure_one()
		print(self.access_token)
		return {
		'type': 'ir.actions.act_url',
		'url': '/web/pivot/export_increment_xls/%s?access_token=%s' % (self.id, self.access_token),
		'target': 'new',
		}

	def get_report(self):
		financial_year = self.year.id
		review_cycle = self.review_month
		self.env.cr.execute("delete from increment_report_child")
		kra_dets = self.env['annual.kra.details'].search([('year','=',financial_year),('review_cycle','=',review_cycle),('status','=','approved')])
		if kra_dets:
			for k in kra_dets:
				self.env['increment.report.child'].create({
					'employee_code':k.employee_code,
					'employee':k.employee.id,
					'employee_name':k.employee.name,
					'department':k.department.id,
					'tl_ikra':k.reportee1_total_rating,
					'tl_iar':k.reportee1_total_cb,
					'reportee2_ikra':k.reportee2_total_rating,
					'reportee2_iar':k.reportee2_total_cb,
					'reportee3_ikra':k.reportee3_total_rating,
					'reportee3_iar':k.reportee3_total_cb,
					'hr_ikra':k.hr_total_rating,
					'hr_iar':k.hr_total_cb,
					'sum_ikra':k.sum_ikra,
					'sum_iar':k.sum_iar,
					'current_gross':k.employee.gross_salary,
					'current_ctc':k.employee.current_ctc,
					'proposed_increment':k.proposed_increment,
					'weightage':k.final_weightage,
					'actual_increment':k.actual_increment,
					'final_increment':None,
					'increment_id':self.id
					})
		return True

class IncrementReportChild(models.Model):
	_name = 'increment.report.child'

	increment_id = fields.Many2one('increment.report','Increment ID')
	employee_code = fields.Char('Employee Code')
	employee_name =fields.Char('Employee')
	employee = fields.Many2one('hr.employee','Employee Name')
	department = fields.Many2one('hr.department','Department')
	tl_ikra = fields.Float('TL IKRA')
	tl_iar = fields.Float('TL IAR')
	hr_ikra = fields.Float('HR IKRA')
	hr_iar = fields.Float('HR IAR')
	reportee2_ikra = fields.Float('Reportee2 IKRA')
	reportee2_iar = fields.Float('Reportee2 IAR')
	reportee3_ikra = fields.Float('Reportee3 IKRA')
	reportee3_iar = fields.Float('Reportee3 IAR')
	sum_ikra = fields.Float('SUM IKRA')
	sum_iar = fields.Float('SUM IAR')
	current_gross = fields.Float('Current Gross')
	current_ctc = fields.Float('Current CTC')
	proposed_increment = fields.Char('Proposed Increment')
	weightage = fields.Float('Weightage')
	actual_increment = fields.Float('TL Actual Increment')
	final_increment = fields.Float('Final Increment')

class CriticalBehaViourAttributes(models.Model):
	_name = "critical.behaviour.attributes"

	cba_id = fields.Many2one('annual.kra.details','KRA Deta')
	name = fields.Char('Name')
	grade = fields.Integer('Grade')

class CriticalBehaViourLines(models.Model):
	_name = "critical.behaviour.lines"

	cbl_id = fields.Many2one('annual.kra.details','KRA Deta')
	description = fields.Char('Name')
	self_rating = fields.Float('Self Rating')
	tl_rating = fields.Float('Reportee1 Rating')
	reportee2_rating = fields.Float('Reportee2 Rating')
	reportee3_rating = fields.Float('Reportee3 Rating')
	hr_rating =fields.Float('HR Rating')
	check1 = fields.Boolean('self check', compute='get_user')
	check2 = fields.Boolean('hr check', compute='get_user')
	rp2_check = fields.Boolean('reportee2 check', compute='get_user')
	rp3_check = fields.Boolean('reportee3 check', compute='get_user')
	tl_check = fields.Boolean('tl check', compute='get_user')

	@api.onchange('self_rating')
	def onchange_name(self):
		res = {}
		if self.self_rating == 0.0 or self.self_rating > 5.0:
			raise ValidationError(_("Kindly give proper Self Rating in Critical Behaviour Attributes!"))
		return res

	def get_user(self):
		for each in self:
			employee = each.cbl_id.employee.user_id.id
			print(employee)
			res_user = self.env['res.users'].search([('id', '=', each._uid)])
			print(res_user.id, employee,'iddddddddddddd')
			check2 = False
			check1 = False
			tl_check = False
			rp2_check= False
			rp3_check = False
			
			each.check2 = False
			each.check1 = False
			each.tl_check = False
			each.rp2_check= False
			each.rp3_check = False
			if res_user.has_group('hr.group_hr_manager') or res_user.has_group('hr.group_hr_user'):
				if employee == res_user.id:
					check1 = True
				elif each.cbl_id.employee.parent_id.user_id.id == res_user.id:
					tl_check = True
				elif each.cbl_id.employee.parent_id.parent_id.user_id.id == res_user.id:
					rp2_check = True
				elif each.cbl_id.employee.parent_id.parent_id.parent_id.user_id.id == res_user.id:
					rp3_check = True
				else:
					if each.cbl_id.employee.hr_executive_id.user_id.id == res_user.id:
						check2 = True
					else:
						check2 = False

			elif res_user.has_group('orient_hr_resignation.group_reporting_manager'):
				if employee == res_user.id:
					check1 = True
				else:
					if each.cbl_id.employee.parent_id.user_id.id == res_user.id:
						tl_check = True
					else:
						tl_check = False

				if employee == res_user.id:
					check1 = True
				else:
					if each.cbl_id.employee.parent_id.parent_id.user_id.id == res_user.id:
						rp2_check = True
					else:
						rp2_check = False

				if employee == res_user.id:
					check1 = True
				else:
					if each.cbl_id.employee.parent_id.parent_id.parent_id.user_id.id == res_user.id:
						rp3_check = True
					else:
						rp3_check = False	
			else:
				if employee == res_user.id:
					check1 = True
				else:
					check1 = False
			
			if check1 == True and tl_check == False and rp2_check == False and rp3_check == False and check2 == False :
				each.check1 = True
			elif check1 == False and tl_check == True and rp2_check == False and rp3_check == False and check2 == False:
				each.tl_check = True
			elif check1 == False and tl_check == False and rp2_check == True and rp3_check == False and check2 == False:
				each.rp2_check = True
			elif check1 == False and tl_check == False and rp2_check == False and rp3_check == True and check2 == False:
				each.rp3_check = True
			elif check1 == False and tl_check == False and rp2_check == False and rp3_check == False and check2 == True:
				each.check2 = True


class AppraisalDueReport(models.Model):
	_name = 'appraisal.due.report'
	_inherit = ['mail.thread', 'mail.activity.mixin']


	def _get_default_access_token(self):
		return str(uuid.uuid4())
		
	review_cycle = fields.Selection([('January','January'),('July','July')], string="Review Cycle")
	financial_year = fields.Many2one('year.master','Year')
	application_year = fields.Many2one('year.master.annual','Application Year')
	appraisal_one2many = fields.One2many('appraisal.due.child','due_id','Appraisal Details')
	skipped_appraisal_one2many = fields.One2many('appraisal.due.child','skipped_due_id','Appraisal Details')
	pip_appraisal_one2many = fields.One2many('appraisal.due.child','pip_due_id','Appraisal Details')
	exists = fields.Boolean('Exists',default=False)
	email_chars = fields.Char('Email')
	manager_email_chars = fields.Char("Manager's Email")
	company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env['res.company']._company_default_get('account.invoice'))
	access_token = fields.Char('Security Token', copy=False,default=_get_default_access_token)
	select_all = fields.Boolean('Select All',default=False)

	@api.onchange('select_all')
	def onchange_select_all(self):
		res = {}
		if self.select_all:
			if self.appraisal_one2many:
				for x in self.appraisal_one2many:
					x.update({'select':True})
			if self.skipped_appraisal_one2many:
				for y in self.skipped_appraisal_one2many:
					y.update({'select':True})
			if self.pip_appraisal_one2many:
				for z in self.pip_appraisal_one2many:
					z.update({'select':True})
		else:
			if self.appraisal_one2many:
				for x in self.appraisal_one2many:
					x.update({'select':False})
			if self.skipped_appraisal_one2many:
				for y in self.skipped_appraisal_one2many:
					y.update({'select':False})
			if self.pip_appraisal_one2many:
				for z in self.pip_appraisal_one2many:
					z.update({'select':False})
		return res

	@api.multi
	def send_email(self):
		emails = []
		manager_emails = []
		check=False
		if self.appraisal_one2many:
			for x in self.appraisal_one2many:
				if x.select:
					check=True
		if self.skipped_appraisal_one2many:
			for y in self.skipped_appraisal_one2many:
				if y.select:
					check=True
		if self.pip_appraisal_one2many:
			for z in self.pip_appraisal_one2many:
				if z.select:
					check=True
		if check==False:
			raise ValidationError(_("Kindly select any record!!"))
		for s in self.appraisal_one2many:
			if s.select:
				emails.append(s.employee.work_email)
				manager_emails.append(s.employee.parent_id.work_email)
		for p in self.skipped_appraisal_one2many:
			if p.select:
				emails.append(p.employee.work_email)
				manager_emails.append(p.employee.parent_id.work_email)
		for d in self.pip_appraisal_one2many:
			if d.select:
				emails.append(d.employee.work_email)
				manager_emails.append(d.employee.parent_id.work_email)
		if emails != []:
			emails_list = ",".join(str(x) for x in emails)
			self.write({'email_chars':emails_list})
		if manager_emails != []:
			manager_emails_list = ",".join(str(x) for x in manager_emails)
			self.write({'manager_email_chars':manager_emails_list})
		self.ensure_one()
		template = self.env.ref('orient_pms.mail_template_data_notification_email_annual_appraisal', False)
		compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
		ctx = dict(
			default_model='appraisal.due.report',
			default_res_id=self.id,
			default_use_template=bool(template),
			default_template_id=template and template.id or False,
			default_composition_mode='comment',
			mark_invoice_as_sent=True,
			custom_layout="orient_pms.mail_template_data_notification_email_annual_appraisal",
			force_email=True
		)
		return {
			'name': _('Compose Email'),
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'mail.compose.message',
			'views': [(compose_form.id, 'form')],
			'view_id': compose_form.id,
			'target': 'new',
			'context': ctx,
		}

	@api.multi
	def generate_excel(self,access_uid=None):
		self.ensure_one()
		return {
		'type': 'ir.actions.act_url',
		'url': '/web/pivot/export_due_xls/%s?access_token=%s' % (self.id, self.access_token),
		'target': 'new',
		}


	@api.multi
	def search_records(self):
		if not self.review_cycle:
			raise ValidationError(_("Kindly Select Review Cycle!"))
		if not self.financial_year.id:
			raise ValidationError(_("Kindly Select Financial Year!"))
		review_cycle = self.review_cycle
		financial_year = self.financial_year.name
		application_year = self.application_year.name
		year = ''
		print(review_cycle, financial_year, application_year)
		emp_obj=self.env['hr.employee']
		kra_obj=self.env['kra.main']
		appraisal_obj=self.env['annual.kra.details']
		self.env.cr.execute("delete from appraisal_due_child")
		emp_records = self.env['hr.employee'].search([('appraisal_cycle','=',review_cycle)])
		q1_rating = ''
		q2_rating = ''
		q3_rating = ''
		q4_rating = ''
		print(emp_records)
		for emp_recs in emp_records:
			print(emp_recs)
			current_date =  datetime.now().date()
			joining_date = emp_recs.joining_date
			date_dt= datetime.strptime(joining_date, "%Y-%m-%d").date()
			current_date= datetime.strptime(str(current_date), "%Y-%m-%d").date()
			tenure = relativedelta(current_date, date_dt)
			if review_cycle == 'January':
				pip_applicable = False
				get_year = get_current_financial_year(self)
				search_year = self.env['year.master'].search([('name','=',str(get_year))])
				if search_year:
					year = search_year.id
				split_year = get_year.split('-')
				year1 = str(int(split_year[0])-1)
				year2 = str(int(split_year[1])-1)
				print (year1,year2)
				review_start_date1=year2+'-04-01'
				review_end_date1=year2+'-06-30'
				review_start_date2=year2+'-07-01'
				review_end_date2=year2+'-09-30'
				review_start_date3=year2+'-10-01'
				review_end_date3=year2+'-12-31'
				review_start_date4=year2+'-01-01'
				review_end_date4=year2+'-03-31'
				search_annual_form=appraisal_obj.search([('employee','=',emp_recs.id),('year','=',year),('status','=','approved')])
				search_quarter4=kra_obj.search([('review_start_date','=',review_start_date4),('review_end_date','=',review_end_date4),('employee','=',emp_recs.id),('state','=','done')])
				search_quarter1=kra_obj.search([('review_start_date','=',review_start_date1),('review_end_date','=',review_end_date1),('employee','=',emp_recs.id),('state','=','done')])							
				search_quarter2=kra_obj.search([('review_start_date','=',review_start_date2),('review_end_date','=',review_end_date2),('employee','=',emp_recs.id),('state','=','done')])
				search_quarter3=kra_obj.search([('review_start_date','=',review_start_date3),('review_end_date','=',review_end_date3),('employee','=',emp_recs.id),('state','=','done')])
				q1_rating = search_quarter1.final_rating
				q2_rating = search_quarter2.final_rating
				q3_rating = search_quarter3.final_rating
				q4_rating = search_quarter4.final_rating
				if search_quarter4.pip_applicable:
					pip_applicable=True
				if search_quarter1.pip_applicable:
					pip_applicable=True
				if search_quarter2.pip_applicable:
					pip_applicable=True
				if search_quarter3.pip_applicable:
					pip_applicable=True
				if tenure.years >= 1 and tenure.years < 2 and not (search_quarter4.id != False and search_quarter1.id != False and search_quarter2.id != False and search_quarter3.id != False):
					print (emp_recs.name,'name',tenure.years)
					self.write({'exists':True})
					if pip_applicable:
						self.env['appraisal.due.child'].create({
														'pip_due_id':self.id,
														'employee':emp_recs.id,
														'emp_code':emp_recs.emp_code,
														'joining_date':emp_recs.joining_date,
														'parent_id':emp_recs.parent_id.id,
														'department':emp_recs.department_id.id,
														'designation':emp_recs.job_id.id,
														'appraisal_cycle':emp_recs.appraisal_cycle,
														'position_type':emp_recs.position_type
							})
					else:
						self.env['appraisal.due.child'].create({
														'due_id':self.id,
														'employee':emp_recs.id,
														'emp_code':emp_recs.emp_code,
														'joining_date':emp_recs.joining_date,
														'parent_id':emp_recs.parent_id.id,
														'department':emp_recs.department_id.id,
														'designation':emp_recs.job_id.id,
														'appraisal_cycle':emp_recs.appraisal_cycle,
														'position_type':emp_recs.position_type
							})
				elif tenure.years >= 1 and tenure.years < 2 and (search_quarter4.id != False and search_quarter1.id != False and search_quarter2.id != False and search_quarter3.id != False):
					print (emp_recs.name,'name',tenure.years)
					self.write({'exists':True})
					
					if pip_applicable:
						self.env['appraisal.due.child'].create({
														'pip_due_id':self.id,
														'employee':emp_recs.id,
														'emp_code':emp_recs.emp_code,
														'joining_date':emp_recs.joining_date,
														'parent_id':emp_recs.parent_id.id,
														'department':emp_recs.department_id.id,
														'designation':emp_recs.job_id.id,
														'appraisal_cycle':emp_recs.appraisal_cycle,
														'position_type':emp_recs.position_type,
														'quarter1':q1_rating,
														'quarter2':q2_rating,
														'quarter3':q3_rating,
														'quarter4':q4_rating,
							})
					else:
						self.env['appraisal.due.child'].create({
														'due_id':self.id,
														'employee':emp_recs.id,
														'emp_code':emp_recs.emp_code,
														'joining_date':emp_recs.joining_date,
														'parent_id':emp_recs.parent_id.id,
														'department':emp_recs.department_id.id,
														'designation':emp_recs.job_id.id,
														'appraisal_cycle':emp_recs.appraisal_cycle,
														'position_type':emp_recs.position_type,
														'quarter1':q1_rating,
														'quarter2':q2_rating,
														'quarter3':q3_rating,
														'quarter4':q4_rating,
							})
				elif tenure.years >= 2 and (search_quarter4.id != False and search_quarter1.id != False and search_quarter2.id != False and search_quarter3.id != False):
					print (emp_recs.name,'name',tenure.years)
					self.write({'exists':True})
					date_dt=False
					q1_rating = ''
					q2_rating = ''
					q3_rating = ''
					q4_rating = ''
					emp_records1 = self.env['hr.employee'].search([('appraisal_cycle','=','July')])
					for emp_recs1 in emp_records1:
						current_date =  datetime.now().date()
						joining_date = emp_recs1.joining_date
						if joining_date:
							date_dt= datetime.strptime(joining_date, "%Y-%m-%d").date()
						current_date= datetime.strptime(str(current_date), "%Y-%m-%d").date()
						tenure = relativedelta(current_date, date_dt)
						get_year = get_current_financial_year(self)
						search_year = self.env['year.master'].search([('name','=',str(get_year))])
						if search_year:
							year = search_year.id
						split_year = get_year.split('-')
						year1 = str(int(split_year[0])-1)
						year2 = str(int(split_year[1])-1)
						print (get_year,year1,year2)
						pip_applicable = False
						review_start_date1=year2+'-04-01'
						review_end_date1=year2+'-06-30'
						review_start_date2=year1+'-07-01'
						review_end_date2=year1+'-09-30'
						review_start_date3=year1+'-10-01'
						review_end_date3=year1+'-12-31'
						review_start_date4=year2+'-01-01'
						review_end_date4=year2+'-03-31'
						search_annual_form1=appraisal_obj.search([('employee','=',emp_recs1.id),('year','=',year),('status','=','approved')])
						search_quarter2=kra_obj.search([('review_start_date','=',review_start_date2),('review_end_date','=',review_end_date2),('employee','=',emp_recs1.id),('state','=','done')])
						search_quarter3=kra_obj.search([('review_start_date','=',review_start_date3),('review_end_date','=',review_end_date3),('employee','=',emp_recs1.id),('state','=','done')])
						search_quarter4=kra_obj.search([('review_start_date','=',review_start_date4),('review_end_date','=',review_end_date4),('employee','=',emp_recs1.id),('state','=','done')])
						search_quarter1=kra_obj.search([('review_start_date','=',review_start_date1),('review_end_date','=',review_end_date1),('employee','=',emp_recs1.id),('state','=','done')])
						q1_rating = search_quarter1.final_rating
						q2_rating = search_quarter2.final_rating
						q3_rating = search_quarter3.final_rating
						q4_rating = search_quarter4.final_rating
						if not search_annual_form1:
							self.env['appraisal.due.child'].create({
																'skipped_due_id':self.id,
																'employee':emp_recs1.id,
																'emp_code':emp_recs1.emp_code,
																'joining_date':emp_recs1.joining_date,
																'parent_id':emp_recs1.parent_id.id,
																'department':emp_recs1.department_id.id,
																'designation':emp_recs1.job_id.id,
																'appraisal_cycle':emp_recs1.appraisal_cycle,
																'position_type':emp_recs1.position_type,
																'quarter1':q1_rating,
																'quarter2':q2_rating,
																'quarter3':q3_rating,
																'quarter4':q4_rating,									})
					if not search_annual_form:
						print ('emp_recs',emp_recs.name,q1_rating,q2_rating,q3_rating,q4_rating)
						self.env['appraisal.due.child'].create({
															'skipped_due_id':self.id,
															'employee':emp_recs.id,
															'emp_code':emp_recs.emp_code,
															'joining_date':emp_recs.joining_date,
															'parent_id':emp_recs.parent_id.id,
															'department':emp_recs.department_id.id,
															'designation':emp_recs.job_id.id,
															'appraisal_cycle':emp_recs.appraisal_cycle,
															'position_type':emp_recs.position_type,
															'quarter1':q1_rating,
															'quarter2':q2_rating,
															'quarter3':q3_rating,
															'quarter4':q4_rating,
								})
					else:
						if pip_applicable:
							print ('emp_recs',emp_recs.name,q1_rating,q2_rating,q3_rating,q4_rating)
							self.env['appraisal.due.child'].create({
															'pip_due_id':self.id,
															'employee':emp_recs.id,
															'emp_code':emp_recs.emp_code,
															'joining_date':emp_recs.joining_date,
															'parent_id':emp_recs.parent_id.id,
															'department':emp_recs.department_id.id,
															'designation':emp_recs.job_id.id,
															'appraisal_cycle':emp_recs.appraisal_cycle,
															'position_type':emp_recs.position_type,
															'quarter1':q1_rating,
															'quarter2':q2_rating,
															'quarter3':q3_rating,
															'quarter4':q4_rating,
								})
						else:
							print ('emp_recs',emp_recs.name,q1_rating,q2_rating,q3_rating,q4_rating)
							self.env['appraisal.due.child'].create({
															'due_id':self.id,
															'employee':emp_recs.id,
															'emp_code':emp_recs.emp_code,
															'joining_date':emp_recs.joining_date,
															'parent_id':emp_recs.parent_id.id,
															'department':emp_recs.department_id.id,
															'designation':emp_recs.job_id.id,
															'appraisal_cycle':emp_recs.appraisal_cycle,
															'position_type':emp_recs.position_type,
															'quarter1':q1_rating,
															'quarter2':q2_rating,
															'quarter3':q3_rating,
															'quarter4':q4_rating,
								})
			if review_cycle == 'July':
				get_year = get_current_financial_year(self)
				search_year = self.env['year.master'].search([('name','=',str(get_year))])
				if search_year:
					year = search_year.id
				split_year = get_year.split('-')
				year1 = str(int(split_year[0])-1)
				year2 = str(int(split_year[1])-1)
				print (get_year,year1,year2)
				pip_applicable = False
				review_start_date1=year2+'-04-01'
				review_end_date1=year2+'-06-30'
				review_start_date2=year1+'-07-01'
				review_end_date2=year1+'-09-30'
				review_start_date3=year1+'-10-01'
				review_end_date3=year1+'-12-31'
				review_start_date4=year2+'-01-01'
				review_end_date4=year2+'-03-31'
				search_annual_form=appraisal_obj.search([('employee','=',emp_recs.id),('year','=',year),('status','=','approved')],order='employee_code asc')
				search_quarter2=kra_obj.search([('review_start_date','=',review_start_date2),('review_end_date','=',review_end_date2),('employee','=',emp_recs.id),('state','=','done')],limit=1)
				search_quarter3=kra_obj.search([('review_start_date','=',review_start_date3),('review_end_date','=',review_end_date3),('employee','=',emp_recs.id),('state','=','done')],limit=1)
				search_quarter4=kra_obj.search([('review_start_date','=',review_start_date4),('review_end_date','=',review_end_date4),('employee','=',emp_recs.id),('state','=','done')],limit=1)
				search_quarter1=kra_obj.search([('review_start_date','=',review_start_date1),('review_end_date','=',review_end_date1),('employee','=',emp_recs.id),('state','=','done')],limit=1)
				if search_quarter2.pip_applicable:
					pip_applicable=True
				if search_quarter3.pip_applicable:
					pip_applicable=True
				if search_quarter4.pip_applicable:
					pip_applicable=True
				if search_quarter1.pip_applicable:
					pip_applicable=True
				if tenure.years >= 1 or tenure.months>=9:
					print (emp_recs.name,'name',tenure.years,tenure.months)
					self.write({'exists':True})
					# if pip_applicable:
					# 	self.env['appraisal.due.child'].create({
					# 									'pip_due_id':self.id,
					# 									'employee':emp_recs.id,
					# 									'emp_code':emp_recs.emp_code,
					# 									'joining_date':emp_recs.joining_date,
					# 									'parent_id':emp_recs.parent_id.id,
					# 									'department':emp_recs.department_id.id,
					# 									'designation':emp_recs.job_id.id,
					# 									'appraisal_cycle':emp_recs.appraisal_cycle,
					# 									'position_type':emp_recs.position_type
					# 		})
					# else:
					self.env['appraisal.due.child'].create({
													'due_id':self.id,
													'employee':emp_recs.id,
													'emp_code':emp_recs.emp_code,
													'joining_date':emp_recs.joining_date,
													'parent_id':emp_recs.parent_id.id,
													'department':emp_recs.department_id.id,
													'designation':emp_recs.job_id.id,
													'appraisal_cycle':emp_recs.appraisal_cycle,
													'position_type':emp_recs.position_type,
													'quarter1':search_quarter1.final_rating,
													'quarter2':search_quarter2.final_rating,
													'quarter3':search_quarter3.final_rating,
													'quarter4':search_quarter4.final_rating
						})
				# elif tenure.years >= 1 and tenure.years < 2 and (search_quarter2.id != False and search_quarter3.id != False and search_quarter4.id != False and search_quarter1.id != False):
				# 	print (emp_recs.name,'name',tenure.years)
				# 	self.write({'exists':True})
				# 	if pip_applicable:
				# 		self.env['appraisal.due.child'].create({
				# 										'pip_due_id':self.id,
				# 										'employee':emp_recs.id,
				# 										'emp_code':emp_recs.emp_code,
				# 										'joining_date':emp_recs.joining_date,
				# 										'parent_id':emp_recs.parent_id.id,
				# 										'department':emp_recs.department_id.id,
				# 										'designation':emp_recs.job_id.id,
				# 										'appraisal_cycle':emp_recs.appraisal_cycle,
				# 										'position_type':emp_recs.position_type,
				# 										'quarter1':search_quarter1.final_rating,
				# 										'quarter2':search_quarter2.final_rating,
				# 										'quarter3':search_quarter3.final_rating,
				# 										'quarter4':search_quarter4.final_rating,
				# 			})
				# 	else:
				# 		self.env['appraisal.due.child'].create({
				# 										'due_id':self.id,
				# 										'employee':emp_recs.id,
				# 										'emp_code':emp_recs.emp_code,
				# 										'joining_date':emp_recs.joining_date,
				# 										'parent_id':emp_recs.parent_id.id,
				# 										'department':emp_recs.department_id.id,
				# 										'designation':emp_recs.job_id.id,
				# 										'appraisal_cycle':emp_recs.appraisal_cycle,
				# 										'position_type':emp_recs.position_type,
				# 										'quarter1':search_quarter1.final_rating,
				# 										'quarter2':search_quarter2.final_rating,
				# 										'quarter3':search_quarter3.final_rating,
				# 										'quarter4':search_quarter4.final_rating,
				# 			})
				# elif tenure.years >= 2 and (search_quarter2.id != False and search_quarter3.id != False and search_quarter4.id != False and search_quarter1.id != False):
				# 	print (emp_recs.name,'name',tenure.years)
				# 	self.write({'exists':True})
				# 	emp_records1 = self.env['hr.employee'].search([('appraisal_cycle','=','January')])
				# 	for emp_recs1 in emp_records1:
				# 		current_date =  datetime.now().date()
				# 		joining_date = emp_recs1.joining_date
				# 		date_dt= datetime.strptime(joining_date, "%Y-%m-%d").date()
				# 		current_date= datetime.strptime(str(current_date), "%Y-%m-%d").date()
				# 		tenure = relativedelta(current_date, date_dt)
				# 		get_year = get_current_financial_year(self)
				# 		split_year = get_year.split('-')
				# 		year1 = str(int(split_year[0])-1)
				# 		year2 = str(int(split_year[1])-1)
				# 		get_year1  = year1+"-"+year2
				# 		search_year = self.env['year.master'].search([('name','=',str(get_year))])
				# 		if search_year:
				# 			year = search_year.id
				# 		split_year1 = get_year1.split('-')
				# 		year1 = str(int(split_year1[0])-1)
				# 		year2 = str(int(split_year1[1])-1)
				# 		print (year1,year2)
				# 		review_start_date1=year2+'-04-01'
				# 		review_end_date1=year2+'-06-30'
				# 		review_start_date2=year2+'-07-01'
				# 		review_end_date2=year2+'-09-30'
				# 		review_start_date3=year2+'-10-01'
				# 		review_end_date3=year2+'-12-31'
				# 		review_start_date4=year2+'-01-01'
				# 		review_end_date4=year2+'-03-31'
				# 		search_annual_form1=appraisal_obj.search([('employee','=',emp_recs1.id),('year','=',year),('status','=','approved')])
				# 		search_quarter4=kra_obj.search([('review_start_date','=',review_start_date4),('review_end_date','=',review_end_date4),('employee','=',emp_recs1.id),('state','=','done')])
				# 		search_quarter1=kra_obj.search([('review_start_date','=',review_start_date1),('review_end_date','=',review_end_date1),('employee','=',emp_recs1.id),('state','=','done')])							
				# 		search_quarter2=kra_obj.search([('review_start_date','=',review_start_date2),('review_end_date','=',review_end_date2),('employee','=',emp_recs1.id),('state','=','done')])
				# 		search_quarter3=kra_obj.search([('review_start_date','=',review_start_date3),('review_end_date','=',review_end_date3),('employee','=',emp_recs1.id),('state','=','done')])
				# 		if not search_annual_form1:
				# 			self.env['appraisal.due.child'].create({
				# 												'skipped_due_id':self.id,
				# 												'employee':emp_recs1.id,
				# 												'emp_code':emp_recs1.emp_code,
				# 												'joining_date':emp_recs1.joining_date,
				# 												'parent_id':emp_recs1.parent_id.id,
				# 												'department':emp_recs1.department_id.id,
				# 												'designation':emp_recs1.job_id.id,
				# 												'appraisal_cycle':emp_recs1.appraisal_cycle,
				# 												'position_type':emp_recs1.position_type,
				# 												'quarter1':search_quarter1.final_rating,
				# 												'quarter2':search_quarter2.final_rating,
				# 												'quarter3':search_quarter3.final_rating,
				# 												'quarter4':search_quarter4.final_rating,
				# 					})
				# 	if not search_annual_form:
				# 		self.env['appraisal.due.child'].create({
				# 										'skipped_due_id':self.id,
				# 										'employee':emp_recs.id,
				# 										'emp_code':emp_recs.emp_code,
				# 										'joining_date':emp_recs.joining_date,
				# 										'parent_id':emp_recs.parent_id.id,
				# 										'department':emp_recs.department_id.id,
				# 										'designation':emp_recs.job_id.id,
				# 										'appraisal_cycle':emp_recs.appraisal_cycle,
				# 										'position_type':emp_recs.position_type,
				# 										'quarter1':search_quarter1.final_rating,
				# 										'quarter2':search_quarter2.final_rating,
				# 										'quarter3':search_quarter3.final_rating,
				# 										'quarter4':search_quarter4.final_rating,
				# 			})
				# 	else:
				# 		if pip_applicable:
				# 			self.env['appraisal.due.child'].create({
				# 											'pip_due_id':self.id,
				# 											'employee':emp_recs.id,
				# 											'emp_code':emp_recs.emp_code,
				# 											'joining_date':emp_recs.joining_date,
				# 											'parent_id':emp_recs.parent_id.id,
				# 											'department':emp_recs.department_id.id,
				# 											'designation':emp_recs.job_id.id,
				# 											'appraisal_cycle':emp_recs.appraisal_cycle,
				# 											'position_type':emp_recs.position_type,
				# 											'quarter1':search_quarter1.final_rating,
				# 											'quarter2':search_quarter2.final_rating,
				# 											'quarter3':search_quarter3.final_rating,
				# 											'quarter4':search_quarter4.final_rating,
				# 				})
				# 		else:
				# 			self.env['appraisal.due.child'].create({
				# 											'due_id':self.id,
				# 											'employee':emp_recs.id,
				# 											'emp_code':emp_recs.emp_code,
				# 											'joining_date':emp_recs.joining_date,
				# 											'parent_id':emp_recs.parent_id.id,
				# 											'department':emp_recs.department_id.id,
				# 											'designation':emp_recs.job_id.id,
				# 											'appraisal_cycle':emp_recs.appraisal_cycle,
				# 											'position_type':emp_recs.position_type,
				# 											'quarter1':search_quarter1.final_rating,
				# 											'quarter2':search_quarter2.final_rating,
				# 											'quarter3':search_quarter3.final_rating,
				# 											'quarter4':search_quarter4.final_rating,
				# 				})	
		return True

	# @api.multi
	# def search_records(self):
	# 	if not self.review_cycle:
	# 		raise ValidationError(_("Kindly Select Review Cycle!"))
	# 	if not self.financial_year.id:
	# 		raise ValidationError(_("Kindly Select Financial Year!"))
	# 	review_cycle = self.review_cycle
	# 	financial_year = self.financial_year.name
	# 	application_year = self.application_year.name
	# 	year = ''
	# 	print(review_cycle, financial_year, application_year)
	# 	emp_obj=self.env['hr.employee']
	# 	kra_obj=self.env['kra.main']
	# 	appraisal_obj=self.env['annual.kra.details']
	# 	self.env.cr.execute("delete from appraisal_due_child")
	# 	emp_records = self.env['hr.employee'].search([('appraisal_cycle','=',review_cycle)])
	# 	q1_rating = ''
	# 	q2_rating = ''
	# 	q3_rating = ''
	# 	q4_rating = ''
	# 	print(emp_records)
	# 	for emp_recs in emp_records:
	# 		print(emp_recs)
	# 		current_date =  datetime.now().date()
	# 		joining_date = emp_recs.joining_date
	# 		date_dt= datetime.strptime(joining_date, "%Y-%m-%d").date()
	# 		current_date= datetime.strptime(str(current_date), "%Y-%m-%d").date()
	# 		tenure = relativedelta(current_date, date_dt)
	# 		if review_cycle == 'January':
	# 			pip_applicable = False
	# 			get_year = get_current_financial_year(self)
	# 			search_year = self.env['year.master'].search([('name','=',str(get_year))])
	# 			if search_year:
	# 				year = search_year.id
	# 			split_year = get_year.split('-')
	# 			year1 = str(int(split_year[0])-1)
	# 			year2 = str(int(split_year[1])-1)
	# 			print (year1,year2)
	# 			review_start_date1=year2+'-04-01'
	# 			review_end_date1=year2+'-06-30'
	# 			review_start_date2=year2+'-07-01'
	# 			review_end_date2=year2+'-09-30'
	# 			review_start_date3=year2+'-10-01'
	# 			review_end_date3=year2+'-12-31'
	# 			review_start_date4=year2+'-01-01'
	# 			review_end_date4=year2+'-03-31'
	# 			search_annual_form=appraisal_obj.search([('employee','=',emp_recs.id),('year','=',year),('status','=','approved')])
	# 			search_quarter4=kra_obj.search([('review_start_date','=',review_start_date4),('review_end_date','=',review_end_date4),('employee','=',emp_recs.id),('state','=','done')])
	# 			search_quarter1=kra_obj.search([('review_start_date','=',review_start_date1),('review_end_date','=',review_end_date1),('employee','=',emp_recs.id),('state','=','done')])							
	# 			search_quarter2=kra_obj.search([('review_start_date','=',review_start_date2),('review_end_date','=',review_end_date2),('employee','=',emp_recs.id),('state','=','done')])
	# 			search_quarter3=kra_obj.search([('review_start_date','=',review_start_date3),('review_end_date','=',review_end_date3),('employee','=',emp_recs.id),('state','=','done')])
	# 			q1_rating = search_quarter1.final_rating
	# 			q2_rating = search_quarter2.final_rating
	# 			q3_rating = search_quarter3.final_rating
	# 			q4_rating = search_quarter4.final_rating
	# 			if search_quarter4.pip_applicable:
	# 				pip_applicable=True
	# 			if search_quarter1.pip_applicable:
	# 				pip_applicable=True
	# 			if search_quarter2.pip_applicable:
	# 				pip_applicable=True
	# 			if search_quarter3.pip_applicable:
	# 				pip_applicable=True
	# 			if tenure.years >= 1 and tenure.years < 2 and not (search_quarter4.id != False and search_quarter1.id != False and search_quarter2.id != False and search_quarter3.id != False):
	# 				print (emp_recs.name,'name',tenure.years)
	# 				self.write({'exists':True})
	# 				if pip_applicable:
	# 					self.env['appraisal.due.child'].create({
	# 													'pip_due_id':self.id,
	# 													'employee':emp_recs.id,
	# 													'emp_code':emp_recs.emp_code,
	# 													'joining_date':emp_recs.joining_date,
	# 													'parent_id':emp_recs.parent_id.id,
	# 													'department':emp_recs.department_id.id,
	# 													'designation':emp_recs.job_id.id,
	# 													'appraisal_cycle':emp_recs.appraisal_cycle,
	# 													'position_type':emp_recs.position_type
	# 						})
	# 				else:
	# 					self.env['appraisal.due.child'].create({
	# 													'due_id':self.id,
	# 													'employee':emp_recs.id,
	# 													'emp_code':emp_recs.emp_code,
	# 													'joining_date':emp_recs.joining_date,
	# 													'parent_id':emp_recs.parent_id.id,
	# 													'department':emp_recs.department_id.id,
	# 													'designation':emp_recs.job_id.id,
	# 													'appraisal_cycle':emp_recs.appraisal_cycle,
	# 													'position_type':emp_recs.position_type
	# 						})
	# 			elif tenure.years >= 1 and tenure.years < 2 and (search_quarter4.id != False and search_quarter1.id != False and search_quarter2.id != False and search_quarter3.id != False):
	# 				print (emp_recs.name,'name',tenure.years)
	# 				self.write({'exists':True})
					
	# 				if pip_applicable:
	# 					self.env['appraisal.due.child'].create({
	# 													'pip_due_id':self.id,
	# 													'employee':emp_recs.id,
	# 													'emp_code':emp_recs.emp_code,
	# 													'joining_date':emp_recs.joining_date,
	# 													'parent_id':emp_recs.parent_id.id,
	# 													'department':emp_recs.department_id.id,
	# 													'designation':emp_recs.job_id.id,
	# 													'appraisal_cycle':emp_recs.appraisal_cycle,
	# 													'position_type':emp_recs.position_type,
	# 													'quarter1':q1_rating,
	# 													'quarter2':q2_rating,
	# 													'quarter3':q3_rating,
	# 													'quarter4':q4_rating,
	# 						})
	# 				else:
	# 					self.env['appraisal.due.child'].create({
	# 													'due_id':self.id,
	# 													'employee':emp_recs.id,
	# 													'emp_code':emp_recs.emp_code,
	# 													'joining_date':emp_recs.joining_date,
	# 													'parent_id':emp_recs.parent_id.id,
	# 													'department':emp_recs.department_id.id,
	# 													'designation':emp_recs.job_id.id,
	# 													'appraisal_cycle':emp_recs.appraisal_cycle,
	# 													'position_type':emp_recs.position_type,
	# 													'quarter1':q1_rating,
	# 													'quarter2':q2_rating,
	# 													'quarter3':q3_rating,
	# 													'quarter4':q4_rating,
	# 						})
	# 			elif tenure.years >= 2 and (search_quarter4.id != False and search_quarter1.id != False and search_quarter2.id != False and search_quarter3.id != False):
	# 				print (emp_recs.name,'name',tenure.years)
	# 				self.write({'exists':True})
	# 				date_dt=False
	# 				q1_rating = ''
	# 				q2_rating = ''
	# 				q3_rating = ''
	# 				q4_rating = ''
	# 				emp_records1 = self.env['hr.employee'].search([('appraisal_cycle','=','July')])
	# 				for emp_recs1 in emp_records1:
	# 					current_date =  datetime.now().date()
	# 					joining_date = emp_recs1.joining_date
	# 					if joining_date:
	# 						date_dt= datetime.strptime(joining_date, "%Y-%m-%d").date()
	# 					current_date= datetime.strptime(str(current_date), "%Y-%m-%d").date()
	# 					tenure = relativedelta(current_date, date_dt)
	# 					get_year = get_current_financial_year(self)
	# 					search_year = self.env['year.master'].search([('name','=',str(get_year))])
	# 					if search_year:
	# 						year = search_year.id
	# 					split_year = get_year.split('-')
	# 					year1 = str(int(split_year[0])-1)
	# 					year2 = str(int(split_year[1])-1)
	# 					print (get_year,year1,year2)
	# 					pip_applicable = False
	# 					review_start_date1=year2+'-04-01'
	# 					review_end_date1=year2+'-06-30'
	# 					review_start_date2=year1+'-07-01'
	# 					review_end_date2=year1+'-09-30'
	# 					review_start_date3=year1+'-10-01'
	# 					review_end_date3=year1+'-12-31'
	# 					review_start_date4=year2+'-01-01'
	# 					review_end_date4=year2+'-03-31'
	# 					search_annual_form1=appraisal_obj.search([('employee','=',emp_recs1.id),('year','=',year),('status','=','approved')])
	# 					search_quarter2=kra_obj.search([('review_start_date','=',review_start_date2),('review_end_date','=',review_end_date2),('employee','=',emp_recs1.id),('state','=','done')])
	# 					search_quarter3=kra_obj.search([('review_start_date','=',review_start_date3),('review_end_date','=',review_end_date3),('employee','=',emp_recs1.id),('state','=','done')])
	# 					search_quarter4=kra_obj.search([('review_start_date','=',review_start_date4),('review_end_date','=',review_end_date4),('employee','=',emp_recs1.id),('state','=','done')])
	# 					search_quarter1=kra_obj.search([('review_start_date','=',review_start_date1),('review_end_date','=',review_end_date1),('employee','=',emp_recs1.id),('state','=','done')])
	# 					q1_rating = search_quarter1.final_rating
	# 					q2_rating = search_quarter2.final_rating
	# 					q3_rating = search_quarter3.final_rating
	# 					q4_rating = search_quarter4.final_rating
	# 					if not search_annual_form1:
	# 						self.env['appraisal.due.child'].create({
	# 															'skipped_due_id':self.id,
	# 															'employee':emp_recs1.id,
	# 															'emp_code':emp_recs1.emp_code,
	# 															'joining_date':emp_recs1.joining_date,
	# 															'parent_id':emp_recs1.parent_id.id,
	# 															'department':emp_recs1.department_id.id,
	# 															'designation':emp_recs1.job_id.id,
	# 															'appraisal_cycle':emp_recs1.appraisal_cycle,
	# 															'position_type':emp_recs1.position_type,
	# 															'quarter1':q1_rating,
	# 															'quarter2':q2_rating,
	# 															'quarter3':q3_rating,
	# 															'quarter4':q4_rating,									})
	# 				if not search_annual_form:
	# 					print ('emp_recs',emp_recs.name,q1_rating,q2_rating,q3_rating,q4_rating)
	# 					self.env['appraisal.due.child'].create({
	# 														'skipped_due_id':self.id,
	# 														'employee':emp_recs.id,
	# 														'emp_code':emp_recs.emp_code,
	# 														'joining_date':emp_recs.joining_date,
	# 														'parent_id':emp_recs.parent_id.id,
	# 														'department':emp_recs.department_id.id,
	# 														'designation':emp_recs.job_id.id,
	# 														'appraisal_cycle':emp_recs.appraisal_cycle,
	# 														'position_type':emp_recs.position_type,
	# 														'quarter1':q1_rating,
	# 														'quarter2':q2_rating,
	# 														'quarter3':q3_rating,
	# 														'quarter4':q4_rating,
	# 							})
	# 				else:
	# 					if pip_applicable:
	# 						print ('emp_recs',emp_recs.name,q1_rating,q2_rating,q3_rating,q4_rating)
	# 						self.env['appraisal.due.child'].create({
	# 														'pip_due_id':self.id,
	# 														'employee':emp_recs.id,
	# 														'emp_code':emp_recs.emp_code,
	# 														'joining_date':emp_recs.joining_date,
	# 														'parent_id':emp_recs.parent_id.id,
	# 														'department':emp_recs.department_id.id,
	# 														'designation':emp_recs.job_id.id,
	# 														'appraisal_cycle':emp_recs.appraisal_cycle,
	# 														'position_type':emp_recs.position_type,
	# 														'quarter1':q1_rating,
	# 														'quarter2':q2_rating,
	# 														'quarter3':q3_rating,
	# 														'quarter4':q4_rating,
	# 							})
	# 					else:
	# 						print ('emp_recs',emp_recs.name,q1_rating,q2_rating,q3_rating,q4_rating)
	# 						self.env['appraisal.due.child'].create({
	# 														'due_id':self.id,
	# 														'employee':emp_recs.id,
	# 														'emp_code':emp_recs.emp_code,
	# 														'joining_date':emp_recs.joining_date,
	# 														'parent_id':emp_recs.parent_id.id,
	# 														'department':emp_recs.department_id.id,
	# 														'designation':emp_recs.job_id.id,
	# 														'appraisal_cycle':emp_recs.appraisal_cycle,
	# 														'position_type':emp_recs.position_type,
	# 														'quarter1':q1_rating,
	# 														'quarter2':q2_rating,
	# 														'quarter3':q3_rating,
	# 														'quarter4':q4_rating,
	# 							})
	# 		if review_cycle == 'July':
	# 			get_year = get_current_financial_year(self)
	# 			search_year = self.env['year.master'].search([('name','=',str(get_year))])
	# 			if search_year:
	# 				year = search_year.id
	# 			split_year = get_year.split('-')
	# 			year1 = str(int(split_year[0])-1)
	# 			year2 = str(int(split_year[1])-1)
	# 			print (get_year,year1,year2)
	# 			pip_applicable = False
	# 			review_start_date1=year2+'-04-01'
	# 			review_end_date1=year2+'-06-30'
	# 			review_start_date2=year1+'-07-01'
	# 			review_end_date2=year1+'-09-30'
	# 			review_start_date3=year1+'-10-01'
	# 			review_end_date3=year1+'-12-31'
	# 			review_start_date4=year2+'-01-01'
	# 			review_end_date4=year2+'-03-31'
	# 			search_annual_form=appraisal_obj.search([('employee','=',emp_recs.id),('year','=',year),('status','=','approved')])
	# 			search_quarter2=kra_obj.search([('review_start_date','=',review_start_date2),('review_end_date','=',review_end_date2),('employee','=',emp_recs.id),('state','=','done')])
	# 			search_quarter3=kra_obj.search([('review_start_date','=',review_start_date3),('review_end_date','=',review_end_date3),('employee','=',emp_recs.id),('state','=','done')])
	# 			search_quarter4=kra_obj.search([('review_start_date','=',review_start_date4),('review_end_date','=',review_end_date4),('employee','=',emp_recs.id),('state','=','done')])
	# 			search_quarter1=kra_obj.search([('review_start_date','=',review_start_date1),('review_end_date','=',review_end_date1),('employee','=',emp_recs.id),('state','=','done')])
	# 			if search_quarter2.pip_applicable:
	# 				pip_applicable=True
	# 			if search_quarter3.pip_applicable:
	# 				pip_applicable=True
	# 			if search_quarter4.pip_applicable:
	# 				pip_applicable=True
	# 			if search_quarter1.pip_applicable:
	# 				pip_applicable=True
	# 			if tenure.years >= 1 and tenure.years <2 and not (search_quarter2.id != False and search_quarter3.id != False and search_quarter4.id != False and search_quarter1.id != False):
	# 				print (emp_recs.name,'name',tenure.years)
	# 				self.write({'exists':True})
	# 				if pip_applicable:
	# 					self.env['appraisal.due.child'].create({
	# 													'pip_due_id':self.id,
	# 													'employee':emp_recs.id,
	# 													'emp_code':emp_recs.emp_code,
	# 													'joining_date':emp_recs.joining_date,
	# 													'parent_id':emp_recs.parent_id.id,
	# 													'department':emp_recs.department_id.id,
	# 													'designation':emp_recs.job_id.id,
	# 													'appraisal_cycle':emp_recs.appraisal_cycle,
	# 													'position_type':emp_recs.position_type
	# 						})
	# 				else:
	# 					self.env['appraisal.due.child'].create({
	# 													'due_id':self.id,
	# 													'employee':emp_recs.id,
	# 													'emp_code':emp_recs.emp_code,
	# 													'joining_date':emp_recs.joining_date,
	# 													'parent_id':emp_recs.parent_id.id,
	# 													'department':emp_recs.department_id.id,
	# 													'designation':emp_recs.job_id.id,
	# 													'appraisal_cycle':emp_recs.appraisal_cycle,
	# 													'position_type':emp_recs.position_type
	# 						})
	# 			elif tenure.years >= 1 and tenure.years < 2 and (search_quarter2.id != False and search_quarter3.id != False and search_quarter4.id != False and search_quarter1.id != False):
	# 				print (emp_recs.name,'name',tenure.years)
	# 				self.write({'exists':True})
	# 				if pip_applicable:
	# 					self.env['appraisal.due.child'].create({
	# 													'pip_due_id':self.id,
	# 													'employee':emp_recs.id,
	# 													'emp_code':emp_recs.emp_code,
	# 													'joining_date':emp_recs.joining_date,
	# 													'parent_id':emp_recs.parent_id.id,
	# 													'department':emp_recs.department_id.id,
	# 													'designation':emp_recs.job_id.id,
	# 													'appraisal_cycle':emp_recs.appraisal_cycle,
	# 													'position_type':emp_recs.position_type,
	# 													'quarter1':search_quarter1.final_rating,
	# 													'quarter2':search_quarter2.final_rating,
	# 													'quarter3':search_quarter3.final_rating,
	# 													'quarter4':search_quarter4.final_rating,
	# 						})
	# 				else:
	# 					self.env['appraisal.due.child'].create({
	# 													'due_id':self.id,
	# 													'employee':emp_recs.id,
	# 													'emp_code':emp_recs.emp_code,
	# 													'joining_date':emp_recs.joining_date,
	# 													'parent_id':emp_recs.parent_id.id,
	# 													'department':emp_recs.department_id.id,
	# 													'designation':emp_recs.job_id.id,
	# 													'appraisal_cycle':emp_recs.appraisal_cycle,
	# 													'position_type':emp_recs.position_type,
	# 													'quarter1':search_quarter1.final_rating,
	# 													'quarter2':search_quarter2.final_rating,
	# 													'quarter3':search_quarter3.final_rating,
	# 													'quarter4':search_quarter4.final_rating,
	# 						})
	# 			elif tenure.years >= 2 and (search_quarter2.id != False and search_quarter3.id != False and search_quarter4.id != False and search_quarter1.id != False):
	# 				print (emp_recs.name,'name',tenure.years)
	# 				self.write({'exists':True})
	# 				emp_records1 = self.env['hr.employee'].search([('appraisal_cycle','=','January')])
	# 				for emp_recs1 in emp_records1:
	# 					current_date =  datetime.now().date()
	# 					joining_date = emp_recs1.joining_date
	# 					date_dt= datetime.strptime(joining_date, "%Y-%m-%d").date()
	# 					current_date= datetime.strptime(str(current_date), "%Y-%m-%d").date()
	# 					tenure = relativedelta(current_date, date_dt)
	# 					get_year = get_current_financial_year(self)
	# 					split_year = get_year.split('-')
	# 					year1 = str(int(split_year[0])-1)
	# 					year2 = str(int(split_year[1])-1)
	# 					get_year1  = year1+"-"+year2
	# 					search_year = self.env['year.master'].search([('name','=',str(get_year))])
	# 					if search_year:
	# 						year = search_year.id
	# 					split_year1 = get_year1.split('-')
	# 					year1 = str(int(split_year1[0])-1)
	# 					year2 = str(int(split_year1[1])-1)
	# 					print (year1,year2)
	# 					review_start_date1=year2+'-04-01'
	# 					review_end_date1=year2+'-06-30'
	# 					review_start_date2=year2+'-07-01'
	# 					review_end_date2=year2+'-09-30'
	# 					review_start_date3=year2+'-10-01'
	# 					review_end_date3=year2+'-12-31'
	# 					review_start_date4=year2+'-01-01'
	# 					review_end_date4=year2+'-03-31'
	# 					search_annual_form1=appraisal_obj.search([('employee','=',emp_recs1.id),('year','=',year),('status','=','approved')])
	# 					search_quarter4=kra_obj.search([('review_start_date','=',review_start_date4),('review_end_date','=',review_end_date4),('employee','=',emp_recs1.id),('state','=','done')])
	# 					search_quarter1=kra_obj.search([('review_start_date','=',review_start_date1),('review_end_date','=',review_end_date1),('employee','=',emp_recs1.id),('state','=','done')])							
	# 					search_quarter2=kra_obj.search([('review_start_date','=',review_start_date2),('review_end_date','=',review_end_date2),('employee','=',emp_recs1.id),('state','=','done')])
	# 					search_quarter3=kra_obj.search([('review_start_date','=',review_start_date3),('review_end_date','=',review_end_date3),('employee','=',emp_recs1.id),('state','=','done')])
	# 					if not search_annual_form1:
	# 						self.env['appraisal.due.child'].create({
	# 															'skipped_due_id':self.id,
	# 															'employee':emp_recs1.id,
	# 															'emp_code':emp_recs1.emp_code,
	# 															'joining_date':emp_recs1.joining_date,
	# 															'parent_id':emp_recs1.parent_id.id,
	# 															'department':emp_recs1.department_id.id,
	# 															'designation':emp_recs1.job_id.id,
	# 															'appraisal_cycle':emp_recs1.appraisal_cycle,
	# 															'position_type':emp_recs1.position_type,
	# 															'quarter1':search_quarter1.final_rating,
	# 															'quarter2':search_quarter2.final_rating,
	# 															'quarter3':search_quarter3.final_rating,
	# 															'quarter4':search_quarter4.final_rating,
	# 								})
	# 				if not search_annual_form:
	# 					self.env['appraisal.due.child'].create({
	# 													'skipped_due_id':self.id,
	# 													'employee':emp_recs.id,
	# 													'emp_code':emp_recs.emp_code,
	# 													'joining_date':emp_recs.joining_date,
	# 													'parent_id':emp_recs.parent_id.id,
	# 													'department':emp_recs.department_id.id,
	# 													'designation':emp_recs.job_id.id,
	# 													'appraisal_cycle':emp_recs.appraisal_cycle,
	# 													'position_type':emp_recs.position_type,
	# 													'quarter1':search_quarter1.final_rating,
	# 													'quarter2':search_quarter2.final_rating,
	# 													'quarter3':search_quarter3.final_rating,
	# 													'quarter4':search_quarter4.final_rating,
	# 						})
	# 				else:
	# 					if pip_applicable:
	# 						self.env['appraisal.due.child'].create({
	# 														'pip_due_id':self.id,
	# 														'employee':emp_recs.id,
	# 														'emp_code':emp_recs.emp_code,
	# 														'joining_date':emp_recs.joining_date,
	# 														'parent_id':emp_recs.parent_id.id,
	# 														'department':emp_recs.department_id.id,
	# 														'designation':emp_recs.job_id.id,
	# 														'appraisal_cycle':emp_recs.appraisal_cycle,
	# 														'position_type':emp_recs.position_type,
	# 														'quarter1':search_quarter1.final_rating,
	# 														'quarter2':search_quarter2.final_rating,
	# 														'quarter3':search_quarter3.final_rating,
	# 														'quarter4':search_quarter4.final_rating,
	# 							})
	# 					else:
	# 						self.env['appraisal.due.child'].create({
	# 														'due_id':self.id,
	# 														'employee':emp_recs.id,
	# 														'emp_code':emp_recs.emp_code,
	# 														'joining_date':emp_recs.joining_date,
	# 														'parent_id':emp_recs.parent_id.id,
	# 														'department':emp_recs.department_id.id,
	# 														'designation':emp_recs.job_id.id,
	# 														'appraisal_cycle':emp_recs.appraisal_cycle,
	# 														'position_type':emp_recs.position_type,
	# 														'quarter1':search_quarter1.final_rating,
	# 														'quarter2':search_quarter2.final_rating,
	# 														'quarter3':search_quarter3.final_rating,
	# 														'quarter4':search_quarter4.final_rating,
	# 							})	
	# 	return True

class AppraisalDueChild(models.Model):
	_name = 'appraisal.due.child'

	due_id = fields.Many2one('appraisal.due.report','')
	skipped_due_id = fields.Many2one('appraisal.due.report','')
	pip_due_id = fields.Many2one('appraisal.due.report','')
	employee= fields.Many2one('hr.employee','Employee')
	emp_code = fields.Integer('Employee Code')
	parent_id = fields.Many2one('hr.employee','Reporting Manager')
	department = fields.Many2one('hr.department','Department')
	designation = fields.Many2one('hr.job','Designation')
	appraisal_cycle = fields.Selection([('January','January'),('July','July')], string="Review Cycle")
	quarter1 = fields.Char('Q1')
	quarter2 = fields.Char('Q2')
	quarter3 = fields.Char('Q3')
	quarter4 = fields.Char('Q4')
	position_type = fields.Selection([('probation','Probation'),('confirm','Permanent')])
	pip_applicable = fields.Boolean('Eligible for PIP')
	select = fields.Boolean('Select')
	joining_date = fields.Date('Joining Date')

class EmployeeReportingHierarchy(models.Model):
	_name = "employee.reporting.hierarchy"

	name = fields.Many2one('hr.employee','Employee Name')
	reportee_1 = fields.Many2one('hr.employee','Reportee 1')
	reportee_2 = fields.Many2one('hr.employee','Reportee 2')
	reportee_3 = fields.Many2one('hr.employee','Reportee 3')
	hr_reportee = fields.Many2one('hr.employee','HR')
	sub_department_form = fields.Many2one('sub.department','Form Applicable')
	emp_code = fields.Char('Employee Code')
	reportee1_code = fields.Char('Reportee1 Code')
	reportee2_code = fields.Char('Reportee2 Code')
	reportee3_code = fields.Char('Reportee3 Code')
	hr_reportee_code = fields.Char('HR Reportee Code')


	@api.model
	def create(self,vals):
		kra_id =super(EmployeeReportingHierarchy, self).create(vals)
		print (vals,'valssss')
		vals.update
		if vals.get('name') and vals.get('sub_department_form'):
			search_emp = self.env['hr.employee'].search([('id','=',vals['name'])])
			if search_emp:
				search_emp.write({'pms_form_applicable':vals['sub_department_form']})
				emp_rec = self.search([('name','=',search_emp.id)])
				if emp_rec:
					emp_rec.unlink()
				if vals.get('hr_reportee'):
					search_emp1 = self.env['hr.employee'].search([('id','=',vals['hr_reportee'])])
					if search_emp1:
						search_emp.write({'hr_executive_id':search_emp1.id})
		if vals.get('emp_code') and vals.get('sub_department_form'):
			search_emp = self.env['hr.employee'].search([('emp_code','=',vals['emp_code'])])
			if search_emp:
				vals.update({'name':search_emp.id})
				search_emp.write({'pms_form_applicable':vals['sub_department_form']})
				emp_rec = self.search([('name','=',search_emp.id)])
				if emp_rec:
					emp_rec.unlink()
				if vals.get('hr_reportee_code'):
					search_emp1 = self.env['hr.employee'].search([('emp_code','=',vals['hr_reportee_code'])])
					if search_emp1:
						search_emp.write({'hr_executive_id':search_emp1.id})
		if vals.get('reportee1_code'):
			search_emp = self.env['hr.employee'].search([('emp_code','=',vals['reportee1_code'])])
			if search_emp:
				vals.update({'reportee_1':search_emp.id})
		if vals.get('hr_reportee_code'):
			search_emp = self.env['hr.employee'].search([('emp_code','=',vals['hr_reportee_code'])])
			if search_emp:
				vals.update({'hr_reportee':search_emp.id})
		if vals.get('reportee2_code'):
			search_emp = self.env['hr.employee'].search([('emp_code','=',vals['reportee2_code'])])
			if search_emp:
				vals.update({'reportee_2':search_emp.id})
		kra_id.update(vals)
		return kra_id

	@api.multi
	def write(self,vals):
		if vals.get('hr_reportee'):
			search_emp1 = self.env['hr.employee'].search([('id','=',vals['hr_reportee'])])
			if search_emp1:
				employee = self.name
				employee.write({'hr_executive_id':search_emp1.id})
		if vals.get('sub_department_form'):
			employee = self.name
			employee.write({'pms_form_applicable':vals['sub_department_form']})
		if vals.get('reportee_1'):
			search_emp = self.env['hr.employee'].search([('id','=',vals['reportee_1'])])
			if search_emp:
				employee = self.name
				employee.write({'parent_id':search_emp.id})
		return super(EmployeeReportingHierarchy, self).write(vals)
		

	@api.onchange('name')
	def onchange_name(self):
		res = {}
		if not self.name or not self.name:
			return
		else:
			self.emp_code = self.name.emp_code
			self.reportee_1 = self.name.parent_id.id if self.name.parent_id.id else None
			self.reportee_2 = self.name.parent_id.parent_id.id if self.name.parent_id.parent_id.id else None
			self.reportee_3 = self.name.parent_id.parent_id.parent_id.id if self.name.parent_id.parent_id.parent_id.id else None
			self.hr_reportee = self.name.hr_executive_id.id if self.name.hr_executive_id.id else None
		return res

class IncrementList(models.Model):
	_name = 'increment.list'

	select_type = fields.Selection([('year','Year'),('review_month','Review Month'),('status','Status')],string="Select Type")
	financial_year = fields.Many2one('year.master', 'Year')
	review_cycle = fields.Selection([('July','July'),('January','January')], string='Review Month') 
	state = fields.Selection([('pending','Pending'),('approved','Approved')],'Status')
	increment_child_list_one2many = fields.One2many('increment.child.list','inc_list_id','')

	@api.multi
	def view_increment_list(self):
		print (self.id)
		self.ensure_one()
		if not self.increment_child_list_one2many:
			raise ValidationError(_("No record to view!!"))
		elif self.increment_child_list_one2many:
			for rec in self.increment_child_list_one2many:
				rec.write({'readonly_chk':False})
				if rec.select:
					kra_form = self.env.ref('orient_pms.view_incrementrecord_form', False)

					return {
						'name': _('(Increment)'),
						'type': 'ir.actions.act_window',
						'view_type': 'form',
						'view_mode': 'form',
						'res_model': 'increment.child.list',
						'res_id': rec.id,
						'views': [(kra_form.id, 'form')],
						'view_id': self.id,
						'target': 'new',
					}
		else:
			raise ValidationError(_("No record selected!!"))

	@api.multi
	def add_increment_list(self):
		print (self.id)
		year = None
		self.ensure_one()
		increment_list_child_obje = self.env['increment.child.list']
		kra_form = self.env.ref('orient_pms.view_incrementrecord_form', False)
		get_year = get_current_financial_year(self)
		split_year = get_year.split('-')
		get_year =  get_year.split('-')
		get_year1 = int(get_year[0])+1
		get_year2 = int(get_year[1])+1
		get_year3 = str(get_year1) + "-" + str(get_year2)
		employee = self.env['hr.employee'].search([('user_id','=',self._uid)])
		review_start_date = ''
		review_end_date = ''
		year1 = str(split_year[0])
		year2 = str(split_year[1])
		print (year1,year2)
		if employee.appraisal_cycle == 'January':
			review_start_date = year1+'-01-01'
			review_end_date = year1+'-12-31'
		if employee.appraisal_cycle == 'July':
			review_start_date = str(int(year2)-1)+'-07-01'
			review_end_date = year2+'-06-30'
		search_subordinate = self.env['hr.employee'].search([('parent_id','=',employee.id)])
		gs_id = increment_list_child_obje.create({'employee_code':employee.emp_code,
			'employee':employee.id,
			'designation':employee.job_id.id,
			'department':employee.department_id.id,
			'location':employee.site_master_id.id,
			'joining_date':employee.joining_date,
			'main_id':self.id,'inc_list_id':None,'status':'pending',
			'readonly_chk':False,
			'review_start_date':review_start_date,
			'review_end_date':review_end_date,
			})

		search_subordinate = self.env['hr.employee'].search([('parent_id','=',employee.id)])
		print (search_subordinate)
		for m in search_subordinate:
			kra_recs = self.env['annual.kra.details'].search([('employee','=',m.id),('status','=','approved'),('increment_status','=','not_updated')])
			print (kra_recs)
			if kra_recs:
				count=0
				search_recs = self.env['employee.reporting.hierarchy'].search([('name','=',m.id)])
				if search_recs:
					count=0
					for c in search_recs:
						if c.reportee_1.id != False:
							count+=1 
						if c.reportee_2.id != False:
							count+=1
						if c.reportee_3.id != False:
							count+=1
						if c.hr_reportee.id != False:
							count+=1
				if count==0:
					count=1
				for s in kra_recs:
					s.write({'current_gross':m.gross_salary,'current_ctc':m.current_ctc,
						'reporting_levels':count,})
		return {
			'name': _('Increment List'),
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'increment.child.list',
			'res_id': gs_id.id,
			'views': [(kra_form.id, 'form')],
			'view_id': self.id,
			'target': 'new',
		}


	@api.multi
	def search_increment_list(self):
		select_type = self.select_type
		if self.increment_child_list_one2many:
			for i in self.increment_child_list_one2many:
				if i.inc_list_id.id:
					i.write({'inc_list_id':None})

		if select_type == 'year':
			financial_year = self.financial_year.id

			year_record = self.env['increment.child.list'].search([('year','=',financial_year)])
			if year_record:
				for y in year_record:
					y.write({'inc_list_id':self.id})			
			
		elif select_type == 'review_month':
			review_cycle = self.review_cycle
			month_record = self.env['increment.child.list'].search([('review_cycle','=',review_cycle)])
			if month_record:
				for m in month_record:
					m.write({'inc_list_id':self.id})

		elif select_type == 'status':
			state = self.state
			state_record = self.env['increment.child.list'].search([('status','=',state)])
			if state_record:
				for s in state_record:
					s.write({'inc_list_id':self.id})				
		return True

class IncrementChildList(models.Model):
	_name = 'increment.child.list'

	inc_list_id = fields.Many2one('increment.list','')
	select = fields.Boolean('Select')
	employee_code = fields.Char('Employee Code')
	employee = fields.Many2one('hr.employee','Employee Name')
	location = fields.Many2one('site.master','Location')
	designation = fields.Many2one('hr.job','Designation')
	department = fields.Many2one('hr.department','Department')
	joining_date = fields.Date('Joining Date')
	year = fields.Many2one('year.master','Year')
	review_cycle = fields.Selection([('January','January'),('July','July')], string="Review Cycle")
	review_start_date = fields.Date('Review Start Date')
	review_end_date = fields.Date('Review End Date')
	status = fields.Selection([('pending','Pending'),('approved','Approved'),('rejected','Rejected')],'Status')
	increment_rec_one2many_new = fields.One2many('annual.kra.details','inc_child_list_id1','')
	main_id = fields.Char('Main ID')
	readonly_chk = fields.Boolean('Check',default=False)
	active = fields.Boolean('Active',default=True)



	@api.multi
	def save_exit(self):
		for recs in self:
			get_year = get_current_financial_year(self)
			split_year = get_year.split('-')
			review_start_date = ''
			review_end_date = ''
			year1 = str(split_year[0])
			year2 = str(split_year[1])
			print (year1,year2)
			if recs.employee.appraisal_cycle == 'January':
				review_start_date = year1+'-01-01'
				review_end_date = year1+'-12-31'
			if recs.employee.appraisal_cycle == 'July':
				review_start_date = str(int(year2)-1)+'-07-01'
				review_end_date = year2+'-06-30'
			for rec in recs.increment_rec_one2many_new:
				print (rec.id)
				if rec.actual_increment == 0.0 :
					raise ValidationError(_("Kindly enter proper increment value!"))
				print (rec.annual_kra_id,'ppppppppppp')
				rec.write({'actual_increment':rec.actual_increment,'increment_status':'updated'})
			self.write({'inc_list_id':self.main_id,'readonly_chk':True,'status':'approved','review_start_date':review_start_date,'review_end_date':review_end_date})

	@api.onchange('year','review_cycle','increment_rec_one2many_new')
	def onchange_year(self):
		print (self.id,'selffff',self._origin.id,self.year.id,self.review_cycle)
		res = {'increment_rec_one2many_new':None}
		search_subordinate = self.env['hr.employee'].search([('parent_id','=',self.employee.id)])
		for m in search_subordinate:
			kra_recs = self.env['annual.kra.details'].search([('employee','=',m.id),('status','=','approved'),('increment_status','=','not_updated'),('year','=',self.year.id),('review_cycle','=',self.review_cycle)])
			print("kra_recssssssss",kra_recs)
			if kra_recs:
				for s in kra_recs:
					print(m.current_ctc, (type(m.current_ctc)))
					self.update({'increment_rec_one2many_new':[(1, s.id , {'inc_child_list_id1':self._origin.id})]})
				return res
			else:
				self.write({'increment_rec_one2many_new':[(6, 0, None)]})
				return res

class KraFreezeDate(models.Model):
	_name = 'kra.freeze.date'

	from_date = fields.Date('From Date')
	to_date = fields.Date('To Date')

class KraMappingReport(models.Model):
	_name = 'kra.mapping.report'

	def _get_default_access_token(self):
		return str(uuid.uuid4())

	report_type = fields.Selection([('employee','Employee Wise'),('designation','Designation Wise')],'Report Type',default="employee")
	employee = fields.Many2one('hr.employee','Employee')
	department = fields.Many2one('hr.department','Department')
	exists = fields.Boolean('Exists',default=False)
	mapping_report_one2many = fields.One2many('mapping.report.lines','mapping_report_lines_id','')
	access_token = fields.Char('Security Token', copy=False,default=_get_default_access_token)

	@api.model_cr_context
	def _init_column(self, column_name):
		""" Initialize the value of the given column for existing rows.

			Overridden here because we need to generate different access tokens
			and by default _init_column calls the default method once and applies
			it for every record.
		"""
		if column_name != 'access_token':
			super(KraMappingReport, self)._init_column(column_name)
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
	def search_records(self,access_uid=None):
		self.ensure_one()
		emp_obj = self.env['hr.employee']		
		mapping_report_obj = self.env['mapping.report.lines']
		kra_mapping_obj = self.env['kra.mapping.report']
		if self.mapping_report_one2many:
			for line in self.mapping_report_one2many:
				line.unlink()
		if not self.report_type:
			raise ValidationError(_("Kindly select Report Type!"))
		kra_mapped = ''
		status = ''
		search_emp = emp_obj.search([('id','>',0)])
		if search_emp:
			sr_no = 1
			for emp_rec in search_emp:
				if emp_rec.cost_center_id.name!='ITES - FMS/PS' and emp_rec.department_id.name not in ('FM','FM Backup'):
					if emp_rec.kra_one2many:
						kra_mapped = 'yes'
					else:
						kra_mapped = 'no'
					if emp_rec.active:
						status = 'active'
					else:
						status = 'inactive'
					if emp_rec.name!='Administrator':
						emp_qr = mapping_report_obj.create({
									'sr_no':sr_no,
									'mapping_report_lines_id':self.id,
									'reporting_code':emp_rec.parent_id.emp_code,
									'reporting_name':emp_rec.parent_id.name,
									'hr_code':emp_rec.hr_executive_id.emp_code,
									'hr_name':emp_rec.hr_executive_id.name,
									'employee':emp_rec.id,
									'employee_name':emp_rec.name,
									'employee_code':emp_rec.emp_code,
									'designation':emp_rec.job_id.id,
									'department':emp_rec.department_id.id,
									'kra_mapped':kra_mapped,
									'status':status,
									'joining_date':emp_rec.joining_date					
									})
						sr_no+=1
		rm_list = []					
		count=1
		sr_no_list=[]
		for rec in range(0,len(rm_list)):
			search_lines = mapping_report_obj.search([('sr_no','=',count),('mapping_report_lines_id','=',self.id)])
			for recs in search_lines:
				sr_no_list.append(recs.id)
			if (len(sr_no_list)>1):
				for recs1 in search_lines:
					if recs1.id!=sr_no_list[0]:
						recs1.write({'sr_no':False,'reporting_name':False,'reporting_code':False})
			count+=1
			sr_no_list = []
		self.write({'exists':True})
		return {
		'type': 'ir.actions.act_url',
		'url': '/web/pivot/export_mapping_xls/%s?access_token=%s' % (self.id, self.access_token),
		'target': 'new',
		}

class MappingReportLines(models.Model):
	_name = 'mapping.report.lines'
	_order = 'employee_code asc'

	sr_no = fields.Integer('Sr. No.')
	reporting_code = fields.Char('Reporting Code')
	reporting_name = fields.Char('Reporting Name')
	hr_code = fields.Char('HR Code')
	hr_name = fields.Char('HR Name')
	joining_date = fields.Date('Joining Date')
	mapping_report_lines_id = fields.Many2one('kra.mapping.report','')
	employee = fields.Many2one('hr.employee','Employee')
	employee_name = fields.Char('Employee Name')
	department =  fields.Many2one('hr.department','Department')
	designation = fields.Many2one('hr.job','Designation')
	employee_code = fields.Char('Employee Code')
	kra_mapped = fields.Selection([('yes','Yes'),('no','No')],'KRA Mapped?')
	status = fields.Selection([('active','Active'),('inactive','Inactive')],default='active',string='Status')


class QuarterlyRatingUpload(models.Model):
	_name = 'quarterly.rating.upload'

	@api.model
	def _file_read(self, full_path, fname, bin_size=False):
		import_config = self.env['import.config'].search([],limit=1)
		source_path = str(import_config.source_path)
		destination_path = str(import_config.destination_path)
		full_path = source_path
		r = ''
		try:
			if bin_size:
				r = human_size(os.path.getsize(full_path))
			else:
				r = base64.b64encode(open(full_path,'rb').read())
		except (IOError, OSError):
			_logger.info("_read_file reading %s", full_path, exc_info=True)
		return r


	@api.depends('datas_fname','db_datas')
	def _compute_datas(self):
		bin_size = self._context.get('bin_size')
		result ={}
		for attach in self:
			if attach.datas_fname:
				result[attach.id]= self._file_read(attach.file_url,attach.datas_fname, bin_size)
			else:
				result[attach.id] = attach.db_datas


	@api.model
	def _file_write(self, value, file_name):
		db_datas = value
		bin_value = base64.b64decode(value)
		fname = file_name
		import_config = self.env['import.config'].search([],limit=1)
		source_path = str(import_config.source_path)
		destination_path = str(import_config.destination_path)
		full_path = source_path+fname
		if not os.path.exists(full_path):
			try:
				with open(full_path, 'wb') as fp:
					fp.write(bin_value)
					os.chmod(full_path,0o777)
					# shutil.chown(full_path, user='odoouser', group='odoouser')
			except IOError:
				_logger.info("_file_write writing %s", full_path, exc_info=True)
		return full_path


	def _inverse_datas(self):
		for attach in self:
			# compute the fields that depend on datas
			file_name = attach.datas_fname
			fname = ''
			if not file_name:
				raise ValidationError(_('Kindly select file for import!!'))
			value = attach.datas
			bin_data = base64.b64decode(value) if value else b''
			if file_name.endswith('.xls'):
				fname = self._file_write(value,file_name)
			vals={'file_url':fname}
			# write as superuser, as user probably does not have write access
			super(QuarterlyRatingUpload, attach.sudo()).write(vals)

	name = fields.Char('Name',default="Import Quarterly Data")
	file_url = fields.Char('Url', index=True, size=1024)
	datas_fname = fields.Char('File Name')
	datas = fields.Binary(string='File Content', compute='_compute_datas', inverse='_inverse_datas')
	db_datas = fields.Binary('Database Data')
	state = fields.Selection([('draft', 'Draft'),('done', 'Done'),('failed','Failed')], string='Status', default='draft')
	check_exists = fields.Boolean('Check Exists', default=False)


	@api.multi
	def import_quarterly_data(self):
		todays_date = datetime.now()
		append_data=[]
		attendance_date_val =[]
		check_year_id = False
		year = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").year
		month = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").month
		search_year = self.env['year.master.annual'].search([('name','=',str(year))])
		if search_year:
			check_year_id=search_year[0].id
		kra_obj = self.env['kra.main']
		kra_rating_obj = self.env['kra.rating']
		pip_obj = self.env['pip.list']
		for rec in self:
			if not rec.datas_fname:
				raise ValidationError(_('Kindly select file for import!!'))
			datas_fname = str(rec.datas_fname)
			import_config = self.env['import.config'].search([],limit=1)
			source_path = str(import_config.source_path)
			destination_path = str(import_config.destination_path)
			failed_path = str(import_config.failed_path)
			file_path = source_path+datas_fname
			workbook = open_workbook(file_path)
			worksheet = workbook.sheet_by_index(0)
			try:
				for row in range(1, worksheet.nrows):
					m1_flag = False
					m2_flag = False
					m3_flag = False
					weightage = 0.0
					total_weightage = 0.0
					ratings = 0.0
					# print("row------",row)
					emp_code = worksheet.cell(row,4).value
					# if emp_code==7929.0:
					quarter = worksheet.cell(row,2).value
					m1_rating = worksheet.cell(row,7).value
					m2_rating = worksheet.cell(row,8).value
					m3_rating = worksheet.cell(row,9).value
					print (m1_rating,m2_rating,m3_rating,'rating')
					# if m2_rating == '':
					# 	print ('consider blank')
					# if m3_rating == '':
					# 	print ('consider blank')
					if m1_rating!='':
						m1_flag=True
					if m2_rating!='':
						m2_flag=True
					if m3_rating!='':
						m3_flag=True
					if m1_flag and m2_flag and m3_flag:
						weightage = float(m1_rating+m2_rating+m3_rating)/3
						# total_weightage+=weightage
					if m1_flag and m2_flag and not m3_flag:
						weightage = float(m1_rating+m2_rating)/2
						# total_weightage+=weightage
					if m1_flag and m3_flag and not m2_flag:
						weightage = float(m1_rating+m3_rating)/2
						# total_weightage+=weightage
					if m2_flag and m3_flag and not m1_flag:
						weightage = float(m2_rating+m3_rating)/2
						# total_weightage+=weightage
					if m1_flag and not m2_flag and not m3_flag:
						weightage = float(m1_rating)
						# total_weightage+=weightage
					if not m1_flag and m3_flag and not m2_flag:
						weightage = float(m3_rating)
						# total_weightage+=weightage
					if m2_flag and not m3_flag and not m1_flag:
						weightage = float(m2_rating)
					if quarter == 'Q1':
						quarter = 'First'
						review_start = '2018-04-01'
						review_end = '2018-06-30'
						kra_month = 'June'
					if quarter == 'Q2':
						quarter = 'Second'
						review_start = '2018-07-01'
						review_end = '2018-09-30'
						kra_month = 'September'
					if quarter == 'Q3':
						quarter = 'Third'
						review_start = '2018-10-01'
						review_end = '2018-12-31'
						kra_month = 'December'
					if quarter == 'Q4':
						quarter = 'Fourth'
						review_start = '2019-01-01'
						review_end = '2019-03-31'
						kra_month = 'March'
					search_emp = self.env['hr.employee'].search([('emp_code', '=', int(emp_code))])
					if search_emp:
						check_record = self.env['kra.main'].search([('employee_code','=',emp_code),('kra_year','=',12),('quarter','=',quarter),('state','=','done')])
						if not check_record:
							# print (emp_code,'emp_codeee')
							emp_kra = kra_obj.create({
							'employee':search_emp.id,
							'company_id':1,
							'employee_code':emp_code,
							'designation':search_emp.job_id.id,
							'department':search_emp.department_id.id,
							'location':search_emp.company_id.id,
							'kra_year':12,
							'quarter':quarter,
							'active':True,
							'review_start_date':review_start,
							'review_end_date':review_end,
							'check1': False,
							'state': 'done',
							'application_date': str(datetime.now().date()),	
							'kra_month': kra_month,						
							})
							print('weightage,man_rating',weightage)
							create_id = kra_rating_obj.create({
										# 'sr_no':str(count),
										# 'kra':kra.id.kra_master_id.id,
										'kra_name':worksheet.cell(row,5).value,
										'description':worksheet.cell(row,6).value,
										'man_rating':round(weightage),
										'kra_id':kra_obj.browse(emp_kra.id).id,
										'check1':False,
										})
						else:
							create_id = kra_rating_obj.create({
										# 'sr_no':str(count),
										# 'kra':kra.id.kra_master_id.id,
										'kra_name':worksheet.cell(row,5).value,
										'description':worksheet.cell(row,6).value,
										'man_rating':round(weightage),
										'kra_id':check_record.id,
										'check1':False,
										})
							print (weightage,'llllllllllllll')
							if check_record.kra_one2many:
								for x in check_record.kra_one2many:
									total_weightage+=float(x.man_rating)
							total_weightage = round(total_weightage)
							print (total_weightage,'total_weightagemmmmmmmmmmmmm')
							scale_new= self.env['appraisal.scale'].search([('minimum','<=',float(total_weightage)),('maximum','>=',float(total_weightage))])
							check_record.write({'final_rating':scale_new.scale,'pip_applicable':scale_new.pip_applicable})
								# if scale_new.scale <= 2.0:
								# 	create_id1 = pip_obj.create({
								# 							'employee':search_emp.id,
								# 							'designation':search_emp.job_id.id,
								# 							'quarter':quarter,
								# 							'kra_year':12,
								# 							'ratings':scale_new.scale,
								# 							})
					# self.write({'check_exists':True})
				destination_file_name = datas_fname.split('.')
				main_file_name = destination_file_name[0]+'_'+str(todays_date)+'.'+destination_file_name[1]
				destination_path = destination_path+main_file_name
				state = 'done'
			except Exception  as exc:
				destination_file_name = datas_fname.split('.')
				main_file_name = destination_file_name[0]+'_'+str(todays_date)+'.'+destination_file_name[1]
				destination_path = failed_path+main_file_name
				state = 'failed'
			rec.state = state
			shutil.move(file_path,destination_path)

