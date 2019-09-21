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

class Binary(http.Controller):

	@http.route(['/web/pivot/exit_report_xls/<int:exit_id>'], type='http', auth="public")
	def exit_report_xls(self, exit_id, access_token):
		exit_data = request.env['exit.reports'].browse(exit_id)
		book = xlwt.Workbook(encoding='utf-8')
		sheet1 = book.add_sheet("Exit Report")
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
		# sheet1.write_merge(2, 2, 0, 1, 'Review Cycle:', sub_style)
		# sheet1.write_merge(2, 2, 2, 5, appraisal_data.review_cycle, style)
		# sheet1.write_merge(3, 3, 0, 1, 'Financial Year:', sub_style)
		# sheet1.write_merge(3, 3, 2, 5, appraisal_data.financial_year.name, style)
		# sheet1.write_merge(4, 4, 0, 1,'Application Year:', sub_style)
		# sheet1.write_merge(4, 4, 2, 5, appraisal_data.application_year.name, style)


		sheet1.write_merge(7, 7, 0, 13, 'Exit Report', style_header)
		sheet1.write(9, 0, 'Sr. No.', style_header)
		sheet1.write_merge(9, 9, 1, 2, 'Reporting Code', style_header)
		sheet1.write_merge(9, 9, 3, 4, 'Reporting Name', style_header)
		sheet1.write_merge(9, 9, 5, 6, 'Employee Code', style_header)
		sheet1.write_merge(9, 9, 7, 8, 'Employee Name', style_header)
		sheet1.write_merge(9, 9, 9, 10, 'Department', style_header)
		sheet1.write_merge(9, 9, 11, 12, 'Designation', style_header)
		sheet1.write_merge(9, 9, 13, 14, 'Joining Date', style_header)
		sheet1.write_merge(9, 9, 15, 16, 'Resignation Date', style_header)
		sheet1.write_merge(9, 9, 17, 18, 'Last Working Date', style_header)
		sheet1.write_merge(9, 9, 19, 22, 'Reason of Resignation', style_header)
		sheet1.write_merge(9, 9, 23, 24, 'Notice Period', style_header)
		sheet1.write_merge(9, 9, 25, 26, 'Site', style_header)
		sheet1.write_merge(9, 9, 27, 28, 'State', style_header)
		count=0
		sr_no=[]
		row=10

		search_rec = request.env['hr.resignation'].search([('approved_relieving_date', '>=', exit_data.from_date),('approved_relieving_date', '<=', exit_data.to_date)])
		for x in search_rec:
			if x.state:
				state =''
				if x.state == 'draft':
					state = 'Pending'
				elif x.state == 'confirm':
					state = 'Manager Approval'
				elif x.state == 'approved':
					state = 'HR Approval'
				elif x.state == 'resignation_accepted':
					state = 'Resignation Accepted'
				elif x.state == 'cancel':
					state = 'Cancel'
				elif x.state == 'rejected':
					state = 'Rejected'
				else:
					state = 'Resignation Revoked'
				count+=1
				sheet1.write(row,col, count, style_header)
				sheet1.write_merge(row,row,1, 2, x.reporting_manager_id.emp_code, style_left)
				sheet1.write_merge(row,row,3, 4, x.reporting_manager_id.name, style_left)
				sheet1.write_merge(row,row,5, 6, x.employee_id.emp_code, style_right)
				sheet1.write_merge(row,row,7, 8, x.employee_id.name, style_right)
				sheet1.write_merge(row,row,9, 10, x.department_id.name, style_right)
				sheet1.write_merge(row,row,11, 12, x.employee_id.job_id.name, style_right)
				sheet1.write_merge(row,row,13, 14, x.joined_date, style_right)
				sheet1.write_merge(row,row,15, 16, x.expected_relieving_date, style_right)
				sheet1.write_merge(row,row,17, 18, x.approved_relieving_date, style_right)
				sheet1.write_merge(row,row,19, 22, x.reason_resignation.name, style_right)
				sheet1.write_merge(row,row,23, 24, x.notice_period, style_right)
				sheet1.write_merge(row,row,25, 26, x.employee_id.site_master_id.name, style_right)
				sheet1.write_merge(row,row,27, 28, state, style_right)
				row+=1

		filename = 'Exit_Report.xls' #%(appraisal_data.review_cycle)
		response = request.make_response(None,
			headers=[('Content-Type', 'application/vnd.ms-excel'),
					('Content-Disposition', content_disposition(filename))])
		book.save(response.stream)
		return response