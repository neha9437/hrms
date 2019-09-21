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
from calendar import monthrange

month_sel = {'jan': 'January','feb': 'February','mar': 'March','apr': 'April','may': 'May',
			'jun':'June','jul':'July','aug':'August','sep':'September','oct':'October',
			'nov':'November','dec':'December'}

class Binary(http.Controller):

	@http.route(['/web/pivot/attendance_export_xls/<int:appraisal_id>'], type='http', auth="public")
	def attendance_export_xls(self, appraisal_id, access_token):
		appraisal_data = request.env['hr.attendance.export'].browse(appraisal_id)
		book = xlwt.Workbook(encoding='utf-8')
		sheet1 = book.add_sheet("Attendance Data")
		style = xlwt.XFStyle()
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
		# style.num_format_str = '0.0'
		# alignment
		alignment = xlwt.Alignment()
		alignment.horz = xlwt.Alignment.HORZ_LEFT
		style.alignment = alignment
		style.alignment.wrap = 100

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
		# style_right.num_format_str = '0.0'
		style_right.alignment.wrap = 12

		alignment3 = xlwt.Alignment()
		alignment3.horz = xlwt.Alignment.HORZ_LEFT
		style_left.alignment = alignment3
		# style_left.num_format_str = '0.0'
		style_left.alignment.wrap = 100

		alignment4 = xlwt.Alignment()
		alignment4.horz = xlwt.Alignment.HORZ_RIGHT
		style_right_bold.alignment = alignment2
		# style_right_bold.num_format_str = '0.0'
		style_right_bold.alignment.wrap = 12

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

		row = 0
		col = 0

		from_date = appraisal_data.from_date
		to_date = appraisal_data.to_date
		print("11111111111111111",from_date,to_date)


		sheet1.write_merge(2, 2, 0, 1, 'From Date:', sub_style)
		sheet1.write_merge(2, 2, 2, 5, appraisal_data.from_date, style)
		sheet1.write_merge(3, 3, 0, 1, 'To Date:', sub_style)
		sheet1.write_merge(3, 3, 2, 5, appraisal_data.to_date, style)
		# sheet1.write_merge(4, 4, 0, 1,'Application Year:', sub_style)
		# sheet1.write_merge(4, 4, 2, 5, appraisal_data.application_year.name, style)

		attendance_rec = request.env['hr.attendance'].search([('attendance_date','>',from_date),('attendance_date','<=',to_date)],order='employee_code, attendance_date')
		# print(attendance_rec,'attendance')

		sheet1.write_merge(6, 6, 0, 25, 'Attendance Data', style_header)
		sheet1.write(8, 0, 'Sr. No.', style_header)
		sheet1.write_merge(8, 8, 1, 1, 'Employee Code', style_header)
		sheet1.write_merge(8, 8, 2, 4, 'Employee Name', style_header)
		sheet1.write_merge(8, 8, 5, 6, 'Department', style_header)
		sheet1.write_merge(8, 8, 7, 8, 'Designation', style_header)
		sheet1.write_merge(8, 8, 9, 9, 'Site', style_header)
		sheet1.write_merge(8, 8, 10, 10, 'Shift', style_header)
		sheet1.write_merge(8, 8, 11, 11, 'Date', style_header)
		sheet1.write_merge(8, 8, 12, 12, 'In Time', style_header)
		sheet1.write_merge(8, 8, 13, 13, 'Out Time', style_header)
		sheet1.write_merge(8, 8, 14, 14, 'Worked Hours', style_header)
		sheet1.write_merge(8, 8, 15, 15, 'Status', style_header)
		

		count=0
		sr_no=[]
		row=10

		for x in attendance_rec:
			count+=1
			sr_no.append(count)
			sheet1.write(row,col, count, style_header)
			sheet1.write_merge(row,row,1, 1, x.employee_id.emp_code, style_right)
			sheet1.write_merge(row,row,2, 4, x.employee_id.name, style_right)
			sheet1.write_merge(row,row,5, 6, x.employee_id.department_id.name, style_right)
			sheet1.write_merge(row,row,7, 8, x.employee_id.job_id.name, style_right)
			sheet1.write_merge(row,row,9, 9, x.employee_id.site_master_id.name, style_right)
			sheet1.write_merge(row,row,10, 10, x.shift.name, style_right)
			sheet1.write_merge(row,row,11, 11, x.attendance_date, style_right)
			sheet1.write_merge(row,row,12, 12, x.in_time, style_right)
			sheet1.write_merge(row,row,13, 13, x.out_time, style_right)
			sheet1.write_merge(row,row,14, 14, x.worked_hours, style_right)
			sheet1.write_merge(row,row,15, 15, x.employee_status, style_right)

			row+=1

		filename = 'AttendanceExport.xls' #%(appraisal_data.review_cycle)
		response = request.make_response(None,
			headers=[('Content-Type', 'application/vnd.ms-excel'),
					('Content-Disposition', content_disposition(filename))])
		book.save(response.stream)
		return response


# Attendance data : site wise, department wise and employee wise
	@http.route(['/web/pivot/attendance_exportreport_xls/<int:appraisal_id>'], type='http', auth="public")
	def attendance_exportreport_xls(self, appraisal_id, access_token):
		att_data = request.env['attendance.reports'].browse(appraisal_id)
		book = xlwt.Workbook(encoding='utf-8')
		sheet1 = book.add_sheet("Attendance Data")
		style = xlwt.XFStyle()
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
		# style.num_format_str = '0.0'
		# alignment
		alignment = xlwt.Alignment()
		alignment.horz = xlwt.Alignment.HORZ_LEFT
		style.alignment = alignment
		style.alignment.wrap = 100

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
		style_right_bold.alignment = alignment2
		# style_right.num_format_str = '0'
		style_right.alignment.wrap = 12
		style_right_bold.alignment.wrap = 12

		alignment3 = xlwt.Alignment()
		alignment3.horz = xlwt.Alignment.HORZ_LEFT
		style_left.alignment = alignment3
		# style_left.num_format_str = '0.0'
		style_left.alignment.wrap = 100

		# alignment4 = xlwt.Alignment()
		# alignment4.horz = xlwt.Alignment.HORZ_RIGHT
		# style_right_bold.alignment = alignment2
		# style_right_bold.num_format_str = '0.0'
		# style_right_bold.alignment.wrap = 12

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

		style_right_bold = xlwt.easyxf('pattern: pattern solid, fore_colour yellow;'
								  		'font: colour black, bold False;'
								  		'align: horiz right;')

		row = 0
		col = 0

		from_date = att_data.from_date
		to_date = att_data.to_date
		site_master_id = att_data.site_master_id.id
		department_id = att_data.department_id.id
		employee_id = att_data.employee_id.id
		print("hhhh",from_date,to_date)


		sheet1.write_merge(2, 2, 0, 1, 'From Date:', sub_style)
		sheet1.write_merge(2, 2, 2, 5, att_data.from_date, style)
		sheet1.write_merge(3, 3, 0, 1, 'To Date:', sub_style)
		sheet1.write_merge(3, 3, 2, 5, att_data.to_date, style)
		# sheet1.write_merge(4, 4, 0, 1,'Application Year:', sub_style)
		# sheet1.write_merge(4, 4, 2, 5, appraisal_data.application_year.name, style)

		attendance_rec = request.env['hr.attendance'].search([('attendance_date','>=',from_date),('attendance_date','<=',to_date)],order='employee_code, attendance_date')
		# print(attendance_rec,'attendance')

		sheet1.write_merge(6, 6, 0, 15, 'Attendance Data', style_header)
		sheet1.write(8, 0, 'Sr. No.', style_header)
		sheet1.write_merge(8, 8, 1, 1, 'Employee Code', style_header)
		sheet1.write_merge(8, 8, 2, 4, 'Employee Name', style_header)
		sheet1.write_merge(8, 8, 5, 6, 'Department', style_header)
		sheet1.write_merge(8, 8, 7, 8, 'Designation', style_header)
		sheet1.write_merge(8, 8, 9, 9, 'Site', style_header)
		sheet1.write_merge(8, 8, 10, 10, 'Shift', style_header)
		sheet1.write_merge(8, 8, 11, 11, 'Date', style_header)
		sheet1.write_merge(8, 8, 12, 12, 'In Time', style_header)
		sheet1.write_merge(8, 8, 13, 13, 'Out Time', style_header)
		sheet1.write_merge(8, 8, 14, 14, 'Worked Hours', style_header)
		sheet1.write_merge(8, 8, 15, 15, 'Early Leaving', style_header)
		sheet1.write_merge(8, 8, 16, 16, 'Late Coming', style_header)
		sheet1.write_merge(8, 8, 17, 17, 'Extra Worked Hours', style_header)
		sheet1.write_merge(8, 8, 18, 18, 'Status', style_header)
		

		count=0
		sr_no=[]
		row=10

		for x in attendance_rec:
			if x.worked_hours:
				if x.worked_hours >= 9.0:
					extra_worked_hours = x.worked_hours - 9.0
					extra_hours = float("{0:.2f}".format(extra_worked_hours))
					extra_hours = str(extra_hours).replace('.',':')
					print(extra_hours,'extra_hours')
					worked_hours = str(x.worked_hours).replace('.',':')
				else:
					extra_hours = '00:00'
					worked_hours = str(x.worked_hours).replace('.',':')
			else:
				extra_hours = '00:00'
				worked_hours = str(x.worked_hours).replace('.',':')

			if x.approve_check == True:
				final_style = style_right_bold
			else:
				final_style = style_right

			if not site_master_id and not department_id and not employee_id:
				# print("plainnnnnnnnnnnnnnnnnnn")
				count+=1
				sr_no.append(count)
				sheet1.write(row,col, count, style_header)
				sheet1.write_merge(row,row,1, 1, x.employee_id.emp_code, final_style)
				sheet1.write_merge(row,row,2, 4, x.employee_id.name, final_style)
				sheet1.write_merge(row,row,5, 6, x.employee_id.department_id.name, final_style)
				sheet1.write_merge(row,row,7, 8, x.employee_id.job_id.name, final_style)
				sheet1.write_merge(row,row,9, 9, x.employee_id.site_master_id.name, final_style)
				sheet1.write_merge(row,row,10, 10, x.shift.name, final_style)
				sheet1.write_merge(row,row,11, 11, x.attendance_date, final_style)
				sheet1.write_merge(row,row,12, 12, x.in_time, final_style)
				sheet1.write_merge(row,row,13, 13, x.out_time, final_style)
				sheet1.write_merge(row,row,14, 14, worked_hours, final_style)
				sheet1.write_merge(row,row,15, 15, x.early_leaving, final_style)
				sheet1.write_merge(row,row,16, 16, x.late_coming, final_style)
				sheet1.write_merge(row,row,17, 17, extra_hours, final_style)
				sheet1.write_merge(row,row,18, 18, x.employee_status, final_style)

				row+=1
				
			elif site_master_id and not department_id and not employee_id:
				# print("site_master_id")
				if x.employee_id.site_master_id.id == site_master_id:
					print(x.employee_id.id,'emp id')
					count+=1
					sr_no.append(count)
					sheet1.write(row,col, count, style_header)
					sheet1.write_merge(row,row,1, 1, x.employee_id.emp_code, final_style)
					sheet1.write_merge(row,row,2, 4, x.employee_id.name, final_style)
					sheet1.write_merge(row,row,5, 6, x.employee_id.department_id.name, final_style)
					sheet1.write_merge(row,row,7, 8, x.employee_id.job_id.name, final_style)
					sheet1.write_merge(row,row,9, 9, x.employee_id.site_master_id.name, final_style)
					sheet1.write_merge(row,row,10, 10, x.shift.name, final_style)
					sheet1.write_merge(row,row,11, 11, x.attendance_date, final_style)
					sheet1.write_merge(row,row,12, 12, x.in_time, final_style)
					sheet1.write_merge(row,row,13, 13, x.out_time, final_style)
					sheet1.write_merge(row,row,14, 14, worked_hours, final_style)
					sheet1.write_merge(row,row,15, 15, x.early_leaving, final_style)
					sheet1.write_merge(row,row,16, 16, x.late_coming, final_style)
					sheet1.write_merge(row,row,17, 17, extra_hours, final_style)
					sheet1.write_merge(row,row,18, 18, x.employee_status, final_style)

					row+=1

			elif department_id and not site_master_id and not employee_id:
				# print("department_id")
				if x.employee_id.department_id.id == department_id:
					print(x.employee_id.id,'emp id')
					count+=1
					sr_no.append(count)
					sheet1.write(row,col, count, style_header)
					sheet1.write_merge(row,row,1, 1, x.employee_id.emp_code, final_style)
					sheet1.write_merge(row,row,2, 4, x.employee_id.name, final_style)
					sheet1.write_merge(row,row,5, 6, x.employee_id.department_id.name, final_style)
					sheet1.write_merge(row,row,7, 8, x.employee_id.job_id.name, final_style)
					sheet1.write_merge(row,row,9, 9, x.employee_id.site_master_id.name, final_style)
					sheet1.write_merge(row,row,10, 10, x.shift.name, final_style)
					sheet1.write_merge(row,row,11, 11, x.attendance_date, final_style)
					sheet1.write_merge(row,row,12, 12, x.in_time, final_style)
					sheet1.write_merge(row,row,13, 13, x.out_time, final_style)
					sheet1.write_merge(row,row,14, 14, worked_hours, final_style)
					sheet1.write_merge(row,row,15, 15, x.early_leaving, final_style)
					sheet1.write_merge(row,row,16, 16, x.late_coming, final_style)
					sheet1.write_merge(row,row,17, 17, extra_hours, final_style)
					sheet1.write_merge(row,row,18, 18, x.employee_status, final_style)

					row+=1

			elif site_master_id and department_id and not employee_id:
				# print("both")
				if x.employee_id.site_master_id.id == site_master_id and x.employee_id.department_id.id == department_id:
					print(x.employee_id.id,'emp id')
					count+=1
					sr_no.append(count)
					sheet1.write(row,col, count, style_header)
					sheet1.write_merge(row,row,1, 1, x.employee_id.emp_code, final_style)
					sheet1.write_merge(row,row,2, 4, x.employee_id.name, final_style)
					sheet1.write_merge(row,row,5, 6, x.employee_id.department_id.name, final_style)
					sheet1.write_merge(row,row,7, 8, x.employee_id.job_id.name, final_style)
					sheet1.write_merge(row,row,9, 9, x.employee_id.site_master_id.name, final_style)
					sheet1.write_merge(row,row,10, 10, x.shift.name, final_style)
					sheet1.write_merge(row,row,11, 11, x.attendance_date, final_style)
					sheet1.write_merge(row,row,12, 12, x.in_time, final_style)
					sheet1.write_merge(row,row,13, 13, x.out_time, final_style)
					sheet1.write_merge(row,row,14, 14, worked_hours, final_style)
					sheet1.write_merge(row,row,15, 15, x.early_leaving, final_style)
					sheet1.write_merge(row,row,16, 16, x.late_coming, final_style)
					sheet1.write_merge(row,row,17, 17, extra_hours, final_style)
					sheet1.write_merge(row,row,18, 18, x.employee_status, final_style)

					row+=1

			elif employee_id and not site_master_id and not department_id:
				if x.employee_id.id == employee_id:
					print(x.employee_id.id,'emp id')
					count+=1
					sr_no.append(count)
					sheet1.write(row,col, count, style_header)
					sheet1.write_merge(row,row,1, 1, x.employee_id.emp_code, final_style)
					sheet1.write_merge(row,row,2, 4, x.employee_id.name, final_style)
					sheet1.write_merge(row,row,5, 6, x.employee_id.department_id.name, final_style)
					sheet1.write_merge(row,row,7, 8, x.employee_id.job_id.name, final_style)
					sheet1.write_merge(row,row,9, 9, x.employee_id.site_master_id.name, final_style)
					sheet1.write_merge(row,row,10, 10, x.shift.name, final_style)
					sheet1.write_merge(row,row,11, 11, x.attendance_date, final_style)
					sheet1.write_merge(row,row,12, 12, x.in_time, final_style)
					sheet1.write_merge(row,row,13, 13, x.out_time, final_style)
					sheet1.write_merge(row,row,14, 14, worked_hours, final_style)
					sheet1.write_merge(row,row,15, 15, x.early_leaving, final_style)
					sheet1.write_merge(row,row,16, 16, x.late_coming, final_style)
					sheet1.write_merge(row,row,17, 17, extra_hours, final_style)
					sheet1.write_merge(row,row,18, 18, x.employee_status, final_style)				

					row+=1

		filename = 'AttendanceExport.xls' #%(appraisal_data.review_cycle)
		response = request.make_response(None,
			headers=[('Content-Type', 'application/vnd.ms-excel'),
					('Content-Disposition', content_disposition(filename))])
		book.save(response.stream)
		return response


# Attendance date : Number of working days
	@http.route(['/web/pivot/attendance_month_exportreport_xls/<int:att_id>'], type='http', auth="public")
	def attendance_month_exportreport_xls(self, att_id, access_token):
		att_data = request.env['attendance.reports'].browse(att_id)
		book = xlwt.Workbook(encoding='utf-8')
		sheet1 = book.add_sheet("Attendance Data")
		style = xlwt.XFStyle()
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
		# style.num_format_str = '0.0'
		# alignment
		alignment = xlwt.Alignment()
		alignment.horz = xlwt.Alignment.HORZ_LEFT
		style.alignment = alignment
		style.alignment.wrap = 100

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
		# style_right.num_format_str = '0.0'
		style_right.alignment.wrap = 12

		alignment3 = xlwt.Alignment()
		alignment3.horz = xlwt.Alignment.HORZ_LEFT
		style_left.alignment = alignment3
		# style_left.num_format_str = '0.0'
		style_left.alignment.wrap = 100

		alignment4 = xlwt.Alignment()
		alignment4.horz = xlwt.Alignment.HORZ_RIGHT
		style_right_bold.alignment = alignment2
		# style_right_bold.num_format_str = '0.0'
		style_right_bold.alignment.wrap = 12

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

		row = 0
		col = 0

		from_date = att_data.from_date
		to_date = att_data.to_date
		site_master_id = att_data.site_master_id.id
		department_id = att_data.department_id.id
		employee_id = att_data.employee_id.id
		print("hhhh",from_date,to_date)


		sheet1.write_merge(2, 2, 0, 1, 'From Date:', sub_style)
		sheet1.write_merge(2, 2, 2, 5, att_data.from_date, style)
		sheet1.write_merge(3, 3, 0, 1, 'To Date:', sub_style)
		sheet1.write_merge(3, 3, 2, 5, att_data.to_date, style)


		sheet1.write_merge(6, 6, 0, 21, 'Attendance Data', style_header)
		sheet1.write(8, 0, 'Sr. No.', style_header)
		sheet1.write_merge(8, 8, 1, 1, 'Employee Code', style_header)
		sheet1.write_merge(8, 8, 2, 4, 'Employee Name', style_header)
		sheet1.write_merge(8, 8, 5, 6, 'Designation', style_header)
		sheet1.write_merge(8, 8, 7, 8, 'Site', style_header)
		sheet1.write_merge(8, 8, 9, 9, 'January', style_header)
		sheet1.write_merge(8, 8, 10, 10, 'February', style_header)
		sheet1.write_merge(8, 8, 11, 11, 'March', style_header)
		sheet1.write_merge(8, 8, 12, 12, 'April', style_header)
		sheet1.write_merge(8, 8, 13, 13, 'May', style_header)
		sheet1.write_merge(8, 8, 14, 14, 'June', style_header)
		sheet1.write_merge(8, 8, 15, 15, 'July', style_header)
		sheet1.write_merge(8, 8, 16, 16, 'August', style_header)
		sheet1.write_merge(8, 8, 17, 17, 'September', style_header)
		sheet1.write_merge(8, 8, 18, 18, 'October', style_header)
		sheet1.write_merge(8, 8, 19, 19, 'November', style_header)
		sheet1.write_merge(8, 8, 20, 20, 'December', style_header)
		sheet1.write_merge(8, 8, 21, 21, 'Total', style_header)

		count=0
		sr_no=[]
		row=10
		emp_id = []

		if site_master_id and not department_id and not employee_id:
			emp_recs = request.env['hr.employee'].search([('active','=','t'),('site_master_id','=',site_master_id)])
			print(emp_recs,'emp_recs')


			for emp in emp_recs:
				print("------------------------------------------------")
				attendance_rec = request.env['hr.attendance'].search([('attendance_date','>=',from_date),('attendance_date','<=',to_date),('employee_id','=',emp.id),('employee_status','in',('P','half_day_p_ab','half_day_sl','half_day_pl'))],order='employee_code, attendance_date')
				print(attendance_rec,'attendance')

				emp_name = emp.name
				emp_code = emp.emp_code
				job_id = emp.job_id.name
				site_id = emp.site_master_id.name

				month_count = []
				if attendance_rec:
					for x in attendance_rec:

						print(x.employee_id.name,'Name')
						attendance_date = x.attendance_date
						# print(attendance_date,'attendance_date')
						month = datetime.strptime(str(attendance_date), "%Y-%m-%d").month
						# print(month,'month')
						month_count.append(month)
						print(month_count,'month_count')

					jan = month_count.count(1)
					feb = month_count.count(2)
					mar = month_count.count(3)
					apr = month_count.count(4)
					may = month_count.count(5)
					jun = month_count.count(6)
					jul = month_count.count(7)
					aug = month_count.count(8)
					sep = month_count.count(9)
					octo= month_count.count(10)
					nov = month_count.count(11)
					dec = month_count.count(12)
					total = jan+feb+mar+apr+may+jun+jul+aug+sep+octo+nov+dec
					print(jan,feb,mar,apr,may,jun,jul,aug,sep,octo,nov,dec,'----------work days count')

					count+=1

					sr_no.append(count)
					sheet1.write(row,col, count, style_header)
					sheet1.write_merge(row,row,1, 1, emp_code, style_right)
					sheet1.write_merge(row,row,2, 4, emp_name, style_right)
					sheet1.write_merge(row,row,5, 6, job_id, style_right)
					sheet1.write_merge(row,row,7, 8, site_id, style_right)
					sheet1.write_merge(row,row,9, 9, jan, style_right)
					sheet1.write_merge(row,row,10, 10, feb, style_right)
					sheet1.write_merge(row,row,11, 11, mar, style_right)
					sheet1.write_merge(row,row,12, 12, apr, style_right)
					sheet1.write_merge(row,row,13, 13, may, style_right)
					sheet1.write_merge(row,row,14, 14, jun, style_right)
					sheet1.write_merge(row,row,15, 15, jul, style_right)
					sheet1.write_merge(row,row,16, 16, aug, style_right)
					sheet1.write_merge(row,row,17, 17, sep, style_right)
					sheet1.write_merge(row,row,18, 18, octo, style_right)
					sheet1.write_merge(row,row,19, 19, nov, style_right)
					sheet1.write_merge(row,row,20, 20, dec, style_right)
					sheet1.write_merge(row,row,21, 21, total, style_right)

					row+=1

		elif employee_id and not site_master_id and not department_id:
			emp_recs = request.env['hr.employee'].search([('active','=','t'),('id','=',employee_id)])
			print(emp_recs,'emp_recs')

			month_count = []

			for emp in emp_recs:
				attendance_rec = request.env['hr.attendance'].search([('attendance_date','>=',from_date),('attendance_date','<=',to_date),('employee_id','=',emp.id)],order='employee_code, attendance_date')
				print(attendance_rec,'attendance')	
				emp_id = emp.id
				job_id = emp.job_id.id
				site_id = emp.site_master_id.id		
				for x in attendance_rec:
					if x.employee_status in ('P','half_day_p_ab','half_day_sl','half_day_pl'):
						attendance_date = x.attendance_date
						# print(attendance_date,'attendance_date')
						month = datetime.strptime(str(attendance_date), "%Y-%m-%d").month
						# print(month,'month')
						month_count.append(month)
				print(month_count,'month_count')

				jan = month_count.count(1)
				feb = month_count.count(2)
				mar = month_count.count(3)
				apr = month_count.count(4)
				may = month_count.count(5)
				jun = month_count.count(6)
				jul = month_count.count(7)
				aug = month_count.count(8)
				sep = month_count.count(9)
				octo= month_count.count(10)
				nov = month_count.count(11)
				dec = month_count.count(12)
				total = jan+feb+mar+apr+may+jun+jul+aug+sep+octo+nov+dec

				print(jan,feb,mar,apr,may,jun,jul,aug,sep,octo,nov,dec,'----------')

				count+=1

				sr_no.append(count)
				sheet1.write(row,col, count, style_header)
				sheet1.write_merge(row,row,1, 1, emp.emp_code, style_right)
				sheet1.write_merge(row,row,2, 4, emp.name, style_right)
				sheet1.write_merge(row,row,5, 6, emp.job_id.name, style_right)
				sheet1.write_merge(row,row,7, 8, emp.site_master_id.name, style_right)
				sheet1.write_merge(row,row,9, 9, jan, style_right)
				sheet1.write_merge(row,row,10, 10, feb, style_right)
				sheet1.write_merge(row,row,11, 11, mar, style_right)
				sheet1.write_merge(row,row,12, 12, apr, style_right)
				sheet1.write_merge(row,row,13, 13, may, style_right)
				sheet1.write_merge(row,row,14, 14, jun, style_right)
				sheet1.write_merge(row,row,15, 15, jul, style_right)
				sheet1.write_merge(row,row,16, 16, aug, style_right)
				sheet1.write_merge(row,row,17, 17, sep, style_right)
				sheet1.write_merge(row,row,18, 18, octo, style_right)
				sheet1.write_merge(row,row,19, 19, nov, style_right)
				sheet1.write_merge(row,row,20, 20, dec, style_right)
				sheet1.write_merge(row,row,21, 21, total, style_right)

				row+=1

		elif site_master_id and employee_id and not department_id:
			emp_recs = request.env['hr.employee'].search([('active','=','t'),('id','=',employee_id),('site_master_id','=',site_master_id)])
			print(emp_recs,'emp_recs')

			month_count = []

			for emp in emp_recs:
				print("------------------------------------------------")
				attendance_rec = request.env['hr.attendance'].search([('attendance_date','>=',from_date),('attendance_date','<=',to_date),('employee_id','=',emp.id),('employee_status','in',('P','half_day_p_ab','half_day_sl','half_day_pl'))],order='employee_code, attendance_date')
				print(attendance_rec,'attendance')

				emp_name = emp.name
				emp_code = emp.emp_code
				job_id = emp.job_id.name
				site_id = emp.site_master_id.name

				month_count = []
				if attendance_rec:
					for x in attendance_rec:

						print(x.employee_id.name,'Name')
						attendance_date = x.attendance_date
						# print(attendance_date,'attendance_date')
						month = datetime.strptime(str(attendance_date), "%Y-%m-%d").month
						# print(month,'month')
						month_count.append(month)
						print(month_count,'month_count')

					jan = month_count.count(1)
					feb = month_count.count(2)
					mar = month_count.count(3)
					apr = month_count.count(4)
					may = month_count.count(5)
					jun = month_count.count(6)
					jul = month_count.count(7)
					aug = month_count.count(8)
					sep = month_count.count(9)
					octo= month_count.count(10)
					nov = month_count.count(11)
					dec = month_count.count(12)
					total = jan+feb+mar+apr+may+jun+jul+aug+sep+octo+nov+dec

					print(jan,feb,mar,apr,may,jun,jul,aug,sep,octo,nov,dec,'----------work days count')

					count+=1

					sr_no.append(count)
					sheet1.write(row,col, count, style_header)
					sheet1.write_merge(row,row,1, 1, emp_code, style_right)
					sheet1.write_merge(row,row,2, 4, emp_name, style_right)
					sheet1.write_merge(row,row,5, 6, job_id, style_right)
					sheet1.write_merge(row,row,7, 8, site_id, style_right)
					sheet1.write_merge(row,row,9, 9, jan, style_right)
					sheet1.write_merge(row,row,10, 10, feb, style_right)
					sheet1.write_merge(row,row,11, 11, mar, style_right)
					sheet1.write_merge(row,row,12, 12, apr, style_right)
					sheet1.write_merge(row,row,13, 13, may, style_right)
					sheet1.write_merge(row,row,14, 14, jun, style_right)
					sheet1.write_merge(row,row,15, 15, jul, style_right)
					sheet1.write_merge(row,row,16, 16, aug, style_right)
					sheet1.write_merge(row,row,17, 17, sep, style_right)
					sheet1.write_merge(row,row,18, 18, octo, style_right)
					sheet1.write_merge(row,row,19, 19, nov, style_right)
					sheet1.write_merge(row,row,20, 20, dec, style_right)
					sheet1.write_merge(row,row,21, 21, total, style_right)

					row+=1

		filename = 'AttendanceExport.xls' 
		response = request.make_response(None,
			headers=[('Content-Type', 'application/vnd.ms-excel'),
					('Content-Disposition', content_disposition(filename))])
		book.save(response.stream)
		return response


## Attendance Summary


	@http.route(['/web/pivot/attendance_summaryreport_xls/<int:appraisal_id>'], type='http', auth="public")
	def attendance_summaryreport_xls(self, appraisal_id, access_token):
		appraisal_data = request.env['attendance.reports'].browse(appraisal_id)
		book = xlwt.Workbook(encoding='utf-8')
		sheet1 = book.add_sheet("Attendance Data")
		style = xlwt.XFStyle()
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
		# style.num_format_str = '0.0'
		# alignment
		alignment = xlwt.Alignment()
		alignment.horz = xlwt.Alignment.HORZ_LEFT
		style.alignment = alignment
		style.alignment.wrap = 100

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
		# style_right.num_format_str = '0.0'
		style_right.alignment.wrap = 12

		alignment3 = xlwt.Alignment()
		alignment3.horz = xlwt.Alignment.HORZ_LEFT
		style_left.alignment = alignment3
		# style_left.num_format_str = '0.0'
		style_left.alignment.wrap = 100

		alignment4 = xlwt.Alignment()
		alignment4.horz = xlwt.Alignment.HORZ_RIGHT
		style_right_bold.alignment = alignment2
		# style_right_bold.num_format_str = '0.0'
		style_right_bold.alignment.wrap = 12

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


		sheet1.write_merge(2, 2, 0, 1, 'From Date:', sub_style)
		sheet1.write_merge(2, 2, 2, 5, appraisal_data.from_date, style)
		sheet1.write_merge(3, 3, 0, 1, 'To Date:', sub_style)
		sheet1.write_merge(3, 3, 2, 5, appraisal_data.to_date, style)
		# sheet1.write_merge(4, 4, 0, 1,'Application Year:', sub_style)
		# sheet1.write_merge(4, 4, 2, 5, appraisal_data.application_year.name, style)

		print (appraisal_data.from_date)
		month_sel = appraisal_data.month_sel
		year_sel = appraisal_data.year_sel.name
		if not appraisal_data.time_period:
			raise ValidationError(_('Kindly select Period!!'))
		if not month_sel:
			raise ValidationError(_('Kindly select Month!!'))
		if not year_sel:
			raise ValidationError(_('Kindly select Year!!'))
		all_dates = monthrange(int(year_sel), int(month_sel))
		all_dates = list(all_dates)

		sheet1.write_merge(6, 6, 0, 25, 'Attendance Data', style_header)
		sheet1.write(8, 0, 'Sr. No.', style_header)
		sheet1.write_merge(8, 8, 1, 1, 'Emp Code', style_header)
		sheet1.write_merge(8, 8, 2, 5, 'Employee Name', style_header)
		col = 6
		row = 8
		for dt in range(1,all_dates[1]+1):
			sheet1.write_merge(row, row, col, col, str(dt), style_header)
			col+=1

		count=0
		sr_no=[]
		row=9
		
		# row = 0
		col = 0
		from_date = appraisal_data.from_date
		to_date = appraisal_data.to_date
		site_master_id = appraisal_data.site_master_id.id
		department_id = appraisal_data.department_id.id
		employee_id = appraisal_data.employee_id.id


		print("11111111111111111",from_date,to_date)
		if site_master_id and not department_id:

			emp_records = request.env['hr.employee'].search([('site_master_id','=',site_master_id)],order='emp_code')
			print(emp_records,'emp_records')
			row1 = 9
			for emp in emp_records:
				# if emp.emp_code in (1,7047):
				count+=1
				sheet1.write(row,col, count, style_header)
				sheet1.write(row,col+1, emp.emp_code, style_right)
				sheet1.write_merge(row,row,2,5,emp.name, style_right)				
				row+=1				
				col1 = 6
				for dt in range(1,all_dates[1]+1):
					# print (dt)
					att_date = str(year_sel) + '-'+str(month_sel)+'-'+str(dt)
				# 	# print (att_date,'att_date')
					attendance_recs = request.env['hr.attendance'].search([('attendance_date','=',str(att_date)),('employee_code','=',emp.emp_code)],order='attendance_date',limit=1)
					if attendance_recs:
						employee_status = attendance_recs.employee_status
						if employee_status == 'half_day_p_ab':
							employee_status = 'Half P + Half AB'
						if employee_status == 'half_day_sl':
							employee_status = 'Half Day SL/CL + Half Day P'
						if employee_status == 'half_day_pl':
							employee_status = 'Half Day PL + Half Day P'
						sheet1.write(row1, col1, employee_status, style_right)
					else:
						sheet1.write(row1, col1, 'AB', style_right)
					col1+=1
				row1+=1
		filename = 'Attendance_Summary_Report.xls' #%(appraisal_data.review_cycle)
		response = request.make_response(None,
			headers=[('Content-Type', 'application/vnd.ms-excel'),
					('Content-Disposition', content_disposition(filename))])
		book.save(response.stream)
		return response