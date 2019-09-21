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
import requests
from odoo.tools import config, human_size, ustr, html_escape
import PyPDF2

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

class EmployeeProvisional(models.Model):
	_name = "employee.provisional"


	def _get_employee_id(self):
        # assigning the related employee of the logged in user
		employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
		return employee_rec.id

	name = fields.Char('Name',default='Add/Modify Employees Provisional Investments')
	employee = fields.Many2one('hr.employee', 'Employee Name') #,default=_get_employee_id,
	year = fields.Many2one('year.master','Financial Year')
	particulars_name = fields.Many2one('particulars.master','Search')
	section = fields.Many2one('section.master','Section *')
	particulars = fields.Many2one('particulars.master','Particulars *')
	description = fields.Char('Description')
	date_of_submission = fields.Date('Date Of Submission')
	amount = fields.Float('Amount')
	provisional_lines = fields.One2many('employee.provisional.lines','provisional_id', 'Provisional Lines')
	check_exists = fields.Boolean('check_exists',default=False)
	period_exists = fields.Boolean('Period Required',default=False)
	from_date = fields.Date('From Month of Rent/Loan Paid')
	to_date = fields.Date('To Month of Rent/Loan Paid')



	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(EmployeeProvisional, self).fields_view_get(
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

	# @api.model
	# def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
	# 	context = self._context or {}
	# 	print (context,'context')
	# 	asset_id = self.env.context.get('active_id')
	# 	print (asset_id,'asset_id')
	# 	res = super(EmployeeProvisional, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=False)
	# 	# cmp_select = []
	# 	# CompanyObj = self.env['res.company']
	# 	done_recs = []
	# 	# companies = CompanyObj.search([])
	# 	# #display in the widget selection of companies, only the companies that haven't been configured yet (but don't care about the demo chart of accounts)
	# 	# self._cr.execute("SELECT company_id FROM account_account WHERE deprecated = 'f' AND name != 'Chart For Automated Tests' AND name NOT LIKE '%(test)'")
	# 	# configured_cmp = [r[0] for r in self._cr.fetchall()]
	# 	# unconfigured_cmp = list(set(companies.ids) - set(configured_cmp))
	# 	for field in res['fields']:
	# 		if field == 'employee':
	# 			employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
	# 			print('employee_id',employee_rec.id)
	# 			if employee_rec:
	# 				res.update({'employee':employee_rec.id})
	# 				recs = self.env['employee.provisional.lines'].search([('employee', '=', employee_rec.id)])
	# 				if recs:
	# 					for m in recs:
	# 						done_recs.append(m.id)
	# 					res.update({'provisional_lines': [(6, 0, done_recs)]})
	# 				print (recs,done_recs,'ppppppppppp')
	# 		if field == 'provisional_lines':
	# 			print ('xxxxxxxxxxxxx','ppppppppppppppp')
	# 	return res

	@api.onchange('particulars')
	def onchange_name(self):
		res = {'period_exists':False}
		period_required = False
		if not self.particulars or not self.particulars:
			return
		else:
			particulars = self.particulars.id
			particulars_data = self.env['particulars.master'].browse(particulars)
			self.description = particulars_data.description
			if particulars_data.period_required:
				self.period_exists = True
		return res

	@api.onchange('section')
	def onchange_section(self):
		res = {'period_exists':False}
		self.period_exists = False
		self.particulars = False
		self.description = False
		return res

	@api.multi
	def search_recs(self):
		if self.particulars_name:
			self.write({'particulars':self.particulars_name.id,'section':self.particulars_name.section.id,'description':self.particulars_name.description})
		if not self.particulars_name:
			raise ValidationError(_("Kindly Enter particulars to search!"))

	@api.multi
	def add_recs(self):
		# if self.name:
		# 	self.write({'particulars':self.name.id,'section':self.name.section.id,'description':self.name.description})
		if not self.section:
			raise ValidationError(_("Kindly Select Section!"))
		if not self.particulars:
			raise ValidationError(_("Kindly Select Particulars!"))
		if not self.amount:
			raise ValidationError(_("Kindly enter Amount!"))
		self.write({'check_exists':True})
		self.env['employee.provisional.lines'].create({
									'employee':self.employee.id,
									'provisional_id':self.id,
									'amount':self.amount,
									'status':'Pending',
									'particulars':self.particulars.id,
									'section':self.section.id,
									'year':self.year.id,
									'date_of_submission':self.date_of_submission,
									'particulars_name':self.particulars.name,
									'period_exists':self.period_exists,
									'from_date':self.from_date,
									'description':self.description,
									'to_date':self.to_date})
		self.write({'particulars_name':False,'section':False,'period_exists':False,'particulars':False,'description':False,'amount':False})

	def view_recs(self):
		recs = self.env['employee.provisional.lines'].search([('employee', '=', self.employee.id)])
		print (recs,self.id,'recsss')
		if recs:
			for record in recs:
				print (record,'recooooo')
				record.write({'provisional_id':self.id})
			self.write({'check_exists':True})
		else:
			raise ValidationError(_("No record Found!"))

	@api.model
	def default_get(self, fields):
		rec = super(EmployeeProvisional, self).default_get(fields)
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
			rec['year']=search_year[0].id
		rec['date_of_submission'] = today_date
		employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
		rec['employee'] = employee_rec.id
		print (rec)
		return rec

class EmployeeProvisionalLines(models.Model):
	_name = "employee.provisional.lines"

	employee = fields.Many2one('hr.employee', 'Employee Name') #,default=_get_employee_id,
	year = fields.Many2one('year.master','Financial Year')
	name = fields.Many2one('particulars.master','Search')
	section = fields.Many2one('section.master','Section *')
	particulars = fields.Many2one('particulars.master','Particulars *')
	description = fields.Char('Description')
	date_of_submission = fields.Date('Date Of Submission')
	status = fields.Selection([('Pending','Pending'),('Authorized','Authorized'),('Rejected','Rejected')],string="Status")
	particulars_name = fields.Char('Particulars')
	amount = fields.Float('Amount')
	doc_attachment = fields.Binary('Attachment',attachment=True)
	attachments = fields.Many2many('ir.attachment', 'att_id',string="Attachments", domain=[('res_model', '=', _name)])
	provisional_id = fields.Many2one('employee.provisional', 'Provisional ID')
	period_exists = fields.Boolean('Period Required',default=False)
	from_date = fields.Date('From Month of Rent/Loan Paid')
	to_date = fields.Date('To Month of Rent/Loan Paid')
	# attach_1 = fields.Binary('Attach')


	@api.multi
	def select_rec(self):		
		self.ensure_one()
		for rec in self:
			print(rec.id)
			provisional_line_form = self.env.ref('orient_tds.view_employee_provisional_lines_form', False)
			ctx = dict(
				default_section=self.section.id,
				default_particulars=self.particulars.id,
				default_description=self.description,
				default_amount=self.amount)
			return {
				'name': _('Modify Employees Provisional Investments'),
				'type': 'ir.actions.act_window',
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'employee.provisional.lines',
				'res_id': rec.id,
				'views': [(provisional_line_form.id, 'form')],
				'view_id': provisional_line_form.id,
				'target': 'new',
				'context': ctx,
			}

	@api.multi
	def attach_file(self):		
		self.ensure_one()
		for rec in self:
			print(rec.id)
			provisional_line_form = self.env.ref('orient_tds.view_employee_provisional_lines_form_attach', False)
			ctx = dict(
				default_section=self.section.id,
				default_particulars=self.particulars.id,
				default_description=self.description,
				default_amount=self.amount)
			return {
				'name': _('Modify Employees Provisional Investments'),
				'type': 'ir.actions.act_window',
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'employee.provisional.lines',
				'res_id': rec.id,
				'views': [(provisional_line_form.id, 'form')],
				'view_id': provisional_line_form.id,
				'target': 'new',
				'context': ctx,
			}

	@api.onchange('particulars')
	def onchange_name(self):
		res = {'period_exists':False}
		period_required = False
		if not self.particulars or not self.particulars:
			return
		else:
			particulars = self.particulars.id
			particulars_data = self.env['particulars.master'].browse(particulars)
			self.description = particulars_data.description
			if particulars_data.period_required:
				self.period_exists = True
		return res

	@api.onchange('section')
	def onchange_section(self):
		res = {'period_exists':False}
		self.period_exists = False
		self.particulars = False
		self.description = False
		return res

	@api.multi
	def search_records(self):
		if self.name:
			self.update({'particulars':self.name.id,'particulars_name':self.particulars.name,'section':self.name.section.id,'description':self.name.description})
		if not self.name:
			raise ValidationError(_("Kindly Enter particulars to search!"))
		return True

	@api.multi
	def approve_rec(self):
		self.status='Authorized'
		return True

	@api.multi
	def reject_rec(self):
		self.status='Rejected'
		return True

	@api.multi
	def save_exit(self):
		if not self.section:
			raise ValidationError(_("Kindly Select Section!"))
		if not self.particulars:
			raise ValidationError(_("Kindly Select Particulars!"))
		if not self.amount:
			raise ValidationError(_("Kindly enter Amount!"))
		self.write({'particulars':self.particulars.id,'particulars_name':self.particulars.name,'section':self.section.id,'description':self.description})

	@api.multi
	def save_attachment(self):
		# if not self.section:
		# 	raise ValidationError(_("Kindly Select Section!"))
		# if not self.particulars:
		# 	raise ValidationError(_("Kindly Select Particulars!"))
		# if not self.amount:
		# 	raise ValidationError(_("Kindly enter Amount!"))
		if self.attachments:
			for m in self.attachments:
				m.write({'att_id':self.id,'name':'kkkkkkkk'})
		# self.write({'particulars':self.particulars.id,'particulars_name':self.particulars.name,'section':self.section.id,'description':self.description})



class SectionMaster(models.Model):
	_name = "section.master"

	name = fields.Char('Name')
	active = fields.Boolean('Active',default=True)	

class ParticularsMaster(models.Model):
	_name = "particulars.master"

	name = fields.Char('Name')
	section = fields.Many2one('section.master','Section')
	description = fields.Char('Description')
	period_required = fields.Boolean('Period Required?')
	active = fields.Boolean('Active',default=True)

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    att_id = fields.Many2one('employee.provisional.lines','Lines')
    datas_fname = fields.Char('File Name')
    datas = fields.Binary(string='File Content', attachment=True)#compute='_compute_datas', inverse='_inverse_datas'
    db_datas = fields.Binary('Database Data') 
    file_url = fields.Char('Url', index=True, size=1024)


    # @api.depends('datas_fname','db_datas')
    # def _compute_datas(self):
    #     bin_size = self._context.get('bin_size')
    #     result ={}
    #     for attach in self:
    #         if attach.datas_fname:
    #             result[attach.id]= self._file_read(attach.file_url,attach.datas_fname)
    #         else:
    #             result[attach.id] = attach.db_datas

    # def _inverse_datas(self):
    #     for attach in self:
    #         # compute the fields that depend on datas
    #         file_name = attach.datas_fname
    #         value = attach.datas
    #         bin_data = base64.b64decode(value) if value else b''
    #         if file_name.endswith('.csv'):
    #             fname = self._file_write(value,file_name)
    #             vals={'file_url':fname}
    #         # write as superuser, as user probably does not have write access
    #         super(irattachment, attach.sudo()).write(vals)

class PaySlipView(models.Model):
	_name = "pay.slip.view"

	employee_id = fields.Many2one('hr.employee','Employee')
	emp_code = fields.Char('Emp Code')
	month_sel = fields.Selection([('January','January'),('February','February'),('March','March'),('April','April'),
								('May','May'),('June','June'),('July','July'),('August','August'),
								('September','September'),('October','October'),('November','November'),
								('December','December')], string="Month")
	year_sel = fields.Many2one('year.master.annual','Year')
	name = fields.Char('Name')

	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(PaySlipView, self).fields_view_get(
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
	def html_payslip(self):
		return True

	@api.model
	def default_get(self, fields):
		rec = super(PaySlipView, self).default_get(fields)
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
		search_year = self.env['year.master.annual'].search([('name','=',str(year))])
		if search_year:
			rec['year_sel']=search_year[0].id
		rec['month_sel'] = current_month
		employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
		rec['employee_id'] = employee_rec.id

		print (rec)
		return rec

class PaySlip(models.Model):
	_name = "pay.slip"

	employee_id = fields.Many2one('hr.employee','Employee')
	emp_code = fields.Char('Emp Code')
	month_sel = fields.Selection([('January','January'),('February','February'),('March','March'),('April','April'),
								('May','May'),('June','June'),('July','July'),('August','August'),
								('September','September'),('October','October'),('November','November'),
								('December','December')], string="Month")
	year_sel = fields.Many2one('year.master.annual','Year')
	name = fields.Char('Name')
	pan = fields.Char('PAN NO')
	uan = fields.Char('UAN NO')
	paid_days =  fields.Float('PAID DAYS')
	join_date = fields.Date('DT. OF JOIN')
	pf_no = fields.Char('PF NO.')
	addhar_no = fields.Char('AADHAAR NO')
	esic_no = fields.Char('ESIC NO')
	bank_account_no = fields.Char('BANK ACCOUNT NO')
	present_days = fields.Float('PRESENT DAYS')
	absent_days = fields.Float('ABSENT DAYS')
	pl = fields.Float('PL')
	holiday = fields.Float('HOLIDAY')
	c_off = fields.Float('C-OFF')
	w_off = fields.Float('W-OFF')

	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(PaySlip, self).fields_view_get(
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
	def html_payslip(self):
		return True

	@api.multi
	def pdf_payslip(self):
		current_date =  datetime.now().date()
		current_month = datetime.strptime(str(current_date), "%Y-%m-%d").strftime('%B')
		current_year = datetime.strptime(str(current_date), "%Y-%m-%d").strftime('%Y')
		search_pay_slip = self.search([('emp_code','=',self.employee_id.emp_code),('month_sel','=',self.month_sel),('year_sel','=',self.year_sel.id)])
		if not search_pay_slip:
			raise ValidationError(_("Salary Slip not generated for the selected Month and Year!!"))
		
		if search_pay_slip:
			return self.env.ref('orient_tds.action_generate_pay_slip').report_action(search_pay_slip)

	@api.model
	def default_get(self, fields):
		rec = super(PaySlip, self).default_get(fields)
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
		search_year = self.env['year.master.annual'].search([('name','=',str(year))])
		if search_year:
			rec['year_sel']=search_year[0].id
		rec['month_sel'] = current_month
		employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
		rec['employee_id'] = employee_rec.id
		rec['join_date'] = str(employee_rec.joining_date) if employee_rec.joining_date else ''
		check_rec = self.search([('emp_code','=',employee_rec.emp_code),('month_sel','=',current_month),('year_sel','=',rec['year_sel'])])
		if check_rec:
			rec['pl'] = check_rec.pl
			rec['holiday'] = check_rec.holiday
			rec['c_off'] = check_rec.c_off
			rec['w_off'] = check_rec.w_off
			rec['basic_da']=check_rec.basic_da
			rec['basic_arrear'] = check_rec.basic_arrear
			rec['hra']=check_rec.hra
			rec['hra_arrear'] = check_rec.hra_arrear
			rec['transport_allowance'] =check_rec.transport_allowance
			rec['transport_allowance_arrear'] =check_rec.transport_allowance_arrear
			rec['prof_development']=check_rec.prof_development
			rec['prof_development_arrear']=check_rec.prof_development_arrear
			rec['other_allowance']=check_rec.other_allowance
			rec['other_allowance_arrear'] = check_rec.other_allowance_arrear
			rec['attire_allowance'] = check_rec.attire_allowance
			rec['attire_allowance_arrear'] = check_rec.attire_allowance_arrear
			rec['medical_allowance'] = check_rec.medical_allowance
			rec['medical_allowance_arrear'] = check_rec.medical_allowance_arrear
			rec['educational_allowance'] = check_rec.educational_allowance
			rec['educational_allowance_arrear'] = check_rec.educational_allowance_arrear
			rec['contribution_towards_nps_us_80ccd'] = check_rec.contribution_towards_nps_us_80ccd
			rec['contribution_towards_nps_us_80ccd_arrear'] = check_rec.contribution_towards_nps_us_80ccd_arrear
			rec['news_paper_journal_allowance'] = check_rec.news_paper_journal_allowance
			rec['news_paper_journal_allowance_arrear'] = check_rec.news_paper_journal_allowance_arrear
			rec['gadget_for_professional_use'] = check_rec.gadget_for_professional_use
			rec['gadget_for_professional_use_arrear'] = check_rec.gadget_for_professional_use_arrear
			rec['gross_salary'] = check_rec.gross_salary
			rec['pf'] = check_rec.pf
			rec['pf_arrear'] = check_rec.pf_arrear
			rec['esic'] = check_rec.esic
			rec['esic_arrear'] = check_rec.esic_arrear
			rec['tds'] = check_rec.tds
			rec['tds_arrear'] = check_rec.tds_arrear
			rec['pt'] = check_rec.pt
			rec['pt_arrear'] = check_rec.pt_arrear
			rec['conveyance'] = check_rec.conveyance
			rec['conveyance_arrear'] = check_rec.conveyance_arrear
			rec['mobile_allowance'] = check_rec.mobile_allowance
			rec['mobile_allowance_arrear'] = check_rec.mobile_allowance_arrear
			rec['total_deductions'] = check_rec.total_deductions
			rec['net_pay'] = check_rec.net_pay
			rec['total_earnings']= check_rec.total_earnings
			rec['statutory_bonus']=check_rec.statutory_bonus
			rec['paid_leave_encashment']=check_rec.paid_leave_encashment
			rec['total_deductions']=check_rec.total_deductions
			rec['net_pay']=check_rec.net_pay
			rec['total_earnings']=check_rec.total_earnings
			rec['loan']=check_rec.loan
			rec['salary_advance']=check_rec.salary_advance
			rec['mobile_deduction']=check_rec.mobile_deduction
			rec['other_deductions']=check_rec.other_deductions
			rec['other_earnings']=check_rec.other_earnings
		print (rec)
		return rec


class Form16(models.Model):
	_name = "form.16"


	form_a = fields.Binary('Form 16 Part A',attachment=True)
	form_b = fields.Binary('Form 16 Part B',attachment=True)
	employee_id = fields.Many2one('hr.employee','Employee')
	month_sel = fields.Selection([('1','January'),('2','February'),('3','March'),('4','April'),
								('5','May'),('6','June'),('7','July'),('8','August'),
								('9','September'),('10','October'),('11','November'),
								('12','December')], string="Month")
	year_sel = fields.Many2one('year.master','Assessment Year')
	generated = fields.Boolean(default=False,string='Generated?')


	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(Form16, self).fields_view_get(
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
	def generate_form_16(self):
		res_vals = {}
		pdf_file_encode1 = False
		pdf_file_encode2 = False
		if self.env.user.id == 1:
			raise ValidationError(_('Login with different user!'))
		emp_code = self.env.user.login
		emp_id = self.env['hr.employee'].search([('emp_code','=',emp_code)],limit=1)
		if emp_id.pan:
			pan = emp_id.pan
		else:
			raise ValidationError(_('PAN number is not yet linked to your profile. Please contact HR!'))
		part_a = '_'
		part_b = '_PARTB_'	
		year = self.year_sel.name
		year_name = 'NA'
		if year == '2013-2014':
			year_name = '2013-14'
		if year == '2014-2015':
			year_name = '2014-15'
		if year == '2015-2016':
			year_name = '2015-16'
		if year == '2016-2017':
			year_name = '2016-17'
		if year == '2017-2018':
			year_name = '2017-18'
		if year == '2018-2019':
			year_name = '2018-19'
		if year == '2019-2020':
			year_name = '2019-20'
		if year == '2020-2021':
			year_name = '2020-21'
		extention = '.pdf'
		file_name_part_a = pan+part_a+year_name+extention
		file_name_part_b = pan+part_b+year_name+extention
		source_path = '/home/odoouser/form_16/'
		full_path_part_a = source_path+file_name_part_a
		full_path_part_b = source_path+file_name_part_b
		# if not os.path.exists(full_path_part_a):
			# raise ValidationError(_('File not found ! %s Please contact the HR or the administrator.')% full_path_part_a)
		# if not os.path.exists(full_path_part_b):
			# raise ValidationError(_('File not found ! %s Please contact the HR or the administrator.')% full_path_part_b)		
		if os.path.exists(full_path_part_a):
			with open(full_path_part_a, "rb") as pdf_file:
				pdf_file_encode1 = base64.b64encode(pdf_file.read())
				res_vals.update({'form_a':pdf_file_encode1})
		if os.path.exists(full_path_part_b):
			with open(full_path_part_b, "rb") as pdf_file:
				pdf_file_encode2 = base64.b64encode(pdf_file.read())
				res_vals.update({'form_b':pdf_file_encode2})
		if not pdf_file_encode1 and not pdf_file_encode2:
			raise ValidationError(_('File not found ! %s Please contact the HR or the administrator.')% pan)
		res_vals.update({'generated': True})
		res = self.write(res_vals)
		return res



	@api.model
	def default_get(self, fields):
		rec = super(Form16, self).default_get(fields)
		context = dict(self._context or {})
		active_id = context.get('active_id', False)
		current_year = None
		get_year = get_current_financial_year(self)
		year = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").year
		month = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").month
		search_year = self.env['year.master'].search([('name','=',str(get_year))])
		if search_year:
			current_year = search_year.id
		rec['month_sel'] = str(month)
		employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
		rec['employee_id'] = employee_rec.id
		rec['year_sel'] = current_year
		print (rec)
		return rec


class TdsSummary(models.Model):
	_name = "tds.summary"

	employee_id = fields.Many2one('hr.employee','Employee')
	month_sel = fields.Selection([('1','January'),('2','February'),('3','March'),('4','April'),
								('5','May'),('6','June'),('7','July'),('8','August'),
								('9','September'),('10','October'),('11','November'),
								('12','December')], string="Month")
	year_sel = fields.Many2one('year.master','Year')


	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(TdsSummary, self).fields_view_get(
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


	@api.model
	def default_get(self, fields):
		rec = super(TdsSummary, self).default_get(fields)
		context = dict(self._context or {})
		active_id = context.get('active_id', False)
		current_year = None
		get_year = get_current_financial_year(self)
		year = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").year
		month = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").month
		search_year = self.env['year.master'].search([('name','=',str(get_year))])
		if search_year:
			current_year = search_year.id
		rec['month_sel'] = str(month)
		employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
		rec['employee_id'] = employee_rec.id
		rec['year_sel'] = current_year
		print (rec)
		return rec

	@api.multi
	def tds_summary(self):
		return True

	@api.multi
	def tds_summary_details(self):
		return True

class ConveyanceReimbursement(models.Model):
	_name = "conveyance.reimbursement"

	name = fields.Char('Name',default="Conveyance Reimbursement")
	employee_id = fields.Many2one('hr.employee','Employee')
	month_sel = fields.Selection([('1','January'),('2','February'),('3','March'),('4','April'),
								('5','May'),('6','June'),('7','July'),('8','August'),
								('9','September'),('10','October'),('11','November'),
								('12','December')], string="Month")
	year = fields.Many2one('year.master','Year')
	monthly_amount = fields.Float('Conveyance Applicable(Monthly)')
	remaining_amount = fields.Float('Balance Amount')
	application_amount = fields.Float('Application Amount')
	doc_attachment = fields.Binary('Attachment',attachment=True)
	conveyance_reimbursement_lines = fields.One2many('conveyance.reimbursement.lines','conveyance_reimbursement_id', 'Conveyance Reimbursement Lines')
	record_exists = fields.Boolean('Record Exists',default=False)


	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(ConveyanceReimbursement, self).fields_view_get(
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


	@api.model
	def default_get(self, fields):
		rec = super(ConveyanceReimbursement, self).default_get(fields)
		context = dict(self._context or {})
		active_id = context.get('active_id', False)
		current_year = None
		yearly_amount = 0.0
		total_conveyance_applied = 0.0
		get_year = get_current_financial_year(self)
		year = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").year
		month = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").month
		search_year = self.env['year.master'].search([('name','=',str(get_year))])
		if search_year:
			current_year = search_year.id
		rec['month_sel'] = str(month)
		employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
		rec['employee_id'] = employee_rec.id
		rec['year'] = current_year
		search_monthly_rec = self.env['conveyance.reimbursement.import'].search([('employee','=',employee_rec.id),('year_id','=',current_year)])
		if search_monthly_rec:
			rec['monthly_amount'] = search_monthly_rec.monthly_conveyance
			yearly_amount = search_monthly_rec.authorized_amount
		search_lines = self.env['conveyance.reimbursement.lines'].search([('employee','=',employee_rec.id),('year','=',current_year)])
		if search_lines:
			for x in search_lines:
				total_conveyance_applied += x.authorized_amount
		rec['remaining_amount'] = yearly_amount - total_conveyance_applied
		return rec

	@api.multi
	def add_conveyance(self):
		# if self.name:
		# 	self.write({'particulars':self.name.id,'section':self.name.section.id,'description':self.name.description})
		search_monthly_rec = self.env['conveyance.reimbursement.import'].search([('employee','=',self.employee_id.id)])
		if not search_monthly_rec:
			raise ValidationError(_("You are not eligible to add Conveyance!!"))
		if not self.month_sel:
			raise ValidationError(_("Kindly Select Month!"))
		if not self.year.id:
			raise ValidationError(_("Kindly Select Year!"))
		if not self.application_amount:
			raise ValidationError(_("Kindly enter Application Amount!"))
		current_year = None
		get_year = get_current_financial_year(self)
		year = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").year
		month = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").month
		search_year = self.env['year.master'].search([('name','=',str(get_year))])
		if search_year:
			current_year = search_year.id
		if current_year!=self.year.id:
			raise ValidationError(_("You cannot add Conveyance for Previous Year!"))
		search_lines = self.env['conveyance.reimbursement.lines'].search([('employee','=',self.employee_id.id),('month_sel','=',self.month_sel),('year','=',self.year.id)])
		if search_lines:
			raise ValidationError(_("You have already applied for conveyance for the selected Month!"))
		if self.application_amount > self.remaining_amount:
			raise ValidationError(_("Application Amount cannot exceed Balance Amount!"))
		if self.application_amount > self.monthly_amount:
			raise ValidationError(_("Application Amount cannot exceed Monthly Amount!"))
		# if not self.doc_attachment:
		# 	raise ValidationError(_("Kindly attach supporting attachment!"))
		self.write({'record_exists':True})
		self.env['conveyance.reimbursement.lines'].create({
									'employee':self.employee_id.id,
									'conveyance_reimbursement_id':self.id,
									'applied_amount':self.application_amount,
									'authorized_amount':self.application_amount,
									'status':'Pending',
									'month_sel':self.month_sel,
									'year':self.year.id,
									'application_date':datetime.now().date()})
		self.write({'application_amount':0.0})

	@api.multi
	def conveyance_summary(self):
		# if self.name:
		# 	self.write({'particulars':self.name.id,'section':self.name.section.id,'description':self.name.description})
		search_lines = self.env['conveyance.reimbursement.lines'].search([('employee','=',self.employee_id.id),('year','=',self.year.id)])
		print (search_lines,'lllllllll')
		if search_lines:
			for recs in search_lines:
				recs.write({'conveyance_reimbursement_id':self.id})
			self.write({'record_exists':True,'application_amount':0.0})
		else:
			raise ValidationError(_("No data found!!"))


class ConveyanceReimbursementLines(models.Model):
	_name = "conveyance.reimbursement.lines"

	employee = fields.Many2one('hr.employee', 'Employee Name') #,default=_get_employee_id,
	year = fields.Many2one('year.master','Financial Year')
	application_date = fields.Date('Application Date')
	month_sel = fields.Selection([('1','January'),('2','February'),('3','March'),('4','April'),
								('5','May'),('6','June'),('7','July'),('8','August'),
								('9','September'),('10','October'),('11','November'),
								('12','December')], string="Month")
	status = fields.Selection([('Pending','Pending'),('Authorized','Authorized'),('Rejected','Rejected')],string="Status")
	applied_amount = fields.Float('Applied Amount')
	authorized_amount = fields.Float('Authorized Amount')
	doc_attachment = fields.Binary('Attachment',attachment=True)
	# attachments = fields.One2many('ir.attachment', 'att_id',string="Attachments")
	conveyance_reimbursement_id = fields.Many2one('conveyance.reimbursement', 'Conveyance ID')


class ConveyanceReimbursementImport(models.Model):
	_name = "conveyance.reimbursement.import"

	employee = fields.Many2one('hr.employee', 'Employee Name') #,default=_get_employee_id,
	employee_code = fields.Char('Employee Code')
	year_id = fields.Many2one('year.master','Financial Year')
	monthly_conveyance = fields.Float('Monthly Conveyance')
	authorized_amount = fields.Float('Authorized Yearly Amount')


	@api.onchange('employee')
	def onchange_name(self):
		res = {'employee_code':False}
		if not self.employee or not self.employee:
			return
		else:
			self.employee_code = self.employee.emp_code
		return res

	@api.model
	def create(self,vals):
		rem_id =super(ConveyanceReimbursementImport, self).create(vals)
		current_year = None		
		if rem_id:
			emp_code = rem_id.employee_code
			year_id = False
			employee_id=self.env['hr.employee'].search([('emp_code','=',int(emp_code))])
			if employee_id:
				get_year = get_current_financial_year(self)
				year = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").year
				month = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").month
				search_year = self.env['year.master'].search([('name','=',str(get_year))])
				if search_year:
					current_year = search_year.id
				if not search_year:
					raise ValidationError(_("Financial Year not defined in the Year Master!!"))
				rem_id.update({'employee':employee_id.id,'year_id':current_year})
			else:
				raise ValidationError(_("Employee not found for mentioned Employee Code '%s'!")%(rem_id.employee_code))
			return rem_id


class DocumentsMaster(models.Model):
	_name = "documents.master"

	type_of_document = fields.Selection([('policy','Policy Document'),('application','Application Document')])
	name = fields.Char('Description')
	doc_attachment =  fields.Binary('Attachment',attachment=True)

	@api.multi
	def save_document(self):
		# if self.name:
		# 	self.write({'particulars':self.name.id,'section':self.name.section.id,'description':self.name.description})
		if not self.name:
			raise ValidationError(_("Kindly give description!"))
		if not self.type_of_document:
			raise ValidationError(_("Kindly select Type of Document!"))
		if not self.doc_attachment:
			raise ValidationError(_("Kindly attach supporting Document!"))
		if self.type_of_document == 'policy':
			self.env['policy.documents'].create({
									'type_of_document':'policy',
									'name':self.name,
									'doc_attachment':self.doc_attachment
									})
		if self.type_of_document == 'application':
			self.env['application.documents'].create({
									'type_of_document':'application',
									'name':self.name,
									'doc_attachment':self.doc_attachment
									})


class PolicyDocuments(models.Model):
	_name = "policy.documents"

	type_of_document = fields.Selection([('policy','Policy Document'),('application','Application Document')])
	name = fields.Char('Description')
	doc_attachment = fields.Binary('Attachment',attachment=True)


	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(PolicyDocuments, self).fields_view_get(
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



class ApplicationDocuments(models.Model):
	_name = "application.documents"

	type_of_document = fields.Selection([('policy','Policy Document'),('application','Application Document')])
	name = fields.Char('Description')
	doc_attachment = fields.Binary('Attachment',attachment=True)
	

	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(ApplicationDocuments, self).fields_view_get(
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
