from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import xlsxwriter
try:
	import xlwt
except ImportError:
	xlwt = None
from datetime import datetime,timedelta
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
from openerp.osv.orm import setup_modifiers
from odoo.tools import config, human_size, ustr, html_escape
from odoo.tools.mimetypes import guess_mimetype
import logging
import shutil
from xlrd import open_workbook
import re
import os

def is_valid_email(self,email):
	if len(email) > 7:
		return bool(re.match( "^.+@(\[?)[a-zA-Z0-9-.]+.([a-zA-Z]{2,3}|[0-9]{1,3})(]?)$", email))


class QuikRecruitments(models.Model):
	_name = "quik.recruitments"


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
		result = {}
		for attach in self:
			if attach.datas_fname:
				result[attach.id] = self._file_read(attach.file_url,attach.datas_fname, bin_size)
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
		full_path = source_path + fname
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
			# if not file_name:
			# 	raise ValidationError(_('Please select file to import!!'))
			value = attach.datas
			bin_data = base64.b64decode(value) if value else b''
			if file_name:
				if file_name.endswith('.xls'):
					fname = self._file_write(value,file_name)
			vals = {'file_url':fname}
			# write as superuser, as user probably does not have write access
			super(QuikRecruitments, attach.sudo()).write(vals)


	name = fields.Char('Name',default="Import Applications")
	file_url = fields.Char('Url', index=True, size=1024)
	datas_fname = fields.Char('File Name')
	datas = fields.Binary(string='Applications', compute='_compute_datas', inverse='_inverse_datas')
	db_datas = fields.Binary('Database Data')
	applicant_ids = fields.One2many('hr.applicant', 'quik_recruitment_id', ondelete='restrict')
	applicant_search = fields.Selection([('imported','Imported Applications'),('verified','Verified Applications')], string="Search")
	searched = fields.Boolean(default=False,string='Searched ?')
	imported = fields.Boolean(default=False,string='Imported ?')
	mail_sent = fields.Boolean(default=False,string='Mails Sent ?')
	employees_created = fields.Boolean(default=False,string='Employees created?')
	# select_all = fields.Boolean(default=False,string='Select All')


	@api.multi
	def fetch_applications(self):
		# delete existing searched ids
		applicant_obj = self.env['hr.applicant']
		existing_applicant_ids = applicant_obj.search([('quik_recruitment_id','=',self.id)])
		existing_applicant_ids.write({'quik_recruitment_id': None})
		remaining_applicant_ids = []
		if self.applicant_search == 'imported':
			remaining_applicant_ids = applicant_obj.search([('quik_recruitment_id','!=',False),('state','=','hr')])
			if remaining_applicant_ids:
				for each_remaining_applicant_id in remaining_applicant_ids:
					each_remaining_applicant_id.write({'quik_recruitment_id':self.id})
				self.write({'searched':True,'imported':True})
			else:
				raise ValidationError(_('No Records!!'))
		elif self.applicant_search == 'verified':
			remaining_applicant_ids = applicant_obj.search([('quik_recruitment_id','!=',False),('state','=','selected'),('portal_id','!=',False)])
			if remaining_applicant_ids:
				for each_remaining_applicant_id in remaining_applicant_ids:
					each_remaining_applicant_id.write({'quik_recruitment_id':self.id})
				self.write({'searched':True,'imported':True,'mail_sent':True})
			else:
				raise ValidationError(_('No Records!!'))
		else:
			raise UserError(_('Select search type!'))
		return True

	@api.multi
	def import_quik_applications(self):
		if not self.datas_fname:
			raise ValidationError(_('Kindly select file for import!!'))
		applicant_obj = self.env['hr.applicant']
		# delete existing searched ids
		existing_applicant_ids = applicant_obj.search([('quik_recruitment_id','=',self.id)])
		existing_applicant_ids.write({'quik_recruitment_id': None})
		datas_fname = str(self.datas_fname)
		import_config = self.env['import.config'].search([],limit=1)
		source_path = str(import_config.source_path)
		destination_path = str(import_config.destination_path)
		failed_path = str(import_config.failed_path)
		file_path = source_path+datas_fname
		workbook = open_workbook(file_path)
		worksheet = workbook.sheet_by_index(0)
		for row in range(1, worksheet.nrows):
			print("row",row)
			#column0--------------------------------------------------------------------------------------------
			applicant_name = (worksheet.cell(row,0).value) 
			if not applicant_name:
				if os.path.isfile('/home/odoouser/attendance/import_applications.xls'):
					os.remove('/home/odoouser/attendance/import_applications.xls')
				raise UserError(_('No/Improper applicant name %s !') % (applicant_name))
			#column1--------------------------------------------------------------------------------------------
			email = (worksheet.cell(row,1).value)
			if not email:
				if os.path.isfile('/home/odoouser/attendance/import_applications.xls'):
					os.remove('/home/odoouser/attendance/import_applications.xls')
				raise UserError(_('No/Improper email %s !') % (email))
			check_valid_email = is_valid_email(self,email)
			if not check_valid_email:
				if os.path.isfile('/home/odoouser/attendance/import_applications.xls'):
					os.remove('/home/odoouser/attendance/import_applications.xls')
				raise UserError(_('Invalid email %s ! Please correct it') % (email))
			#column2--------------------------------------------------------------------------------------------
			mobile = int((worksheet.cell(row,2).value))
			if not mobile:
				if os.path.isfile('/home/odoouser/attendance/import_applications.xls'):
					os.remove('/home/odoouser/attendance/import_applications.xls')
				raise UserError(_('No/Improper mobile %s !') % (mobile))
			#column3--------------------------------------------------------------------------------------------
			site = (worksheet.cell(row,3).value)
			if not site:
				if os.path.isfile('/home/odoouser/attendance/import_applications.xls'):
					os.remove('/home/odoouser/attendance/import_applications.xls')
				raise UserError(_('No/Improper site %s !') % (site))
			site_id = self.env['site.master'].search([('name','=',site)],limit=1)
			if not site_id:
				if os.path.isfile('/home/odoouser/attendance/import_applications.xls'):
					os.remove('/home/odoouser/attendance/import_applications.xls')
				raise UserError(_('No such site in the system %s !') % (site))
			#column4--------------------------------------------------------------------------------------------
			designation = (worksheet.cell(row,4).value)
			if not designation:
				if os.path.isfile('/home/odoouser/attendance/import_applications.xls'):
					os.remove('/home/odoouser/attendance/import_applications.xls')
				raise UserError(_('No/Improper designation %s !') % (designation))
			designation_id = self.env['hr.job'].search([('name','=',designation)],limit=1)
			if not designation_id:
				if os.path.isfile('/home/odoouser/attendance/import_applications.xls'):
					os.remove('/home/odoouser/attendance/import_applications.xls')
				raise UserError(_('No such designation in the system %s !') % (designation))
			#column5--------------------------------------------------------------------------------------------
			department = (worksheet.cell(row,5).value)
			if not department:
				if os.path.isfile('/home/odoouser/attendance/import_applications.xls'):
					os.remove('/home/odoouser/attendance/import_applications.xls')
				raise UserError(_('No/Improper department %s !') % (department))
			department_id = self.env['hr.department'].search([('name','=',department)],limit=1)
			if not department_id:
				if os.path.isfile('/home/odoouser/attendance/import_applications.xls'):
					os.remove('/home/odoouser/attendance/import_applications.xls')
				raise UserError(_('No such department in the system %s !') % (department))
			#column6--------------------------------------------------------------------------------------------
			hr_spoc_code = int((worksheet.cell(row,6).value))
			if not hr_spoc_code:
				if os.path.isfile('/home/odoouser/attendance/import_applications.xls'):
					os.remove('/home/odoouser/attendance/import_applications.xls')
				raise UserError(_('No/Improper employee code for HR SPOC %s !') % (hr_spoc_code))
			hr_spoc_id = self.env['hr.employee'].search([('emp_code','=',hr_spoc_code)],limit=1)
			if not hr_spoc_id:
				if os.path.isfile('/home/odoouser/attendance/import_applications.xls'):
					os.remove('/home/odoouser/attendance/import_applications.xls')
				raise UserError(_('No such HR SPOC in the system %s !') % (hr_spoc_code))
			#column7--------------------------------------------------------------------------------------------
			doj = (worksheet.cell(row,7).value)
			if not doj:
				if os.path.isfile('/home/odoouser/attendance/import_applications.xls'):
					os.remove('/home/odoouser/attendance/import_applications.xls')
				raise UserError(_('No/Improper date of joining %s !') % (doj))
			#---------------------------------------------------------------------------------------------------
			print("row details-----",row,applicant_name,email,mobile,site,designation,department,hr_spoc_code,doj)
			application_vals = {
				'name': designation_id.name,
				'partner_name':applicant_name,
				'email_from':email.lower(),
				'partner_mobile':mobile,
				'job_id':designation_id.id,
				'department_id':department_id.id,
				'location':site_id.id,
				'hr_spoc':hr_spoc_id.id,
				'availability':doj,
				'active':True,
				'company_id':1,
				'stage_id':1,
				'state':'hr',
				'offer_letter_sent':False,
				'interview':True,
				'verified':False,
				'employee_created':False,
				'quik_recruitment_id':self.id
			}
			applicant_obj.create(application_vals)
		self.write({'imported':True})
		if os.path.isfile('/home/odoouser/attendance/import_applications.xls'):
			os.remove('/home/odoouser/attendance/import_applications.xls')
		return True

	
	@api.multi
	def send_mail_to_quik_applicants(self):
		if self.applicant_ids:
			batch_applicant_ids = self.applicant_ids.ids[:25]
			print("batch_applicant_ids",batch_applicant_ids)
			# iterating over the quik applicants
			for each_application_id in batch_applicant_ids:
				print("each_application_id",each_application_id)
				each_application_id = self.env['hr.applicant'].browse(each_application_id)
				print("each_application_id",each_application_id)
				existing_user_id = self.env['res.users'].search([('login','=',each_application_id.email_from)])
				if existing_user_id:
					related_partner_id = existing_user_id.partner_id
					existing_user_id.unlink() 
					related_partner_id.unlink()
				#creating new user for portal login
				email_from = each_application_id.email_from
				service_portal_user_id = self.env['res.users'].create({
					'name':each_application_id.partner_name,
					'login': email_from
				})
				print("name,login",each_application_id.partner_name,email_from)
				users = self.env['res.users'].search([('login', '=', email_from)])
				if len(users) != 1:
					raise Exception(_('Invalid username or email'))
				#updating user in applicant form
				applicant_id = self.env['hr.applicant'].search([('email_from','=',email_from)],limit=1)
				self.env.cr.execute("update hr_applicant set user_id=%s where id=%s" %(str(service_portal_user_id.id),str(applicant_id.id)))
				#generating token for newly created user
				users.action_reset_password_custom()
				#assignig employee and portal group to newly created user
				service_portal_group_id = self.env['res.groups'].search([('name','=','Service Portal User')])
				employee_group_id = self.env['res.groups'].search([('name','=','Employee')])
				group_id = service_portal_group_id.id
				user_id = service_portal_user_id.id
				que = self.env.cr.execute('insert into res_groups_users_rel (gid,uid) values (%s,%s)',(group_id,user_id))
				#deleting other groups assigned to the portal user
				self.env.cr.execute("delete from res_groups_users_rel where uid=%s and gid!=%s and gid!=%s" %(str(user_id),str(group_id),str(employee_group_id.id)))
				#rendering the selection email template
				self.ensure_one()
				ir_model_data = self.env['ir.model.data']
				template_id = ir_model_data.get_object_reference('orient_rms', 'selection_portal_login_email_template_quik_recruitments')[1]
				# ctx = {
				# 	'default_model': 'hr.applicant',
				# 	'default_res_id': each_application_id,
				# 	'default_use_template': bool(template_id),
				# 	'default_template_id': template_id,
				# 	'default_composition_mode': 'comment',
				# }
				ress=self.env['mail.template'].browse(template_id).send_mail(applicant_id.id, force_send=True)
				if ress:
					# updating applicant id state
					self.env.cr.execute("update hr_applicant set state='selected', offer_letter_sent=%s, interview=%s where id=%s" %(str(True),str(True),str(applicant_id.id)))
					self.env.cr.commit()
			self.write({'mail_sent':True})
			# self.env.cr.commit()
		else:
			raise ValidationError(_('No Records!!'))
		return True


	@api.multi
	def create_quik_employees(self):
		if self.applicant_ids:
			# iterating over the quik applicants
			for each_application_id in self.applicant_ids:
				each_application_id.create_employee_from_applicant()
			self.write({'employees_created':True})
		return True