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

month_sel = {'jan': 'January','feb': 'February','mar': 'March','apr': 'April','may': 'May',
			'jun':'June','jul':'July','aug':'August','sep':'September','oct':'October',
			'nov':'November','dec':'December'}

class Binary(http.Controller):

	@http.route(['/web/pivot/quarterly_rating_annual_xls/<int:appraisal_id>'], type='http', auth="public")
	def quarterly_rating_annual_xls(self, appraisal_id, access_token):
		appraisal_data = request.env['quarterly.rating.annual'].browse(appraisal_id)
		book = xlwt.Workbook(encoding='utf-8')
		sheet1 = book.add_sheet("Quarterly Rating Annual")
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
		style.num_format_str = '0.0'
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
		# sheet1.write_merge(2, 2, 0, 1, 'Review Cycle:', sub_style)
		# sheet1.write_merge(2, 2, 2, 5, appraisal_data.review_cycle, style)
		# sheet1.write_merge(3, 3, 0, 1, 'Financial Year:', sub_style)
		# sheet1.write_merge(3, 3, 2, 5, appraisal_data.financial_year.name, style)
		# sheet1.write_merge(4, 4, 0, 1,'Application Year:', sub_style)
		# sheet1.write_merge(4, 4, 2, 5, appraisal_data.application_year.name, style)


		sheet1.write_merge(7, 7, 0, 13, 'Quarterly Rating Report For Annual', style_header)
		sheet1.write(9, 0, 'Sr. No.', style_header)
		sheet1.write_merge(9, 9, 1, 2, 'Reporting Code', style_header)
		sheet1.write_merge(9, 9, 3, 4, 'Reporting Name', style_header)
		# sheet1.write_merge(9, 9, 7, 7, 'Reporting Manager', style_header)
		# sheet1.write_merge(9, 9, 5, 6, 'HR Code', style_header)
		# sheet1.write_merge(9, 9, 7, 8, 'HR Name', style_header)
		sheet1.write_merge(9, 9, 5, 6, 'Employee Code', style_header)
		sheet1.write_merge(9, 9, 7, 8, 'Employee Name', style_header)
		sheet1.write_merge(9, 9, 9, 10, 'Department', style_header)
		sheet1.write_merge(9, 9, 11, 12, 'Designation', style_header)
		sheet1.write_merge(9, 9, 13, 14, 'Joining Date', style_header)
		sheet1.write_merge(9, 9, 15, 16, 'Quarter1', style_header)
		sheet1.write_merge(10, 10, 15, 15, 'Ratings', style_header)
		sheet1.write_merge(10, 10, 16, 16, 'Status', style_header)
		sheet1.write_merge(9, 9, 17, 18, 'Quarter2', style_header)
		sheet1.write_merge(10, 10, 17, 17, 'Ratings', style_header)
		sheet1.write_merge(10, 10, 18, 18, 'Status', style_header)
		sheet1.write_merge(9, 9, 19, 20, 'Quarter3', style_header)
		sheet1.write_merge(10, 10, 19, 19, 'Ratings', style_header)
		sheet1.write_merge(10, 10, 20, 20, 'Status', style_header)
		sheet1.write_merge(9, 9, 21, 22, 'Quarter4', style_header)
		sheet1.write_merge(10, 10, 21, 21, 'Ratings', style_header)
		sheet1.write_merge(10, 10, 22, 22, 'Status', style_header)
		sheet1.write_merge(9, 9, 23, 24, 'Eligible For PIP', style_header)

		count=0
		sr_no=[]
		row=11
		eligible_for_pip = ''
		for x in appraisal_data.quarterly_rating_annual_one2many:
				if x.eligible_for_pip:
					eligible_for_pip = 'Yes'
				else:
					eligible_for_pip = 'No'
				print(x.employee.name,'iiiiiiiiiiiii')
				count+=1
				sr_no.append(count)
				sheet1.write(row,col, count, style_header)
				sheet1.write_merge(row,row,1, 2, x.reporting_code, style_left)
				sheet1.write_merge(row,row,3, 4, x.reporting_name, style_left)
				# sheet1.write_merge(row,row,5, 6, x.hr_code, style_right)
				# sheet1.write_merge(row,row,7, 8, x.hr_name, style_right)
				sheet1.write_merge(row,row,5, 6, x.employee_code, style_right)
				sheet1.write_merge(row,row,7, 8, x.employee_name, style_right)
				sheet1.write_merge(row,row,9, 10, x.department.name, style_right)
				sheet1.write_merge(row,row,11, 12, x.designation.name, style_right)
				sheet1.write_merge(row,row,13, 14, x.joining_date, style_right)
				sheet1.write_merge(row,row,15, 15, x.quarter1, style_right)
				sheet1.write_merge(row,row,17, 17, x.quarter2, style_right)
				sheet1.write_merge(row,row,19, 19, x.quarter3, style_right)
				sheet1.write_merge(row,row,21, 21, x.quarter4, style_right)
				sheet1.write_merge(row,row,16, 16, x.q1_status, style_right)
				sheet1.write_merge(row,row,18, 18, x.q2_status, style_right)
				sheet1.write_merge(row,row,20, 20, x.q3_status, style_right)
				sheet1.write_merge(row,row,22, 22, x.q4_status, style_right)
				sheet1.write_merge(row,row,23, 24, eligible_for_pip, style_right)
				row+=1

		filename = 'QuarterlyRatingForAnnual.xls' #%(appraisal_data.review_cycle)
		response = request.make_response(None,
			headers=[('Content-Type', 'application/vnd.ms-excel'),
					('Content-Disposition', content_disposition(filename))])
		book.save(response.stream)
		return response

	@http.route(['/web/pivot/export_mapping_xls/<int:appraisal_id>'], type='http', auth="public")
	def export_mapping_xls(self, appraisal_id, access_token):
		appraisal_data = request.env['kra.mapping.report'].browse(appraisal_id)
		book = xlwt.Workbook(encoding='utf-8')
		sheet1 = book.add_sheet("PySheet1")
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
		style.num_format_str = '0.0'
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
		# sheet1.write_merge(2, 2, 0, 1, 'Review Cycle:', sub_style)
		# sheet1.write_merge(2, 2, 2, 5, appraisal_data.review_cycle, style)
		# sheet1.write_merge(3, 3, 0, 1, 'Financial Year:', sub_style)
		# sheet1.write_merge(3, 3, 2, 5, appraisal_data.financial_year.name, style)
		# sheet1.write_merge(4, 4, 0, 1,'Application Year:', sub_style)
		# sheet1.write_merge(4, 4, 2, 5, appraisal_data.application_year.name, style)


		sheet1.write_merge(7, 7, 0, 13, 'KRA Mapping Report', style_header)
		sheet1.write(9, 0, 'Sr. No.', style_header)
		sheet1.write_merge(9, 9, 1, 2, 'Reporting Code', style_header)
		sheet1.write_merge(9, 9, 3, 4, 'Reporting Name', style_header)
		# sheet1.write_merge(9, 9, 7, 7, 'Reporting Manager', style_header)
		# sheet1.write_merge(9, 9, 5, 6, 'HR Code', style_header)
		# sheet1.write_merge(9, 9, 7, 8, 'HR Name', style_header)
		sheet1.write_merge(9, 9, 5, 6, 'Employee Code', style_header)
		sheet1.write_merge(9, 9, 7, 8, 'Employee Name', style_header)
		sheet1.write_merge(9, 9, 9, 10, 'Department', style_header)
		sheet1.write_merge(9, 9, 11, 12, 'Designation', style_header)
		sheet1.write_merge(9, 9, 13, 14, 'Joining Date', style_header)
		sheet1.write_merge(9, 9, 15, 16, 'Kra Mapped', style_header)
		sheet1.write_merge(9, 9, 17, 18, 'Status', style_header)
		count=0
		sr_no=[]
		row=10

		for x in appraisal_data.mapping_report_one2many:
			# if x.select:
				kra_mapped =''
				if x.kra_mapped == 'yes':
					kra_mapped = 'Yes'
				else:
					kra_mapped = 'No'
				print(x.employee.name,'iiiiiiiiiiiii')
				count+=1
				sr_no.append(count)
				sheet1.write(row,col, count, style_header)
				sheet1.write_merge(row,row,1, 2, x.reporting_code, style_left)
				sheet1.write_merge(row,row,3, 4, x.reporting_name, style_left)
				# sheet1.write_merge(row,row,5, 6, x.hr_code, style_right)
				# sheet1.write_merge(row,row,7, 8, x.hr_name, style_right)
				sheet1.write_merge(row,row,5, 6, x.employee_code, style_right)
				sheet1.write_merge(row,row,7, 8, x.employee_name, style_right)
				sheet1.write_merge(row,row,9, 10, x.department.name, style_right)
				sheet1.write_merge(row,row,11, 12, x.designation.name, style_right)
				sheet1.write_merge(row,row,13, 14, x.joining_date, style_right)
				sheet1.write_merge(row,row,15, 16, kra_mapped, style_right)
				sheet1.write_merge(row,row,17, 18, x.status, style_right)
				row+=1

		filename = 'KraMappingReport.xls' #%(appraisal_data.review_cycle)
		response = request.make_response(None,
			headers=[('Content-Type', 'application/vnd.ms-excel'),
					('Content-Disposition', content_disposition(filename))])
		book.save(response.stream)
		return response


	@http.route(['/web/pivot/export_due_xls/<int:appraisal_id>'], type='http', auth="public")
	def export_due_xls(self, appraisal_id, access_token):
		appraisal_data = request.env['appraisal.due.report'].browse(appraisal_id)
		book = xlwt.Workbook(encoding='utf-8')
		sheet1 = book.add_sheet("Appraisal Due")
		sheet2 = book.add_sheet("Appraisal Due (PIP Applicable)")
		sheet3 = book.add_sheet("Appraisal Due (Skipped Employees)")
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
		style.num_format_str = '0.0'
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
		sheet1.write_merge(2, 2, 0, 1, 'Review Cycle:', sub_style)
		sheet1.write_merge(2, 2, 2, 5, appraisal_data.review_cycle, style)
		sheet1.write_merge(3, 3, 0, 1, 'Financial Year:', sub_style)
		sheet1.write_merge(3, 3, 2, 5, appraisal_data.financial_year.name, style)
		sheet1.write_merge(4, 4, 0, 1,'Application Year:', sub_style)
		sheet1.write_merge(4, 4, 2, 5, appraisal_data.application_year.name, style)


		sheet1.write_merge(7, 7, 0, 13, 'Appraisal Due Report', style_header)
		sheet1.write(9, 0, 'Sr. No.', style_header)
		sheet1.write_merge(9, 9, 1, 5, 'Employee', style_header)
		sheet1.write_merge(9, 9, 6, 6, 'Employee Code', style_header)
		sheet1.write_merge(9, 9, 7, 7, 'Joining Date', style_header)
		sheet1.write_merge(9, 9, 8, 8, 'Reporting Manager', style_header)
		sheet1.write_merge(9, 9, 9, 9, 'Department', style_header)
		sheet1.write_merge(9, 9, 10, 10, 'Designation', style_header)
		sheet1.write_merge(9, 9, 11, 11, 'Review Cycle', style_header)
		sheet1.write_merge(9, 9, 12, 12, 'Quarter 1', style_header)
		sheet1.write_merge(9, 9, 13, 13, 'Quarter 2', style_header)
		sheet1.write_merge(9, 9, 14, 14, 'Quarter 3', style_header)
		sheet1.write_merge(9, 9, 15, 15, 'Quarter 4', style_header)
		sheet1.write_merge(9, 9, 16, 16, 'Position Type', style_header)

		count=0
		sr_no=[]
		row=10

		for x in appraisal_data.appraisal_one2many:
			# if x.select:
				print(x.employee.name,'iiiiiiiiiiiii')
				count+=1
				sr_no.append(count)
				sheet1.write(row,col, count, style_header)
				sheet1.write_merge(row,row,1, 5, x.employee.name, style_left)
				sheet1.write_merge(row,row,6, 6, x.emp_code, style_left)
				sheet1.write_merge(row,row,7, 7, x.joining_date, style_right)
				sheet1.write_merge(row,row,8, 8, x.parent_id.name, style_right)
				sheet1.write_merge(row,row,9, 9, x.department.name, style_right)
				sheet1.write_merge(row,row,10, 10, x.designation.name, style_right)
				sheet1.write_merge(row,row,11, 11, x.appraisal_cycle, style_right)
				sheet1.write_merge(row,row,12, 12, x.quarter1, style_right)
				sheet1.write_merge(row,row,13, 13, x.quarter2, style_right)
				sheet1.write_merge(row,row,14, 14, x.quarter3, style_right)
				sheet1.write_merge(row,row,15, 15, x.quarter4, style_right)
				sheet1.write_merge(row,row,16, 16, x.position_type, style_right)
				row+=1

		row = 0
		col = 0

		sheet2.write_merge(2, 2, 0, 1, 'Review Cycle:', sub_style)
		sheet2.write_merge(2, 2, 2, 5, appraisal_data.review_cycle, style)
		sheet2.write_merge(3, 3, 0, 1, 'Financial Year:', sub_style)
		sheet2.write_merge(3, 3, 2, 5, appraisal_data.financial_year.name, style)
		sheet2.write_merge(4, 4, 0, 1,'Application Year:', sub_style)
		sheet2.write_merge(4, 4, 2, 5, appraisal_data.application_year.name, style)


		sheet2.write_merge(7, 7, 0, 13, 'Appraisal Due Report (PIP Applicable)', style_header)
		sheet2.write(9, 0, 'Sr. No.', style_header)
		sheet2.write_merge(9, 9, 1, 5, 'Employee', style_header)
		sheet2.write_merge(9, 9, 6, 6, 'Employee Code', style_header)
		sheet2.write_merge(9, 9, 7, 7, 'Joining Date', style_header)
		sheet2.write_merge(9, 9, 8, 8, 'Reporting Manager', style_header)
		sheet2.write_merge(9, 9, 9, 9, 'Department', style_header)
		sheet2.write_merge(9, 9, 10, 10, 'Designation', style_header)
		sheet2.write_merge(9, 9, 11, 11, 'Review Cycle', style_header)
		sheet2.write_merge(9, 9, 12, 12, 'Quarter 1', style_header)
		sheet2.write_merge(9, 9, 13, 13, 'Quarter 2', style_header)
		sheet2.write_merge(9, 9, 14, 14, 'Quarter 3', style_header)
		sheet2.write_merge(9, 9, 15, 15, 'Quarter 4', style_header)
		sheet2.write_merge(9, 9, 16, 16, 'Position Type', style_header)

		count=0
		sr_no=[]
		row=10

		for x in appraisal_data.pip_appraisal_one2many:
			# if x.select:
				print(x.employee.name,'iiiiiiiiiiiii')
				count+=1
				sr_no.append(count)
				sheet2.write(row,col, count, style_header)
				sheet2.write_merge(row,row,1, 5, x.employee.name, style_left)
				sheet2.write_merge(row,row,6, 6, x.emp_code, style_left)
				sheet2.write_merge(row,row,7, 7, x.joining_date, style_right)
				sheet2.write_merge(row,row,8, 8, x.parent_id.name, style_right)
				sheet2.write_merge(row,row,9, 9, x.department.name, style_right)
				sheet2.write_merge(row,row,10, 10, x.designation.name, style_right)
				sheet2.write_merge(row,row,11, 11, x.appraisal_cycle, style_right)
				sheet2.write_merge(row,row,12, 12, x.quarter1, style_right)
				sheet2.write_merge(row,row,13, 13, x.quarter2, style_right)
				sheet2.write_merge(row,row,14, 14, x.quarter3, style_right)
				sheet2.write_merge(row,row,15, 15, x.quarter4, style_right)
				sheet2.write_merge(row,row,16, 16, x.position_type, style_right)
				row+=1

		row = 0
		col = 0
		
		sheet3.write_merge(2, 2, 0, 1, 'Review Cycle:', sub_style)
		sheet3.write_merge(2, 2, 2, 5, appraisal_data.review_cycle, style)
		sheet3.write_merge(3, 3, 0, 1, 'Financial Year:', sub_style)
		sheet3.write_merge(3, 3, 2, 5, appraisal_data.financial_year.name, style)
		sheet3.write_merge(4, 4, 0, 1,'Application Year:', sub_style)
		sheet3.write_merge(4, 4, 2, 5, appraisal_data.application_year.name, style)


		sheet3.write_merge(7, 7, 0, 13, 'Appraisal Due Report (Skipped Employees)', style_header)
		sheet3.write(9, 0, 'Sr. No.', style_header)
		sheet3.write_merge(9, 9, 1, 5, 'Employee', style_header)
		sheet3.write_merge(9, 9, 6, 6, 'Employee Code', style_header)
		sheet3.write_merge(9, 9, 7, 7, 'Joining Date', style_header)
		sheet3.write_merge(9, 9, 8, 8, 'Reporting Manager', style_header)
		sheet3.write_merge(9, 9, 9, 9, 'Department', style_header)
		sheet3.write_merge(9, 9, 10, 10, 'Designation', style_header)
		sheet3.write_merge(9, 9, 11, 11, 'Review Cycle', style_header)
		sheet3.write_merge(9, 9, 12, 12, 'Quarter 1', style_header)
		sheet3.write_merge(9, 9, 13, 13, 'Quarter 2', style_header)
		sheet3.write_merge(9, 9, 14, 14, 'Quarter 3', style_header)
		sheet3.write_merge(9, 9, 15, 15, 'Quarter 4', style_header)
		sheet3.write_merge(9, 9, 16, 16, 'Position Type', style_header)

		count=0
		sr_no=[]
		row=10

		for x in appraisal_data.skipped_appraisal_one2many:
			# if x.select:
				print(x.employee.name,'iiiiiiiiiiiii')
				count+=1
				sr_no.append(count)
				sheet3.write(row,col, count, style_header)
				sheet3.write_merge(row,row,1, 5, x.employee.name, style_left)
				sheet3.write_merge(row,row,6, 6, x.emp_code, style_left)
				sheet3.write_merge(row,row,7, 7, x.joining_date, style_right)
				sheet3.write_merge(row,row,8, 8, x.parent_id.name, style_right)
				sheet3.write_merge(row,row,9, 9, x.department.name, style_right)
				sheet3.write_merge(row,row,10, 10, x.designation.name, style_right)
				sheet3.write_merge(row,row,11, 11, x.appraisal_cycle, style_right)
				sheet3.write_merge(row,row,12, 12, x.quarter1, style_right)
				sheet3.write_merge(row,row,13, 13, x.quarter2, style_right)
				sheet3.write_merge(row,row,14, 14, x.quarter3, style_right)
				sheet3.write_merge(row,row,15, 15, x.quarter4, style_right)
				sheet3.write_merge(row,row,16, 16, x.position_type, style_right)
				row+=1

		filename = 'AppraisalDueReport_%s.xls' %(appraisal_data.review_cycle)
		response = request.make_response(None,
			headers=[('Content-Type', 'application/vnd.ms-excel'),
					('Content-Disposition', content_disposition(filename))])
		book.save(response.stream)
		return response


	@http.route(['/web/pivot/export_status_xls/<int:status_id>'], type='http', auth="public")
	def export_status_xls(self, status_id, access_token):
		appraisal_data = request.env['annual.review.status.report'].browse(status_id)
		site_list = []
		for x in appraisal_data:
			print (x.site_id)
			for m in x.site_id:
				site_list.append(m.name)
		print(appraisal_data)
		book = xlwt.Workbook(encoding='utf-8')
		sheet1 = book.add_sheet("PySheet1")
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
		style.num_format_str = '0.0'
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
		style_right.num_format_str = '0.0'
		style_right.alignment.wrap = 120

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
		sheet1.write_merge(2, 2, 0, 1, 'Company:', sub_style)
		sheet1.write_merge(2, 2, 2, 5, appraisal_data.company_id.name, style)
		sheet1.write_merge(3, 3, 0, 1, 'Financial Year:', sub_style)
		sheet1.write_merge(3, 3, 2, 5, appraisal_data.financial_year.name, style)
		sheet1.write_merge(4, 4, 0, 1,'Application Year:', sub_style)
		sheet1.write_merge(4, 4, 2, 5, appraisal_data.year_of_application.name, style)
		sheet1.write_merge(5, 5, 0, 1,'Location:', sub_style)
		sheet1.write_merge(5, 5, 2, 5, ', '.join(site_list), style)
		sheet1.write_merge(7, 7, 6, 7, appraisal_data.form_type, style)


		# sheet1.write_merge(9, 9, 0, 13, 'Appraisal Due Report', style_header)
		sheet1.write(9, 0, 'Sr. No.', style_header)
		sheet1.write_merge(9, 9, 1, 5, 'Employee', style_header)
		sheet1.write_merge(9, 9, 6, 6, 'Employee Code', style_header)
		sheet1.write_merge(9, 9, 7, 7, 'Location', style_header)
		sheet1.write_merge(9, 9, 8, 8, 'Department', style_header)
		sheet1.write_merge(9, 9, 9, 9, 'Designation', style_header)
		sheet1.write_merge(9, 9, 10, 10, 'Reporting To', style_header)
		sheet1.write_merge(9, 9, 11, 11, 'Application Date', style_header)
		sheet1.write_merge(9, 9, 12, 12, 'Financial Year', style_header)
		sheet1.write_merge(9, 9, 13, 14, 'Status', style_header)
		sheet1.write_merge(9, 9, 15, 16, 'Approved Date', style_header)

		count=0
		sr_no=[]
		row=10

		for x in appraisal_data.annual_review_one2many:
			# if x.select:
				status=''
				print(x.employee.name,'iiiiiiiiiiiii')
				count+=1
				# if appraisal_data.form_type == 'Goalsheet':
				# 	if x.status=='pending':
				# 		status="Pending"
				# 	if x.status=='approved':
				# 		status='Approved'
				# 	if x.status=='rejected':
				# 		status="Rejected"
				# else:
				# 	if x.approve1_char!='':
				# 		status = status +'\n' +x.approve1_char
				# 	if x.approve2_char!='':
				# 		status = status +'\n' +x.approve2_char
				# 	if x.approve3_char!='':
				# 		status = status +'\n' +x.approve3_char
				# 	if x.approve4_char!='':
				# 		status = status +'\n' +x.approve4_char
				# print (status,'status')
				sr_no.append(count)
				sheet1.row(row).height_mismatch = True
				sheet1.row(row).height = 23*48
				sheet1.write(row,col, count, style_header)
				sheet1.write_merge(row,row,1, 5, x.employee.name, style_left)
				sheet1.write_merge(row,row,6, 6, int(x.employee_code), style_left)
				sheet1.write_merge(row,row,7, 7, x.employee.site_master_id.name, style_right)
				sheet1.write_merge(row,row,8, 8, x.employee.department_id.name, style_right)
				sheet1.write_merge(row,row,9, 9, x.employee.job_id.name, style_right)
				sheet1.write_merge(row,row,10, 10, x.employee.parent_id.name, style_right)
				sheet1.write_merge(row,row,11, 11, x.application_date, style_right)
				sheet1.write_merge(row,row,12, 12, x.financial_year.name, style_right)
				sheet1.write_merge(row,row,13, 14, x.status, style_left)
				sheet1.write_merge(row,row,15, 16, x.approved_date, style_right)
				row+=1

		filename = 'AppraisalStatusReport_%s.xls' %(appraisal_data.review_cycle)
		response = request.make_response(None,
			headers=[('Content-Type', 'application/vnd.ms-excel'),
					('Content-Disposition', content_disposition(filename))])
		book.save(response.stream)
		return response

	@http.route(['/web/pivot/export_increment_status_xls/<int:status_id1>'], type='http', auth="public")
	def export_increment_status_xls(self, status_id1, access_token):
		appraisal_data = request.env['increment.status.report'].browse(status_id1)
		print(appraisal_data)
		book = xlwt.Workbook(encoding='utf-8')
		sheet1 = book.add_sheet("PySheet1")
		style = xlwt.XFStyle()
		style_header = xlwt.XFStyle()
		style_right = xlwt.XFStyle()
		style_right_bold = xlwt.XFStyle()
		style_left = xlwt.XFStyle()
		font = xlwt.Font()
		font.bold = True
		style.font = font
		style_header.font = font
		style_header.num_format_str = '0.00'
		style_right_bold.font = font
		# background color
		pattern = xlwt.Pattern()
		pattern.pattern = xlwt.Pattern.SOLID_PATTERN
		pattern.pattern_fore_colour = xlwt.Style.colour_map['pale_blue']
		style.pattern = pattern
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
		style_right.num_format_str = '0.00'
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
		sheet1.write_merge(2, 2, 0, 1, 'Year:', sub_style)
		sheet1.write_merge(2, 2, 2, 5, appraisal_data.year.name, style)
		sheet1.write_merge(3, 3, 0, 1, 'Review Month:', sub_style)
		sheet1.write_merge(3, 3, 2, 5, appraisal_data.review_month, style)

		if appraisal_data.report_type == 'tl':
			sheet1.write(5, 0, 'Sr. No.', style_header)
			sheet1.write_merge(5, 5, 1, 5, 'TL Code', style_header)
			sheet1.write_merge(5, 5, 6, 6, 'TL Name', style_header)
			sheet1.write_merge(5, 5, 7, 7, 'Department', style_header)
			sheet1.write_merge(5, 5, 8, 8, 'Increment Status', style_header)

			count=0
			sr_no=[]
			row=7

			for x in appraisal_data.increment_status_one2many_tl:
				# if x.select:
					print(x.employee.name,'iiiiiiiiiiiii')
					count+=1
					sr_no.append(count)
					if x.increment_status == 'updated':
						increment_status = 'Updated'
					if x.increment_status == 'not_updated':
						increment_status = 'Not Updated'
					sheet1.write(row,col, count, style_header)
					sheet1.write_merge(row,row, 1, 5, x.tl_code, style_left)
					sheet1.write_merge(row,row, 6, 6, x.tl_name.name, style_left)
					sheet1.write_merge(row,row, 7, 7, x.department.name, style_right)
					sheet1.write_merge(row,row, 8, 8, increment_status, style_right)
					row+=1
		if appraisal_data.report_type == 'emp':
		# sheet1.write_merge(9, 9, 0, 13, 'Appraisal Due Report', style_header)
			sheet1.write(5, 0, 'Sr. No.', style_header)
			sheet1.write_merge(5, 5, 1, 5, 'TL Code', style_header)
			sheet1.write_merge(5, 5, 6, 6, 'TL Name', style_header)
			sheet1.write_merge(5, 5, 7, 7, 'Employee Code', style_header)
			sheet1.write_merge(5, 5, 8, 8, 'Employee Name', style_header)
			sheet1.write_merge(5, 5, 9, 9, 'Department', style_header)
			sheet1.write_merge(5, 5, 10, 10, 'Increment Status', style_header)

			count=0
			sr_no=[]
			row=7

			for x in appraisal_data.increment_status_one2many_emp:
				# if x.select:
					print(x.employee.name,'iiiiiiiiiiiii')
					count+=1
					increment_status =''
					sr_no.append(count)
					if x.increment_status == 'updated':
						increment_status = 'Updated'
					if x.increment_status == 'not_updated':
						increment_status = 'Not Updated'
					sheet1.write(row,col, count, style_header)
					sheet1.write_merge(row,row, 1, 5, x.tl_code, style_left)
					sheet1.write_merge(row,row, 6, 6, x.tl_name.name, style_left)
					sheet1.write_merge(row,row, 7, 7, x.employee_code, style_right)
					sheet1.write_merge(row,row, 8, 8, x.employee.name, style_right)
					sheet1.write_merge(row,row, 9, 9, x.department.name, style_right)
					sheet1.write_merge(row,row, 10, 10, increment_status, style_right)
					row+=1
		filename = 'IncrementStatusReport_%s.xls' %(appraisal_data.review_month)
		response = request.make_response(None,
			headers=[('Content-Type', 'application/vnd.ms-excel'),
					('Content-Disposition', content_disposition(filename))])
		book.save(response.stream)
		return response
	

	@http.route(['/web/pivot/export_increment_xls/<int:status_id1>'], type='http', auth="public")
	def export_increment_xls(self, status_id1, access_token):
		appraisal_data = request.env['increment.report'].browse(status_id1)
		print(appraisal_data)
		book = xlwt.Workbook(encoding='utf-8')
		sheet1 = book.add_sheet("PySheet1")
		style = xlwt.XFStyle()
		style_header = xlwt.XFStyle()
		style_right = xlwt.XFStyle()
		style_right_bold = xlwt.XFStyle()
		style_left = xlwt.XFStyle()
		font = xlwt.Font()
		font.bold = True
		style.font = font
		style_header.font = font
		style_header.num_format_str = '0.00'
		style_right_bold.font = font
		# background color
		pattern = xlwt.Pattern()
		pattern.pattern = xlwt.Pattern.SOLID_PATTERN
		pattern.pattern_fore_colour = xlwt.Style.colour_map['pale_blue']
		style.pattern = pattern
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
		style_right.num_format_str = '0.00'
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
		sheet1.write_merge(2, 2, 0, 1, 'Year:', sub_style)
		sheet1.write_merge(2, 2, 2, 5, appraisal_data.year.name, style)
		sheet1.write_merge(3, 3, 0, 1, 'Review Month:', sub_style)
		sheet1.write_merge(3, 3, 2, 5, appraisal_data.review_month, style)


		# sheet1.write_merge(9, 9, 0, 13, 'Appraisal Due Report', style_header)
		sheet1.write(5, 0, 'Sr. No.', style_header)
		sheet1.write_merge(5, 5, 1, 5, 'Employee', style_header)
		sheet1.write_merge(5, 5, 6, 6, 'Employee Code', style_header)
		sheet1.write_merge(5, 5, 7, 7, 'Department', style_header)
		sheet1.write_merge(5, 5, 8, 8, 'TL IKRA', style_header)
		sheet1.write_merge(5, 5, 9, 9, 'TL IAR', style_header)
		sheet1.write_merge(5, 5, 10, 10, 'Reportee2 IKRA', style_header)
		sheet1.write_merge(5, 5, 11, 11, 'Reportee2 IAR', style_header)
		sheet1.write_merge(5, 5, 12, 12, 'Reportee3 IKRA', style_header)
		sheet1.write_merge(5, 5, 13, 13, 'Reportee3 IAR', style_header)
		sheet1.write_merge(5, 5, 14, 14, 'HR IKRA', style_header)
		sheet1.write_merge(5, 5, 15, 15, 'HR IAR', style_header)
		sheet1.write_merge(5, 5, 16, 16, 'SUM IKRA', style_header)
		sheet1.write_merge(5, 5, 17, 17, 'SUM IAR', style_header)
		sheet1.write_merge(5, 5, 18, 18, 'Current Gross', style_header)
		sheet1.write_merge(5, 5, 19, 19, 'Current CTC', style_header)
		sheet1.write_merge(5, 5, 20, 20, 'Proposed Increment', style_header)
		sheet1.write_merge(5, 5, 21, 21, 'Weightage', style_header)
		sheet1.write_merge(5, 5, 22, 22, 'TL Actual Increment', style_header)
		sheet1.write_merge(5, 5, 23, 23, 'Final Increment', style_header)

		count=0
		sr_no=[]
		row=7

		for x in appraisal_data.increment_one2many:
			# if x.select:
				print(x.employee_name,'iiiiiiiiiiiii')
				count+=1
				sr_no.append(count)
				sheet1.write(row,col, count, style_header)
				sheet1.write_merge(row,row, 1, 5, x.employee.name, style_left)
				sheet1.write_merge(row,row, 6, 6, x.employee_code, style_left)
				sheet1.write_merge(row,row, 7, 7, x.department.name, style_right)
				sheet1.write_merge(row,row, 8, 8, x.tl_ikra, style_right)
				sheet1.write_merge(row,row, 9, 9, x.tl_iar, style_right)
				sheet1.write_merge(row,row, 10, 10, x.reportee2_ikra, style_right)
				sheet1.write_merge(row,row, 11, 11, x.reportee2_iar, style_right)
				sheet1.write_merge(row,row, 12, 12, x.reportee3_ikra, style_right)
				sheet1.write_merge(row,row, 13, 13, x.reportee3_iar, style_right)
				sheet1.write_merge(row,row, 14, 14, x.hr_ikra, style_right)
				sheet1.write_merge(row,row, 15, 15, x.hr_iar, style_right)
				sheet1.write_merge(row,row, 16, 16, x.sum_ikra, style_right)
				sheet1.write_merge(row,row, 17, 17, x.sum_iar, style_right)
				sheet1.write_merge(row,row, 18, 18, x.current_gross, style_right)
				sheet1.write_merge(row,row, 19, 19, x.current_ctc, style_right)
				sheet1.write_merge(row,row, 20, 20, x.proposed_increment, style_right)
				sheet1.write_merge(row,row, 21, 21, x.weightage, style_right)
				sheet1.write_merge(row,row, 22, 22, x.actual_increment, style_right)
				sheet1.write_merge(row,row, 23, 23, x.final_increment, style_right)
				row+=1

		filename = 'IncrementReport_%s.xls' %(appraisal_data.review_month)
		response = request.make_response(None,
			headers=[('Content-Type', 'application/vnd.ms-excel'),
					('Content-Disposition', content_disposition(filename))])
		book.save(response.stream)
		return response

	@http.route(['/web/pivot/export_xls/<int:kra_id>'], type='http', auth="public")
	def export_xls(self, kra_id, access_token):
		kra_data = request.env['kra.main'].browse(kra_id)
		final_rating = float(kra_data.final_rating)
		book = xlwt.Workbook(encoding='utf-8')
		sheet1 = book.add_sheet("PySheet1")
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
		style.num_format_str = '0.0'
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
		sheet1.write_merge(row, row, 0, 13, 'Quarterly KRA Review Report', style_header)
		sheet1.write_merge(2, 2, 0, 1, 'Name:', sub_style)
		sheet1.write_merge(2, 2, 2, 5, kra_data.employee.name, style)
		sheet1.write_merge(3, 3, 0, 1, 'Designation:', sub_style)
		sheet1.write_merge(3, 3, 2, 5, kra_data.designation.name, style)
		sheet1.write_merge(4, 4, 0, 1,'Location:', sub_style)
		sheet1.write_merge(4, 4, 2, 5, kra_data.location.name, style)
		sheet1.write_merge(5, 5, 0, 1, 'Year:', sub_style)
		sheet1.write_merge(5, 5, 2, 5, kra_data.kra_year.name, style)
		sheet1.write_merge(6, 6, 0, 1, 'Rating:', sub_style)
		sheet1.write_merge(6, 6, 2, 5, kra_data.final_rating, style)

		sheet1.write_merge(2, 2, 7, 8, 'Employee Code:', sub_style)
		sheet1.write_merge(2, 2, 9, 12, kra_data.employee_code, style)
		sheet1.write_merge(3, 3, 7, 8, 'Department:', sub_style)
		sheet1.write_merge(3, 3, 9, 12, kra_data.department.name, style)
		sheet1.write_merge(5, 5, 7, 8, 'Month:', sub_style)
		sheet1.write_merge(5, 5, 9, 12, month_sel.get(kra_data.kra_month), style)

		sheet1.write_merge(8, 8, 0, 13, 'Quarterly KRA Review Form', style_header)
		sheet1.write(9, 0, 'Sr. No.', style_header)
		sheet1.write_merge(9, 9, 1, 5, 'Key Result Area', style_header)
		sheet1.write_merge(9, 9, 6, 9, 'Key Performance Indicator', style_header)
		sheet1.write_merge(9, 9, 10, 10, 'Weightage', style_header)
		sheet1.write_merge(9, 9, 11, 11, 'Self', style_header)
		sheet1.write_merge(9, 9, 12, 12, 'Team Leader', style_header)
		sheet1.write_merge(9, 9, 13, 13, 'Document', style_header)
		count=0
		sr_no=[]
		row=10
		total_man_rating=0.0
		total_emp_rating=0.0
		for x in kra_data.kra_one2many:
			total_emp_rating += x.emp_rating
			total_man_rating += x.man_rating
			count+=1
			sr_no.append(count)
			sheet1.write(row,col, count, style_header)
			sheet1.write_merge(row,row,1,5, x.kra_name, style_left)
			sheet1.write_merge(row,row,6,9, x.description, style_left)
			sheet1.write_merge(row,row,10,10, x.weightage, style_right)
			sheet1.write_merge(row,row,11,11, x.emp_rating, style_right)
			sheet1.write_merge(row,row,12,12, x.man_rating, style_right)
			row+=1
		sheet1.write_merge(row,row,1,9, 'GRAND TOTAL', style_header)
		sheet1.write_merge(row,row,10,10, '100.0', style_right_bold)
		sheet1.write_merge(row,row,11,11, total_emp_rating, style_right_bold)
		sheet1.write_merge(row,row,12,12, total_man_rating, style_right_bold)
		sheet1.col(row).width = 7000
		row1=row
		row1+=2
		sheet1.write_merge(row1, row1, 0, 13, 'Quarterly Review Meeting', style_header)
		row1+=1
		sheet1.write(row1,0, 'Sr. No.', style_header)
		sheet1.write_merge(row1, row1, 1,5,'Agenda', style_header)
		sheet1.write_merge(row1, row1, 6,8,'Outcomes', style_header)
		sheet1.write_merge(row1, row1, 9,12,'Action To Be Taken', style_header)
		sheet1.write_merge(row1, row1, 13,13,'Deadline Date', style_header)

		count=0
		row1+=1
		for y in kra_data.quarterly_meeting_one2many:
			count+=1
			sheet1.write(row1,col, count, style_header)
			sheet1.write_merge(row1,row1,1,5, y.agenda_item, style_left)
			if y.outcomes==False:
				sheet1.write_merge(row1,row1,6,8, '', style_header)
			else:
				sheet1.write_merge(row1,row1,6,8, y.outcomes, style_left)
			if y.action_taken==False:
				sheet1.write_merge(row1,row1,9,12, '', style_right)
			else:
				sheet1.write_merge(row1,row1,9,12, y.action_taken, style_left)
			if y.deadline_date==False:
				sheet1.write_merge(row1,row1,13,13, '', style_right)
			else:
				sheet1.write_merge(row1,row1,13,13, y.deadline_date, style_left)
			row1+=1
		filename = 'KRA_%s.xls' %(kra_data.employee.name)
		response = request.make_response(None,
			headers=[('Content-Type', 'application/vnd.ms-excel'),
					('Content-Disposition', content_disposition(filename))])
		book.save(response.stream)
		return response

	@http.route(['/web/pivot/export_qr_status_xls/<int:kra_id>'], type='http', auth="public")
	def export_qr_status_xls(self, kra_id, access_token):
		qr_status = request.env['qr.status.report'].browse(kra_id)
		quarter = qr_status.quarter
		year = qr_status.kra_year.name
		book = xlwt.Workbook(encoding='utf-8')
		sheet1 = book.add_sheet("Quarterly_Review_Status_Report")
		sheet1.row(4).height_mismatch = True
		sheet1.row(4).height = 26*20
		style = xlwt.XFStyle()
		style_header = xlwt.XFStyle()
		style_right = xlwt.XFStyle()
		style_right_bold = xlwt.XFStyle()
		style_left = xlwt.XFStyle()
		style_left_light = xlwt.XFStyle()
		style_center = xlwt.XFStyle()
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
		style_header.alignment.wrap = 1
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
		alignment5.horz = xlwt.Alignment.HORZ_CENTER
		style_center.alignment = alignment5
		# style_center.num_format_str = '0.0'
		style_center.alignment.wrap = 12

		alignment6 = xlwt.Alignment()
		alignment6.horz = xlwt.Alignment.HORZ_LEFT
		style_left_light.alignment = alignment6
		# style_center.num_format_str = '0.0'
		style_left_light.alignment.wrap = 12

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
		style_center.borders = borders
		style_left_light.borders = borders

		row = 0
		col = 0
		report_date = "Report Date : "+ str(datetime.now().date().strftime("%d/%m/%Y"))
		string = "Review Quarter : " + quarter + " Financial Year : " + year + " (" + qr_status.duration_string + ")"
		sheet1.write_merge(row, row, 0, 15, report_date, style_right_bold)
		sheet1.write_merge(row+1, row+1, 0, 15, 'Orient Technologies PVT LTD', style_header)
		sheet1.write_merge(row+2, row+2, 0, 15, 'Quarterly Review Status Report', style_header)
		sheet1.write_merge(row+3, row+3, 0, 15, string, style_header)
		sheet1.write_merge(row+4, row+4, 0, 2, 'Applications Done', style)
		sheet1.write_merge(row+5, row+5, 0, 2, 'Applications Not Done', style)
		sheet1.write_merge(row+6, row+6, 0, 2, 'Total Applications', style)
		sheet1.write_merge(row+4, row+4, 3, 15, qr_status.applications_done, style)
		sheet1.write_merge(row+5, row+5, 3, 15, qr_status.applications_not_done, style)
		sheet1.write_merge(row+6, row+6, 3, 15, (qr_status.total_applications), style)
		sheet1.write(row+7, 0, 'Sr. No.', style_header)
		sheet1.write(row+7, 1, 'Reporting\nCode', style_header)
		sheet1.write(row+7, 2, 'Reporting Name', style_header)
		sheet1.col(2).width = 150 * 70 
		sheet1.write(row+7, 3, 'HR Code', style_header)
		sheet1.write(row+7, 4, 'HR Name', style_header)
		sheet1.col(4).width = 150 * 70
		sheet1.write(row+7, 5, 'Employee\nCode', style_header)
		sheet1.write(row+7, 6, 'Employee Name', style_header)
		sheet1.col(6).width = 150 * 70
		sheet1.write(row+7, 7, 'Department', style_header)
		sheet1.col(7).width = 150 * 70
		sheet1.write(row+7, 8, 'Designation', style_header)
		sheet1.col(8).width = 150 * 70
		sheet1.write(row+7, 9, 'Application\nDate', style_header)
		sheet1.write(row+7, 10, 'Approved\nDate', style_header)
		sheet1.write(row+7, 11, 'Review\nStatus', style_header)
		sheet1.write(row+7, 12, 'Average\nRating', style_header)
		sheet1.write(row+7, 13, 'Review\nSummary', style_header)
		sheet1.col(13).width = 150 * 70
		sheet1.write(row+7, 14, 'Eligible For\r\nPIP', style_header)
		sheet1.write(row+7, 15, 'Employee\nStatus', style_header)
		sheet1.row(row+7).height_mismatch = True
		sheet1.row(row+7).height = 26*20
		row = 8
		for x in qr_status.qr_status_report_lines:

			sr_no = x.sr_no if x.sr_no else ''
			reporting_name = x.reporting_name if x.reporting_name else ''
			reporting_code = x.reporting_code if x.reporting_code else ''
			hr_name = x.hr_name if x.hr_name else ''
			application_date = x.application_date if x.application_date else ''
			if application_date:
				application_date = datetime.strptime(str(application_date), "%Y-%m-%d").strftime("%d %b %Y")
			approved_date = x.approved_date if x.approved_date else ''
			if approved_date:
				approved_date = datetime.strptime(str(approved_date), "%Y-%m-%d").strftime("%d %b %Y")
			review_summary = x.review_summary if x.review_summary else ''
			sheet1.write(row,0, sr_no, style_center)
			sheet1.write(row,1, reporting_code, style_center)
			sheet1.write(row,2, reporting_name, style_left_light)
			sheet1.write(row,3, x.hr_code, style_center)
			sheet1.write(row,4, hr_name, style_center)
			sheet1.write(row,5, x.employee_code, style_center)
			sheet1.write(row,6, x.employee_name, style_left_light)
			sheet1.write(row,7, x.department.name, style_left_light)
			sheet1.write(row,8, x.designation.name, style_left_light)
			sheet1.write(row,9, application_date, style_center)
			sheet1.write(row,10, approved_date, style_center)
			sheet1.write(row,11, x.review_status, style_left_light)
			sheet1.write(row,12, x.average_rating, style_center)
			sheet1.write(row,13, review_summary, style_left_light)
			sheet1.write(row,14, x.eligible_for_pip, style_left_light)
			sheet1.write(row,15, x.employee_status, style_left_light)
			row+=1
		filename = 'Quarterly Report.xls'
		response = request.make_response(None,
			headers=[('Content-Type', 'application/vnd.ms-excel'),
					('Content-Disposition', content_disposition(filename))])
		book.save(response.stream)
		return response