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
from odoo.tools import consteq, float_round, image_resize_images, image_resize_image, ustr


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

month_sel = (('January', 'January'),('February', 'February'),('March', 'March'),('April', 'April'),('May', 'May'),('June','June'),('July','July'),('August','August'),('September','September'),('October','October'),('November','November'),('December','December'))

class KraMaster(models.Model):
	_name = 'kra.master'

	name = fields.Char('KRA')
	designation = fields.Many2many('hr.job','kra_designation_rel', 'kra_designation_id', 'designation_kra_id',copy=False, string='Designation')
	employee = fields.Many2many('hr.employee',string='Emp Name')
	all_employee = fields.Boolean('All Employee')
	kpi_one2many = fields.One2many('kra.kpi','kpi_id','KPI')
	weightage = fields.Float('Weightage')
	active = fields.Boolean('Active',default=True)

	@api.model
	def create(self,vals):
		print("create")
		total_weightage=0.0
		kpi=''
		kra=''
		kra_id =super(KraMaster, self).create(vals)
		print (kra_id.id,kra_id)
		if kra_id:
			kpi_id = kra_id.kpi_one2many
			if kpi_id:
				for kpis in kpi_id:
					total_weightage += float(kpis.weightage)
					if kpis.weightage==0.0:
						raise ValidationError(_("Weightage of KPI cannot be 0!!"))
					if kpis.weightage<0.0:
						raise ValidationError(_("Weightage of KPI cannot be less than 0!!"))
				kra_id.weightage=total_weightage
				if float(total_weightage)!=float(kra_id.weightage):
					raise ValidationError(_("Total Weightage of KPI's does not match with KRA Weightage!!"))
			else:
				raise ValidationError(_("Kindly Map KPI's to KRA!!"))

			if vals.get('designation'):
				designation = vals.get('designation')
				designation_ids = designation[0][2]

				for each in designation_ids:
					job_id = self.env['hr.job'].browse(each).id
					if job_id:
						kpi_id = kra_id.kpi_one2many
						if kpi_id:
							count=1
							for kpis in kpi_id:
								if count>1:
									kra = ''
								else:
									kra = kra_id.name
								self.env['kra.job'].create({'job_kra_id':job_id,
															'kra_master':kra_id.id,
															'kra_name':kra,
															'kpi':kpis.name.name,
															'weightage':kpis.weightage,
															})
								count+=1	
		return kra_id	

	@api.multi
	def write(self, vals):
		total_weightage=0.0
		kra=''
		kra_id=super(KraMaster, self).write(vals)
		print (kra_id,'writeeeee')
		if vals.get('kpi_one2many'):
			kpi_id = self.kpi_one2many
			if kpi_id:
				for kpis in kpi_id:
					total_weightage += float(kpis.weightage)
					if kpis.weightage==0.0:
						raise ValidationError(_("Weightage of KPI cannot be 0!!"))
					if kpis.weightage<0.0:
						raise ValidationError(_("Weightage of KPI cannot be less than 0!!"))
				self.env.cr.execute('update kra_master set weightage=%s where id=%s',(total_weightage,self.id))
				self.env.cr.commit();
				if float(total_weightage)!=float(self.weightage):
					raise ValidationError(_("Total Weightage of KPI's does not match with KRA Weightage!!"))
			else:
				raise ValidationError(_("Kindly Map KPI's to KRA!!"))
		if vals.get('weightage'):
			kpi_id = self.kpi_one2many
			if kpi_id:
				for kpis in kpi_id:
					total_weightage += float(kpis.weightage)
					if kpis.weightage==0:
						raise ValidationError(_("Weightage of KPI cannot be 0!!"))
					if kpis.weightage<0:
						raise ValidationError(_("Weightage of KPI cannot be less than 0!!"))
				self.env.cr.execute('update kra_master set weightage=%s where id=%s',(total_weightage,self.id))
				self.env.cr.commit();
				if float(total_weightage)!=float(self.weightage):
					raise ValidationError(_("Total Weightage of KPI's does not match with KRA Weightage!!"))

		if vals.get('designation'):
			designation = vals.get('designation')
			designation_ids = designation[0][2]

			for each in designation_ids:
				job_id = self.env['hr.job'].browse(each)
				if job_id:
					k_id = self.env['kra.job'].search([('job_kra_id','=',job_id.id),('kra_master','=',self.id)])
					if not k_id:
						kpi_id = self.kpi_one2many
						if kpi_id:
							count = 1
							for kpis in kpi_id:
								if count > 1:
									kra = ''
								else:
									kra = self.name
								self.env['kra.job'].create({'job_kra_id':job_id.id,
															'kra_master':self.id,
															'kra_name':kra,
															'kpi': kpis.name.name,
															'weightage':kpis.weightage,
															})
								count+=1
					else:
						kpi_id = self.kpi_one2many
						if kpi_id:
							count = 1
							for kpis in kpi_id:
								if count > 1:
									kra = ''
								else:
									kra = self.name
								self.env['kra.job'].write({'job_kra_id':job_id.id,
															'kra_master':self.id,
															'kra_name':kra,
															'kpi': kpis.name.name,
															'weightage':kpis.weightage,
															})
								count+=1
		return kra_id


class KraKpi(models.Model):
	_name = 'kra.kpi'

	name = fields.Many2one('kpi.master','Question')
	description = fields.Char('Description')
	hint = fields.Char('Hint')
	weightage = fields.Float('Weightage')
	kpi_id = fields.Many2one('kra.master','KRA')

	@api.onchange('name')
	def onchange_name(self):
		res = {}
		if not self.name or not self.name:
			return
		else:
			name = self.name.id
			kpa_data = self.env['kpi.master'].browse(name)
			self.description = kpa_data.description
			self.weightage = kpa_data.weightage
		return res


class KpiMaster(models.Model):
	_name = 'kpi.master'

	name = fields.Char('Question')
	description = fields.Char('Description')
	hint = fields.Char('Hint')
	weightage = fields.Float('Weightage')
	kpi_id = fields.Many2one('kra.master','KRA')
	active = fields.Boolean('Active', default=True)

class EmployeeKpi(models.Model):
	_name = 'employee.kpi'

	kpi_name = fields.Char('Question')
	description = fields.Char('Description')
	hint = fields.Char('Hint')
	kpi_weightage = fields.Float('Weightage')
	emp_kpi_id = fields.Many2one('employee.kra.kpi','KRA')


class JobTemplate(models.Model):
	_name = "job.template"

	name = fields.Char('Name')
	department = fields.Many2one('hr.department','Department')
	kra = fields.Many2one('kra.master','KRA')
	expected_employees = fields.Integer('Expected New Employees')
	decription = fields.Char('Job Description')


class KraRating(models.Model):
	_name="kra.rating"

	kra = fields.Many2one('kra.master','Question')
	kra_name = fields.Char('Key Result Area')
	description = fields.Char('Description')
	hint = fields.Char('Hint')
	weightage = fields.Float('Weightage')
	emp_rating = fields.Float('Employee Rating')
	emp_remarks = fields.Char('Employee Remarks')
	man_rating = fields.Float('Manager Rating')
	man_remarks = fields.Char('Manager Remarks')
	final = fields.Float('Final Score')
	kra_id = fields.Many2one('kra.main','KRA id')
	sr_no = fields.Char('Sr. No.')
	check1 = fields.Boolean(string="check field", compute='get_user')
	check2 = fields.Boolean(string="check fields", compute='get_user')
	state = fields.Selection([('draft','Pending'),('done','Approved'),('cancel','Rejected')
								], string="State", default='draft')
	self_check = fields.Boolean('Self Check')
	comments = fields.Char('Comments')	

	def get_user(self):
		for each in self:
			employee = each.kra_id.employee.user_id.id
			res_user = self.env['res.users'].search([('id', '=', each._uid)])
			if res_user.has_group('hr.group_hr_manager') or res_user.has_group('hr.group_hr_user') or res_user.has_group('orient_hr_resignation.group_reporting_manager'):
				if employee == res_user.id:
					each.check1 = False
					each.check2 = True
				else:
					if each.kra_id.employee.parent_id.user_id.id == res_user.id:
						each.check1 = True
						each.check2 = False
					else:
						each.check1 = False
						each.check2 = True
			else:
				each.check1 = False
				each.check2 = True

	@api.onchange('kra')
	def onchange_name(self):
		res = {}
		if not self.kra or not self.kra:
			return
		else:
			kra = self.kra.id
			print(kra)
			kpa_data = self.env['kpi.master'].browse(kra)
			self.description = kpa_data.description
			self.weightage = kpa_data.weightage
		return res

class KraMain(models.Model):
	_name = "kra.main"
	_rec_name = 'employee'

	def _get_default_access_token(self):
		return str(uuid.uuid4())

	kra_month = fields.Selection([('January', 'January'),('February', 'February'),
								('March', 'March'),('April', 'April'),
								('May', 'May'),('June','June'),
								('July','July'),('August','August'),
								('September','September'),('October','October'),
								('November','November'),('December','December')
								], string='KRA Month')
	final_rating = fields.Float('Rating')
	kra_year = fields.Many2one('year.master','Year')
	quarter  = fields.Selection([('First','First Quarter'),('Second','Second Quarter'),
								 ('Third','Third Quarter'),('Fourth','Fourth Quarter')
								], string="KRA Quarter")
	employee = fields.Many2one('hr.employee','Employee')
	parent_id = fields.Many2one('hr.employee','Reporting Manager')
	parent_work_email = fields.Char('Manager Email')
	company_id = fields.Many2one('res.company','Company')
	designation = fields.Many2one('hr.job','Designation')
	employee_code = fields.Char('Employee Code')
	department = fields.Many2one('hr.department','Department')
	location = fields.Many2one('res.company','Location')
	kra      = fields.Many2one('kra.master','KRA')
	kra_one2many = fields.One2many('kra.rating','kra_id','KRA')
	quarterly_meeting_one2many = fields.One2many('quarterly.meeting','quarterly_meeting_id','KRA')
	state = fields.Selection([('draft','Pending'),('done','Approved'),('cancel','Rejected')
								], string="State", default='draft')
	sr_no = fields.Char('Sr. No.')

	check1 = fields.Boolean(string="check field", compute='get_user')
	active = fields.Boolean('Active')
	review_start_date = fields.Date("Review Start Date")
	review_end_date = fields.Date("Review End Date")
	pip_applicable = fields.Boolean('PIP Applicable?',default=False)
	access_token = fields.Char('Security Token', copy=False,default=_get_default_access_token)
	approved_date = fields.Date('Approved Date')
	application_date = fields.Date('Application Date')
	review_summary = fields.Text('Review Summary')
	button_check = fields.Boolean('button_check', compute='get_user')
	check_user = fields.Boolean('Check User')
	quarterly_kra_auth_id = fields.Many2one('quarterly.kra.review.auth','')
	select_record = fields.Boolean('Select')
	attachment = fields.Binary('Attach File',attachment=True)

	@api.multi
	def save_exit(self):
		self.write({'active':True})

	@api.model_cr_context
	def _init_column(self, column_name):
		""" Initialize the value of the given column for existing rows.

			Overridden here because we need to generate different access tokens
			and by default _init_column calls the default method once and applies
			it for every record.
		"""
		if column_name != 'access_token':
			super(KraMain, self)._init_column(column_name)
		else:
			query = """UPDATE %(table_name)s
						  SET %(column_name)s = md5(md5(random()::varchar || id::varchar) || clock_timestamp()::varchar)::uuid::varchar
						WHERE %(column_name)s IS NULL
					""" % {'table_name': self._table, 'column_name': column_name}
			self.env.cr.execute(query)

	def _generate_access_token(self):
		for invoice in self:
			invoice.access_token = self._get_default_access_token()

	def get_user(self):
		employee= self.employee.user_id.id
		res_user = self.env['res.users'].search([('id', '=', self._uid)])
		if res_user.has_group('hr.group_hr_manager') or res_user.has_group('hr.group_hr_user') or res_user.has_group('orient_hr_resignation.group_reporting_manager'):
			self.check1 = True
			print(employee, self._uid,'******')
			if employee == self._uid:
				print("11111111")
				self.button_check = True
			else:
				if self.employee.parent_id.user_id.id == self._uid:
					print("2222222222")
					self.button_check = False
				else:
					print("333333333333")
					self.button_check = True
		else:
			print("4444444444")
			self.check1 = False
		print(self.state, self.button_check,'--state and button_check-------------')	


	@api.onchange('kra_one2many')
	def onchange_kra_one2many(self):
		res = {}
		for line in self:
			for each in line.kra_one2many:
				each.final = each.man_rating + each.emp_rating
		return res

	@api.multi
	def submit_to_employee(self):
		total_weightage = 0.0
		for rec in self:
			for kpi in rec.kra_one2many:
				total_weightage += float(kpi.weightage)
			if float(total_weightage) != 100:
				raise ValidationError(_("Total Weightage cannot exceed 100"))
			rec.state = 'employee'
			template_id = self.env.ref('orient_pms.email_template_for_self_rating', False)
			self.env['mail.template'].browse(template_id.id).send_mail(rec.id, force_send=True)

	@api.multi
	def submit_to_manager(self):
		check = False
		for rec in self:
			# if not rec.attachment:
			# 	raise ValidationError(_("Kindly attach documents to justify your ratings!"))
			for kpi in rec.kra_one2many:
				# if kpi.emp_rating<=0:
				# 	raise ValidationError(_("Self Rating cannot be 0"))
				if kpi.emp_rating >kpi.weightage:
					raise ValidationError(_("Self Rating cannot be greater than the weightage"))
				if kpi.comments=='':
					raise ValidationError(_("Kindly give your comments/justification"))
				kpi.write({'state':'draft','self_check':True})
			for kpi in rec.kra_one2many:
				if kpi.emp_rating>0:
					check = True
					break
			if check == False:
				raise ValidationError(_("Self Rating cannot be 0 for all KRA's"))
			rec.state = 'draft'
			rec.active = True
			template_id = self.env.ref('orient_pms.email_template_self_rating_done', False)
			self.env['mail.template'].browse(template_id.id).send_mail(rec.id, force_send=True)
			self.ensure_one()
			kra_form = self.env.ref('orient_pms.view_kramain_form', False)
			return {
				'name': _('KRA/KPI Mapping'),
				'type': 'ir.actions.act_window',
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'kra.main',
				'res_id': self.id,
				'views': [(kra_form.id, 'form')],
				'view_id': self.id,
				'target': 'current',
			}

	@api.multi
	def approve(self):
		res_user = self.env['res.users'].search([('id', '=', self._uid)])
		if self.employee.user_id.id==res_user.id:
			raise ValidationError(_("Access Denied to approve your own KRA record!"))
		total_emp=0
		total_man=0
		scale=0.0
		pip_applicable = False
		check = False
		pip_obj = self.env['pip.list']
		for rec in self:
			for kpi in rec.kra_one2many:
				if kpi.man_rating >kpi.weightage:
					raise ValidationError(_("TL's Rating cannot be greater than the weightage"))
				if kpi.comments=='':
					raise ValidationError(_("Kindly give your comments/justification"))
				if kpi.man_rating>0.0:
					check = True
				print (kpi.man_rating,'lllllllll')
				total_emp+=kpi.emp_rating
				total_man+=float(kpi.man_rating)
				kpi.write({'state':'done'})
		for rec in self:
			for kpi in rec.kra_one2many:
				if kpi.man_rating>0:
					check = True
					break
			if check == False:
				raise ValidationError(_("TL's Rating cannot be 0 for all KRA's"))
			rating = float(total_man)
			print (type(rating),rating,'rating',total_man)
			scale_new= self.env['appraisal.scale'].search([('minimum','<=',float(rating)),('maximum','>=',float(rating))])
			print (scale_new.scale)
			self.final_rating=float(scale_new.scale)
			self.pip_applicable=scale_new.pip_applicable
			if scale_new.scale <= 2.0:
				create_id = pip_obj.create({
										'employee':rec.employee.id,
										'designation':rec.designation.id,
										'quarter':rec.quarter,
										'kra_year':rec.kra_year.id,
										'ratings':scale_new.scale,
										'month':rec.kra_month,
										})
				template_id = self.env.ref('orient_pms.email_template_pip_selection', False)
				self.env['mail.template'].browse(template_id.id).send_mail(rec.id, force_send=True)
			rec.pip_applicable = scale_new.pip_applicable
			rec.final_rating = scale_new.scale
			rec.state = 'done'
			rec.approved_date = str(datetime.now().date())
			template_id = self.env.ref('orient_pms.email_template_manager_rating_done', False)
			self.write({'select_record':False})
			self.env['mail.template'].browse(template_id.id).send_mail(rec.id, force_send=True)

	@api.multi
	def cancel(self):
		res_user = self.env['res.users'].search([('id', '=', self._uid)])
		if self.employee.user_id.id==res_user.id:
			raise ValidationError(_("Access Denied to reject your own Quarterly Review record!"))
		for rec in self:
			for kpi in rec.kra_one2many:
				kpi.write({'state':'cancel'})
		self.write({'state':'cancel'})

	@api.multi
	def set_to_draft(self):
		for rec in self:
			for kpi in rec.kra_one2many:
				kpi.write({'state':'draft'})
		self.write({'state':'draft'})

	@api.multi
	def open_review_form(self):
		self.ensure_one()
		kra_form = self.env.ref('orient_pms.view_kramain_form', False)
		return {
			'name': _('KRA/KPI Mapping'),
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'kra.main',
			'res_id': self.id,
			'views': [(kra_form.id, 'form')],
			'view_id': self.id,
			'target': 'new',
		}

	@api.multi
	def generate_xls_report(self,access_uid=None):
		self.ensure_one()
		return {
		'type': 'ir.actions.act_url',
		'url': '/web/pivot/export_xls/%s?access_token=%s' % (self.id, self.access_token),
		'target': 'new',
		}

class YearMaster(models.Model):
	_name = "year.master"

	name=fields.Char('Year')
	start_date = fields.Date('Start Date')
	end_date = fields.Date('End Date')
	active = fields.Boolean('Active', default=True)

class Employee(models.Model):
	_inherit = "hr.employee"

	kra_ids = fields.Many2many('kra.master', 'kra_employee_rel', 'kra_id', 'employee_kra_id', string='KRA Applicable', copy=False)
	job_id = fields.Many2one('hr.job', 'Job Position')
	kra_one2many = fields.One2many('employee.kra.kpi','emp_kra_id','KRA')
	emp_code = fields.Integer('Employee Code')
	hr_executive_id = fields.Many2one('hr.employee','HR Executive')
	appraisal_cycle = fields.Selection([('January','January'),('July','July')],string="Appraisal Cycle")
	can_edit_name = fields.Boolean(compute='_compute_can_edit_name',default=False)

	def _compute_can_edit_name(self):
		for each in self:
			res_user = self.env['res.users'].search([('id', '=', each._uid)])
			if res_user.id!=1:
				if res_user.has_group('base.group_user') and not res_user.has_group('hr.group_hr_user') and not res_user.has_group('hr.group_hr_manager'):
					each.can_edit_name = True
				else:
					each.can_edit_name = False

	@api.model
	def create(self,vals):
		model = self._context.get('params')
		model_id = model.get('model')
		emp_id = super(Employee, self).create(vals)
		total_kra_weightage = 0
		name = ''
		# if vals.get('pan'):
		# 	pan_no = vals.get('pan')
		# 	print (pan_no,'ppppppp')
		# 	if len(pan_no)==10 and pan_no[0:5].isalpha() and pan_no[5:9].isdigit() and pan_no[9].isalpha():
		# 		pass
		# 	else:
		# 		raise ValidationError(_("Kindly Enter proper PAN No"))
		# 	# search_pan = self.env['hr.employee'].search([('pan','=',pan)])
		# 	self.env.cr.execute("SELECT id from hr_employee where pan=%s" % str(pan_no))
		# 	result = self.env.cr.fetchone()
		# 	if result !=[]:
		# 		raise ValidationError(_("PAN No already exists, Kindly enter proper PAN NO!!"))
		if emp_id:
			job_id = emp_id.job_id.id
			job_name=self.env['hr.job'].browse(job_id).name
			if job_id:
				self.env.cr.execute('SELECT kra_designation_id from kra_designation_rel where designation_kra_id= %s' % job_id)
				result = self.env.cr.fetchall()
				des_result = []
				# if result == []:
				# 	raise ValidationError(_("Kindly MAP KRA's to Postion '%s' with weightage 100!!")%(job_name))
				for rec in result:
					des_result.append(rec[0])
					for x in self.env['kra.master'].browse(rec[0]):
						total_kra_weightage+=float(x.weightage)
						if x.kpi_one2many:
							count = 1
							for m in x.kpi_one2many:
								if count>1:
									name=''
								else:
									name=x.name
								emp_id.update({'kra_one2many':[(0, 0, {'kra_master_id':x.id,'name':name,'kpi':m.name.name,'weightage':m.weightage})]})
								count+=1
				# if int(total_kra_weightage) != 100:
				# 	raise ValidationError(_("Total Weightage of KRA's assigned to Postion '%s' should be 100!!")%(job_name))	
			self.env.cr.execute('select max(emp_code) from hr_employee where emp_code not in (90001,90002,90003,90004,90005,90006,90007,90008,90009,90010,90011,90012,90013,90014) and emp_code < 90000')
			emp_code = self.env.cr.fetchone()[0]
			if emp_code == 0 or emp_code == None:
				emp_id.update({'emp_code':1})
			elif emp_code > 0:
				emp_code = emp_code + 1
				emp_id.update({'emp_code':emp_code})
				department_id = emp_id.department_id.id
				hr_id = self.env['hr.department'].browse(department_id)
				emp_id.update({'hr_executive_id':hr_id.hr_executive_id.id})
			# creating user from employee-----------------------------------------------------------------------------------------------------------
			search_shift = self.env['hr.employee.shift.timing'].search([('name','=','G')],limit=1)
			if search_shift:
				emp_id.update({'shift_id':search_shift.id})
			search_nationality = self.env['res.country'].search([('name','=','India')],limit=1)
			if search_nationality:
				emp_id.update({'country_id':search_nationality.id})
			if emp_id and emp_code and vals.get('site_master_id') and vals.get('department_id') and vals.get('joining_date') and search_shift:
				site_master_id = vals.get('site_master_id')
				department_id = vals.get('department_id')
				parent_id = vals.get('parent_id')
				join_date = vals.get('joining_date')
				self.env['hr.attendance'].oncreate_employee_att(emp_id,emp_code,site_master_id,department_id,join_date,search_shift.id)
			users_obj = self.env['res.users']
			partner_obj = self.env['res.partner']
			password = "'$pbkdf2-sha512$25000$Pef8P6f0XsuZ0/q/934PgQ$0uiemDsPZyf/ENm7zFZkx4kP90YX9nvxgTRfgy4Dpj6p1eQ4bFmiPHZaNPo7mU6scwt851CeDolg5JUWwnc1uA'"
			login = "'"+str(emp_code)+"'"
			existing_user_with_code = users_obj.search([('login','=',emp_code)])
			# existing_user_with_email = users_obj.search(['|',('email','=',emp_id.work_email),('email','=',emp_id.personal_email)])
			if existing_user_with_code:
				# if emp_id.work_email:
				# 	e_mail = emp_id.work_email.lower()
				# else:
				# 	e_mail = emp_id.personal_email.lower()
				# write_vals = {
				# 		'email':e_mail,
				# }
				# self.write(write_vals)
				self.env.cr.execute("update hr_employee set user_id=%s where emp_code=%s" %(str(existing_user_with_code.id),str(emp_code)))
			# elif existing_user_with_email:
				# write_vals = {
				# 		'login':emp_code,
				# }
				# self.write(write_vals)
				# self.env.cr.execute("update hr_employee set user_id=%s where emp_code=%s" %(str(existing_user_with_email.id),str(emp_code)))
			else:
				if vals.get('work_email'):
					e_mail = vals.get('work_email').lower()
				else:
					e_mail = vals.get('personal_email').lower()
				user_vals = {
								'active':True,
								'name':vals.get('name'),
								'login':emp_code,
								'email':e_mail,
								'company_id':1,
								'share':False,
								'notification_type':'email',
								'emp_code':emp_code,
								'groups_id': [(6, 0, [self.env.ref('base.group_user').id, self.env.ref('hr_attendance.group_hr_attendance').id])]
							}
				partner_id = partner_obj.search([('name','=',vals.get('name'))])
				if partner_id:
					fin_partner_id = False
					if len(partner_id) > 1:
						partner_id = partner_obj.search([('name','=',emp_id.name),'|',('email','=',emp_id.personal_email),('email','=',emp_id.work_email)])
						if len(partner_id) == 1:
							fin_partner_id = partner_id.id
						elif len(partner_id) == 1:
							fin_partner_id = partner_id.id
						if fin_partner_id:
							user_vals.update({'partner_id':fin_partner_id})
				usr = users_obj.create(user_vals)
				self.env.cr.execute("update res_users set password_crypt=%s where login=%s" %(str(password),str(login)))
				self.env.cr.execute("update hr_employee set user_id=%s where emp_code=%s" %(str(usr.id),str(login)))
			#-----------------------------------------------------------------------------------------------------------------------------------------------
			# print(type(emp_id.name),type(emp_id.emp_code),emp_id.company_id.id,type(emp_id.personal_email))
			# if model_id != 'hr.applicant':
			# 	self.env.cr.execute('INSERT into res_partner(name,display_name,lang,company_id,active,customer,type,is_company,email) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)',(str(emp_id.name),emp_id.emp_code,'en_US',emp_id.company_id.id,True,True,'contact',False,emp_id.personal_email))
			# 	self.env.cr.commit()
			# 	self.env.cr.execute('SELECT id from res_partner where display_name = %s',(str(emp_id.emp_code),))
			# 	parent_rec = self.env.cr.fetchone()[0]
			# 	print(parent_rec,'parent_rec-------------')

			# 	self.env.cr.execute('INSERT into res_users(active,login,company_id,partner_id,password_crypt,notification_type,emp_code) values(%s,%s,%s,%s,%s,%s,%s)',('t',emp_id.emp_code,emp_id.company_id.id,parent_rec,'$pbkdf2-sha512$25000$Pef8P6f0XsuZ0/q/934PgQ$0uiemDsPZyf/ENm7zFZkx4kP90YX9nvxgTRfgy4Dpj6p1eQ4bFmiPHZaNPo7mU6scwt851CeDolg5JUWwnc1uA','email',emp_id.emp_code))
			# 	self.env.cr.commit()

			# 	self.env.cr.execute('SELECT id from res_users where login = %s',(str(emp_id.emp_code),))
			# 	user_rec = self.env.cr.fetchone()[0]
			# 	print(user_rec,'user_rec*****************')

			# 	self.env.cr.execute('SELECT id from resource_resource where name =%s order by id desc limit 1', (str(emp_id.name),))
			# 	resource_rec = self.env.cr.fetchone()[0]
			# 	print(resource_rec,'resource_rec*****************')

			# 	self.env.cr.execute('UPDATE resource_resource set user_id = %s where id=%s',(user_rec,resource_rec))
			# 	self.env.cr.commit()

			# 	self.env.cr.execute("SELECT id from res_groups where name = 'Employee'")
			# 	group_rec = self.env.cr.fetchone()[0]
			# 	print(group_rec,'group_rec*****************')

			# 	self.env.cr.execute('INSERT into res_groups_users_rel(gid,uid) values(%s,%s)', (group_rec,user_rec))	
			# 	self.env.cr.commit()
		return emp_id


	@api.multi
	def write(self, vals):
		if vals.get('department_id'):
			department_id = vals.get('department_id')
			print(department_id)
			hr_id = self.env['hr.department'].browse(department_id)
			print(hr_id,'-------')
			self.hr_executive_id = hr_id.hr_executive_id.id
		if vals.get('kra_one2many'):
			kra_list = vals.get('kra_one2many')
			kra_dict = {}
			total_weightage_list = []
			unchanged_kra_list = []
			for x in kra_list:
				if x[2] is False:
					unchanged_kra_list.append(x[1])
				if type(x[2]) is dict:
					kra_dict['id'] = x[1]
					if 'name' in  x[2]:
						kra_dict['name'] = x[2]['name']
					if 'kpi' in x[2]:
						kra_dict['kpi'] = x[2]['kpi']
					if 'weightage' in x[2]:
						kra_dict['weightage'] = x[2]['weightage']
						total_weightage_list.append(float(x[2]['weightage']))
					if 'weightage' not in x[2]:
						for rec in self.env['employee.kra.kpi'].browse(kra_dict['id']):
							total_weightage_list.append(rec.weightage)
			if unchanged_kra_list:
				for p in self.env['employee.kra.kpi'].browse(unchanged_kra_list):
					total_weightage_list.append(p.weightage)
				total_weightage = sum(total_weightage_list)
				print (total_weightage,'total_weightage')
				if round(total_weightage,2)!=100.0:
					raise ValidationError(_("Total Weightage should be 100.0!!"))
		# if vals.get('pan'):
		# 	pan = vals.get('pan')
		# 	if len(pan)==10 and pan[0:5].isalpha() and pan[5:9].isdigit() and pan[9].isalpha():
		# 		pass
		# 	else:
		# 		raise ValidationError(_("Kindly Enter proper PAN No"))
		# 	search_pan = self.env['hr.employee'].search([('pan','=',str(pan))])
		# 	if search_pan:
		# 		raise ValidationError(_("PAN No already exists, Kindly enter proper PAN NO!!"))
		# if 'image' in vals:
		# 	image = ustr(vals['image'] or '').encode('utf-8')
		# 	user_id = self.user_id
		# 	user_id.write({'image':image})
		if vals.get('job_id'):
			self.write({'kra_one2many':[(6, 0, None)]})
			job_id = vals.get('job_id')
			job_name=self.env['hr.job'].browse(job_id).name
			self.env.cr.execute('SELECT kra_designation_id from kra_designation_rel where designation_kra_id= %s' % job_id)
			result = self.env.cr.fetchall()
			des_result = []
			total_kra_weightage=0
			# if result == []:
			# 	raise ValidationError(_("Kindly MAP KRA's to Postion '%s' with weightage 100!!")%(job_name))
			if result!=[]:
				for rec in result:
					des_result.append(rec[0])
					for x in self.env['kra.master'].browse(rec[0]):
						total_kra_weightage+=float(x.weightage)
						if x.kpi_one2many:
							count = 1
							for m in x.kpi_one2many:
								if count>1:
									name=''
								else:
									name=x.name
								self.write({'kra_one2many':[(0, 0, {'kra_master_id':x.id,'name':name,'kpi':m.name.name,'weightage':m.weightage})]})
								count+=1						
				# if int(total_kra_weightage) != 100:
				# 	raise ValidationError(_("Total Weightage of KRA's assigned to Postion '%s' should be 100!!")%(job_name))
			else:
				self.write({'kra_one2many':[(6, 0, None)]})
		return super(Employee, self).write(vals)

	def quarterly_kra_mail_reminder(self):
		"""Sending reminder mail for employee for Quarterly Reminder Email"""
		quarters_list = ["April","July","October","January"]
		check_date = "05"
		current_date = current_month = current_year = ''
		current_date =  datetime.now().date()
		current_month = datetime.strptime(str(current_date), "%Y-%m-%d").strftime('%B')
		current_year = datetime.strptime(str(current_date), "%Y-%m-%d").strftime('%Y')
		current_day = datetime.strptime(str(current_date), "%Y-%m-%d").strftime('%d')
		if str(check_date) == str(current_day) and str(current_month) in quarters_list:
			template_id = self.env.ref('orient_pms.email_template_for_quarterly_kra_reminder', False)
			hr_position = self.env['hr.job'].search([('hr_manager_bool', '=', True)], limit=1)
			rec = self.env['hr.employee'].search([('job_id', '=',hr_position.id)], limit=1)
			self.env['mail.template'].browse(template_id.id).send_mail(rec.id, force_send=True)


	def quarterly_kra_mail_reminder_managers(self):
		"""Sending reminder mail to managers for Quarterly Reminder Ratings Email"""
		quarters_list = ["April","July","October","January"]
		check_date = "15"
		current_date = current_month = current_year = ''
		current_date =  datetime.now().date()
		current_month = datetime.strptime(str(current_date), "%Y-%m-%d").strftime('%B')
		current_year = datetime.strptime(str(current_date), "%Y-%m-%d").strftime('%Y')
		current_day = datetime.strptime(str(current_date), "%Y-%m-%d").strftime('%d')
		self.env.cr.execute('SELECT distinct(parent_id) from hr_employee where parent_id is not null')
		employee = self.env.cr.fetchall()
		emps = list(set(employee))
		print(emps)
		for man_id in emps:
			man = self.env['hr.employee'].browse(man_id[0])
			rec = man[0]
			if str(check_date) == str(current_day) and str(current_month) in quarters_list:
				template_id = self.env.ref('orient_pms.email_template_for_quarterly_kra_reminder_manager', False)
				print(rec.id,rec.work_email)
				self.env['mail.template'].browse(template_id.id).send_mail(rec.id, force_send=True)

	def cron_annual_review(self):
		annual_kra_obj = self.env['annual.kra']
		kra_master_obj = self.env['kra.master']
		emp_obj = self.env['hr.employee']
		kra_rating_obj = self.env['kra.rating']
		kpi_master_obj = self.env['kpi.master']
		emp_kra_kpi = self.env['employee.kra.kpi']
		goalsheet_obj = self.env['annual.goalsheet']
		behaviour_obj = self.env['annual.behaviour']
		annual_app_obj = self.env['annual.appraisal']
		review_cycle = ['January','July']
		quarter1='April'
		quarter2='July'
		quarter3='October'
		quarter4='January'
		get_year = get_current_financial_year(self)
		split_year = get_year.split('-')
		year1 = str(split_year[0])
		year2 = str(split_year[1])
		print (year1,year2)
		current_date =  datetime.now().date()
		current_date = '2019-01-01'
		if str(current_date) == year1+'-07-01' or str(current_date) == year2+'-01-01':
			current_month = datetime.strptime(str(current_date), "%Y-%m-%d").strftime('%B')
			print (current_month,'mmmmmm')
			emp_obj=self.env['hr.employee']
			kra_obj=self.env['kra.main']
			if current_month in review_cycle:
				rec = emp_obj.search([('appraisal_cycle', '=',str(current_month))])
				print (rec)
				count1=1
				for emp in rec:				
					joining_date = emp.joining_date
					date_dt= datetime.strptime(joining_date, "%Y-%m-%d").date()
					current_date= datetime.strptime(str(current_date), "%Y-%m-%d").date()
					tenure = relativedelta(current_date, date_dt)
					if tenure.years >= 1:
						if current_month in ('July','January'):	
								template_id = self.env.ref('orient_pms.email_template_for_annual_review_reminder', False)
								self.env['mail.template'].browse(template_id.id).send_mail(emp.id, force_send=True)
		return True


class EmployeeKraKpi(models.Model):
	_name = "employee.kra.kpi"

	employee_code = fields.Char('Employee Code')
	emp_kra_id = fields.Many2one('hr.employee', 'Employee KRA')
	name = fields.Char('KRA')
	kpi = fields.Char('KPI')
	weightage = fields.Float('Weightage')
	kra_master_id = fields.Many2one('kra.master','KRA ID')
	emp_kpi_one2many = fields.One2many('employee.kpi','emp_kpi_id','KPI')
	check1 = fields.Boolean(string="check field", compute='get_user')
	check2 = fields.Boolean(string="check fields", compute='get_user')
	imported1 = fields.Boolean('Imported')

	def get_user(self):
		for each in self:
			employee = each.emp_kra_id.user_id.id
			res_user = self.env['res.users'].search([('id', '=', each._uid)])
			if res_user.has_group('hr.group_hr_manager') or res_user.has_group('hr.group_hr_user') or res_user.has_group('orient_hr_resignation.group_reporting_manager'):
				if employee == res_user.id:
					each.check1 = False
					each.check2 = True
				else:
					if each.emp_kra_id.parent_id.user_id.id == res_user.id:
						each.check1 = True
						each.check2 = False
					else:
						each.check1 = True
						each.check2 = False
			else:
				each.check1 = False
				each.check2 = True


	@api.model
	def create(self,vals):
		total_weightage=0.0
		kra_id =super(EmployeeKraKpi, self).create(vals)
		if vals.get('employee_code'):
			search_emp = self.env['hr.employee'].search([('emp_code','=',vals['employee_code'])])
			if search_emp:
				vals.update({'emp_kra_id':search_emp.id})
				if vals['employee_code'] and vals['kpi'] and vals['weightage'] and search_emp.id:
					vals.update({'emp_kra_id':search_emp.id,'imported1':True})
					kra_id.update(vals)
		if vals.get('employee_code'):
			search_emp = self.env['hr.employee'].search([('emp_code','=',vals['employee_code'])])
			if search_emp:
				if search_emp.kra_one2many:
					for m in search_emp.kra_one2many:
						if m.imported1!=True:
							m.unlink()
		if kra_id:
			kpi_id = kra_id.emp_kpi_one2many
			if kpi_id:
				for kpis in kpi_id:
					total_weightage += float(kpis.kpi_weightage)
					if kpis.kpi_weightage==0:
						raise ValidationError(_("Weightage of KPI cannot be 0!!"))
					if kpis.kpi_weightage<0:
						raise ValidationError(_("Weightage of KPI cannot be less than 0!!"))
				if float(total_weightage)!=float(kra_id.weightage):
					raise ValidationError(_("Total Weightage of KPI's does not match with KRA Weightage!!"))			
		self.env.cr.execute("update employee_kra_kpi set imported1 = null")
		return kra_id	

	@api.multi
	def write(self, vals):
		total_weightage=0.0
		kra_id=super(EmployeeKraKpi, self).write(vals)
		if vals.get('emp_kpi_one2many'):
			kpi_id = self.emp_kpi_one2many
			if kpi_id:
				for kpis in kpi_id:
					total_weightage += float(kpis.kpi_weightage)
					if kpis.kpi_weightage==0:
						raise ValidationError(_("Weightage of KPI cannot be 0!!"))
					if kpis.kpi_weightage<0:
						raise ValidationError(_("Weightage of KPI cannot be less than 0!!"))
				if float(total_weightage)!=float(self.weightage):
					raise ValidationError(_("Total Weightage of KPI's does not match with KRA Weightage!!"))
			else:
				raise ValidationError(_("Kindly Map KPI's to KRA!!"))
		return kra_id


	@api.multi
	def open_kpi(self):
		self.ensure_one()
		kra_form = self.env.ref('orient_pms.view_emp_kra_kpi_form', False)
		ctx = dict(default_name=self.name,default_weightage=self.weightage)
		kpi_master_obj = self.env['kpi.master']
		if not self.emp_kpi_one2many:
			for record in self.kra_master_id.kpi_one2many:
				self.env['employee.kpi'].create({
					'emp_kpi_id':self.id,
					'kpi_name':record.name.name,
					'description':record.description,
					'kpi_weightage':record.weightage
					})
		return {
			'name': _('KRA/KPI Mapping'),
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'employee.kra.kpi',
			'res_id': self.id,
			'views': [(kra_form.id, 'form')],
			'view_id': kra_form.id,
			'target': 'new',
			'context': ctx,
		}


class Job(models.Model):

	_inherit = "hr.job"
	
	job_kra_one2many = fields.One2many('kra.job','job_kra_id','KRA')

	@api.model
	def create(self, vals):
		job = super(Job, self).create(vals)
		print(job)

		designation = []
		des_list = []

		if job:
			for s in job.job_kra_one2many:
				print(s,'sssssssssssssss')
				kra_master = s.kra_master.id
				designation = s.kra_master.designation
				des_list.append([kra_master,designation])
			for x,y in des_list:
				print(x,y,'x and y vals')
				self.env.cr.execute('INSERT into kra_designation_rel(kra_designation_id,designation_kra_id) values(%s,%s)' % (x,job.id))
				self.env.cr.commit()
		return job

	@api.multi
	def write(self, vals):
		job = super(Job, self).write(vals)
		job_id = self.id
		print(job_id,'main id')
		des=[]
		kra_des = {}
		designation = []
		des_list = []
		for s in self.job_kra_one2many:
			if s.kra_master:
				kra_master = s.kra_master.id
				designation = s.kra_master.designation
				des_list.append([kra_master,designation])
		print(des_list,'------------')
		for x,y in des_list:
			if y:
				self.env.cr.execute('SELECT designation_kra_id from kra_designation_rel where kra_designation_id= %s and designation_kra_id=%s' % (x,job_id))
				result = self.env.cr.fetchall()
				if result==[]:
					self.env.cr.execute('INSERT into kra_designation_rel(kra_designation_id,designation_kra_id) values(%s,%s)' % (x,job_id))
					self.env.cr.commit()					
			else:
				self.env.cr.execute('INSERT into kra_designation_rel(kra_designation_id,designation_kra_id) values(%s,%s)' % (x,job_id))
				self.env.cr.commit()
		return job


class KraJob(models.Model):

	_name = "kra.job"

	job_kra_id = fields.Many2one('hr.job','Job KRA')
	kra_master = fields.Many2one('kra.master','KRA')
	kra_name = fields.Char('KRA')
	kpi = fields.Char('KPI')
	weightage = fields.Float('Weightage')

class QuarterlyMeeting(models.Model):

	_name = "quarterly.meeting"

	quarterly_meeting_id = fields.Many2one('kra.main','Meeting')
	sr_no = fields.Char('Sr. No.')
	agenda_item = fields.Char('Agenda Item')
	outcomes = fields.Char('Outcomes')
	action_taken = fields.Char('Action To be Taken')
	deadline_date = fields.Date('Deadline Date')
	check1 = fields.Boolean(string="check field", compute='get_user')

	def get_user(self):
		for each in self:
			res_user = self.env['res.users'].search([('id', '=', each._uid)])
			if res_user.has_group('hr.group_hr_manager') or res_user.has_group('hr.group_hr_user') or res_user.has_group('orient_hr_resignation.group_reporting_manager'):
				each.check1 = True
			else:
				each.check1 = False

class PipList(models.Model):

	_name = 'pip.list'
	_rec_name = 'employee'

	employee = fields.Many2one('hr.employee','Employee')
	designation = fields.Many2one('hr.job','Designation')
	ratings = fields.Float('Rating')
	quarter = fields.Selection([('First','First Quarter'),('Second','Second Quarter'),('Third','Third Quarter'),('Fourth','Fourth Quarter')],string='Quarter')
	month = fields.Selection([('January', 'January'),('February', 'February'),
								('March', 'March'),('April', 'April'),
								('May', 'May'),('June','June'),
								('July','July'),('August','August'),
								('September','September'),('October','October'),
								('November','November'),('December','December')
								],string='Month')
	kra_year = fields.Many2one('year.master','Year')
	plan_of_action = fields.Text('Plan Of Action')

class QrStatusReport(models.Model):

	_name = 'qr.status.report'

	def _get_default_access_token(self):
		return str(uuid.uuid4())

	employee = fields.Many2one('hr.employee','Employee')
	designation = fields.Many2one('hr.job','Designation')
	ratings = fields.Float('Rating')
	quarter = fields.Selection([('Q1','Q1'),('Q2','Q2'),('Q3','Q3'),('Q4','Q4')],string='Quarter')
	month = fields.Selection([('January', 'January'),('February', 'February'),
								('March', 'March'),('April', 'April'),
								('May', 'May'),('June','June'),
								('July','July'),('August','August'),
								('September','September'),('October','October'),
								('November','November'),('December','December')
								],string='Month')
	kra_year = fields.Many2one('year.master','Year')
	status = fields.Selection([('Active','Active'),('Inactive','Inactive')],default='Active',string='Status')
	qr_status_report_lines = fields.One2many('qr.status.report.lines','qr_status_report_lines_id','Quarterly Status Report')
	access_token = fields.Char('Security Token', copy=False,default=_get_default_access_token)
	applications_done = fields.Integer('Applications Done')
	applications_not_done = fields.Integer('Applications Not Done')
	total_applications = fields.Integer('Total Applications')
	duration_string = fields.Char('Duration String')


	@api.model_cr_context
	def _init_column(self, column_name):
		""" Initialize the value of the given column for existing rows.

			Overridden here because we need to generate different access tokens
			and by default _init_column calls the default method once and applies
			it for every record.
		"""
		if column_name != 'access_token':
			super(QrStatusReport, self)._init_column(column_name)
		else:
			query = """UPDATE %(table_name)s
						  SET %(column_name)s = md5(md5(random()::varchar || id::varchar) || clock_timestamp()::varchar)::uuid::varchar
						WHERE %(column_name)s IS NULL
					""" % {'table_name': self._table, 'column_name': column_name}
			self.env.cr.execute(query)

	def _generate_access_token(self):
		for invoice in self:
			invoice.access_token = self._get_default_access_token()

	@api.model
	def default_get(self, fields):
		rec = super(QrStatusReport, self).default_get(fields)
		context = dict(self._context or {})
		active_id = context.get('active_id', False)
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
			rec['kra_year']=search_year[0].id
		if current_month:
			for k,y in month_sel:
				if y == current_month:
					if current_month in ('April','May','June'):
						rec['quarter'] = 'Q1'
						rec['duration_string'] = 'April - ' + str(start_year) + ' to June - ' + str(start_year)
					if current_month in ('July','August','September'):
						rec['quarter'] = 'Q2'
						rec['duration_string'] = 'July - ' + str(start_year) + ' to September - ' + str(start_year)
					if current_month in ('October','November','December'):
						rec['quarter'] = 'Q3'
						rec['duration_string'] = 'October - ' + str(start_year) + ' to December - ' + str(start_year)
					if current_month in ('January','February','March'):
						rec['quarter'] = 'Q4'
						rec['duration_string'] = 'January - ' + str(end_year) + ' to March - ' + str(end_year)

		return rec

	@api.multi
	def generate_qr_status_report(self,access_uid=None):
		self.ensure_one()
		emp_obj = self.env['hr.employee']		
		qr_status_report_obj = self.env['qr.status.report.lines']
		kra_main_obj = self.env['kra.main']
		quarter = ''
		application_date = ''
		approved_date = ''
		review_status = 'Not Done'
		average_rating = ''
		review_summary = ''
		eligible_for_pip = False
		if self.qr_status_report_lines:
			for line in self.qr_status_report_lines:
				line.unlink()
		if not self.kra_year:
			raise ValidationError(_("Kindly select Year!"))
		if not self.quarter:
			raise ValidationError(_("Kindly select Quarter!"))
		if not self.status:
			raise ValidationError(_("Kindly select Status!"))
		if self.quarter == 'Q1':
			quarter = 'First'
		if self.quarter == 'Q2':
			quarter = 'Second'
		if self.quarter == 'Q3':
			quarter = 'Third'
		if self.quarter == 'Q4':
			quarter = 'Fourth'
		status = self.status
		active=False
		if status == 'Active':
			active=True
		rm_list = []
		search_emp = []
		applications_done = []
		total_applications = []
		search = emp_obj.search([('active','=', active)])
		# self.write({'total_applications':len(search)})
		for x in search:
			if x.cost_center_id.name!='ITES - FMS/PS' and x.department_id.name not in ('FM','FM Backup'):
				total_applications.append(x.id)
			if x.parent_id.id!=False:
				if x.parent_id.id not in rm_list:
					rm_list.append(x.parent_id.id)
		sr_no = 1
		for rm in rm_list:
			search_emp = emp_obj.search([('parent_id','=',rm)])
			rm_rec = emp_obj.browse(rm)
			for emp_rec in emp_obj.browse(search_emp):
				if emp_rec.id.cost_center_id.name!='ITES - FMS/PS' and emp_rec.id.department_id.name not in ('FM','FM Backup'):
					search_kra = kra_main_obj.search([('employee','=',emp_rec.id.id),('kra_year','=',self.kra_year.id),('quarter','=',quarter)])
					search_lines = self.env['qr.status.report.lines'].search([('sr_no','=',sr_no),('qr_status_report_lines_id','=',self.id)])
					if search_kra:
						for m in search_kra:
							applications_done.append(m.id)
					if search_kra:
						for x in search_kra:
							application_date = x.application_date
							approved_date = x.approved_date
							review_status = x.state
							if review_status in ('reportee','draft','employee'):
								review_status = 'Pending'
							if review_status == 'done':
								review_status = 'Done'
							if review_status == 'cancel':
								review_status = 'Rejected'
							review_summary = x.review_summary
							if review_status == 'Done':
								average_rating = x.final_rating
								if x.pip_applicable:
									eligible_for_pip = 'Yes'
								else:
									eligible_for_pip = 'No'
							else:
								average_rating = ''
								eligible_for_pip = ''
							emp_qr = qr_status_report_obj.create({
									'sr_no':sr_no,
									'qr_status_report_lines_id':self.id,
									'reporting_code':emp_rec.id.parent_id.emp_code,
									'reporting_name':emp_rec.id.parent_id.name,
									'hr_code':emp_rec.id.hr_executive_id.emp_code,
									'hr_name':emp_rec.id.hr_executive_id.name,
									'employee':emp_rec.id.id,
									'employee_name':emp_rec.id.name,
									'employee_code':emp_rec.id.emp_code,
									'designation':emp_rec.id.job_id.id,
									'department':emp_rec.id.department_id.id,
									'application_date':application_date,
									'approved_date':approved_date,
									'review_status':review_status,
									'average_rating':average_rating,
									'review_summary':review_summary,
									'eligible_for_pip':eligible_for_pip,
									'employee_status':'Active' if active else 'Inactive',					
									})
					else:
						emp_qr = qr_status_report_obj.create({
								'sr_no':sr_no,
								'qr_status_report_lines_id':self.id,
								'reporting_code':emp_rec.id.parent_id.emp_code,
								'reporting_name':emp_rec.id.parent_id.name,
								'hr_code':emp_rec.id.hr_executive_id.emp_code,
								'hr_name':emp_rec.id.hr_executive_id.name,
								'employee':emp_rec.id.id,
								'employee_name':emp_rec.id.name,
								'employee_code':emp_rec.id.emp_code,
								'designation':emp_rec.id.job_id.id,
								'department':emp_rec.id.department_id.id,
								'application_date':'',
								'approved_date':'',
								'review_status':'Not Done',
								'average_rating':'',
								'review_summary':'',
								'eligible_for_pip':'',
								'employee_status':'Active' if active else 'Inactive',					
								})
			sr_no+=1
		count=1
		sr_no_list=[]
		for rec in range(0,len(rm_list)):
			search_lines = self.env['qr.status.report.lines'].search([('sr_no','=',count),('qr_status_report_lines_id','=',self.id)])
			for recs in search_lines:
				sr_no_list.append(recs.id)
			if (len(sr_no_list)>1):
				for recs1 in search_lines:
					if recs1.id!=sr_no_list[0]:
						recs1.write({'sr_no':False,'reporting_name':False,'reporting_code':False})
			count+=1
			sr_no_list = []
		self.write({'total_applications':len(total_applications),'applications_done':len(applications_done),'applications_not_done':len(total_applications)-len(applications_done)})
		return {
		'type': 'ir.actions.act_url',
		'url': '/web/pivot/export_qr_status_xls/%s?access_token=%s' % (self.id, self.access_token),
		'target': 'new',
		}


class QrStatusReportLines(models.Model):

	_name = 'qr.status.report.lines'

	sr_no = fields.Integer('Sr. No.')
	reporting_code = fields.Char('Reporting Code')
	reporting_name = fields.Char('Reporting Name')
	hr_code = fields.Char('HR Code')
	hr_name = fields.Char('HR Name')
	qr_status_report_lines_id = fields.Many2one('qr.status.report','Quarterly Review Report')
	employee = fields.Many2one('hr.employee','Employee')
	employee_name = fields.Char('Employee Name')
	department =  fields.Many2one('hr.department','Department')
	application_date = fields.Date("Application Date")
	approved_date = fields.Date("Approved Date")
	review_status = fields.Char("Review Status")
	average_rating = fields.Char("Average Rating")
	review_summary = fields.Char("Review Summary")
	eligible_for_pip = fields.Char('Eligible For PIP')
	employee_status =  fields.Char('Employee Status')
	designation = fields.Many2one('hr.job','Designation')
	employee_code = fields.Char('Employee Code')
	ratings = fields.Float('Rating')
	quarter = fields.Selection([('Q1','Q1'),('Q2','Q2'),('Q3','Q3'),('Q4','Q4')],string='Quarter')
	month = fields.Selection([('January', 'January'),('February', 'February'),
								('March', 'March'),('April', 'April'),
								('May', 'May'),('June','June'),
								('July','July'),('August','August'),
								('September','September'),('October','October'),
								('November','November'),('December','December')
								],string='Month')
	kra_year = fields.Many2one('year.master','Year')
	status = fields.Selection([('active','Active'),('inactive','Inactive')],default='active',string='Status')


class AppraisalScale(models.Model):

	_name = 'appraisal.scale'

	name = fields.Char('Name')
	minimum = fields.Float('Minimum')
	maximum = fields.Float('Maximum')
	scale = fields.Float('Scale')
	pip_applicable = fields.Boolean('PIP Applicable')
	active = fields.Boolean('Active', default=True)

class IncrementScale(models.Model):

	_name = 'increment.scale'

	minimum_weightage = fields.Float('Minimum Weightage')
	maximum_weightage = fields.Float('Maximum Weightage')
	minimum_increment = fields.Integer('Minimum Increment')
	maximum_increment = fields.Integer('Maximum Increment')
	active = fields.Boolean('Active', default=True)

class KraTemplates(models.Model):
	_name = 'kra.templates'

	name = fields.Selection([('Goalsheet','Goalsheet Form'),('Performance Appraisal','Performance Appraisal')],string='Template',default="Goalsheet")
	question_one2many = fields.One2many('kra.questions','question_id')
	behavioural_attributes_one2many = fields.One2many('behavioural.attributes','attributes_id')
	department = fields.Many2one('hr.department','Department')
	financial_year = fields.Many2one('year.master','Year')
	appraisal_cycle = fields.Selection([('January','January'),('July','July')],string="Appraisal Cycle")
	increment = fields.Boolean('Increment')
	recognition = fields.Boolean('Recognition')
	sec_emp = fields.Boolean('Secure Employment')
	creative_work = fields.Boolean('Creative and Challenging Work')
	designation_choice = fields.Boolean('Designation')
	role_exp = fields.Boolean('Role Expansion')
	promotion = fields.Boolean('Promotion')
	training = fields.Boolean('Training and Development')
	last_year = fields.Char('')
	current_year = fields.Char('')
	next_year = fields.Char('')
	designation_last = fields.Char('')
	designation_current = fields.Char('')
	designation_next = fields.Char('')
	salary_last = fields.Char('')
	salary_current = fields.Char('')
	salary_next = fields.Char('')	
	excellent = fields.Boolean('Excellent')
	good = fields.Boolean('Good')
	scope = fields.Boolean('No Scope')
	sub_department = fields.Many2one('sub.department','Sub Department')

class KraQuestions(models.Model):
	_name = 'kra.questions'

	question_id = fields.Many2one('kra.templates','Questions')
	questions = fields.Char('Questions')
	answer = fields.Char('Answer')

class BehaviouralAttributes(models.Model):
	_name = 'behavioural.attributes'

	attributes_id = fields.Many2one('kra.templates','Questions')
	attributes = fields.Char('Attributes')

class SubordinateKraView(models.Model):
	_name = 'subordinate.kra.view'

	name = fields.Many2one('hr.employee','Employee Name')
	emp_code = fields.Integer('Employee Code')
	hr_kra_one2many = fields.One2many('hr.employee','report_id','Subordinate')

	@api.model
	def default_get(self, fields):
		rec = super(SubordinateKraView, self).default_get(fields)
		context = dict(self._context or {})
		uid = context.get('uid')
		emp_id = self.env['hr.employee'].search([('user_id', '=', uid)])
		name = emp_id.id
		emp_code = emp_id.emp_code
		rec['name'] = name
		rec['emp_code'] = emp_code
		return rec	


	@api.multi
	def view_emp_data(self):
		sub_ids = self.env['hr.employee'].search([('parent_id','=',self.name.id)])
		if not sub_ids:
			raise ValidationError(_("No Data Found...!"))
		for hr in sub_ids:
			hr.write({'report_id':self.id})
		return True

	@api.multi
	def view_emp_kra(self):
		self.ensure_one()
		if self.name.kra_one2many:
			kra_det_form = self.env.ref('orient_pms.hr_kra_details_form', False)
			ctx = dict(default_name=self.name,emp_code=self.emp_code)
			return {
				'name': _('KRA'),
				'type': 'ir.actions.act_window',
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'hr.employee',
				'res_id': self.name.id,
				'views': [(kra_det_form.id, 'form')],
				'view_id': kra_det_form.id,
				'target': 'new',
				'context': ctx,
			}
		else:
			raise ValidationError(_("KRA not mapped for this Employee!"))


class HrEmployee(models.Model):
	_inherit = 'hr.employee'

	report_id = fields.Many2one('subordinate.kra.view','Sub')
	site_master_id = fields.Many2one('site.master','Site')

	@api.multi
	def kra_details(self):
		self.ensure_one()
		if self.kra_one2many:
			kra_det_form = self.env.ref('orient_pms.hr_kra_details_form', False)
			ctx = dict(default_name=self.name,emp_code=self.emp_code)
			return {
				'name': _('KRA'),
				'type': 'ir.actions.act_window',
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'hr.employee',
				'res_id': self.id,
				'views': [(kra_det_form.id, 'form')],
				'view_id': kra_det_form.id,
				'target': 'new',
				'context': ctx,
			}
		else:
			raise ValidationError(_("KRA not mapped for this Employee!"))

	def print_employee_report(self):
		for rec in self:
			if not self.year.id:
				raise ValidationError(_("Kindly select Year!"))
			search_salary_struct = self.env['employee.salary.structure'].search([('employee','=',self.id),('year','=',self.year.id)])
			if search_salary_struct:
				self.freeze_records = True
				template_id = self.env.ref('orient_pms.email_template_for_appraisal_acceptance', False)
				self.env['mail.template'].browse(template_id.id).send_mail(rec.id, force_send=True)
				return self.env.ref('orient_pms.action_appraisal_form_generate1').report_action(search_salary_struct.id)
			else:
				raise ValidationError(_("Revised Salary structure not yet uploaded for selected Financial Year!"))

	def reject_appraisal(self):
		for rec in self:
			template_id = self.env.ref('orient_pms.email_template_for_appraisal_rejection', False)
			self.env['mail.template'].browse(template_id.id).send_mail(rec.id, force_send=True)
			self.freeze_records = True

	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):

		res = super(HrEmployee, self).fields_view_get(view_id=view_id, view_type=view_type,toolbar=toolbar, submenu=submenu)
		doc = etree.XML(res['arch'])
		print(view_type,'view_type')
		if self._context.get('uid'):
			uid = self._context.get('uid')
			res_user = self.env['res.users'].search([('id','=',uid)])
			if view_type == 'search' and not res_user.has_group('hr.group_hr_manager') and not res_user.has_group('hr.group_hr_user'):
				for node_form in doc.xpath("//search"):
					node_form.set("create", 'false')
			elif view_type == 'kanban' and not res_user.has_group('hr.group_hr_manager') and not res_user.has_group('hr.group_hr_user'):
				for node_form in doc.xpath("//kanban"):
					node_form.set("create", 'false')
			elif view_type == 'form' and not res_user.has_group('hr.group_hr_manager') and not res_user.has_group('hr.group_hr_user'):
				for node_form in doc.xpath("//form"):
					node_form.set("create", 'false')
			elif view_type == 'tree' and not res_user.has_group('hr.group_hr_manager') and not res_user.has_group('hr.group_hr_user'):
				for node_form in doc.xpath("//tree"):
					node_form.set("create", 'false')
		res['arch'] = etree.tostring(doc)

		return res

class SiteMaster(models.Model):
	_name = "site.master"

	name = fields.Char('Site Name')
	active = fields.Boolean('Active',default=True)
	

class SubDepartment(models.Model):
	_name = 'sub.department'

	name = fields.Char('Sub Department')
	department_id = fields.Many2one('hr.department','Department Name')
	active = fields.Boolean('Active',default=True)

class GenerateAppraisalLetter(models.Model):
	_name = 'generate.appraisal.letter'

	employee = fields.Many2one('hr.employee','Employee Name')
	file_upload = fields.Binary('Upload File')

	def print_employee_report_new(self):
		return self.env.ref('orient_pms.action_appraisal_form_generate').report_action(self)

class QuarterlyKraReviewAuth(models.Model):
	_name = 'quarterly.kra.review.auth'

	quarterly_review_one2many = fields.One2many('kra.main','quarterly_kra_auth_id')
	employee = fields.Many2one('hr.employee','Employee Name')
	approval_status = fields.Selection([('draft','Pending'),
								 ('done','Approved'),('cancel','Rejected')
								], string="Approval Status", default="draft")
	quarter = fields.Selection([('Q1','Q1'),('Q2','Q2'),('Q3','Q3'),('Q4','Q4')], string="Quarter")
	year = fields.Many2one('year.master','Year')

	@api.multi
	def search_quarterly_record(self):
		self.env.cr.execute("update kra_main set select_record = 'f',quarterly_kra_auth_id = null")
		if self._uid!=1:
			domain = []
			emp_list = []
			employee = self.env['hr.employee'].search([('user_id','=',self._uid)])
			print (employee.id)
			search_emp =  self.env['hr.employee'].search([('parent_id','=',employee.id)])
			if search_emp:
				for x in search_emp:
					emp_list.append(x.id)
			if self.employee:
				domain.append(('employee','=',self.employee.id))
			if self.approval_status:
				domain.append(('state','=',self.approval_status))
			if self.year:
				domain.append(('kra_year','=',self.year.id))
			domain.append(('employee','in',emp_list))
			print (domain,'domain')
			search_recs = self.env['kra.main'].search(domain)	
			print (search_recs,'pppppp')
			if search_recs:
				for rec in search_recs:
					rec.write({'quarterly_kra_auth_id':self.id})
		else:
			domain = []
			if self.employee:
				domain.append(('employee','=',self.employee.id))
			if self.approval_status:
				domain.append(('state','=',self.approval_status))
			if self.year:
				domain.append(('kra_year','=',self.year.id))
			domain.append(('state','in',('draft','done')))
			search_recs = self.env['kra.main'].search(domain)	
			if search_recs:
				for rec in search_recs:
					rec.write({'quarterly_kra_auth_id':self.id})

	@api.multi
	def approve_review_form(self):
		self.ensure_one()
		kra_form = self.env.ref('orient_pms.view_kramain_form', False)
		select = False
		if self.quarterly_review_one2many:
			for m in self.quarterly_review_one2many:
				if m.select_record:
					select = True					
					return {
						'name': _('Quarterly KRA Review Form'),
						'type': 'ir.actions.act_window',
						'view_type': 'form',
						'view_mode': 'form',
						'res_model': 'kra.main',
						'res_id': m.id,
						'views': [(kra_form.id, 'form')],
						'view_id': m.id,
						'target': 'new',
					}
			if select == False:
				raise ValidationError(_("Kindly Select Record!"))

class QuarterlyRatingAnnual(models.Model):
	_name = 'quarterly.rating.annual'

	def _get_default_access_token(self):
		return str(uuid.uuid4())

	quarterly_rating_annual_one2many = fields.One2many('quarterly.rating.annual.line','quarterly_rating_annual_id')
	review_cycle = fields.Selection([('January','January'),('July','July')], string="Review Cycle")
	year = fields.Many2one('year.master','Year')
	exists = fields.Boolean('Exists?',default=False)
	access_token = fields.Char('Security Token', copy=False,default=_get_default_access_token)

	@api.model_cr_context
	def _init_column(self, column_name):
		""" Initialize the value of the given column for existing rows.

			Overridden here because we need to generate different access tokens
			and by default _init_column calls the default method once and applies
			it for every record.
		"""
		if column_name != 'access_token':
			super(QuarterlyRatingAnnual, self)._init_column(column_name)
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
	def generate_excel(self,access_uid=None):
		self.ensure_one()
		return {
		'type': 'ir.actions.act_url',
		'url': '/web/pivot/quarterly_rating_annual_xls/%s?access_token=%s' % (self.id, self.access_token),
		'target': 'new',
		}


	@api.multi
	def search_records(self):
		if not self.review_cycle:
			raise ValidationError(_("Kindly Select Review Cycle!"))
		review_cycle = self.review_cycle
		quarter1 = 0.0
		quarter2 = 0.0
		quarter3 = 0.0
		quarter4 = 0.0
		q1_status = ''
		q2_status = ''
		q3_status = ''
		q4_status = ''
		emp_obj=self.env['hr.employee']
		kra_obj=self.env['kra.main']
		appraisal_obj=self.env['annual.kra.details']
		self.env.cr.execute("delete from quarterly_rating_annual_line")
		emp_records = self.env['hr.employee'].search([('appraisal_cycle','=',review_cycle)])
		print(emp_records)
		count=1 
		for emp_recs in emp_records:
			print(emp_recs)
			current_date =  datetime.now().date()
			joining_date = emp_recs.joining_date
			date_dt= datetime.strptime(joining_date, "%Y-%m-%d").date()
			current_date= datetime.strptime(str(current_date), "%Y-%m-%d").date()
			tenure = relativedelta(current_date, date_dt)
			if review_cycle == 'January':
				pip_applicable = False
				pip_applicable1 = False
				pip_applicable2 = False
				pip_applicable3 = False
				pip_applicable4 = False
				get_year = self.year.name
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
				search_quarter4=kra_obj.search([('review_start_date','=',review_start_date4),('review_end_date','=',review_end_date4),('employee','=',emp_recs.id),('active','=',True)])
				search_quarter1=kra_obj.search([('review_start_date','=',review_start_date1),('review_end_date','=',review_end_date1),('employee','=',emp_recs.id),('active','=',True)])							
				search_quarter2=kra_obj.search([('review_start_date','=',review_start_date2),('review_end_date','=',review_end_date2),('employee','=',emp_recs.id),('active','=',True)])
				search_quarter3=kra_obj.search([('review_start_date','=',review_start_date3),('review_end_date','=',review_end_date3),('employee','=',emp_recs.id),('active','=',True)])
				if search_quarter4:
					pip_applicable4=search_quarter4.pip_applicable
					if search_quarter4.state in ('reportee','draft','employee'):
						q4_status = 'Pending'
					if search_quarter4.state == 'done':
						q4_status = 'Done'
					if search_quarter4.state == 'cancel':
						q4_status = 'Rejected'
					quarter4 = search_quarter4.final_rating
				if search_quarter1:
					pip_applicable1=search_quarter1.pip_applicable
					if search_quarter1.state in ('reportee','draft','employee'):
						q1_status = 'Pending'
					if search_quarter1.state == 'done':
						q1_status = 'Done'
					if search_quarter1.state == 'cancel':
						q1_status = 'Rejected'
					quarter1 = search_quarter1.final_rating
				if search_quarter2:
					pip_applicable2=search_quarter2.pip_applicable
					if search_quarter2.state in ('reportee','draft','employee'):
						q2_status = 'Pending'
					if search_quarter2.state == 'done':
						q2_status = 'Done'
					if search_quarter2.state == 'cancel':
						q2_status = 'Rejected'
					quarter2 = search_quarter2.final_rating
				if search_quarter3:
					pip_applicable3=search_quarter3.pip_applicable
					if search_quarter3.state in ('reportee','draft','employee'):
						q3_status = 'Pending'
					if search_quarter3.state == 'done':
						q3_status = 'Done'
					if search_quarter3.state == 'cancel':
						q3_status = 'Rejected'
					quarter3 = search_quarter3.final_rating
				print (pip_applicable1,pip_applicable2,pip_applicable3,pip_applicable4,'pippp')
				if pip_applicable1 or pip_applicable2 or pip_applicable3 or pip_applicable4:
					pip_applicable = True
				if tenure.years >= 1:
					print (emp_recs.name,'name',tenure.years)
					self.write({'exists':True})
					print(pip_applicable,'ppppppppppppp')
					self.env['quarterly.rating.annual.line'].create({
													'quarterly_rating_annual_id':self.id,
													'employee':emp_recs.id,
													'employee_name':emp_recs.name,
													'employee_code':emp_recs.emp_code,
													'reporting_code':emp_recs.parent_id.id,
													'reporting_name':emp_recs.parent_id.name,
													'department':emp_recs.department_id.id,
													'designation':emp_recs.job_id.id,
													'eligible_for_pip':pip_applicable,
													'quarter1':quarter1,
													'quarter2':quarter2,
													'quarter3':quarter3,
													'quarter4':quarter4,
													'q1_status':q1_status,
													'q2_status':q2_status,
													'q3_status':q3_status,
													'q4_status':q4_status,
													'sr_no':count,
													'joining_date':emp_recs.joining_date			
													})
					count+=1
			if review_cycle == 'July':
				get_year = self.year.name
				split_year = get_year.split('-')
				year1 = str(int(split_year[0])-1)
				year2 = str(int(split_year[1])-1)
				print (get_year,year1,year2)
				pip_applicable = False
				pip_applicable1 = False
				pip_applicable2 = False
				pip_applicable3 = False
				pip_applicable4 = False
				review_start_date1=year2+'-04-01'
				review_end_date1=year2+'-06-30'
				review_start_date2=year1+'-07-01'
				review_end_date2=year1+'-09-30'
				review_start_date3=year1+'-10-01'
				review_end_date3=year1+'-12-31'
				review_start_date4=year2+'-01-01'
				review_end_date4=year2+'-03-31'
				search_quarter2=kra_obj.search([('review_start_date','=',review_start_date2),('review_end_date','=',review_end_date2),('employee','=',emp_recs.id),('active','=',True)])
				search_quarter3=kra_obj.search([('review_start_date','=',review_start_date3),('review_end_date','=',review_end_date3),('employee','=',emp_recs.id),('active','=',True)])
				search_quarter4=kra_obj.search([('review_start_date','=',review_start_date4),('review_end_date','=',review_end_date4),('employee','=',emp_recs.id),('active','=',True)])
				search_quarter1=kra_obj.search([('review_start_date','=',review_start_date1),('review_end_date','=',review_end_date1),('employee','=',emp_recs.id),('active','=',True)])
				if search_quarter2:
					pip_applicable2=search_quarter2.pip_applicable
					if search_quarter2.state in ('reportee','draft','employee'):
						q2_status = 'Pending'
					if search_quarter2.state == 'done':
						q2_status = 'Done'
					if search_quarter2.state == 'cancel':
						q2_status = 'Rejected'
					quarter2 = search_quarter2.final_rating
				if search_quarter3:
					pip_applicable3=search_quarter3.pip_applicable
					if search_quarter3.state in ('reportee','draft','employee'):
						q3_status = 'Pending'
					if search_quarter3.state == 'done':
						q3_status = 'Done'
					if search_quarter3.state == 'cancel':
						q3_status = 'Rejected'
					quarter3 = search_quarter3.final_rating
				if search_quarter4:
					pip_applicable4=search_quarter4.pip_applicable
					if search_quarter4.state in ('reportee','draft','employee'):
						q4_status = 'Pending'
					if search_quarter4.state == 'done':
						q4_status = 'Done'
					if search_quarter4.state == 'cancel':
						q4_status = 'Rejected'
					quarter4 = search_quarter4.final_rating
				if search_quarter1:
					pip_applicable1=search_quarter1.pip_applicable
					if search_quarter1.state in ('reportee','draft','employee'):
						q1_status = 'Pending'
					if search_quarter1.state == 'done':
						q1_status = 'Done'
					if search_quarter1.state == 'cancel':
						q1_status = 'Rejected'
					quarter1 = search_quarter1.final_rating
				print (pip_applicable1,pip_applicable2,pip_applicable3,pip_applicable4,'pippp')
				if pip_applicable1 or pip_applicable2 or pip_applicable3 or pip_applicable4:
					pip_applicable = True
				if tenure.years >= 1:
					print (emp_recs.name,'name',tenure.years)
					self.write({'exists':True})
					print(pip_applicable,'ppppppppppppp')
					self.env['appraisal.due.child'].create({
													'quarterly_rating_annual_id':self.id,													'quarterly_rating_annual_id':self.id,
													'employee':emp_recs.id,
													'employee_name':emp_recs.name,
													'employee_code':emp_recs.emp_code,
													'reporting_code':emp_recs.parent_id.id,
													'reporting_name':emp_recs.parent_id.name,
													'department':emp_recs.department_id.id,
													'designation':emp_recs.job_id.id,
													'eligible_for_pip':pip_applicable,
													'quarter1':quarter1,
													'quarter2':quarter2,
													'quarter3':quarter3,
													'quarter4':quarter4,
													'q1_status':q1_status,
													'q2_status':q2_status,
													'q3_status':q3_status,
													'q4_status':q4_status,
													'sr_no':count,	
													'joining_date':emp_recs.joining_date
						})
					count+=1

		return True




class QuarterlyRatingAnnualLine(models.Model):

	_name = 'quarterly.rating.annual.line'

	sr_no = fields.Integer('Sr. No.')
	reporting_code = fields.Char('Reporting Code')
	reporting_name = fields.Char('Reporting Name')
	quarterly_rating_annual_id = fields.Many2one('quarterly.rating.annual','Quarterly Review Report')
	employee = fields.Many2one('hr.employee','Employee')
	employee_name = fields.Char('Employee Name')
	department =  fields.Many2one('hr.department','Department')
	application_date = fields.Date("Application Date")
	approved_date = fields.Date("Approved Date")
	review_status = fields.Char("Review Status")
	average_rating = fields.Char("Average Rating")
	review_summary = fields.Char("Review Summary")
	eligible_for_pip = fields.Boolean('Eligible For PIP')
	employee_status =  fields.Char('Employee Status')
	designation = fields.Many2one('hr.job','Designation')
	employee_code = fields.Char('Employee Code')
	ratings = fields.Float('Rating')
	quarter1 = fields.Float('Q1')
	quarter2 = fields.Float('Q2')
	quarter3 = fields.Float('Q3')
	quarter4 = fields.Float('Q4')
	q1_status = fields.Char('Q1 Status')
	q2_status = fields.Char('Q2 Status')
	q3_status = fields.Char('Q3 Status')
	q4_status = fields.Char('Q4 Status')
	month = fields.Selection([('January', 'January'),('February', 'February'),
								('March', 'March'),('April', 'April'),
								('May', 'May'),('June','June'),
								('July','July'),('August','August'),
								('September','September'),('October','October'),
								('November','November'),('December','December')
								],string='Month')
	kra_year = fields.Many2one('year.master','Year')
	status = fields.Selection([('active','Active'),('inactive','Inactive')],default='active',string='Status')
	joining_date = fields.Date('Joining Date')

class Department(models.Model):

	_inherit = "hr.department"
	
	sub_department = fields.Many2one('sub.department','Annual Appraisal Form')

