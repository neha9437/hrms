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

	@http.route(['/web/pivot/confirmation_due_export_xls/<int:report_id>'], type='http', auth="public")
	def confirmation_due_export_xls(self, report_id, access_token):
		report_data = request.env['employee.confirmation.report'].browse(report_id)
		book = xlwt.Workbook(encoding='utf-8')
		sheet1 = book.add_sheet("Confirmation Due Report")
		style = xlwt.XFStyle()
		style_header = xlwt.XFStyle()
		style_right = xlwt.XFStyle()
		style_right_bold = xlwt.XFStyle()
		style_left = xlwt.XFStyle()
		font = xlwt.Font()
		font.bold = True
		style.font = font
		style_header.font = font
		# style_header.num_format_str = '0.00'
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
		sheet1.write_merge(2, 2, 0, 1, 'Orient Technologies PVT LTD', sub_style)
		sheet1.write_merge(2, 2, 2, 5, 'Employee Confirmation Due Report', style)
		sheet1.write_merge(3, 3, 0, 1, 'Date:', sub_style)
		sheet1.write_merge(3, 3, 2, 5, str(datetime.now().date().strftime("%d/%m/%Y")), style)

		# sheet1.write_merge(9, 9, 0, 13, 'Appraisal Due Report', style_header)
		sheet1.write(5, 0, 'Sr. No.', style_header)
		sheet1.write_merge(5, 5, 1, 5, 'Employee Name', style_header)
		sheet1.write_merge(5, 5, 6, 6, 'Employee Code', style_header)
		sheet1.write_merge(5, 5, 7, 7, 'Reporting To', style_header)
		sheet1.write_merge(5, 5, 8, 8, 'Location', style_header)
		sheet1.write_merge(5, 5, 9, 9, 'Department', style_header)
		sheet1.write_merge(5, 5, 10, 10, 'Joining Date', style_header)
		sheet1.write_merge(5, 5, 11, 11, 'Confirmation Date', style_header)

		count=1
		sr_no=[]
		row=7

		for x in report_data.due_report_lines:
			sheet1.write(row,col, count, style_header)
			sheet1.write_merge(row,row, 1, 5, x.emp_id.name, style_left)
			sheet1.write_merge(row,row, 6, 6, x.emp_code, style_left)
			sheet1.write_merge(row,row, 7, 7, x.emp_id.parent_id.name, style_right)
			sheet1.write_merge(row,row, 8, 8, x.emp_id.site_master_id.name, style_right)
			sheet1.write_merge(row,row, 9, 9, x.emp_id.department_id.name, style_right)
			sheet1.write_merge(row,row, 10, 10, datetime.strptime(str(x.joining_date), "%Y-%m-%d").strftime("%d-%m-%Y"), style_right)
			sheet1.write_merge(row,row, 11, 11, datetime.strptime(str(x.confirmation_date), "%Y-%m-%d").strftime("%d-%m-%Y"), style_right)
			row+=1
			count+=1
		filename = 'Confirmation_Due_Report.xls'
		response = request.make_response(None,
			headers=[('Content-Type', 'application/vnd.ms-excel'),
					('Content-Disposition', content_disposition(filename))])
		book.save(response.stream)
		return response
	
