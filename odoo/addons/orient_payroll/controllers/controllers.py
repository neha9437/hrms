# -*- coding: utf-8 -*-
from odoo import http
from collections import deque
import json
from odoo.tools import ustr
from odoo.tools.misc import xlwt
from odoo.http import content_disposition, dispatch_rpc, request, serialize_exception, Response
try:
	import xlwt
except ImportError:
	xlwt = None
from datetime import datetime,date
import logging
_logger = logging.getLogger(__name__)
import os
import base64, urllib
from io import StringIO,BytesIO
import csv

class Binary(http.Controller):

	@http.route(['/web/pivot/payroll_report_xls/<int:payroll_id>'], type='http', auth="public")
	def payroll_report_xls(self, payroll_id, access_token):
		payroll_data = request.env['payroll.payroll'].browse(payroll_id)
		employee_obj = request.env['hr.employee']
		company_obj = request.env['res.company']
		attendance_obj = request.env['hr.attendance']
		workbook = xlwt.Workbook(encoding='utf-8')
		employee_ids = []
		site_ids = []
		# getting current financial year----------------------------------------------------------------------------
		financial_year_id = False
		curr_date = datetime.today()
		year = curr_date.year
		year_master_ids = request.env['year.master'].search([('name','ilike',year)])
		for each_year_master_id in year_master_ids:
			start_date = datetime.strptime(each_year_master_id.start_date,'%Y-%m-%d')
			end_date = datetime.strptime(each_year_master_id.end_date,'%Y-%m-%d')
			if curr_date >= start_date and curr_date <= end_date:
				financial_year_id = each_year_master_id
		if not financial_year_id:
			raise AccessError("Financial Year is not defined!")
		#------------------------------------------------------------------------------------------------------------
		# select the employees who are active and belong to selected site
		if payroll_data.site_ids:
			for each_site_id in payroll_data.site_ids:
				site_ids.append(each_site_id.id)
				site_employee_ids = employee_obj.search([('active','=',True),('site_master_id','=',each_site_id.id)])
				for each_site_emp_id in site_employee_ids:
					employee_ids.append(each_site_emp_id)
		# select only active employees
		else:
			employee_ids = employee_obj.search([('active','=',True)])
		
		# sheet1: Employee-------------------------------------------------------------------------------------------
		# employee_sheet = workbook.add_sheet("Employees")
		# sub_style = xlwt.easyxf('font: colour black, bold True;')
		# fields = ['Employee_Code','Company_Code','Division_Code','Zone_Code','Branch_Code','Location_Code','Department_Code','Deputation_Code','Salutation','First_Name','Middle_Name','Last_Name','Father_Husband_Name','Gender','Dateof_Birth','ActDate_Of_Birth','Placeof_Birth','Nationality','Religion','Caste','Language','Blood_Group','Marital_Status','Wedding_Anniversary','Handicap','Smoker','Is_Active','Adhar_No','Adhar_Name','Hobbies','Address_1','Address_2','CityName','StateName','Pin_Code','Mobile','Home','Other','Email_Work','Email_Personal','P_Address_1','P_Address_2','P_CityName','P_StateName','P_Pin_Code','P_Mobile','P_Home','EmegContactName','Relation','Emeg_Address_1','Emeg_Address_2','Emeg_CityName','Emeg_StateName','Emeg_Pin_Code','Emeg_Mobile','Emeg_Home','Emeg_Email_Personal']
		# sheet1_head_row = 0
		# sheet1_head_column = -1
		# for each_field in fields:
		# 	sheet1_head_column = sheet1_head_column+1
		# 	employee_sheet.write(sheet1_head_row, sheet1_head_column, each_field, sub_style)
		# sheet1_row = 0
		# for each_emp_id in employee_ids:
		# 	sheet1_row = sheet1_row+1
		# 	each_emp_data = each_emp_id
		# 	emp_code = each_emp_data.emp_code if each_emp_data.emp_code else ''
		# 	company_code = company_obj.search([('id','=',1)]).name
		# 	division_code = '',
		# 	zone_code = '',
		# 	branch_code = each_emp_data.site_master_id.name if each_emp_data.site_master_id else ''
		# 	location_code = each_emp_data.work_location if each_emp_data.work_location else ''
		# 	department_code = each_emp_data.department_id.name if each_emp_data.department_id else ''
		# 	deputation_code = ''
		# 	salutation = each_emp_data.title if each_emp_data.title else ''
		# 	first_name = each_emp_data.first_name if each_emp_data.first_name else ''
		# 	middle_name = each_emp_data.middle_name if each_emp_data.middle_name else ''
		# 	last_name = each_emp_data.last_name if each_emp_data.last_name else ''
		# 	father_husband_name = ''
		# 	gender = each_emp_data.gender if each_emp_data.gender else ''
		# 	date_of_birth = each_emp_data.birthday if each_emp_data.birthday else ''
		# 	actual_late_of_birth = ''
		# 	place_of_birth = ''
		# 	nationality = each_emp_data.country_id.name if each_emp_data.country_id else ''
		# 	religion = ''
		# 	caste = ''
		# 	language = ''
		# 	blood_group = each_emp_data.blood_group if each_emp_data.blood_group else ''
		# 	marital_status = each_emp_data.marital if each_emp_data.marital else ''
		# 	wedding_anniversary = ''
		# 	handicap = ''
		# 	smoker = ''
		# 	active = 'yes' if each_emp_data.active else 'no'
		# 	aadhar = each_emp_data.aadhar if each_emp_data.aadhar else ''
		# 	aadhar_name = ''
		# 	hobbies = ''
		# 	address_1 = each_emp_data.address if each_emp_data.address else ''
		# 	address_2 = ''
		# 	city_name = ''
		# 	state_name = ''
		# 	pin_code = ''
		# 	mobile = each_emp_data.mobile_phone if each_emp_data.mobile_phone else ''
		# 	home = ''
		# 	other = ''
		# 	email_work = each_emp_data.work_email if each_emp_data.work_email else ''
		# 	email_personal = each_emp_data.personal_email if each_emp_data.personal_email else ''
		# 	p_address_1 = ''
		# 	p_address_2 = ''
		# 	p_city_name = ''
		# 	p_state_name = ''
		# 	p_pin_code = ''
		# 	p_mobile = ''
		# 	p_home = ''
		# 	emeg_contact_name = each_emp_data.emergency_contact_name if each_emp_data.emergency_contact_name else ''
		# 	relation = each_emp_data.emergency_contact_relation if each_emp_data.emergency_contact_relation else ''
		# 	emeg_address_1 = ''
		# 	emeg_address_2 = ''
		# 	emeg_city_name = ''
		# 	emeg_state_name = ''
		# 	emeg_pin_code = ''
		# 	emeg_mobile = each_emp_data.emergency_contact_number if each_emp_data.emergency_contact_number else ''
		# 	emeg_home = ''
		# 	emeg_email_personal = ''
		# 	employee_sheet.write(sheet1_row, 0, str(emp_code[0]) if isinstance(emp_code, tuple) else str(emp_code))
		# 	employee_sheet.write(sheet1_row, 1, str(company_code[0]) if isinstance(company_code, tuple) else str(company_code))
		# 	employee_sheet.write(sheet1_row, 2, str(division_code[0]) if isinstance(division_code, tuple) else str(division_code))
		# 	employee_sheet.write(sheet1_row, 3, str(zone_code[0]) if isinstance(zone_code, tuple) else str(zone_code))
		# 	employee_sheet.write(sheet1_row, 4, str(branch_code[0]) if isinstance(branch_code, tuple) else str(branch_code))
		# 	employee_sheet.write(sheet1_row, 5, str(location_code[0]) if isinstance(location_code, tuple) else str(location_code))
		# 	employee_sheet.write(sheet1_row, 6, str(department_code[0]) if isinstance(department_code, tuple) else str(department_code))
		# 	employee_sheet.write(sheet1_row, 7, str(deputation_code[0]) if isinstance(deputation_code, tuple) else str(deputation_code))
		# 	employee_sheet.write(sheet1_row, 8, str(salutation[0]) if isinstance(salutation, tuple) else str(salutation))
		# 	employee_sheet.write(sheet1_row, 9, str(first_name[0]) if isinstance(first_name, tuple) else str(first_name))
		# 	employee_sheet.write(sheet1_row, 10, str(middle_name[0]) if isinstance(middle_name, tuple) else str(middle_name))
		# 	employee_sheet.write(sheet1_row, 11, str(last_name[0]) if isinstance(last_name, tuple) else str(last_name))
		# 	employee_sheet.write(sheet1_row, 12, str(father_husband_name[0]) if isinstance(father_husband_name, tuple) else str(father_husband_name))
		# 	employee_sheet.write(sheet1_row, 13, str(gender[0]) if isinstance(gender, tuple) else str(gender))
		# 	employee_sheet.write(sheet1_row, 14, str(date_of_birth[0]) if isinstance(date_of_birth, tuple) else str(date_of_birth))
		# 	employee_sheet.write(sheet1_row, 15, str(actual_late_of_birth[0]) if isinstance(actual_late_of_birth, tuple) else str(actual_late_of_birth))
		# 	employee_sheet.write(sheet1_row, 16, str(place_of_birth[0]) if isinstance(place_of_birth, tuple) else str(place_of_birth))
		# 	employee_sheet.write(sheet1_row, 17, str(nationality[0]) if isinstance(nationality, tuple) else str(nationality))
		# 	employee_sheet.write(sheet1_row, 18, str(religion[0]) if isinstance(religion, tuple) else str(religion))
		# 	employee_sheet.write(sheet1_row, 19, str(caste[0]) if isinstance(caste, tuple) else str(caste))
		# 	employee_sheet.write(sheet1_row, 20, str(language[0]) if isinstance(language, tuple) else str(language))
		# 	employee_sheet.write(sheet1_row, 21, str(blood_group[0]) if isinstance(blood_group, tuple) else str(blood_group))
		# 	employee_sheet.write(sheet1_row, 22, str(marital_status[0]) if isinstance(marital_status, tuple) else str(marital_status))
		# 	employee_sheet.write(sheet1_row, 23, str(wedding_anniversary[0]) if isinstance(wedding_anniversary, tuple) else str(wedding_anniversary))
		# 	employee_sheet.write(sheet1_row, 24, str(handicap[0]) if isinstance(handicap, tuple) else str(handicap))
		# 	employee_sheet.write(sheet1_row, 25, str(smoker[0]) if isinstance(smoker, tuple) else str(smoker))
		# 	employee_sheet.write(sheet1_row, 26, str(active[0]) if isinstance(active, tuple) else str(active))
		# 	employee_sheet.write(sheet1_row, 27, str(aadhar[0]) if isinstance(aadhar, tuple) else str(aadhar))
		# 	employee_sheet.write(sheet1_row, 28, str(aadhar_name[0]) if isinstance(aadhar_name, tuple) else str(aadhar_name))
		# 	employee_sheet.write(sheet1_row, 29, str(hobbies[0]) if isinstance(hobbies, tuple) else str(hobbies))
		# 	employee_sheet.write(sheet1_row, 30, str(address_1[0]) if isinstance(address_1, tuple) else str(address_1))
		# 	employee_sheet.write(sheet1_row, 31, str(address_2[0]) if isinstance(address_2, tuple) else str(address_2))
		# 	employee_sheet.write(sheet1_row, 32, str(city_name[0]) if isinstance(city_name, tuple) else str(city_name))
		# 	employee_sheet.write(sheet1_row, 33, str(state_name[0]) if isinstance(state_name, tuple) else str(state_name))
		# 	employee_sheet.write(sheet1_row, 34, str(pin_code[0]) if isinstance(pin_code, tuple) else str(pin_code))
		# 	employee_sheet.write(sheet1_row, 35, str(mobile[0]) if isinstance(mobile, tuple) else str(mobile))
		# 	employee_sheet.write(sheet1_row, 36, str(home[0]) if isinstance(home, tuple) else str(home))
		# 	employee_sheet.write(sheet1_row, 37, str(other[0]) if isinstance(other, tuple) else str(other))
		# 	employee_sheet.write(sheet1_row, 38, str(email_work[0]) if isinstance(email_work, tuple) else str(email_work))
		# 	employee_sheet.write(sheet1_row, 39, str(email_personal[0]) if isinstance(email_personal, tuple) else str(email_personal))
		# 	employee_sheet.write(sheet1_row, 40, str(p_address_1[0]) if isinstance(p_address_1, tuple) else str(p_address_1))
		# 	employee_sheet.write(sheet1_row, 41, str(p_address_2[0]) if isinstance(p_address_2, tuple) else str(p_address_2))
		# 	employee_sheet.write(sheet1_row, 42, str(p_city_name[0]) if isinstance(p_city_name, tuple) else str(p_city_name))
		# 	employee_sheet.write(sheet1_row, 43, str(p_state_name[0]) if isinstance(p_state_name, tuple) else str(p_state_name))
		# 	employee_sheet.write(sheet1_row, 44, str(p_pin_code[0]) if isinstance(p_pin_code, tuple) else str(p_pin_code))
		# 	employee_sheet.write(sheet1_row, 45, str(p_mobile[0]) if isinstance(p_mobile, tuple) else str(p_mobile))
		# 	employee_sheet.write(sheet1_row, 46, str(p_home[0]) if isinstance(p_home, tuple) else str(p_home))
		# 	employee_sheet.write(sheet1_row, 47, str(emeg_contact_name[0]) if isinstance(emeg_contact_name, tuple) else str(emeg_contact_name))
		# 	employee_sheet.write(sheet1_row, 48, str(relation[0]) if isinstance(relation, tuple) else str(relation))
		# 	employee_sheet.write(sheet1_row, 49, str(emeg_address_1[0]) if isinstance(emeg_address_1, tuple) else str(emeg_address_1))
		# 	employee_sheet.write(sheet1_row, 50, str(emeg_address_2[0]) if isinstance(emeg_address_2, tuple) else str(emeg_address_2))
		# 	employee_sheet.write(sheet1_row, 51, str(emeg_city_name[0]) if isinstance(emeg_city_name, tuple) else str(emeg_city_name))
		# 	employee_sheet.write(sheet1_row, 52, str(emeg_state_name[0]) if isinstance(emeg_state_name, tuple) else str(emeg_state_name))
		# 	employee_sheet.write(sheet1_row, 53, str(emeg_pin_code[0]) if isinstance(emeg_pin_code, tuple) else str(emeg_pin_code))
		# 	employee_sheet.write(sheet1_row, 54, str(emeg_mobile[0]) if isinstance(emeg_mobile, tuple) else str(emeg_mobile))
		# 	employee_sheet.write(sheet1_row, 55, str(emeg_home[0]) if isinstance(emeg_home, tuple) else str(emeg_home))
		# 	employee_sheet.write(sheet1_row, 56, str(emeg_email_personal[0]) if isinstance(emeg_email_personal, tuple) else str(emeg_email_personal))


		# Sheet2: Attendance
		attendance_sheet = workbook.add_sheet("Attendance")
		sub_style = xlwt.easyxf('font: colour black, bold True;')
		fields = ['Employee Code','Employee Name','Year','Month','Present Days','Absent Days','Privilege Leaves','Sick/Casual Leaves','Compensatory Offs','Maternity Leaves','Paternity Leaves','Marriage Leaves','Week-Offs','Public Holidays','Total Payable Days']
		sheet3_head_row = 0
		sheet3_head_column = -1
		att_emp_ids = []
		# write each field in first row
		for each_field in fields:
			sheet3_head_column = sheet3_head_column+1
			attendance_sheet.write(sheet3_head_row, sheet3_head_column, each_field, sub_style)
		# calculate min and max month according to selected month
		if payroll_data.month == 'jan':
			date_min = '2019-01-01'
			date_max = '2019-01-31'
		if payroll_data.month == 'feb':
			date_min = '2019-02-01'
			date_max = '2019-02-28'
		if payroll_data.month == 'march':
			date_min = '2019-03-01'
			date_max = '2019-03-31'
		if payroll_data.month == 'april':
			date_min = '2019-04-01'
			date_max = '2019-04-30'
		if payroll_data.month == 'may':
			date_min = '2019-05-01'
			date_max = '2019-05-31'
		if payroll_data.month == 'june':
			date_min = '2019-06-01'
			date_max = '2019-06-30'
		if payroll_data.month == 'july':
			date_min = '2019-07-01'
			date_max = '2019-07-31'
		if payroll_data.month == 'august':
			date_min = '2019-08-01'
			date_max = '2019-08-31'
		if payroll_data.month == 'september':
			date_min = '2019-09-01'
			date_max = '2019-09-30'
		if payroll_data.month == 'october':
			date_min = '2019-10-01'
			date_max = '2019-10-31'
		if payroll_data.month == 'november':
			date_min = '2019-11-01'
			date_max = '2019-11-30'
		if payroll_data.month == 'december':
			date_min = '2019-12-01'
			date_max = '2019-12-31'
		# find out the selected month's attendance records belonging to seleted site
		if payroll_data.site_ids:
			month_attendance_ids = attendance_obj.search([('attendance_date','>=',date_min),('attendance_date','<=',date_max),('site_master_id','in',site_ids)])
		# find out selected month's attendance records
		else:
			month_attendance_ids = attendance_obj.search([('attendance_date','>=',date_min),('attendance_date','<=',date_max)])
		# append the employees of these attendance records in a list

		for each_attendance_id in month_attendance_ids:
			att_emp_ids.append(each_attendance_id.employee_id.id)
		att_emp_ids = list(set(att_emp_ids))
		sheet3_row = 0

		# calculate values
		for each_emp_id in att_emp_ids:
			sheet3_row = sheet3_row+1
			each_emp_data = employee_obj.browse(each_emp_id)

			emp_code = each_emp_data.emp_code if each_emp_data.emp_code else ''
			emp_name = each_emp_data.name if each_emp_data.name else ''
			year = financial_year_id.name if financial_year_id else ''
			month = payroll_data.month

			# present days-------------------------------------------------------------------------------------------------------------
			# ['P', 'OD', 'SOD', WFM',  'P+WO', 'Half P + Half OD']
			presents = attendance_obj.search([('employee_id','=',each_emp_id),('attendance_date','>=',date_min),('attendance_date','<=',date_max),'|',('employee_status','=','P'),'|',('employee_status','=','OD'),'|',('employee_status','=','SOD'),'|',('employee_status','=','WFM'),'|',('employee_status','=','P+WO'),('employee_status','=','half_p_half_od')])
			full_present_days = len(presents)

			# half present days
			# ['Half P + Half AB', 'Half Day SL/CL + Half Day P', 'Half Day PL + Half Day P','Half AB + Half OD','HAlf PL + Half OD','Half SL/CL + HAlf OD']
			half_presents = attendance_obj.search([('employee_id','=',each_emp_id),('attendance_date','>=',date_min),('attendance_date','<=',date_max),'|',('employee_status','=','half_day_p_ab'),'|',('employee_status','=','half_day_sl'),'|',('employee_status','=','half_day_pl'),'|',('employee_status','=','half_ab_half_od'),'|',('employee_status','=','half_pl_half_od'),('employee_status','=','half_sl_half_od')])
			half_present_days = len(half_presents) / 2

			present_days = full_present_days + half_present_days
			#---------------------------------------------------------------------------------------------------------------------------

			# absent days----------------------------------------------------------------------------------------------------------------
			# ['AB', 'LWP', 'False']
			absent_days = attendance_obj.search([('employee_id','=',each_emp_id),('attendance_date','>=',date_min),('attendance_date','<=',date_max),'|',('employee_status','=','AB'),'|',('employee_status','=','LWP'),('employee_status','=',' ')])
			full_absent_days = len(absent_days)

			# half absent days
			# ['Half P + Half AB','Half AB + Half OD']
			half_absents = attendance_obj.search([('employee_id','=',each_emp_id),('attendance_date','>=',date_min),('attendance_date','<=',date_max),'|',('employee_status','=','half_day_p_ab'),('employee_status','=','half_ab_half_od')])
			half_absent_days = len(half_absents) / 2

			absent_days = full_absent_days + half_absent_days
			#----------------------------------------------------------------------------------------------------------------------------

			# privilege leaves-----------------------------------------------------------------------------------------------------------
			# ['PL']
			full_privileges = attendance_obj.search([('employee_id','=',each_emp_id),('attendance_date','>=',date_min),('attendance_date','<=',date_max),('employee_status','=','PL')])
			full_privilege_leaves = len(full_privileges)

			# half privilege leaves
			# ['Half Day PL + Half Day P','HAlf PL + Half OD']
			half_privileges = attendance_obj.search([('employee_id','=',each_emp_id),('attendance_date','>=',date_min),('attendance_date','<=',date_max),'|',('employee_status','=','half_day_pl'),('employee_status','=','half_pl_half_od')])
			half_privilege_leaves = len(half_privileges) / 2

			privilege_leaves = full_privilege_leaves + half_privilege_leaves
			#----------------------------------------------------------------------------------------------------------------------------

			# sick/casual leaves---------------------------------------------------------------------------------------------------------
			# ['SL/CL']
			full_sicks = attendance_obj.search([('employee_id','=',each_emp_id),('attendance_date','>=',date_min),('attendance_date','<=',date_max),('employee_status','=','SL/CL')])
			full_sick_leaves = len(full_sicks)

			# half sick leaves
			# ['Half Day SL/CL + Half Day P','Half SL/CL + HAlf OD']
			half_sicks = attendance_obj.search([('employee_id','=',each_emp_id),('attendance_date','>=',date_min),('attendance_date','<=',date_max),('employee_status','=','half_day_sl')])
			half_sick_leaves = len(half_sicks) / 2

			sick_leaves = full_sick_leaves + half_sick_leaves
			#----------------------------------------------------------------------------------------------------------------------------

			# compensatory leaves
			# ['CO']
			comp_leaves = attendance_obj.search([('employee_id','=',each_emp_id),('attendance_date','>=',date_min),('attendance_date','<=',date_max),('employee_status','=','CO')])
			comp_offs = len(comp_leaves)

			# maternity leaves
			# ['ML']
			maternitys = attendance_obj.search([('employee_id','=',each_emp_id),('attendance_date','>=',date_min),('attendance_date','<=',date_max),('employee_status','=','ML')])
			maternity_leaves = len(maternitys)

			# paternity leaves
			# ['PA']
			paternitys = attendance_obj.search([('employee_id','=',each_emp_id),('attendance_date','>=',date_min),('attendance_date','<=',date_max),('employee_status','=','PA')])
			paternity_leaves = len(paternitys)

			# marriage leaves
			# ['MA']
			marriages = attendance_obj.search([('employee_id','=',each_emp_id),('attendance_date','>=',date_min),('attendance_date','<=',date_max),('employee_status','=','MA')])
			marriage_leaves = len(marriages)

			# weekoffs
			#['WO']
			weekly_offs = attendance_obj.search([('employee_id','=',each_emp_id),('attendance_date','>=',date_min),('attendance_date','<=',date_max),('employee_status','=','WO')])
			weekoffs = len(weekly_offs)

			# public holidays----------------------------------------------------------------------------------------------------
			# ['PH','PH+WO']
			holidays = attendance_obj.search([('employee_id','=',each_emp_id),('attendance_date','>=',date_min),('attendance_date','<=',date_max),'|',('employee_status','=','PH'),('employee_status','=','PH+WO')])
			public_holidays = len(holidays)
			#--------------------------------------------------------------------------------------------------------------------

			paid_leaves = privilege_leaves+sick_leaves+comp_offs+maternity_leaves+paternity_leaves+marriage_leaves

			# total payable days
			total_payable_days = present_days+paid_leaves+weekoffs+public_holidays

			attendance_sheet.write(sheet3_row, 0, str(emp_code[0]) if isinstance(emp_code, tuple) else str(emp_code))
			attendance_sheet.write(sheet3_row, 1, str(emp_name[0]) if isinstance(emp_name, tuple) else str(emp_name))
			attendance_sheet.write(sheet3_row, 2, str(year[0]) if isinstance(year, tuple) else str(year))
			attendance_sheet.write(sheet3_row, 3, str(month[0]) if isinstance(month, tuple) else str(month))
			attendance_sheet.write(sheet3_row, 4, str(present_days[0]) if isinstance(present_days, tuple) else str(present_days))
			attendance_sheet.write(sheet3_row, 5, str(absent_days[0]) if isinstance(absent_days, tuple) else str(absent_days))
			attendance_sheet.write(sheet3_row, 6, str(privilege_leaves[0]) if isinstance(privilege_leaves, tuple) else str(privilege_leaves))
			attendance_sheet.write(sheet3_row, 7, str(sick_leaves[0]) if isinstance(sick_leaves, tuple) else str(sick_leaves))
			attendance_sheet.write(sheet3_row, 8, str(comp_offs[0]) if isinstance(comp_offs, tuple) else str(comp_offs))
			attendance_sheet.write(sheet3_row, 9, str(maternity_leaves[0]) if isinstance(maternity_leaves, tuple) else str(maternity_leaves))
			attendance_sheet.write(sheet3_row, 10, str(paternity_leaves[0]) if isinstance(paternity_leaves, tuple) else str(paternity_leaves))
			attendance_sheet.write(sheet3_row, 11, str(marriage_leaves[0]) if isinstance(marriage_leaves, tuple) else str(marriage_leaves))
			attendance_sheet.write(sheet3_row, 12, str(weekoffs[0]) if isinstance(weekoffs, tuple) else str(weekoffs))
			attendance_sheet.write(sheet3_row, 13, str(public_holidays[0]) if isinstance(public_holidays, tuple) else str(public_holidays))
			attendance_sheet.write(sheet3_row, 14, str(total_payable_days[0]) if isinstance(total_payable_days, tuple) else str(total_payable_days))

		
		filename = 'Orient Tech.xls'
		response = request.make_response(None,headers=[('Content-Type', 'application/vnd.ms-excel'),('Content-Disposition', content_disposition(filename))])
		workbook.save(response.stream)
		return response

	@http.route(['/web/pivot/export_conveyance/<int:conveyance_id>'], type='http', auth="public")
	def export_conveyance(self, conveyance_id, access_token):
		conveyance_data = request.env['conveyance.export'].browse(conveyance_id)
		print (conveyance_data.financial_year.id)
		book = xlwt.Workbook(encoding='utf-8')
		sheet1 = book.add_sheet("Conveyance Applied Report",cell_overwrite_ok=True)
		style = xlwt.XFStyle()
		style1 = xlwt.XFStyle()
		style2 = xlwt.XFStyle()
		style_header = xlwt.XFStyle()
		style_right = xlwt.XFStyle()
		style_right_bold = xlwt.XFStyle()
		style_left = xlwt.XFStyle()
		font = xlwt.Font()
		font.bold = True
		style.font = font
		style_header.font = font
		style_right_bold.font = font
		# background color
		pattern = xlwt.Pattern()
		pattern.pattern = xlwt.Pattern.SOLID_PATTERN
		pattern.pattern_fore_colour = xlwt.Style.colour_map['pale_blue']
		style.pattern = pattern
		style.num_format_str = '0.0'
		style1.num_format_str = '0.00'
		# alignment
		alignment = xlwt.Alignment()
		alignment.horz = xlwt.Alignment.HORZ_LEFT
		style.alignment = alignment
		style.alignment.wrap = 100
		style2.alignment = alignment
		style2.alignment.wrap = 100

		borders = xlwt.Borders()
		borders.left = xlwt.Borders.THIN
		borders.right = xlwt.Borders.THIN
		borders.top = xlwt.Borders.THIN
		borders.bottom = xlwt.Borders.THIN
		borders.left_colour = 0x00
		borders.right_colour = 0x00
		borders.top_colour = 0x00
		borders.bottom_colour = 0x00



		pattern1 = xlwt.Pattern()
		pattern1.pattern1 = xlwt.Pattern.SOLID_PATTERN
		pattern1.pattern_fore_colour = xlwt.Style.colour_map['pale_blue']
		style_header.pattern1 = pattern1
		style_header.alignment.wrap = 12
		# alignment

		alignment1 = xlwt.Alignment()
		alignment1.horz = xlwt.Alignment.HORZ_CENTER
		style_header.alignment = alignment1

		alignment2 = xlwt.Alignment()
		alignment2.horz = xlwt.Alignment.HORZ_RIGHT
		style_right.alignment = alignment2
		style_right.num_format_str = '0.0'
		style_right.alignment.wrap = 12

		alignment3 = xlwt.Alignment()
		alignment3.horz = xlwt.Alignment.HORZ_LEFT
		style_left.alignment = alignment3
		style_left.num_format_str = '0.0'
		style_left.alignment.wrap = 100

		alignment4 = xlwt.Alignment()
		alignment4.horz = xlwt.Alignment.HORZ_RIGHT
		style_right_bold.alignment = alignment2
		style_right_bold.num_format_str = '0.0'
		style_right_bold.alignment.wrap = 12

		alignment5 = xlwt.Alignment()
		alignment5.horz = xlwt.Alignment.HORZ_RIGHT
		style1.alignment = alignment5
		style1.num_format_str = '0.00'
		style1.alignment.wrap = 12

		pattern4 = xlwt.Pattern()
		pattern4.pattern = xlwt.Pattern.SOLID_PATTERN
		# style_right_bold.pattern = pattern4

		sub_style = xlwt.easyxf('pattern: pattern solid, fore_colour gray80;'
								'font: colour white, bold True;')
		data_style = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
								 'font: colour black, bold True;')
		total_style = xlwt.easyxf('pattern: pattern solid, fore_colour yellow;'
								  'font: colour black, bold True;')
		style.borders = borders
		style_left.borders =borders
		style_header.borders = borders
		style_right.borders = borders
		style_right_bold.borders = borders

		
		sheet1.write(1, 0, 'SR. NO.', style_header)
		sheet1.write(1, 1, 'EMPLOYEE CODE', style_header)
		sheet1.write(1, 2, 'NAME', style_header)
		sheet1.write(1, 3, 'GRADE', style_header)
		sheet1.write(1, 4, 'A/C NO', style_header)
		sheet1.write(1, 5, 'DEPARTMENT', style_header)
		sheet1.write(1, 6, 'BRANCH NAME', style_header)
		sheet1.write(1, 7, 'Fixed Conyence (Monthly)', style_header)
		sheet1.write(1, 8, 'Total Conveyance for 19-20 as per DOJ', style_header)
		sheet1.write(1, 9, 'April 2019', style_header)
		sheet1.write(1, 10, 'May 2019', style_header)
		sheet1.write(1, 11, 'June 2019', style_header)
		sheet1.write(1, 12, 'July 2019', style_header)
		sheet1.write(1, 13, 'August 2019', style_header)
		sheet1.write(1, 14, 'September 2019', style_header)
		sheet1.write(1, 15, 'October 2019', style_header)
		sheet1.write(1, 16, 'November 2019', style_header)
		sheet1.write(1, 17, 'December 2019', style_header)
		sheet1.write(1, 18, 'January 2020', style_header)
		sheet1.write(1, 19, 'February 2020', style_header)
		sheet1.write(1, 20, 'March 2020', style_header)
		sheet1.write(1, 21, 'Total Applied Conveyance (19-20)', style_header)
		
		employee_list = []
		employee_code = []
		employee_name = []
		employee_grade = []
		account_no = []
		department = []
		branch_name = []
		conveyance_lines_data = request.env['conveyance.reimbursement.lines'].search([('year','=',conveyance_data.financial_year.id)])
		if conveyance_lines_data:
			for x in conveyance_lines_data:
				if x.employee.id not in employee_list and x.employee.emp_code!=0:
					employee_list.append(x.employee.id)
					employee_code.append(x.employee.emp_code)
					employee_name.append(x.employee.name)
					employee_grade.append(x.employee.grade_id.name)
					account_no.append(x.employee.bank_account_number)
					department.append(x.employee.department_id.name)
					branch_name.append(x.employee.site_master_id.name)
		if employee_list:
			row = 2
			col = 0
			count = 1
			
			for m,n,o,p,q,r,s in zip(employee_list,employee_code,employee_name,employee_grade,account_no,department,branch_name):
				if employee_code!=0:
					total_applied_conv = 0.0
					conveyance_lines_browse = request.env['conveyance.reimbursement.lines'].search([('year','=',conveyance_data.financial_year.id),('employee','=',m)])
					sheet1.write(row, col, count, style2)
					sheet1.write(row, col+1, n, style2)
					sheet1.write(row, col+2, o, style1)
					sheet1.write(row, col+3, p, style1)
					sheet1.write(row, col+4, q, style1)
					sheet1.write(row, col+5, r, style1)
					sheet1.write(row, col+6, s, style1)
					search_rec = request.env['conveyance.reimbursement.import'].search([('year_id','=',conveyance_data.financial_year.id),('employee','=',m)])
					if search_rec:
						sheet1.write(row, col+7, search_rec.monthly_conveyance, style1)
						sheet1.write(row, col+8, search_rec.authorized_amount, style1)
					for rec in conveyance_lines_browse:
						if rec.month_sel == '4':
							total_applied_conv+=rec.applied_amount
							sheet1.write(row, col+9, rec.applied_amount, style1)
						if rec.month_sel == '5':
							total_applied_conv+=rec.applied_amount
							sheet1.write(row, col+10, rec.applied_amount, style1)
						if rec.month_sel == '6':
							total_applied_conv+=rec.applied_amount
							sheet1.write(row, col+11, rec.applied_amount, style1)
						if rec.month_sel == '7':
							total_applied_conv+=rec.applied_amount
							sheet1.write(row, col+12, rec.applied_amount, style1)
						if rec.month_sel == '8':
							total_applied_conv+=rec.applied_amount
							sheet1.write(row, col+13, rec.applied_amount, style1)
						if rec.month_sel == '9':
							total_applied_conv+=rec.applied_amount
							sheet1.write(row, col+14, rec.applied_amount, style1)
						if rec.month_sel == '10':
							total_applied_conv+=rec.applied_amount
							sheet1.write(row, col+15, rec.applied_amount, style1)
						if rec.month_sel == '11':
							total_applied_conv+=rec.applied_amount
							sheet1.write(row, col+16, rec.applied_amount, style1)
						if rec.month_sel == '12':
							total_applied_conv+=rec.applied_amount
							sheet1.write(row, col+17, rec.applied_amount, style1)
						if rec.month_sel == '1':
							total_applied_conv+=rec.applied_amount
							sheet1.write(row, col+18, rec.applied_amount, style1)
						if rec.month_sel == '2':
							total_applied_conv+=rec.applied_amount
							sheet1.write(row, col+19, rec.applied_amount, style1)
						if rec.month_sel == '3':
							total_applied_conv+=rec.applied_amount
							sheet1.write(row, col+20, rec.applied_amount, style1)
				sheet1.write(row, col+21, total_applied_conv, style1)	
				row+=1
				count+=1
		filename = 'Conveyance_Applied_Report_%s.xls' %(datetime.now().date())
		response = request.make_response(None,
			headers=[('Content-Type', 'application/vnd.ms-excel'),
					('Content-Disposition', content_disposition(filename))])
		book.save(response.stream)
		return response
