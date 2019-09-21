# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo import SUPERUSER_ID
from odoo.exceptions import UserError, AccessError, ValidationError
import datetime
from datetime import datetime, timedelta
from dateutil import *
from dateutil.relativedelta import relativedelta
from odoo.tools import float_compare
import logging
import math
from odoo.tools.translate import _
from odoo.modules.module import get_module_resource
from dateutil.rrule import rrule, DAILY
import calendar
from collections import OrderedDict

_logger = logging.getLogger(__name__)


class SiteMaster(models.Model):
	_inherit = "site.master"

	holiday_ids = fields.Many2many('holiday.master', 'site_holiday_rel', 'site_id', 'holiday_id', string='Holidays', track_visibility='onchange')
	holiday_old_ids = fields.Many2many('holiday.master', 'site_holiday_old_rel', 'site_old_id', 'holiday_old_id', string='Holidays')
	weekoffs = fields.Selection([('2_4', 'Second & Forth Saturday Off'),('1_3_5', 'First, Third & Fifth Saturday Off'),('all', 'All Saturdays Off'),('no','No Saturdays Off'),('saturday_weekoff','Only Saturdays off')], string='Saturday Weekoffs',default='all')
	# employee_ids = fields.One2many('hr.employee', 'site_master_id', string='Employees', help="Employees belonging to this site")
	existing_holidays = fields.Char('Existing Holidays')
	site_location_master_ids = fields.One2many('site.location.master','site_master_id', 'Site Locations')
	is_a_branch = fields.Boolean(default=False,string='Is a Branch?')
	flexishift = fields.Boolean(default=False,string='Flexishift?')


	# @api.model
	# def create(self, vals):
	# 	if vals.get('holiday_ids'):
	# 		holiday_ids = vals['holiday_ids'][0][2]
	# 		new_each_holiday_ids = ''
	# 		for each_holiday_id in holiday_ids:
	# 			if new_each_holiday_ids:
	# 				new_each_holiday_ids = new_each_holiday_ids+','+str(each_holiday_id)
	# 			else:
	# 				new_each_holiday_ids = str(each_holiday_id)
	# 		vals.update({'existing_holidays':str(new_each_holiday_ids)})
	# 	site = super(SiteMaster, self).create(vals)
	# 	return site


	effective_from = fields.Date('Effective From Date')
	effective_to = fields.Date('Effective To Date')


	# @api.multi
	# def write(self, vals):
	# 	site = super(SiteMaster, self).write(vals)
	# 	attendance_obj = self.env['hr.attendance']
	# 	employee_obj = self.env['hr.employee']
	# 	holiday_obj = self.env['holiday.master']
	# 	# get the employees of site locations first
	# 	site_location_employees = []
	# 	if self.site_location_master_ids:
	# 		for each_line in self.site_location_master_ids:
	# 			for employee_id in each_line.employee_ids:
	# 				site_location_employees.append(employee_id.id)
	# 	site_location_employees = list(set(site_location_employees))
	# 	print("site_location_employees",site_location_employees)
	# 	print("vals",vals)
	# 	if vals.get('holiday_ids'):
	# 		# to update holidays in employee with every change in holidays of a site
	# 		holiday_ids = vals['holiday_ids'][0][2]
	# 		site_emp_ids = employee_obj.search([('site_master_id','=',self.id)])
	# 		print("site_emp_ids",site_emp_ids)
	# 		for each_site_emp_id in site_emp_ids:
	# 			#if this employee belongs to site location igore him
	# 			if each_site_emp_id.id in site_location_employees:
	# 				print("passssssssssssss")
	# 				pass
	# 			else:
	# 				print("updatingggggggggggg")
	# 				each_site_emp_id.write({'holiday_ids':[(6,0,holiday_ids)]})
	# 		# to delete the attendance if holidays from site are removed
	# 		li_existing_holidays = []
	# 		if self.existing_holidays:
	# 			for each_existing_holiday in self.existing_holidays.split(','):
	# 					li_existing_holidays.append(int(each_existing_holiday))
	# 		deleted_holiday_ids = list(set(li_existing_holidays) - set(holiday_ids))
	# 		if deleted_holiday_ids:
	# 			for each_deleted_holiday_id in deleted_holiday_ids:
	# 				holiday_data = holiday_obj.browse(each_deleted_holiday_id)
	# 				site_emply_ids = employee_obj.search([('site_master_id','=',self.id)])
	# 				if site_emply_ids:
	# 					for each_site_emply_id in site_emply_ids:
	# 						print("each_site_emply_id",each_site_emply_id)
	# 						if each_site_emply_id.id in site_location_employees:
	# 							pass
	# 						else:
	# 							existing_attendance_id = attendance_obj.search([('employee_id','=',each_site_emply_id.id),('attendance_date','=',holiday_data.holiday_date),('employee_status','=','PH')])
	# 							if existing_attendance_id:
	# 								existing_attendance_id.write({'employee_status': 'AB'})

	# 		# to update attendance with every change in holidays of a site
	# 		new_each_holiday_ids = ''
	# 		for each_holiday_id in holiday_ids:
	# 			holiday_master = holiday_obj.browse(each_holiday_id)
	# 			site_empl_ids = employee_obj.search([('site_master_id','=',self.id)])
	# 			for site_empl_id in site_empl_ids:
	# 				#if this employee belongs to site location igore him
	# 				if each_site_emp_id.id in site_location_employees:
	# 					pass
	# 				else:
	# 					existing_ph_id = attendance_obj.search([('employee_id','=',site_empl_id.id),('attendance_date','=',holiday_master.holiday_date)])
	# 					if existing_ph_id:
	# 						if len(existing_ph_id)>1:
	# 							for recs in existing_ph_id:
	# 								if recs.employee_status == 'AB' or recs.employee_status ==False or recs.employee_status==' ' or recs.employee_status=='':
	# 									# self.env.cr.execute('update hr_attendance set employee_status=%s where id=%s',('PH',recs.id))
	# 									recs.write({'employee_status':'PH'})
	# 						else:
	# 							if existing_ph_id.employee_status == 'AB' or existing_ph_id.employee_status == None or existing_ph_id.employee_status ==False or existing_ph_id.employee_status==' ' or existing_ph_id.employee_status=='':
	# 								# self.env.cr.execute('update hr_attendance set employee_status=%s where id=%s',('PH',recs.id))
	# 								existing_ph_id.write({'employee_status':'PH'})
	# 					else:
	# 						attendance_obj.create(
	# 							{
	# 								'employee_id':site_empl_id.id,
	# 								'employee_code':site_empl_id.emp_code,
	# 								'attendance_date':holiday_master.holiday_date,
	# 								'department_id_val':site_empl_id.department_id.id,
	# 								'employee_status':'PH',
	# 								'site_master_id':self.id,
	# 								'shift':site_empl_id.shift_id.id,
	# 								'state':'draft',
	# 								'created':True
	# 								# 'check_in':leave_datetime,
	# 								# 'check_out':leave_datetime,
	# 								# 'state':
	# 							})
	# 				if new_each_holiday_ids:
	# 					new_each_holiday_ids = new_each_holiday_ids+','+str(each_holiday_id)
	# 				else:
	# 					new_each_holiday_ids = str(each_holiday_id)
	# 		self.write({'existing_holidays': str(new_each_holiday_ids)})
	# 	return site


	@api.multi
	def assign_public_holidays(self):
		attendance_obj = self.env['hr.attendance']
		employee_obj = self.env['hr.employee']
		holiday_obj = self.env['holiday.master']
		holidays = []
		deleted_hol_ids = []
		# find out employees belonging to site locations first
		site_location_employees = []
		if self.site_location_master_ids:
			for each_line in self.site_location_master_ids:
				for employee_id in each_line.employee_ids:
					site_location_employees.append(employee_id.id)
		site_location_employees = list(set(site_location_employees))
		# find out employees of current site
		site_empl_ids = employee_obj.search([('site_master_id','=',self.id)])
		# find out deleted holidays
		if self.holiday_old_ids:
			holids = set(self.holiday_ids.ids)
			hololdids = set(self.holiday_old_ids.ids)
			deleted_hol_ids = list(hololdids-holids)	
		# if there are holidays to assign
		if self.holiday_ids:
			# iterate current site employees
			for site_empl_id in site_empl_ids:
				# check if current site employee is already in the site location list
				# if yes, ignore that employee. 
				if site_empl_id.id in site_location_employees:
					pass
				# if not find the attendance record 
				else:
					# if holidays are deleted, update the emp attendances of these holidays as AB
					if deleted_hol_ids:
						for each_deleted_hol_id in deleted_hol_ids:
							each_deleted_hol_id = holiday_obj.browse(each_deleted_hol_id)
							delhol_attendance_ids = attendance_obj.search([('employee_id','=',site_empl_id.id),('attendance_date','=',each_deleted_hol_id.holiday_date)])
							for delhol_attendance_id in delhol_attendance_ids:
								delhol_attendance_id.write({'employee_status':'AB'})	
					# iterate holidays
					for each_holiday_id in self.holiday_ids:
						holidays.append(each_holiday_id.id)
						# find attendance records
						existing_att_ids = attendance_obj.search([('employee_id','=',site_empl_id.id),('attendance_date','=',each_holiday_id.holiday_date)])
						if existing_att_ids:
							# if there is attendance record, update it with PH only if its AB or blank
							for existing_att_id in existing_att_ids:
								if existing_att_id.employee_status == 'AB' or existing_att_id.employee_status == None or existing_att_id.employee_status ==False or existing_att_id.employee_status==' ' or existing_att_id.employee_status=='':
									existing_att_id.write({'employee_status':'PH'})
						else:
							# if there is no attendance record, create one
							attendance_obj.create(
								{
									'employee_id':site_empl_id.id,
									'employee_code':site_empl_id.emp_code,
									'attendance_date':each_holiday_id.holiday_date,
									'department_id_val':site_empl_id.department_id.id,
									'site_master_id':self.id,
									'shift':site_empl_id.shift_id.id,
									'employee_status':'PH',
									'state':'draft',
									'created':True
								})
					# update holidays in employee profiles
					site_empl_id.write({'holiday_ids':[(6,0,holidays)]})
			# store holidays to old_holidays to figure out deleted holidays
			old_holidays = []
			if self.holiday_ids:
				for each_old_holiday in self.holiday_ids:
					old_holidays.append(each_old_holiday.id)
				self.write({'holiday_old_ids':[(6,0,old_holidays)]})
		# if not holidays assigned give access error
		else:
			raise AccessError("Nothing to assign!")


	@api.multi
	def assign_site_location_holidays(self):
		attendance_obj = self.env['hr.attendance']
		employee_obj = self.env['hr.employee']
		holiday_obj = self.env['holiday.master']
		site_loc_emp_ids = []
		site_holiday_ids = []
		deleted_emp_ids = []
		deleted_hol_ids = []
		
		for each_site_holiday_id in self.holiday_ids:
			site_holiday_ids.append(each_site_holiday_id.id)

		for line1 in self.site_location_master_ids:
			for curr_emp_id in line1.employee_ids:
				site_loc_emp_ids.append(curr_emp_id.id)

		if site_loc_emp_ids and site_holiday_ids:
			for each_site_emp_id in site_loc_emp_ids:
				each_site_emp_id = employee_obj.browse(each_site_emp_id)
				each_site_emp_id.write({'holiday_ids':[(6,0,[])]})
				for each_site_holiday_id in site_holiday_ids:
					each_site_holiday_id = holiday_obj.browse(each_site_holiday_id)
					att_id = attendance_obj.search([('employee_id','=',each_site_emp_id.id),('attendance_date','=',each_site_holiday_id.holiday_date)])
					if att_id:
						att_id.write({'employee_status':'AB'})
		self.env.cr.commit()

		if self.site_location_master_ids:
			# update the deleted employees or holidays with AB
			# iterate over site_location_master_ids
			for line in self.site_location_master_ids:
				# if there are values in employee_old_ids, find out deleted employees
				if line.employee_old_ids:
					empids = set(line.employee_ids.ids)
					empoldids = set(line.employee_old_ids.ids)
					deleted_emp_ids = list(empoldids-empids)
				# if there are values in employee_old_ids, find out deleted holidays
				if line.holiday_old_ids:
					holids = set(line.holiday_ids.ids)
					hololdids = set(line.holiday_old_ids.ids)
					deleted_hol_ids = list(hololdids-holids)
				# if only employees are deleted, update the emp attendances with allocated holidays as AB
				if deleted_emp_ids and not deleted_hol_ids:
					for each_deleted_emp_id in deleted_emp_ids:
						each_deleted_emp_id = employee_obj.browse(each_deleted_emp_id)
						for holiday_id in line.holiday_ids:
							attendance_ids1 = attendance_obj.search([('employee_id','=',each_deleted_emp_id.id),('attendance_date','=',holiday_id.holiday_date)])
							for attendance_id1 in attendance_ids1:
								attendance_id1.write({'employee_status':'AB'})
				# if only holidays are deleted, update the emp attendances with deleted holidays as AB
				if deleted_hol_ids and not deleted_emp_ids:
					for each_deleted_hol_id in deleted_hol_ids:
						each_deleted_hol_id = holiday_obj.browse(each_deleted_hol_id)
						for emp_id in line.employee_ids:
							attendance_ids2 = attendance_obj.search([('employee_id','=',emp_id.id),('attendance_date','=',each_deleted_hol_id.holiday_date)])
							for attendance_id2 in attendance_ids2:
								attendance_id2.write({'employee_status':'AB'})
				# if both employees and holidays are deleted, update the deleted emp attendances with allocated holidays as AB
				if deleted_emp_ids and deleted_hol_ids:
					for each_deleted_emp_id in deleted_emp_ids:
						each_deleted_emp_id = employee_obj.browse(each_deleted_emp_id)
						for holiday_id in line.holiday_ids:
							attendance_ids3 = attendance_obj.search([('employee_id','=',each_deleted_emp_id.id),('attendance_date','=',holiday_id.holiday_date)])
							for attendance_id in attendance_ids:
								attendance_id3.write({'employee_status':'AB'})
				# assigning the site holidays to deleted employees
				if deleted_emp_ids:
					for each_deleted_emp_id in deleted_emp_ids:
						each_deleted_emp_id = employee_obj.browse(each_deleted_emp_id)
						each_deleted_emp_id.write({'holiday_ids':[(6,0,site_holiday_ids)]})
			self.env.cr.commit()
			# create or update attendance entries with PH
			# iterate over site_location_master_ids
			for line2 in self.site_location_master_ids:
				to_append = [] # list to store the holidays those are to be updated on employee profile
				holidays_to_compare = [] # list to store holidays to find out deleted holidays
				emp_to_compare = [] # list to store epmloyees to find out deleted employees
				for each_to_append in line2.holiday_ids:
					to_append.append(each_to_append.id)
					holidays_to_compare.append(each_to_append.id)
				for employee_id2 in line2.employee_ids:
					emp_to_compare.append(employee_id2.id)
					for holiday_id2 in line2.holiday_ids:
						attendance_id4 = attendance_obj.search([('employee_id','=',employee_id2.id),('attendance_date','=',holiday_id2.holiday_date)])
						if attendance_id4:
							attendance_id4.write({'employee_status':'PH'})
						else:
							attendance_vals = {
												'employee_id':employee_id2.id,
												'employee_code':employee_id2.emp_code,
												'attendance_date':holiday_id2.holiday_date,
												'department_id_val':employee_id2.department_id.id,
												'site_master_id':employee_id2.site_master_id.id,
												'shift':employee_id2.shift_id.id,
												'employee_status':'PH',
												'state':'draft',
												'created': True
												# 'worked_hours':,
												# 'check_in':,
												# 'check_out':,
												# 'in_time':,
												# 'out_time':,
												# 'in_time_updation':,
												# 'out_time_updation':,
												# 'early_leaving':,
												# 'late_coming':,
												# 'import_status':
												# 'reason':
												# 'approve_check':
												# 'remarks':,
											}
							create_id = attendance_obj.create(attendance_vals)
					employee_id2.write({'holiday_ids':[(6,0,to_append)]})
				line2.write({'employee_old_ids':[(6,0,emp_to_compare)]})
				line2.write({'holiday_old_ids':[(6,0,holidays_to_compare)]})
		else:
			raise AccessError("Nothing to assign!")
		return True



	@api.multi
	def assign_weekoffs(self):
		from_date = self.effective_from
		to_date = self.effective_to
		start_date = datetime.strptime(from_date, "%Y-%m-%d").date()
		end_date = datetime.strptime(to_date, "%Y-%m-%d").date()
		delta1 = end_date - start_date
		emp_recs = self.env['hr.employee'].search([('site_master_id','=',self.id)])
		sat_list = []
		sun_list = []
		weekoffs = self.weekoffs
		result = []
		first_list = []
		second_list = []
		third_list = []
		fourth_list = []
		fifth_list = []
		fifth_saturday = ''
		dates = [from_date,to_date]
		start, end = [datetime.strptime(_, "%Y-%m-%d") for _ in dates]
		date_range = list(OrderedDict(((start + timedelta(_)).strftime(r"%m-%Y"), None) for _ in range((end - start).days)).keys())
		for search_employee_id in emp_recs:
			emp_code = search_employee_id.emp_code
			department_id = search_employee_id.department_id.id
			parent_id = search_employee_id.parent_id.id
			if not parent_id:
				parent_id = None
			if not department_id:
				department_id=None

			employee_id = search_employee_id.id

			shift = search_employee_id.shift_id.name if search_employee_id.shift_id.name else ''
			shift_id = search_employee_id.shift_id.id if search_employee_id.shift_id.id else None

			site_master_id = self.id

			for i in range(delta1.days + 1):
				dates = start_date + timedelta(i)
				day_name = calendar.day_name[dates.weekday()]

				if day_name == 'Saturday':
					sat_list.append(dates)
					weekend = True
				else:
					weekend = False
				if day_name == 'Sunday':
					sun_list.append(dates)
			blank = ''
			for sat in list(set(sat_list)):
				self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s', (blank,datetime.strptime(str(sat), "%Y-%m-%d").date(),employee_id))
			for y in date_range:
				split_range = y.split('-')
				c = calendar.Calendar(firstweekday=calendar.SUNDAY)
				monthcal = c.monthdatescalendar(int(split_range[1]),int(split_range[0]))
				second_saturday = [day for week in monthcal for day in week if day.weekday() == calendar.SATURDAY and day.month == int(split_range[0])][1]
				fourth_saturday = [day for week in monthcal for day in week if day.weekday() == calendar.SATURDAY and day.month == int(split_range[0])][3]
				first_saturday = [day for week in monthcal for day in week if day.weekday() == calendar.SATURDAY and day.month == int(split_range[0])][0]
				third_saturday = [day for week in monthcal for day in week if day.weekday() == calendar.SATURDAY and day.month == int(split_range[0])][2]
				if first_saturday in sat_list:
					if first_saturday not in first_list:
						first_list.append(first_saturday)
				if third_saturday in sat_list:
					if third_saturday not in third_list:
						third_list.append(third_saturday)
				ix = [day for week in monthcal for day in week if day.weekday() == calendar.SATURDAY and day.month == int(split_range[0])]
				if len(ix) > 4:
					fifth_saturday = [day for week in monthcal for day in week if day.weekday() == calendar.SATURDAY and day.month == int(split_range[0])][4]
					if fifth_saturday in sat_list:
						if fifth_saturday not in fifth_list:
							fifth_list.append(fifth_saturday)
				if second_saturday in sat_list:
					if second_saturday not in second_list:
						second_list.append(second_saturday)
				if fourth_saturday in sat_list:
					if fourth_saturday not in fourth_list:
						fourth_list.append(fourth_saturday)
			if weekoffs == '2_4':
				for x in first_list:
					holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
					if holiday_rec:
						site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
						if result:
							for site in result:
								if site[0] == site_master_id:									
									employee_status = 'PH'
									search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
									if search_attendance:
										if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
											worked_hours=search_attendance.worked_hours
											day = x.strftime('%A')
											if day in ('Saturday','Sunday'):
												if worked_hours >=3.5:
													employee_status = 'P'
												if worked_hours < 3.5:
													employee_status = 'AB'
											elif day not in ('Saturday','Sunday'):
												if worked_hours > 6.5:
													employee_status = 'P'
												elif worked_hours >=4.5 and worked_hours <= 6.5:
													employee_status = 'half_day_p_ab'
												else:
													employee_status = 'AB'
											self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
											self.env.cr.commit()
										else:
											self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
											self.env.cr.commit()
				for x in third_list:
					holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
					if holiday_rec:
						site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
						result = self.env.cr.fetchall()
						if result:
							for site in result:
								if site[0] == site_master_id:									
									employee_status = 'PH'
									search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
									if search_attendance:
										if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
											worked_hours=search_attendance.worked_hours
											day = x.strftime('%A')
											if day in ('Saturday','Sunday'):
												if worked_hours >=3.5:
													employee_status = 'P'
												if worked_hours < 3.5:
													employee_status = 'AB'
											elif day not in ('Saturday','Sunday'):
												if worked_hours > 6.5:
													employee_status = 'P'
												elif worked_hours >=4.5 and worked_hours <= 6.5:
													employee_status = 'half_day_p_ab'
												else:
													employee_status = 'AB'
											self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
											self.env.cr.commit()
										else:
											self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
											self.env.cr.commit()
				for x in fifth_list:
					holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
					if holiday_rec:
						site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
						result = self.env.cr.fetchall()
						if result:
							for site in result:
								if site[0] == site_master_id:
									employee_status = 'PH'
									search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
									if search_attendance:
										if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
											worked_hours=search_attendance.worked_hours
											day = x.strftime('%A')
											if day in ('Saturday','Sunday'):
												if worked_hours >=3.5:
													employee_status = 'P'
												if worked_hours < 3.5:
													employee_status = 'AB'
											elif day not in ('Saturday','Sunday'):
												if worked_hours > 6.5:
													employee_status = 'P'
												elif worked_hours >=4.5 and worked_hours <= 6.5:
													employee_status = 'half_day_p_ab'
												else:
													employee_status = 'AB'
											self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
											self.env.cr.commit()
										else:
											self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
											self.env.cr.commit()
				for x in second_list:
					employee_status = 'WO'
					holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
					if holiday_rec:
						site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
						result = self.env.cr.fetchall()
						if result:
							for site in result:
								if site[0] == site_master_id:									
									employee_status = 'PH+WO'
									search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
									if search_attendance:
										if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
											worked_hours=search_attendance.worked_hours
											day = x.strftime('%A')
											if day in ('Saturday','Sunday'):
												if worked_hours >=3.5:
													employee_status = 'P'
												if worked_hours < 3.5:
													employee_status = 'AB'
											elif day not in ('Saturday','Sunday'):
												if worked_hours > 6.5:
													employee_status = 'P'
												elif worked_hours >=4.5 and worked_hours <= 6.5:
													employee_status = 'half_day_p_ab'
												else:
													employee_status = 'AB'
											self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
											self.env.cr.commit()
										else:
											self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
											self.env.cr.commit()
									else:
										employee_status = 'PH'
										search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
										if search_attendance:
											if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
												worked_hours=search_attendance.worked_hours
												day = x.strftime('%A')
												if day in ('Saturday','Sunday'):
													if worked_hours >=3.5:
														employee_status = 'P'
													if worked_hours < 3.5:
														employee_status = 'AB'
												elif day not in ('Saturday','Sunday'):
													if worked_hours > 6.5:
														employee_status = 'P'
													elif worked_hours >=4.5 and worked_hours <= 6.5:
														employee_status = 'half_day_p_ab'
													else:
														employee_status = 'AB'
												self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
												self.env.cr.commit()
											else:
												self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
												self.env.cr.commit()
						else:
							employee_status = 'WO'
							search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
							if search_attendance:
								if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
									worked_hours=search_attendance.worked_hours
									day = x.strftime('%A')
									if day in ('Saturday','Sunday'):
										if worked_hours >=3.5:
											employee_status = 'P'
										if worked_hours < 3.5:
											employee_status = 'AB'
									elif day not in ('Saturday','Sunday'):
										if worked_hours > 6.5:
											employee_status = 'P'
										elif worked_hours >=4.5 and worked_hours <= 6.5:
											employee_status = 'half_day_p_ab'
										else:
											employee_status = 'AB'
									self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
									self.env.cr.commit()
								else:
									self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
									self.env.cr.commit()
					else:
						employee_status = 'WO'
						search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
						if search_attendance:
							if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
								worked_hours=search_attendance.worked_hours
								day = x.strftime('%A')
								if day in ('Saturday','Sunday'):
									if worked_hours >=3.5:
										employee_status = 'P'
									if worked_hours < 3.5:
										employee_status = 'AB'
								elif day not in ('Saturday','Sunday'):
									if worked_hours > 6.5:
										employee_status = 'P'
									elif worked_hours >=4.5 and worked_hours <= 6.5:
										employee_status = 'half_day_p_ab'
									else:
										employee_status = 'AB'
								self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
								self.env.cr.commit()
							else:	
								self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
								self.env.cr.commit()
				for x in fourth_list:
					employee_status = 'WO'
					holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
					if holiday_rec:
						site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
						result = self.env.cr.fetchall()
						if result:
							for site in result:
								if site[0] == site_master_id:									
									employee_status = 'PH+WO'
									search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
									if search_attendance:
										if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
											worked_hours=search_attendance.worked_hours
											day = x.strftime('%A')
											if day in ('Saturday','Sunday'):
												if worked_hours >=3.5:
													employee_status = 'P'
												if worked_hours < 3.5:
													employee_status = 'AB'
											elif day not in ('Saturday','Sunday'):
												if worked_hours > 6.5:
													employee_status = 'P'
												elif worked_hours >=4.5 and worked_hours <= 6.5:
													employee_status = 'half_day_p_ab'
												else:
													employee_status = 'AB'
											self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
											self.env.cr.commit()
										else:
											self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
											self.env.cr.commit()
									else:
										employee_status = 'PH'
										search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
										if search_attendance:
											self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
											self.env.cr.commit()
						else:
							employee_status = 'WO'
							search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
							if search_attendance:
								if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
									worked_hours=search_attendance.worked_hours
									day = x.strftime('%A')
									if day in ('Saturday','Sunday'):
										if worked_hours >=3.5:
											employee_status = 'P'
										if worked_hours < 3.5:
											employee_status = 'AB'
									elif day not in ('Saturday','Sunday'):
										if worked_hours > 6.5:
											employee_status = 'P'
										elif worked_hours >=4.5 and worked_hours <= 6.5:
											employee_status = 'half_day_p_ab'
										else:
											employee_status = 'AB'
									self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
									self.env.cr.commit()
								else:
									self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
									self.env.cr.commit()
					else:
						employee_status = 'WO'
						search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
						if search_attendance:
							if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
								worked_hours=search_attendance.worked_hours
								day = x.strftime('%A')
								if day in ('Saturday','Sunday'):
									if worked_hours >=3.5:
										employee_status = 'P'
									if worked_hours < 3.5:
										employee_status = 'AB'
								elif day not in ('Saturday','Sunday'):
									if worked_hours > 6.5:
										employee_status = 'P'
									elif worked_hours >=4.5 and worked_hours <= 6.5:
										employee_status = 'half_day_p_ab'
									else:
										employee_status = 'AB'
								self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
								self.env.cr.commit()
							else:
								self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
								self.env.cr.commit()
			if weekoffs == '1_3_5':
				for x in second_list:
					holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
					if holiday_rec:
						site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
						result = self.env.cr.fetchall()
						if result:
							for site in result:
								if site[0] == site_master_id:									
									employee_status = 'PH'
									search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
									if search_attendance:
										if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
											worked_hours=search_attendance.worked_hours
											day = x.strftime('%A')
											if day in ('Saturday','Sunday'):
												if worked_hours >=3.5:
													employee_status = 'P'
												if worked_hours < 3.5:
													employee_status = 'AB'
											elif day not in ('Saturday','Sunday'):
												if worked_hours > 6.5:
													employee_status = 'P'
												elif worked_hours >=4.5 and worked_hours <= 6.5:
													employee_status = 'half_day_p_ab'
												else:
													employee_status = 'AB'
											self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
											self.env.cr.commit()
									else:
										self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
										self.env.cr.commit()
				for x in fourth_list:
					holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
					if holiday_rec:
						site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
						result = self.env.cr.fetchall()
						if result:
							for site in result:
								if site[0] == site_master_id:									
									employee_status = 'PH'
									search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
									if search_attendance:
										if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
											worked_hours=search_attendance.worked_hours
											day = x.strftime('%A')
											if day in ('Saturday','Sunday'):
												if worked_hours >=3.5:
													employee_status = 'P'
												if worked_hours < 3.5:
													employee_status = 'AB'
											elif day not in ('Saturday','Sunday'):
												if worked_hours > 6.5:
													employee_status = 'P'
												elif worked_hours >=4.5 and worked_hours <= 6.5:
													employee_status = 'half_day_p_ab'
												else:
													employee_status = 'AB'
											self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
											self.env.cr.commit()
										else:
											self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
											self.env.cr.commit()
				for x in first_list:
					employee_status = 'WO'
					holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
					if holiday_rec:
						site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
						result = self.env.cr.fetchall()
						if result:
							for site in result:
								if site[0] == site_master_id:									
									employee_status = 'PH+WO'
									search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
									if search_attendance:
										if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
											worked_hours=search_attendance.worked_hours
											day = x.strftime('%A')
											if day in ('Saturday','Sunday'):
												if worked_hours >=3.5:
													employee_status = 'P'
												if worked_hours < 3.5:
													employee_status = 'AB'
											elif day not in ('Saturday','Sunday'):
												if worked_hours > 6.5:
													employee_status = 'P'
												elif worked_hours >=4.5 and worked_hours <= 6.5:
													employee_status = 'half_day_p_ab'
												else:
													employee_status = 'AB'
											self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
											self.env.cr.commit()
										else:
											self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
											self.env.cr.commit()
									else:
										employee_status = 'PH'
										search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
										if search_attendance:
											if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
												worked_hours=search_attendance.worked_hours
												day = x.strftime('%A')
												if day in ('Saturday','Sunday'):
													if worked_hours >=3.5:
														employee_status = 'P'
													if worked_hours < 3.5:
														employee_status = 'AB'
												elif day not in ('Saturday','Sunday'):
													if worked_hours > 6.5:
														employee_status = 'P'
													elif worked_hours >=4.5 and worked_hours <= 6.5:
														employee_status = 'half_day_p_ab'
													else:
														employee_status = 'AB'
												self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
												self.env.cr.commit()
											else:
												self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
												self.env.cr.commit()
						else:
							employee_status = 'WO'
							search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
							if search_attendance:
								if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
									worked_hours=search_attendance.worked_hours
									day = x.strftime('%A')
									if day in ('Saturday','Sunday'):
										if worked_hours >=3.5:
											employee_status = 'P'
										if worked_hours < 3.5:
											employee_status = 'AB'
									elif day not in ('Saturday','Sunday'):
										if worked_hours > 6.5:
											employee_status = 'P'
										elif worked_hours >=4.5 and worked_hours <= 6.5:
											employee_status = 'half_day_p_ab'
										else:
											employee_status = 'AB'
									self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
									self.env.cr.commit()
								else:
									self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
									self.env.cr.commit()
					else:
						employee_status = 'WO'
						search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
						if search_attendance:
							if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
								worked_hours=search_attendance.worked_hours
								day = x.strftime('%A')
								if day in ('Saturday','Sunday'):
									if worked_hours >=3.5:
										employee_status = 'P'
									if worked_hours < 3.5:
										employee_status = 'AB'
								elif day not in ('Saturday','Sunday'):
									if worked_hours > 6.5:
										employee_status = 'P'
									elif worked_hours >=4.5 and worked_hours <= 6.5:
										employee_status = 'half_day_p_ab'
									else:
										employee_status = 'AB'
								self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
								self.env.cr.commit()
							else:
								self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
								self.env.cr.commit()
				for x in third_list:
					employee_status = 'WO'
					holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
					if holiday_rec:
						site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
						result = self.env.cr.fetchall()
						if result:
							for site in result:
								if site[0] == site_master_id:									
									employee_status = 'PH+WO'
									search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
									if search_attendance:
										if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
											worked_hours=search_attendance.worked_hours
											day = x.strftime('%A')
											if day in ('Saturday','Sunday'):
												if worked_hours >=3.5:
													employee_status = 'P'
												if worked_hours < 3.5:
													employee_status = 'AB'
											elif day not in ('Saturday','Sunday'):
												if worked_hours > 6.5:
													employee_status = 'P'
												elif worked_hours >=4.5 and worked_hours <= 6.5:
													employee_status = 'half_day_p_ab'
												else:
													employee_status = 'AB'
											self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
											self.env.cr.commit()
										else:
											self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
											self.env.cr.commit()
									else:
										employee_status = 'PH'
										search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
										if search_attendance:
											if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
												worked_hours=search_attendance.worked_hours
												day = x.strftime('%A')
												if day in ('Saturday','Sunday'):
													if worked_hours >=3.5:
														employee_status = 'P'
													if worked_hours < 3.5:
														employee_status = 'AB'
												elif day not in ('Saturday','Sunday'):
													if worked_hours > 6.5:
														employee_status = 'P'
													elif worked_hours >=4.5 and worked_hours <= 6.5:
														employee_status = 'half_day_p_ab'
													else:
														employee_status = 'AB'
												self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
												self.env.cr.commit()
											else:
												self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
												self.env.cr.commit()
						else:
							employee_status = 'WO'
							search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
							if search_attendance:
								if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
									worked_hours=search_attendance.worked_hours
									day = x.strftime('%A')
									if day in ('Saturday','Sunday'):
										if worked_hours >=3.5:
											employee_status = 'P'
										if worked_hours < 3.5:
											employee_status = 'AB'
									elif day not in ('Saturday','Sunday'):
										if worked_hours > 6.5:
											employee_status = 'P'
										elif worked_hours >=4.5 and worked_hours <= 6.5:
											employee_status = 'half_day_p_ab'
										else:
											employee_status = 'AB'
									self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
									self.env.cr.commit()
								else:
									self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
									self.env.cr.commit()

					else:
						employee_status = 'WO'
						search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
						if search_attendance:
							if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
								worked_hours=search_attendance.worked_hours
								day = x.strftime('%A')
								if day in ('Saturday','Sunday'):
									if worked_hours >=3.5:
										employee_status = 'P'
									if worked_hours < 3.5:
										employee_status = 'AB'
								elif day not in ('Saturday','Sunday'):
									if worked_hours > 6.5:
										employee_status = 'P'
									elif worked_hours >=4.5 and worked_hours <= 6.5:
										employee_status = 'half_day_p_ab'
									else:
										employee_status = 'AB'
								self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
								self.env.cr.commit()
							else:
								self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
								self.env.cr.commit()
				for x in fifth_list:
					employee_status = 'WO'
					holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
					if holiday_rec:
						site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
						result = self.env.cr.fetchall()
						if result:
							for site in result:
								if site[0] == site_master_id:									
									employee_status = 'PH+WO'
									search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
									if search_attendance:
										if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
											worked_hours=search_attendance.worked_hours
											day = x.strftime('%A')
											if day in ('Saturday','Sunday'):
												if worked_hours >=3.5:
													employee_status = 'P'
												if worked_hours < 3.5:
													employee_status = 'AB'
											elif day not in ('Saturday','Sunday'):
												if worked_hours > 6.5:
													employee_status = 'P'
												elif worked_hours >=4.5 and worked_hours <= 6.5:
													employee_status = 'half_day_p_ab'
												else:
													employee_status = 'AB'
											self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
											self.env.cr.commit()
										else:
											self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
											self.env.cr.commit()
									else:
										employee_status = 'PH'
										search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
										if search_attendance:
											self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
											self.env.cr.commit()
						else:
							employee_status = 'WO'
							search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
							if search_attendance:
								if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
									worked_hours=search_attendance.worked_hours
									day = x.strftime('%A')
									if day in ('Saturday','Sunday'):
										if worked_hours >=3.5:
											employee_status = 'P'
										if worked_hours < 3.5:
											employee_status = 'AB'
									elif day not in ('Saturday','Sunday'):
										if worked_hours > 6.5:
											employee_status = 'P'
										elif worked_hours >=4.5 and worked_hours <= 6.5:
											employee_status = 'half_day_p_ab'
										else:
											employee_status = 'AB'
									self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
									self.env.cr.commit()
								else:
									self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
									self.env.cr.commit()
					else:
						employee_status = 'WO'
						search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
						if search_attendance:
							if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
								worked_hours=search_attendance.worked_hours
								day = x.strftime('%A')
								if day in ('Saturday','Sunday'):
									if worked_hours >=3.5:
										employee_status = 'P'
									if worked_hours < 3.5:
										employee_status = 'AB'
								elif day not in ('Saturday','Sunday'):
									if worked_hours > 6.5:
										employee_status = 'P'
									elif worked_hours >=4.5 and worked_hours <= 6.5:
										employee_status = 'half_day_p_ab'
									else:
										employee_status = 'AB'
								self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
								self.env.cr.commit()
							else:
								self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
								self.env.cr.commit()
			if weekoffs == 'all':
				new_list = first_list + second_list + third_list + fourth_list + fifth_list
				for x in new_list:
					holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
					if holiday_rec:
						site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
						result = self.env.cr.fetchall()
						if result:
							for site in result:
								if site[0] == site_master_id:									
									employee_status = 'PH+WO'
									search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
									if search_attendance:
										if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
											worked_hours=search_attendance.worked_hours
											day = x.strftime('%A')
											if day in ('Saturday','Sunday'):
												if worked_hours !=0.0 and worked_hours>0.0:
													employee_status = 'P'
													self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
													self.env.cr.commit()
												else:
													employee_status = 'WO'
													self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
													self.env.cr.commit()
										else:
											self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
											self.env.cr.commit()
						else:
							employee_status = 'WO'
							search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
							if search_attendance:
								if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
									worked_hours=search_attendance.worked_hours
									day = x.strftime('%A')
									if day in ('Saturday','Sunday'):
										if worked_hours !=0.0 and worked_hours>0.0:
											employee_status = 'P'
											self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
											self.env.cr.commit()
										else:
											employee_status = 'WO'
											self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
											self.env.cr.commit()
								else:
									self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
									self.env.cr.commit()
					else:
						employee_status = 'WO'
						search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
						if search_attendance:
							if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
								worked_hours=search_attendance.worked_hours
								day = x.strftime('%A')
								if day in ('Saturday','Sunday'):
									if worked_hours !=0.0 and worked_hours>0.0:
										employee_status = 'P'
										self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
										self.env.cr.commit()
									else:
										employee_status = 'WO'
										self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
										self.env.cr.commit()
							else:
								self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
								self.env.cr.commit()
			if weekoffs == 'no':
				new_list = first_list + second_list + third_list + fourth_list + fifth_list
				for x in new_list:
					holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
					if holiday_rec:
						site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
						result = self.env.cr.fetchall()
						if result:
							for site in result:
								if site[0] == site_master_id:									
									employee_status = 'PH'
									search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
									if search_attendance:
										if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
											worked_hours=search_attendance.worked_hours
											day = x.strftime('%A')
											if day in ('Saturday','Sunday'):
												if worked_hours >=3.5:
													employee_status = 'P'
												if worked_hours < 3.5:
													employee_status = 'AB'
											elif day not in ('Saturday','Sunday'):
												if worked_hours > 6.5:
													employee_status = 'P'
												elif worked_hours >=4.5 and worked_hours <= 6.5:
													employee_status = 'half_day_p_ab'
												else:
													employee_status = 'AB'
											self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
											self.env.cr.commit()
										else:
											self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
											self.env.cr.commit()
						else:
							employee_status = ''
							search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
							if search_attendance:
								if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
									worked_hours=search_attendance.worked_hours
									day = x.strftime('%A')
									if day in ('Saturday','Sunday'):
										if worked_hours >=3.5:
											employee_status = 'P'
										if worked_hours < 3.5:
											employee_status = 'AB'
									elif day not in ('Saturday','Sunday'):
										if worked_hours > 6.5:
											employee_status = 'P'
										elif worked_hours >=4.5 and worked_hours <= 6.5:
											employee_status = 'half_day_p_ab'
										else:
											employee_status = 'AB'
									self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
									self.env.cr.commit()
								else:
									self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
									self.env.cr.commit()
					else:
						employee_status = ''
						search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
						if search_attendance:
							if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
								worked_hours=search_attendance.worked_hours
								day = x.strftime('%A')
								if day in ('Saturday','Sunday'):
									if worked_hours >=3.5:
										employee_status = 'P'
									if worked_hours < 3.5:
										employee_status = 'AB'
								elif day not in ('Saturday','Sunday'):
									if worked_hours > 6.5:
										employee_status = 'P'
									elif worked_hours >=4.5 and worked_hours <= 6.5:
										employee_status = 'half_day_p_ab'
									else:
										employee_status = 'AB'
								self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
								self.env.cr.commit()
							else:
								self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
								self.env.cr.commit()
			if weekoffs == 'saturday_weekoff':
				for sun in list(set(sun_list)):
					self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s', (blank,datetime.strptime(str(sun), "%Y-%m-%d").date(),employee_id))
					employee_status = ''
					holiday_rec = self.env['holiday.master'].search([('holiday_date','=',sun)])
					if holiday_rec:
						site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
						result = self.env.cr.fetchall()
						if result:
							for site in result:
								if site[0] == site_master_id:									
									employee_status = 'PH'
									search_attendance = self.env['hr.attendance'].search([('attendance_date','=',sun),('employee_code','=',emp_code)],limit=1)
									if search_attendance:
										self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(sun), "%Y-%m-%d").date(),employee_id))
										self.env.cr.commit()
					search_attendance = self.env['hr.attendance'].search([('attendance_date','=',sun),('employee_code','=',emp_code)],limit=1)
					if search_attendance:
						if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
							worked_hours=search_attendance.worked_hours
							day = sun.strftime('%A')
							if day in ('Sunday'):
								if worked_hours > 6.5:
									employee_status = 'P'
								elif worked_hours >=4.5 and worked_hours <= 6.5:
									employee_status = 'half_day_p_ab'
								else:
									employee_status = 'AB'
								self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(sun), "%Y-%m-%d").date(),employee_id))
								self.env.cr.commit()
							else:
								employee_status = ''
								self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(sun), "%Y-%m-%d").date(),employee_id))
								self.env.cr.commit()
						else:
							employee_status = ''
							self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(sun), "%Y-%m-%d").date(),employee_id))
							self.env.cr.commit()
								
				new_list = first_list + second_list + third_list + fourth_list + fifth_list
				for x in new_list:
					holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
					if holiday_rec:
						site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
						result = self.env.cr.fetchall()
						if result:
							for site in result:
								if site[0] == site_master_id:									
									employee_status = 'PH+WO'
									search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
									if search_attendance:
										if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
											worked_hours=search_attendance.worked_hours
											day = x.strftime('%A')
											if day in ('Saturday'):
												if worked_hours !=0.0 and worked_hours>0.0:
													employee_status = 'P+WO'
													self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
													self.env.cr.commit()
												else:
													employee_status = 'WO'
													self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
													self.env.cr.commit()
										else:
											self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
											self.env.cr.commit()
						else:
							employee_status = 'WO'
							search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
							if search_attendance:
								if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
									worked_hours=search_attendance.worked_hours
									day = x.strftime('%A')
									if day in ('Saturday'):
										if worked_hours !=0.0 and worked_hours>0.0:
											employee_status = 'P+WO'
											self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
											self.env.cr.commit()
										else:
											employee_status = 'WO'
											self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
											self.env.cr.commit()
								else:
									self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
									self.env.cr.commit()
					else:
						employee_status = 'WO'
						search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
						if search_attendance:
							if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
								worked_hours=search_attendance.worked_hours
								day = x.strftime('%A')
								if day in ('Saturday'):
									if worked_hours !=0.0 and worked_hours>0.0:
										employee_status = 'P+WO'
										self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
										self.env.cr.commit()
									else:
										employee_status = 'WO'
										self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
										self.env.cr.commit()
							else:
								self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
								self.env.cr.commit()
		return True





class HolidayMaster(models.Model):
	_inherit = 'holiday.master'
	_order = 'holiday_date asc'

	holiday_date = fields.Date('Date')
	site_ids = fields.Many2many('site.master', 'site_holiday_rel', 'holiday_id', 'site_id', string='Sites')


	@api.multi
	def write(self, vals):
		holiday = super(HolidayMaster, self).write(vals)
		for each_site_id in self.site_ids:
			site_emp_ids = self.env['hr.employee'].search([('site_master_id','=',each_site_id.id)])
			if site_emp_ids:
				for each_site_emp_id in site_emp_ids:
					each_site_emp_id.write({'holiday_ids':[(6,0,each_site_id.holiday_ids.ids)]})
		return holiday


class SiteLocationMaster(models.Model):
	_name = 'site.location.master'

	site_master_id = fields.Many2one('site.master','Site')
	site_location_id = fields.Many2one('res.city','Site Location')
	employee_ids = fields.Many2many('hr.employee', 'sitelocationmaster_employee_rel', 'site_location_master_id', 'employee_id', string='Employees')
	employee_old_ids = fields.Many2many('hr.employee', 'sitelocationmaster_employee_old_rel', 'site_location_master_old_id', 'employee_old_id', string='Employees')
	holiday_ids = fields.Many2many('holiday.master', 'sitelocationmaster_holiday_rel', 'site_location_master_id', 'holiday_id', string='Holidays')
	holiday_old_ids = fields.Many2many('holiday.master', 'sitelocationmaster_holiday_old_rel', 'site_location_master_old_id', 'holiday_old_id', string='Holidays')
