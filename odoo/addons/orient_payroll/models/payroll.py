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
from dateutil.relativedelta import relativedelta
from lxml import etree
from openerp.osv.orm import setup_modifiers
import csv
import uuid
from odoo.tools import config, human_size, ustr, html_escape
from odoo.tools.mimetypes import guess_mimetype
import logging
import os
import csv
import shutil
from xlrd import open_workbook

class Payroll(models.Model):
	_name = "payroll.payroll"
	_rec_name = "state"


	def _get_default_access_token(self):
		return str(uuid.uuid4())


	state = fields.Selection([('draft','Draft'),('done','Exported')], string="Status", default="draft")
	month = fields.Selection([('jan','January'),('feb','February'),('march','March'),('april','April'),('may','May'),('june','June'),('july','July'),
							  ('august','August'),('september','September'),('october','October'),('november','November'),('december','December')], 
							  string="Month")
	# data_model = fields.Selection([('employee','Employees'),('attendance','Attendances')],string="Model")
	access_token = fields.Char('Security Token', copy=False, default=_get_default_access_token)
	site_ids = fields.Many2many('site.master', 'site_payroll_rel', 'payroll_id', 'site_id', string='Sites')
	# month_ids = fields.One2many('month.month', 'payroll_id', 'Months')


	@api.model_cr_context
	def _init_column(self, column_name):
		""" Initialize the value of the given column for existing rows.

			Overridden here because we need to generate different access tokens
			and by default _init_column calls the default method once and applies
			it for every record.
		"""
		if column_name != 'access_token':
			super(Payroll, self)._init_column(column_name)
		else:
			query = """UPDATE %(table_name)s
						SET %(column_name)s = md5(md5(random()::varchar || id::varchar) || clock_timestamp()::varchar)::uuid::varchar
						WHERE %(column_name)s IS NULL
					""" % {'table_name': self._table, 'column_name': column_name}
			self.env.cr.execute(query)


	def export_data_for_payroll_old(self):
		employee_obj = self.env['hr.employee']
		attendance_obj = self.env['hr.attendance']
		if self.data_model == 'employee':
			emp_codes = [
							7057,
							7062,
							7063,
							7066,
							7068,
							7069,
							7077,
							7138,
							7144,
							7145,
							7188,
							7215,
							7216,
							7217,
							7219,
							7220,
							7225,
							7226,
							7228,
							7229,
							7266,
							7268,
							7275,
							7304,
							7326,
							7327,
							7331,
							7335,
							7338,
							7348,
							7458,
							7461,
							7462,
							7463,
							7464,
							7466,
							7548,
							7550,
							7586,
							7588,
							7708,
							7748,
							7749,
							7796,
							7850,
							7851,
							7853,
							7854,
							7855,
							7913,
							7916,
							7918,
							7969,
							7970,
							7995,
							7996,
							7997,
							8120,
							8251,
							8290,
							8335,
							8381,
							8387,
							8388,
							8389,
							8417,
							8427,
							8499,
							8510,
							8521,
							8539,
							8589,
							8641,
							8666,
							8667,
							8681,
							8727,
							8750,
							8751,
							8771,
							8797,
							8870,
							9089,
							9153,
							9213,
							9214		
						]
			# employee_ids = employee_obj.search([('active','=',True)])
			csvData = []
			ticket_number = 0
			for each_emp_code in emp_codes:
			# for each_emp_id in employee_ids:
				each_emp_dict = {}
				each_emp_data = employee_obj.search([('emp_code', '=', each_emp_code)])
				# each_emp_data = each_emp_id
				ticket_number = ticket_number + 1
				emp_code  = each_emp_data.emp_code if each_emp_data.emp_code else '-'
				title = each_emp_data.title if each_emp_data.title else None
				name = each_emp_data.name if each_emp_data.name else '-'
				if name:
					name_final = name[:40]
				else:
					name_final = '-'
				address = each_emp_data.address if each_emp_data.address else None
				if address:
					address_final = address.replace(',',' ')
					address_final = address_final[:40]
				else:
					address_final = None
				address2 = ''
				address3 = ''
				address4 = ''
				birthday = each_emp_data.birthday if each_emp_data.birthday else '2000-01-01'
				joining_date = each_emp_data.joining_date if each_emp_data.joining_date else '2000-01-01'
				confirmation_date = each_emp_data.confirmation_date if each_emp_data.confirmation_date else None
				gender = each_emp_data.gender if each_emp_data.gender else '-'
				if gender:
					gender_final = gender[:1]
				else:
					gender_final = None
				grade = each_emp_data.grade_id.name if each_emp_data.grade_id else '-'
				if grade:
					grade_final = grade[:20]
				else:
					grade_final = None
				branch_name = each_emp_data.site_master_id.name if each_emp_data.site_master_id else '-'
				if branch_name:
					branch_name_final = branch_name[:20]
				else:
					branch_name_final = '-'
				department = each_emp_data.department_id.name if each_emp_data.department_id else '-'
				if department:
					department_final = department[:35]
				else:
					department_final = '-'
				designation = each_emp_data.job_id.name if each_emp_data.job_id else None
				if designation:
					designation_final = designation[:60]
				else:
					designation_final = None
				division = '-'
				unit = '-'
				emp_category = each_emp_data.emp_category if each_emp_data.emp_category else None
				if emp_category:
					emp_category_final = emp_category[:50]
				else:
					emp_category_final = None
				group_name = each_emp_data.group_id.name if each_emp_data.group_id else None
				if group_name:
					group_name_final = group_name[:50]
				else:
					group_name_final = None
				pf_uan_no = each_emp_data.pf_uan_no if each_emp_data.pf_uan_no else None
				if pf_uan_no:
					pf_uan_no_final = pf_uan_no[:10]
				else:
					pf_uan_no_final = None
				esic_uan_no = each_emp_data.esic_uan_no if each_emp_data.esic_uan_no else None
				if esic_uan_no:
					esic_uan_no_final = esic_uan_no[:10]
				else:
					esic_uan_no_final = None
				pan = each_emp_data.pan if each_emp_data.pan else None
				if pan:
					pan_final = pan[:20]
				else:
					pan_final = None
				bank_account_number = each_emp_data.bank_account_number if each_emp_data.bank_account_number else None
				if bank_account_number:
					bank_account_number_final = bank_account_number[:20]
				else:
					bank_account_number_final = None
				bank_name = each_emp_data.bank_id.name if each_emp_data.bank_id else None
				if bank_name:
					bank_name_final = bank_name[:10]
				else:
					bank_name_final = None
				marital = each_emp_data.marital if each_emp_data.marital else '-'
				if marital:
					marital_final = marital[:1]
				else:
					marital_final = None
				payment_mode = 'bank'
				per_address = each_emp_data.per_address if each_emp_data.per_address else None
				if per_address:
					per_address_final = per_address.replace(',',' ')	
					per_address_final = per_address_final[:40]	
				else:
					per_address_final = None	
				per_address2 = ''
				per_address3 = ''
				per_address4 = ''
				retirement_date = each_emp_data.retirement_date if each_emp_data.retirement_date else None
				work_email = each_emp_data.work_email if each_emp_data.work_email else None
				if work_email:
					work_email_final = work_email[:80]
				else:
					work_email_final = None
				each_emp_dict.update(
					{
						'Ticket No':ticket_number,
						'Employee Code':emp_code,
						'Title':title,
						'Employee Name':name_final,
						'Local Address1':address_final,
						'Local Address2':address2,
						'Local Address3':address3,
						'Local Address4':address4,
						'Date Of Birth':birthday,
						'Date of Joining':joining_date,
						'Date of Confirmation':confirmation_date,
						'Gender':gender_final,
						'Grade':grade_final,
						'Branch':branch_name,
						'Department':department_final,
						'Designation':designation,
						'Division':division,
						'Unit':unit,
						'Category':emp_category,
						'Group':group_name_final,
						'PF No.':pf_uan_no_final,
						'ESIC No.':esic_uan_no_final,
						'Pan No.':pan_final,
						'Bank A/c No':bank_account_number_final,
						'Bank Name':bank_name_final,
						'Marital Status':marital_final,
						'Payment Mode':payment_mode,
						'Permanent Address1':per_address_final,
						'Permanent Address2':per_address2,
						'Permanent Address3':per_address3,
						'Permanent Address4':per_address4,
						'Date of Leaving':retirement_date,
						'Email Address':work_email_final
					})
				csvData.append(each_emp_dict)
			filename = 'hr_employee.csv'
			fully_qualified_filename = os.path.expanduser('~')+"/payroll_export/"+filename
			d = os.path.dirname(os.path.expanduser('~')+"/payroll_export/")
			if not os.path.exists(d):
				os.makedirs(d)
			with open(fully_qualified_filename, 'w+') as csvFile:
					fields = ['Ticket No','Employee Code','Title','Employee Name','Local Address1','Local Address2','Local Address3','Local Address4','Date Of Birth','Date of Joining','Date of Confirmation','Gender','Grade','Branch','Department','Designation','Division','Unit','Category','Group','PF No.','ESIC No.','Pan No.','Bank A/c No','Bank Name','Marital Status','Payment Mode','Permanent Address1','Permanent Address2','Permanent Address3','Permanent Address4','Date of Leaving','Email Address']
					writer = csv.DictWriter(csvFile, fieldnames=fields)
					writer.writeheader()
					writer.writerows(csvData)
			csvFile.close()
			self.write({'state': 'done'})

		elif self.data_model == 'attendance':
			att_emp_ids = []
			csvData = []
			if self.month == 'jan':
				date_min = '2019-01-01'
				date_max = '2019-01-31'
			if self.month == 'feb':
				date_min = '2019-02-01'
				date_max = '2019-02-28'
			if self.month == 'march':
				date_min = '2019-03-01'
				date_max = '2019-03-31'
			if self.month == 'april':
				date_min = '2019-04-01'
				date_max = '2019-04-30'
			if self.month == 'may':
				date_min = '2019-05-01'
				date_max = '2019-05-31'
			if self.month == 'june':
				date_min = '2019-06-01'
				date_max = '2019-06-30'
			if self.month == 'july':
				date_min = '2019-07-01'
				date_max = '2019-07-31'
			if self.month == 'august':
				date_min = '2019-08-01'
				date_max = '2019-08-31'
			if self.month == 'september':
				date_min = '2019-09-01'
				date_max = '2019-09-30'
			if self.month == 'october':
				date_min = '2019-10-01'
				date_max = '2019-10-31'
			if self.month == 'november':
				date_min = '2019-11-01'
				date_max = '2019-11-30'
			if self.month == 'december':
				date_min = '2019-12-01'
				date_max = '2019-12-31'
			# month_attendance_ids = attendance_obj.search([('attendance_date','>=',date_min),('attendance_date','<=',date_max),('employee_code','in',['7046','7047','6517'])])
			month_attendance_ids = attendance_obj.search([('attendance_date','>=',date_min),('attendance_date','<=',date_max)])

			for each_attendance_id in month_attendance_ids:
				att_emp_ids.append(each_attendance_id.employee_id.id)
			employee_ids = list(set(att_emp_ids))
			# attendances of the employee_ids for selected month
			for each_emp_id in employee_ids:
				each_emp_dict = {}
				emp_data = employee_obj.browse(each_emp_id)

				employee_code = emp_data.emp_code if emp_data.emp_code else None
				month = self.month

				emp_p_ids = attendance_obj.search([('employee_id','=',each_emp_id),('attendance_date','>=',date_min),('attendance_date','<=',date_max),'|',('employee_status','=','P'),'|',('employee_status','=','half_day_p_ab'),'|',('employee_status','=','half_day_sl'),('employee_status','=','half_day_pl')])
				worked_days_final = len(emp_p_ids)
	
				emp_pl_ids = attendance_obj.search([('employee_id','=',each_emp_id),('attendance_date','>=',date_min),('attendance_date','<=',date_max),'|',('employee_status','=','PL'),('employee_status','=','half_day_pl')])
				pl_final = len(emp_pl_ids)

				emp_sl_cl_ids = attendance_obj.search([('employee_id','=',each_emp_id),('attendance_date','>=',date_min),('attendance_date','<=',date_max),'|',('employee_status','=','SL/CL'),('employee_status','=','half_day_sl')])
				sl_cl_final = len(emp_sl_cl_ids)
				
				emp_od_ids = attendance_obj.search([('employee_id','=',each_emp_id),('attendance_date','>=',date_min),('attendance_date','<=',date_max),('employee_status','=','OD')])
				od_final = len(emp_od_ids)

				emp_ma_ids = attendance_obj.search([('employee_id','=',each_emp_id),('attendance_date','>=',date_min),('attendance_date','<=',date_max),('employee_status','=','MA')])
				ma_final = len(emp_ma_ids)

				emp_ml_ids = attendance_obj.search([('employee_id','=',each_emp_id),('attendance_date','>=',date_min),('attendance_date','<=',date_max),('employee_status','=','ML')])
				ml_final = len(emp_ml_ids)

				emp_pa_ids = attendance_obj.search([('employee_id','=',each_emp_id),('attendance_date','>=',date_min),('attendance_date','<=',date_max),('employee_status','=','PA')])
				pa_final = len(emp_pa_ids)

				emp_ph_ids = attendance_obj.search([('employee_id','=',each_emp_id),('attendance_date','>=',date_min),('attendance_date','<=',date_max),('employee_status','=','PH')])
				ph_final = len(emp_ph_ids)

				emp_abs_ids = attendance_obj.search([('employee_id','=',each_emp_id),('attendance_date','>=',date_min),('attendance_date','<=',date_max),'|',('employee_status','=','AB'),'|',('employee_status','=','LWP'),('employee_status','=','half_day_p_ab')])
				absent_days = len(emp_abs_ids)

				emp_wo_ids = attendance_obj.search([('employee_id','=',each_emp_id),('attendance_date','>=',date_min),('attendance_date','<=',date_max),'|',('employee_status','=','WO'),('employee_status','=','PH+WO')])
				wo_final = len(emp_wo_ids)

				shift =  emp_data.shift_id.name if emp_data.shift_id else None

				each_emp_dict.update(
					{
						'Employee Code': employee_code,
						'Month': month,
						'Days Present': worked_days_final,
						'Privilege Leaves': pl_final,
						'Sick/Casual Leaves': sl_cl_final,
						'On Duty': od_final,
						'Marriage Leaves': ma_final,
						'Maternity Leaves': ml_final,
						'Paternity Leaves': pa_final,
						'Paid Holidays': ph_final,
						'Absent(Leaves Without Pay)': absent_days,
						'Weekly off': wo_final,
						'Shift': shift
					})
				csvData.append(each_emp_dict)
			filename = 'hr_attendance.csv'
			fully_qualified_filename = os.path.expanduser('~')+"/payroll_export/"+filename
			d = os.path.dirname(os.path.expanduser('~')+"/payroll_export/")
			if not os.path.exists(d):
				os.makedirs(d)
			with open(fully_qualified_filename, 'w+') as csvFile:
				fields = ['Employee Code','Month','Days Present','Privilege Leaves','Sick/Casual Leaves','On Duty','Marriage Leaves','Maternity Leaves','Paternity Leaves','Paid Holidays','Weekly off','Absent(Leaves Without Pay)','Shift']
				writer = csv.DictWriter(csvFile, fieldnames=fields)
				writer.writeheader()
				writer.writerows(csvData)
			csvFile.close()
			self.write({'state': 'done'})


	@api.multi
	def export_data_for_payroll(self,access_uid=None):
		return {
				'type': 'ir.actions.act_url',
				'url': '/web/pivot/payroll_report_xls/%s?access_token=%s' % (self.id, self.access_token),
				'target': 'new',
				}


class Month(models.Model):
	_name = "month.month"

	name = fields.Char('Name')
	# payroll_id = fields.Many2one('payroll.payroll')


class SiteMaster(models.Model):
	_inherit = "site.master"

	payroll_id = fields.Many2one('payroll.payroll')


class ImportSalary(models.Model):
	_name = 'import.salary'
	_description = "Salary Import"


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
			super(ImportSalary, attach.sudo()).write(vals)

	name = fields.Char('Name',default="Import Salary")
	file_url = fields.Char('Url', index=True, size=1024)
	datas_fname = fields.Char('File Name')
	datas = fields.Binary(string='File Content', compute='_compute_datas', inverse='_inverse_datas')
	db_datas = fields.Binary('Database Data')
	state = fields.Selection([('draft', 'Draft'),('done', 'Done'),('failed','Failed')], string='Status', default='draft')
	pay_slip_lines = fields.One2many('pay.slip','pay_slip_id','Pay Slip')
	check_exists = fields.Boolean('Check Exists',default=False)

	@api.multi
	def import_salary(self):
		todays_date = datetime.now()
		append_data=[]
		attendance_date_val =[]
		check_year_id = False
		year = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").year
		month = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").month
		search_year = self.env['year.master.annual'].search([('name','=',str(year))])
		if search_year:
			check_year_id=search_year[0].id
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
					print("row------",row)
					emp_code = int(worksheet.cell(row,2).value)
					print (emp_code)
					if emp_code != '' and emp_code != 'Emp Code':
						emp_name = worksheet.cell(row,3).value
						search_emp = self.env['hr.employee'].search([('emp_code', '=', str(emp_code))])
						month = worksheet.cell(row,1).value
						location = worksheet.cell(row,4).value
						department = worksheet.cell(row,5).value
						cost_center =  worksheet.cell(row,6).value
						bank_account_no = str(worksheet.cell(row,11).value)
						pf_no = worksheet.cell(row,13).value
						esic_no =  worksheet.cell(row,14).value
						present_days = worksheet.cell(row,15).value
						paid_days = worksheet.cell(row,16).value
						pl = worksheet.cell(row,21).value
						basic_da = worksheet.cell(row,23).value
						basic_arrear = worksheet.cell(row,24).value
						hra = worksheet.cell(row,25).value
						hra_arrear = worksheet.cell(row,27).value
						conveyance = worksheet.cell(row,26).value
						prof_development = worksheet.cell(row,28).value
						other_allowance = worksheet.cell(row,29).value
						attire_allowance = worksheet.cell(row,30).value
						medical_allowance = worksheet.cell(row,31).value
						educational_allowance = worksheet.cell(row,32).value
						transport_allowance = worksheet.cell(row,33).value
						mobile_allowance = worksheet.cell(row,34).value
						contribution_towards_nps_us_80ccd = worksheet.cell(row,42).value
						other_earnings = worksheet.cell(row,43).value
						news_paper_journal_allowance = worksheet.cell(row,46).value
						paid_leave_encashment = worksheet.cell(row,47).value
						gadget_for_professional_use = worksheet.cell(row,51).value
						statutory_bonus = worksheet.cell(row,54).value
						pf = worksheet.cell(row,58).value
						pf_arrear = worksheet.cell(row,57).value
						esic = worksheet.cell(row,59).value
						esic_arrear = worksheet.cell(row,56).value
						tds = worksheet.cell(row,63).value
						pt = worksheet.cell(row,61).value
						gross_salary = worksheet.cell(row,70).value
						nps = worksheet.cell(row,67).value
						total_deductions = worksheet.cell(row,68).value
						net_pay = worksheet.cell(row,69).value
						total_earnings = worksheet.cell(row,55).value
						loan = worksheet.cell(row,60).value
						salary_advance = worksheet.cell(row,62).value
						mobile_deduction = worksheet.cell(row,64).value
						other_deductions = worksheet.cell(row,65).value
						check_rec = self.env['pay.slip'].search([('emp_code','=',emp_code),('month_sel','=',month),('year_sel','=',check_year_id)])
						if check_rec:
							for x in check_rec:
								x.unlink()
						if search_emp:
							create_id = self.env['pay.slip'].create(
							{
								'name': str(emp_name),
								'employee_id':search_emp.id,
								'join_date':search_emp.joining_date,
								'uan':search_emp.pf_uan_no if search_emp.pf_uan_no else None,
								'emp_code': str(emp_code),
								'pf_no': str(pf_no),
								'esic_no': str(esic_no),
								'present_days': present_days,
								'paid_days': paid_days,
								'bank_account_no': str(bank_account_no),
								'gross_salary':gross_salary,
								'pl':pl,
								'basic_da':basic_da,
								'basic_arrear':basic_arrear,
								'hra':hra,
								'hra_arrear':hra_arrear,
								'conveyance':conveyance,
								'prof_development':prof_development,
								'other_allowance':other_allowance,
								'attire_allowance':attire_allowance,
								'medical_allowance':medical_allowance,
								'educational_allowance':educational_allowance,
								'transport_allowance':transport_allowance,
								'mobile_allowance':mobile_allowance,
								'contribution_towards_nps_us_80ccd':contribution_towards_nps_us_80ccd,
								'news_paper_journal_allowance':news_paper_journal_allowance,
								'paid_leave_encashment':paid_leave_encashment,
								'gadget_for_professional_use':gadget_for_professional_use,
								'statutory_bonus':statutory_bonus,
								'pf':pf,
								'pf_arrear':pf_arrear,
								'esic':esic,
								'esic_arrear':esic_arrear,
								'tds':tds,
								'pt':pt,
								'total_deductions':total_deductions,
								'net_pay':net_pay,
								'total_earnings':total_earnings,
								'loan':loan,
								'salary_advance':salary_advance,
								'mobile_deduction':mobile_deduction,
								'other_deductions':other_deductions,
								'other_earnings':other_earnings,
								'pay_slip_id':self.id,
								'nps':nps,
							})
							if create_id:
								create_id.write({'employee_id':search_emp.id,'join_date':search_emp.joining_date,'month_sel':month})
				self.write({'check_exists':True})
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

class PaySlip(models.Model):
	_inherit = "pay.slip"

	pay_slip_id = fields.Many2one('import.salary','Import Salary')
	new_gross_salary = fields.Float('New Gross Salary')
	new_monthly_ctc = fields.Float('New Monthly CTC')
	current_basic = fields.Float('Current Basic')
	basic_da = fields.Float('Basic + DA')
	basic_arrear = fields.Float('Basic Arrear')	
	hra = fields.Float('HRA')
	hra_arrear = fields.Float('HRA Arrear')
	transport_allowance = fields.Float('Transport Allowance')
	transport_allowance_arrear = fields.Float('Transport Arrear')
	prof_development = fields.Float('Prof.Development')
	prof_development_arrear = fields.Float('Prof.Development Arrear')
	other_allowance = fields.Float('Other Allowance')
	other_allowance_arrear = fields.Float('Other Allowance Arrear')
	attire_allowance = fields.Float('Attire Allowance')
	attire_allowance_arrear = fields.Float('Attire Allowance Arrear')
	medical_allowance = fields.Float('Medical Allowance')
	medical_allowance_arrear = fields.Float('Medical Allowance Arrear')
	educational_allowance = fields.Float('Educational Allowance')
	educational_allowance_arrear = fields.Float('Educational Allowance Arrear')
	statutory_bonus = fields.Float('Statutory Bonus')
	paid_leave_encashment = fields.Float('Paid Leave Encashment')
	contribution_towards_nps_us_80ccd = fields.Float('CONTRIBUTION TOWARDS NPS U/S 80CCD(2)')
	contribution_towards_nps_us_80ccd_arrear = fields.Float('NPS Arrear')
	other_earnings = fields.Float('Other Earnings')
	news_paper_journal_allowance = fields.Float('NEWS PAPER / JOURNAL ALLOWANCE')
	news_paper_journal_allowance_arrear = fields.Float('NEWS PAPER / JOURNAL ALLOWANCE')
	gadget_for_professional_use = fields.Float('GADGET FOR PROFESSIONAL USE')
	gadget_for_professional_use_arrear = fields.Float('GADGET FOR PROFESSIONAL USE')
	gross_salary = fields.Float('Gross Salary')
	pf = fields.Float('PF')
	pf_arrear = fields.Float('PF Arrear')
	esic = fields.Float('ESIC')
	esic_arrear = fields.Float('ESIC Arrear')
	tds = fields.Float('TDS')
	tds_arrear = fields.Float('TDS Arrear')
	pt = fields.Float('P.T')
	pt_arrear = fields.Float('P.T. Arrear')
	conveyance = fields.Float('Conveyance')
	conveyance_arrear = fields.Float('Conveyance Arrear')
	mobile_allowance = fields.Float('Mobile Allowance')
	mobile_allowance_arrear = fields.Float('Mobile Allowance Arrear')
	udio = fields.Float('UDIO')
	pli_qbi = fields.Float('PLI / QBI')
	qbi = fields.Float('QBI')
	mediclaim = fields.Float('Mediclaim')
	gratuity = fields.Float('Gratuity')
	loan = fields.Float('Loan')
	salary_advance = fields.Float('Salary Advance')
	mobile_deduction = fields.Float('Mobile Deduction')
	other_deductions = fields.Float('Other Deduction')
	total_deductions = fields.Float('Total Deductions')
	net_pay = fields.Float('Net Pay')
	total_earnings = fields.Float('Total Earnings')
	nps = fields.Float('NPS') 
	
class ConveyanceExport(models.Model):
	_name = "conveyance.export"

	def _get_default_access_token(self):
		return str(uuid.uuid4())

	access_token = fields.Char('Security Token', copy=False, default=_get_default_access_token)
	employee_code = fields.Selection([('draft','Draft'),('done','Exported')], string="Status", default="draft")
	employee_id = fields.Selection([('jan','January'),('feb','February'),('march','March'),('april','April'),('may','May'),('june','June'),('july','July'),
							  ('august','August'),('september','September'),('october','October'),('november','November'),('december','December')], 
							  string="Month")
	# data_model = fields.Selection([('employee','Employees'),('attendance','Attendances')],string="Model")
	employee_name = fields.Char('Security Token', copy=False, default=_get_default_access_token)
	employee_grade = fields.Many2many('site.master', 'site_payroll_rel', 'payroll_id', 'site_id', string='Sites')
	doj = fields.Date('DOJ')
	bank_account_number = fields.Char('Account No')
	department = fields.Many2one('hr.department','Department')
	branch_name = fields.Many2one('site.master','Branch Name')
	fixed_conveyance_monthly = fields.Float('Fixed Conveyance Monthly')
	total_conveyance_as_per_doj = fields.Float('Total Conveyance as per DOJ')
	april_conveyance = fields.Float('April')
	may_conveyance = fields.Float('May')
	june_conveyance = fields.Float('June')
	july_conveyance = fields.Float('July')
	august_conveyance = fields.Float('August')
	september_conveyance = fields.Float('September')
	october_conveyance = fields.Float('October')
	november_conveyance = fields.Float('November')
	december_conveyance = fields.Float('December')
	january_conveyance = fields.Float('January')
	february_conveyance = fields.Float('February')
	march_conveyance = fields.Float('March')
	financial_year = fields.Many2one('year.master','Financial Year')

	@api.model_cr_context
	def _init_column(self, column_name):
		""" Initialize the value of the given column for existing rows.

			Overridden here because we need to generate different access tokens
			and by default _init_column calls the default method once and applies
			it for every record.
		"""
		if column_name != 'access_token':
			super(ConveyanceExport, self)._init_column(column_name)
		else:
			query = """UPDATE %(table_name)s
						SET %(column_name)s = md5(md5(random()::varchar || id::varchar) || clock_timestamp()::varchar)::uuid::varchar
						WHERE %(column_name)s IS NULL
					""" % {'table_name': self._table, 'column_name': column_name}
			self.env.cr.execute(query)

	@api.multi
	def generate_xls_conveyance(self,access_uid=None):
		self.ensure_one()
		return {
		'type': 'ir.actions.act_url',
		'url': '/web/pivot/export_conveyance/%s?access_token=%s' % (self.id, self.access_token),
		'target': 'new',
		}


	@api.model
	def default_get(self, fields):
		rec = super(ConveyanceExport, self).default_get(fields)
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
			rec['financial_year']=search_year[0].id
		return rec


