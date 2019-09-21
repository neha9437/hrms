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


class EmployeeSalaryStructure(models.Model):
	_name = 'employee.salary.structure'

	name = fields.Char('Employee Name')
	year = fields.Many2one('year.master','Year')
	year_str = fields.Char('Year')
	employee_code = fields.Char('Employee Code')
	current_grade = fields.Char('Current Grade')
	proposed_grade = fields.Char('Proposed Grade')
	employee = fields.Many2one('hr.employee','Employee')
	# final_rating = fields.Float('Rating', compute='calculate_ratings',store=True)
	tl_name = fields.Char('Team Leader Name')
	tl_id = fields.Many2one('hr.employee',string='TL Primary Key')
	department = fields.Many2one('hr.department','Department Primary Key')
	department_name = fields.Char('Department Name')
	designation = fields.Many2one('hr.job',string='Designation Primary Key')
	designation_name = fields.Char('Current Designation Name')
	proposed_designation = fields.Many2one('hr.job',string='Proposed Designation Primary Key')
	proposed_designation_name = fields.Char('Proposed Designation Name')
	site_id = fields.Many2one('site.master','Branch Name')
	old_ctc = fields.Float('Old CTC')
	old_gross_salary = fields.Float('Old Gross Salary')
	proposed_increment = fields.Char('PROPOSED % INCREMENT')
	increment_by_team_leader = fields.Float('Increment by Team Leader %')
	new_gross_salary = fields.Float('New Gross Salary')
	new_monthly_ctc = fields.Float('New Monthly CTC')
	current_basic = fields.Float('Current Basic')
	basic_da = fields.Float('Basic + DA')
	hra = fields.Float('HRA')
	transport_allowance_residence_office = fields.Float('Transport Allowance Residence - Office')
	prof_development = fields.Float('Prof.Development')
	other_allowance = fields.Float('Other Allowance')
	medical_reimbursement = fields.Float('Medical Reimbursement')
	educational_allowance = fields.Float('Educational Allowance')
	advance_bonus_payout = fields.Float('Advance Bonus Payout')
	contribution_towards_nps_us_80ccd = fields.Float('CONTRIBUTION TOWARDS NPS U/S 80CCD(2)')
	news_paper_journal_allowance = fields.Float('NEWS PAPER / JOURNAL ALLOWANCE')
	gadget_for_professional_use = fields.Float('GADGET FOR PROFESSIONAL USE')
	gross_salary = fields.Float('Gross Salary')
	pf = fields.Float('PF')
	esic = fields.Float('ESIC')
	conveyance = fields.Float('Conveyance')
	mobile = fields.Float('Mobile')
	udio = fields.Float('UDIO')
	pli_qbi = fields.Float('PLI / QBI')
	qbi = fields.Float('QBI')
	mediclaim = fields.Float('Mediclaim')
	gratuity = fields.Float('Gratuity')
	monthly_ctc_t = fields.Float('Monthly CTC (T)')
	pt = fields.Float('P.T')
	total_deductions = fields.Float('Total Deductions')
	net_pay = fields.Float('Net Pay')
	salary_with_effect_from = fields.Date('Salary With Effect From')

	_sql_constraints = [
         ('employee_salary_import_id', 'UNIQUE(employee_code, year_str)', 'Salary structure Already Exists for Employee with the mentioned year')
    ]

	@api.model
	def create(self,vals):
		emp_id =super(EmployeeSalaryStructure, self).create(vals)
		emp_name = ''
		if emp_id:
			if not emp_id.employee_code:
				raise ValidationError(_("Kindly give Employee Code!!"))
			if not emp_id.proposed_grade:
				raise ValidationError(_("Kindly give Proposed Grade!!"))
			emp_code = emp_id.employee_code
			if not emp_id.name:
				raise ValidationError(_("Kindly give Employee Name!!"))
				
			if not emp_id.year_str:
				raise ValidationError(_("Kindly sepecify Financial Year in Year Column!!"))
			emp_name = emp_id.name
			year = emp_id.year_str
			year_id = False
			employee_id=self.env['hr.employee'].search([('emp_code','=',int(emp_code))])
			if employee_id:
				search_year = self.env['year.master'].search([('name','=',str(year))])
				if search_year:
					year_id = search_year.id
				if not search_year:
					raise ValidationError(_("Financial Year not defined in the Year Master!!"))
				emp_id.update({'employee':employee_id.id,'name':employee_id.name,'year':year_id})
				print (emp_name,employee_id.name)
				if emp_name not in employee_id.name:
					raise ValidationError(_("Employee not found for mentioned Employee Code '%s'!")%(emp_id.employee_code))
				if not emp_id.salary_with_effect_from:
					raise ValidationError(_("Kindly sepecify salary with Effect from Date!!"))
			else:
				raise ValidationError(_("Employee not found for mentioned Employee Code '%s'!")%(emp_id.employee_code))
			return emp_id

	def print_employee_report_new(self):
		if not self.employee.id:
			raise ValidationError(_("Employee code isn't mapped properly!"))
		return self.env.ref('orient_pms.action_appraisal_form_generate1').report_action(self)


