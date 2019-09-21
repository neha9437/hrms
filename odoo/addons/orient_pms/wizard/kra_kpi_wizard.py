# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError, ValidationError

from datetime import datetime

month_sel = (('January', 'January'),('February', 'February'),('March', 'March'),('April', 'April'),('May', 'May'),('June','June'),('July','July'),('August','August'),('September','September'),('October','October'),('November','November'),('December','December'))

First_Quarter = 'April, May, June'
Second_Quarter = 'July, August, September'
Third_Quarter = 'October, November, December'
Fourth_Quarter = 'January, February, March'


class KraKpiWizard(models.TransientModel):

	_name = "kra.kpi.wizard"
	_description = "KRA Wizard"

	month = fields.Selection([('January', 'January'),('February', 'February'),
								('March', 'March'),('April', 'April'),
								('May', 'May'),('June','June'),
								('July','July'),('August','August'),
								('September','September'),('October','October'),
								('November','November'),('December','December')],default='January',string='Month')
	kra_year = fields.Many2one('year.master','Year')	
	quarter = fields.Selection([('First','First Quarter'),('Second','Second Quarter'),('Third','Third Quarter'),('Fourth','Fourth Quarter')],string='Quarter')
	# employee = fields.Many2many('hr.employee','kra_kpi_employee','kra_kpi_id','emp_id',string='Employees')
	employee = fields.Many2one('hr.employee',string="Employee",default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1))
	all_employee = fields.Boolean('All Employees')
	duration = fields.Char('Duration')

	@api.onchange('quarter')
	def onchange_quarter(self):
		quarter = self.quarter
		if quarter == 'First':
			# self.month = 'April'
			self.duration = 'April, May, June'
		if quarter == 'Second':
			# self.month = 'July'
			self.duration = 'July, August, September'
		if quarter == 'Third':
			# self.month = 'October'
			self.duration  = 'October, November, December'
		if quarter == 'Fourth':
			# self.month = 'January'
			self.duration = 'January, February, March'

	@api.model
	def default_get(self, fields):
		rec = super(KraKpiWizard, self).default_get(fields)
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
					rec['month'] = k
					if rec['month'] in ('April','May','June'):
						rec['quarter'] = 'Fourth'
						rec['duration'] = Fourth_Quarter
						financial_start_date = str(start_year-1)+'-04-01'
						financial_end_date = str(end_year-1)+'-03-31'
						search_year = self.env['year.master'].search([('start_date','=',financial_start_date),('end_date','=',financial_end_date)])
						if search_year:
							rec['kra_year']=search_year[0].id
					if rec['month'] in ('July','August','September'):
						rec['quarter'] = 'First'
						rec['duration'] = First_Quarter
					if rec['month'] in ('October','November','December'):
						rec['quarter'] = 'Second'
						rec['duration'] = Second_Quarter
					if rec['month'] in ('January','February','March'):
						rec['quarter'] = 'Third'
						rec['duration'] = Third_Quarter
		return rec

	@api.multi
	def create_kra(self):
		kra_obj = self.env['kra.main']
		kra_master_obj = self.env['kra.master']
		emp_obj = self.env['hr.employee']
		kra_rating_obj = self.env['kra.rating']
		kpi_master_obj = self.env['kpi.master']
		emp_kra_kpi = self.env['employee.kra.kpi']
		quarterly_meeting_obj = self.env['quarterly.meeting']
		sr_no_list = [1,2,3,4,5,6]
		kra_month = ''
		agenda_item = ['MINUTES/ ACTIONS FROM PREVIOUS MEETING',
					'CURRENT CHALLENGES FACED',
					'TRAINING REQUIREMENT?',
					'ANY ESCALATIONS FROM TEAM/CLIENT/OTHER',
					'APPRECIATION RECEIVED FROM TEAM/CLIENT/OTHER?',
					"TL'S CONCERNS"]
		for record in self:
			joining_date = record.employee.joining_date
			# if record.employee.cost_center_id.name=='ITES - FMS/PS' and record.employee.department_id.name not in ('FM','FM Backup'):
			# 	raise ValidationError(_("Access Denied!!"))
			if not record.kra_year.id:
				raise ValidationError(_("Kindly select Year!"))
			if not record.quarter:
				raise ValidationError(_("Kindly select Quarter!"))
			for kra_id in record.employee:
				check_previous_record = self.env['kra.main'].search([('employee','=',kra_id.id),('quarter','!=',record.quarter),('state','=','pending')])
				if check_previous_record:
					raise ValidationError(_("Your Previous Quarter Review is pending, kindly process it and get approved!!")) #%(kra_id.name,record.quarter)	
				check_record = self.env['kra.main'].search([('employee','=',kra_id.id),('kra_year','=',record.kra_year.id),('quarter','=',record.quarter),('state','!=','cancel')])
				if check_record:
					raise ValidationError(_("Quarterly Review form has been already created for %s for %s quarter!!")%(kra_id.name,record.quarter))
				else:
					start_date = record.kra_year.start_date
					end_date = record.kra_year.end_date
					split_date = record.kra_year.start_date.split('-')
					print (split_date[:4])
					review_start = ''
					review_end = ''
					if record.quarter=='First':
						review_start = split_date[0] +'-04-01'
						review_end = split_date[0] +'-06-30'
						kra_month = 'April'
					if record.quarter=='Second':						
						review_start = split_date[0] +'-07-01'
						review_end = split_date[0] +'-09-30'
						kra_month = 'July'
					if record.quarter=='Third':
						review_start = split_date[0] +'-10-01'
						review_end = split_date[0] +'-12-31'
						kra_month = 'October'
					if record.quarter=='Fourth':
						review_start = str(int(split_date[0])+1) +'-01-01'
						review_end = str(int(split_date[0])+1) +'-03-31'
						kra_month = 'January'
					if str(review_end) < str(joining_date):
						raise ValidationError(_("You are not eligible to create Quarterly Review form for selected Quarter!!"))
					kra_ids = emp_obj.browse(kra_id.kra_one2many)
					calculate_weightage = 0.0
					if kra_ids:
						for kra in kra_ids:
							calculate_weightage+=float(kra.id.weightage)
					if calculate_weightage!=100:
						raise ValidationError(_("Your KRA/KPI's total weightage is not 100. Kindly contact HR Department!!"))
					emp_kra = kra_obj.create({
					'employee':kra_id.id,
					'company_id':kra_id.company_id.id,
					'employee_code':kra_id.emp_code,
					'designation':kra_id.job_id.id,
					'department':kra_id.department_id.id,
					'location':kra_id.company_id.id,
					'kra_month':kra_month,
					'kra_year':record.kra_year.id,
					'quarter':record.quarter,
					'active':False,
					'review_start_date':review_start,
					'review_end_date':review_end,
					'check1': False,
					'application_date': str(datetime.now().date())							
					})
					kra_ids = emp_obj.browse(kra_id.kra_one2many)
					count=1
					kpi_ids=[]
					if kra_ids:
						for kra in kra_ids:
							if kra.id.name!='':
								create_id = kra_rating_obj.create({
									'sr_no':str(count),
									'kra':kra.id.kra_master_id.id,
									'kra_name':kra.id.name,
									'description':kra.id.kpi,
									'weightage':kra.id.weightage,
									'kra_id':kra_obj.browse(emp_kra.id).id,
									'check1':False,
									})
								count+=1
							else:
								create_id = kra_rating_obj.create({
									'sr_no':'',	
									'kra':kra.id.kra_master_id.id,
									'kra_name':kra.id.name,
									'description':kra.id.kpi,
									'weightage':kra.id.weightage,
									'kra_id':kra_obj.browse(emp_kra.id).id,
									'check1':False,
									})
						for x,y in zip(sr_no_list,agenda_item):
							quarterly_meeting_obj.create({
								'quarterly_meeting_id':kra_obj.browse(emp_kra.id).id,
								'sr_no':x,
								'agenda_item':y,
								'check1':True,
								})

						kra_form = self.env.ref('orient_pms.view_kramain_form', False)
						return {
							'name': _('Quarterly KRA Review'),
							'type': 'ir.actions.act_window',
							'view_type': 'form',
							'view_mode': 'form',
							'res_model': 'kra.main',
							'res_id': emp_kra.id,
							'views': [(kra_form.id, 'form')],
							'view_id': emp_kra.id,
							'target': 'new',
						}

					else:
						raise ValidationError(_("KRA/KPI's has not been mapped for %s!!")%(kra_id.name))
		# return True
		

class AnnualKraWizard(models.TransientModel):

	_name = "annual.kra.wizard"
	_description = "Annual KRA Wizard"

	# month = fields.Selection([('January', 'January'),('February', 'February'),
	# 							('March', 'March'),('April', 'April'),
	# 							('May', 'May'),('June','June'),
	# 							('July','July'),('August','August'),
	# 							('September','September'),('October','October'),
	# 							('November','November'),('December','December')],default='January',string='Month')
	kra_year = fields.Many2one('year.master','Year')	
	# quarter = fields.Selection([('First','First Quarter'),('Second','Second Quarter'),('Third','Third Quarter'),('Fourth','Fourth Quarter')],string='Quarter')
	# employee = fields.Many2many('hr.employee','kra_kpi_employee','kra_kpi_id','emp_id',string='Employees')
	employee = fields.Many2one('hr.employee',string="Employee",default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1))
	# all_employee = fields.Boolean('All Employees')
	# duration = fields.Char('Duration')

	@api.model
	def default_get(self, fields):
		rec = super(AnnualKraWizard, self).default_get(fields)
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
		return rec