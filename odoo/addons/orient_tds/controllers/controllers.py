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


	@http.route(['/web/pivot/export_training_xls/<int:training_id>'], type='http', auth="public")
	def export_training_xls(self, training_id, access_token):
		appraisal_data = request.env['training.excel'].browse(training_id)
		print(appraisal_data,'-----')

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
		sheet1.write_merge(2, 2, 0, 1, 'From Date:', sub_style)
		sheet1.write_merge(2, 2, 2, 5, appraisal_data.from_date, style)
		sheet1.write_merge(3, 3, 0, 1, 'To Date:', sub_style)
		sheet1.write_merge(3, 3, 2, 5, appraisal_data.to_date, style)
		# sheet1.write_merge(4, 4, 0, 1,'Location:', sub_style)


		sheet1.write_merge(6, 6, 6, 9, 'Training Data', style)

		sheet1.write(9, 0, 'Sr. No.', style_header)
		sheet1.write_merge(9,9, 1, 1, 'From Date', style_header)
		sheet1.write_merge(9, 9, 2, 2, 'To Date', style_header)
		sheet1.write_merge(9, 9, 3, 6, 'Training Name', style_header)
		sheet1.write_merge(9, 9, 7, 9, 'Employee', style_header)
		sheet1.write_merge(9, 9, 10, 10, 'Employee Code', style_header)
		sheet1.write_merge(9, 9, 11, 11, 'Department', style_header)
		sheet1.write_merge(9, 9, 12, 12, 'Designation', style_header)
		sheet1.write_merge(9, 9, 13, 13, 'Reporting To', style_header)
		# sheet1.write_merge(9, 9, 14, 14, 'Financial Year', style_header)

		count=0
		sr_no=[]
		row=10

		for each in appraisal_data.training_one2many:

			for x in each.training_id:
				print(x.from_date,x.to_date,'000000')
				for emp in x.employee:
					count+=1
					sr_no.append(count)
					sheet1.write(row, col, count, style_header)
					sheet1.write_merge(row,row, 1, 1, x.from_date, style_left)
					sheet1.write_merge(row,row, 2, 2, x.to_date, style_left)
					sheet1.write_merge(row,row,3, 6, x.name, style_left)
					sheet1.write_merge(row,row,7, 9, emp.name, style_left)
					sheet1.write_merge(row, row, 10,10, emp.emp_code, style_left)

					sheet1.write_merge(row,row,11,11, emp.department_id.name, style_right)
					sheet1.write_merge(row,row,12, 12, emp.job_id.name, style_right)
					sheet1.write_merge(row,row,13, 13, emp.parent_id.name, style_right)

					row+=1


		filename = 'TrainingDetails.xls'
		response = request.make_response(None,
			headers=[('Content-Type', 'application/vnd.ms-excel'),
					('Content-Disposition', content_disposition(filename))])
		book.save(response.stream)
		return response