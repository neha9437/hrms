# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from lxml import etree
from openerp.osv.orm import setup_modifiers
from datetime import datetime, timedelta

# EMPLOYEE TAB

class Employee(models.Model):
	_inherit = "hr.employee"

	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(Employee, self).fields_view_get(
			view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		doc = etree.XML(res['arch'])
		current_date = datetime.now().date()
		if self._context.get('uid'):
			uid = self._context.get('uid')
			emp_id = self.env['hr.employee'].search([('user_id','=',uid)])
			if emp_id:
				fnf_record = self.env['fnf.form'].search([('employee_id','=',emp_id.id)])
				if fnf_record:
					if str(fnf_record.last_working_date) < str(current_date) <= str(fnf_record.fnf_date):
						for node in doc.xpath("//form"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//field"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//button"):
							node.set('invisible',('1'))
							setup_modifiers(node)
					res['arch'] = etree.tostring(doc)
		return res

class HrResignation(models.Model):
	_inherit = "hr.resignation"

	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(HrResignation, self).fields_view_get(
			view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		doc = etree.XML(res['arch'])
		current_date = datetime.now().date()
		if self._context.get('uid'):
			uid = self._context.get('uid')
			emp_id = self.env['hr.employee'].search([('user_id','=',uid)])
			if emp_id:
				fnf_record = self.env['fnf.form'].search([('employee_id','=',emp_id.id)])
				if fnf_record:
					if str(fnf_record.last_working_date) < str(current_date) <= str(fnf_record.fnf_date):
						for node in doc.xpath("//form"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//field"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//button"):
							node.set('invisible',('1'))
							setup_modifiers(node)
					res['arch'] = etree.tostring(doc)
		return res

class EmployeeExit(models.Model):
	_inherit = "hr.employee.exit"

	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(EmployeeExit, self).fields_view_get(
			view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		doc = etree.XML(res['arch'])
		current_date = datetime.now().date()
		if self._context.get('uid'):
			uid = self._context.get('uid')
			emp_id = self.env['hr.employee'].search([('user_id','=',uid)])
			if emp_id:
				fnf_record = self.env['fnf.form'].search([('employee_id','=',emp_id.id)])
				if fnf_record:
					if str(fnf_record.last_working_date) < str(current_date) <= str(fnf_record.fnf_date):
						for node in doc.xpath("//form"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//field"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//button"):
							node.set('invisible',('1'))
							setup_modifiers(node)
					res['arch'] = etree.tostring(doc)
		return res

class FnFCalculations(models.Model):
	_inherit = "fnf.form"

	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(FnFCalculations, self).fields_view_get(
			view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		doc = etree.XML(res['arch'])
		current_date = datetime.now().date()
		if self._context.get('uid'):
			uid = self._context.get('uid')
			emp_id = self.env['hr.employee'].search([('user_id','=',uid)])
			if emp_id:
				fnf_record = self.env['fnf.form'].search([('employee_id','=',emp_id.id)])
				if fnf_record:
					if str(fnf_record.last_working_date) < str(current_date) <= str(fnf_record.fnf_date):
						for node in doc.xpath("//form"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//field"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//button"):
							node.set('invisible',('1'))
							setup_modifiers(node)
					res['arch'] = etree.tostring(doc)
		return res

class ClearanceForm(models.Model):
	_inherit = "department.clearance"

	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(ClearanceForm, self).fields_view_get(
			view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		doc = etree.XML(res['arch'])
		current_date = datetime.now().date()
		if self._context.get('uid'):
			uid = self._context.get('uid')
			emp_id = self.env['hr.employee'].search([('user_id','=',uid)])
			if emp_id:
				fnf_record = self.env['fnf.form'].search([('employee_id','=',emp_id.id)])
				if fnf_record:
					if str(fnf_record.last_working_date) < str(current_date) <= str(fnf_record.fnf_date):
						for node in doc.xpath("//form"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//field"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//button"):
							node.set('invisible',('1'))
							setup_modifiers(node)
					res['arch'] = etree.tostring(doc)
		return res

class HrDepartment(models.Model):
	_inherit = "hr.department"

	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(HrDepartment, self).fields_view_get(
			view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		doc = etree.XML(res['arch'])
		current_date = datetime.now().date()
		if self._context.get('uid'):
			uid = self._context.get('uid')
			emp_id = self.env['hr.employee'].search([('user_id','=',uid)])
			if emp_id:
				fnf_record = self.env['fnf.form'].search([('employee_id','=',emp_id.id)])
				if fnf_record:
					if str(fnf_record.last_working_date) < str(current_date) <= str(fnf_record.fnf_date):
						for node in doc.xpath("//form"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//field"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//button"):
							node.set('invisible',('1'))
							setup_modifiers(node)
					res['arch'] = etree.tostring(doc)
		return res

# PMS TAB

class KraMain(models.Model):
	_inherit = "kra.main"

	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(KraMain, self).fields_view_get(
			view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		doc = etree.XML(res['arch'])
		current_date = datetime.now().date()
		if self._context.get('uid'):
			uid = self._context.get('uid')
			emp_id = self.env['hr.employee'].search([('user_id','=',uid)])
			if emp_id:
				fnf_record = self.env['fnf.form'].search([('employee_id','=',emp_id.id)])
				if fnf_record:
					if str(fnf_record.last_working_date) < str(current_date) <= str(fnf_record.fnf_date):
						for node in doc.xpath("//form"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//field"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//button"):
							node.set('invisible',('1'))
							setup_modifiers(node)
					res['arch'] = etree.tostring(doc)
				else:
					# quarters_list = ['April','July','October','December','January']
					quarters_list = ['April','July','October','January']
					check_date = self.env['kra.freeze.date'].search([('id','>',0)])
					from_date = check_date.from_date
					to_date = check_date.to_date
					print(from_date, to_date, 'datessssssssssssss')
					if from_date and to_date:
						current_date =  datetime.now().date()
						current_month = datetime.strptime(str(current_date), "%Y-%m-%d").strftime('%B')
						print(current_month, 'monthhhhhhhhh')
						# if current_month in quarters_list:
						# 	print(emp_id.id,'emp_id')
						if str(from_date) <= str(current_date) <= str(to_date):
							for node in doc.xpath("//form"):
								node.set('readonly',('1'))
								setup_modifiers(node)

							for node in doc.xpath("//field"):
								node.set('readonly',('1'))
								setup_modifiers(node)

							for node in doc.xpath("//button"):
								node.set('invisible',('1'))
								setup_modifiers(node)
						res['arch'] = etree.tostring(doc)
		return res

class KraKpiWizard(models.TransientModel):
	_inherit = "kra.kpi.wizard"

	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(KraKpiWizard, self).fields_view_get(
			view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		doc = etree.XML(res['arch'])
		current_date = datetime.now().date()
		if self._context.get('uid'):
			uid = self._context.get('uid')
			emp_id = self.env['hr.employee'].search([('user_id','=',uid)])
			if emp_id:
				fnf_record = self.env['fnf.form'].search([('employee_id','=',emp_id.id)])
				if fnf_record:
					if str(fnf_record.last_working_date) < str(current_date) <= str(fnf_record.fnf_date):
						for node in doc.xpath("//form"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//field"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//button"):
							node.set('invisible',('1'))
							setup_modifiers(node)
					res['arch'] = etree.tostring(doc)
				else:
					# quarters_list = ['April','July','October','December','January']
					quarters_list = ['April','July','October','January']
					check_date = self.env['kra.freeze.date'].search([('id','>',0)])
					from_date = check_date.from_date
					to_date = check_date.to_date
					print(from_date, to_date, 'datessssssssssssss')
					if from_date and to_date:
						current_date =  datetime.now().date()
						current_month = datetime.strptime(str(current_date), "%Y-%m-%d").strftime('%B')
						print(current_month, 'monthhhhhhhhh')
						# if current_month in quarters_list:
						# 	asdjaskld
						print(emp_id.id,'emp_id')
						if str(from_date) <= str(current_date) <= str(to_date):
							# asdajsdhjk
							for node in doc.xpath("//form"):
								node.set('readonly',('1'))
								setup_modifiers(node)

							for node in doc.xpath("//field"):
								node.set('readonly',('1'))
								setup_modifiers(node)

							for node in doc.xpath("//button"):
								node.set('invisible',('1'))
								setup_modifiers(node)
						res['arch'] = etree.tostring(doc)
		return res

class PipList(models.Model):
	_inherit = "pip.list"

	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(PipList, self).fields_view_get(
			view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		doc = etree.XML(res['arch'])
		current_date = datetime.now().date()
		if self._context.get('uid'):
			uid = self._context.get('uid')
			emp_id = self.env['hr.employee'].search([('user_id','=',uid)])
			if emp_id:
				fnf_record = self.env['fnf.form'].search([('employee_id','=',emp_id.id)])
				if fnf_record:
					if str(fnf_record.last_working_date) < str(current_date) <= str(fnf_record.fnf_date):
						for node in doc.xpath("//form"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//field"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//button"):
							node.set('invisible',('1'))
							setup_modifiers(node)
					res['arch'] = etree.tostring(doc)
		return res

class KraMaster(models.Model):
	_inherit = "kra.master"

	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(KraMaster, self).fields_view_get(
			view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		doc = etree.XML(res['arch'])
		current_date = datetime.now().date()
		if self._context.get('uid'):
			uid = self._context.get('uid')
			emp_id = self.env['hr.employee'].search([('user_id','=',uid)])
			if emp_id:
				fnf_record = self.env['fnf.form'].search([('employee_id','=',emp_id.id)])
				if fnf_record:
					if str(fnf_record.last_working_date) < str(current_date) <= str(fnf_record.fnf_date):
						for node in doc.xpath("//form"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//field"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//button"):
							node.set('invisible',('1'))
							setup_modifiers(node)
					res['arch'] = etree.tostring(doc)
		return res

class KpiMaster(models.Model):
	_inherit = "kpi.master"

	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(KpiMaster, self).fields_view_get(
			view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		doc = etree.XML(res['arch'])
		current_date = datetime.now().date()
		if self._context.get('uid'):
			uid = self._context.get('uid')
			emp_id = self.env['hr.employee'].search([('user_id','=',uid)])
			if emp_id:
				fnf_record = self.env['fnf.form'].search([('employee_id','=',emp_id.id)])
				if fnf_record:
					if str(fnf_record.last_working_date) < str(current_date) <= str(fnf_record.fnf_date):
						for node in doc.xpath("//form"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//field"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//button"):
							node.set('invisible',('1'))
							setup_modifiers(node)
					res['arch'] = etree.tostring(doc)
		return res

class YearMaster(models.Model):
	_inherit = "year.master"

	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(YearMaster, self).fields_view_get(
			view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		doc = etree.XML(res['arch'])
		current_date = datetime.now().date()
		if self._context.get('uid'):
			uid = self._context.get('uid')
			emp_id = self.env['hr.employee'].search([('user_id','=',uid)])
			if emp_id:
				fnf_record = self.env['fnf.form'].search([('employee_id','=',emp_id.id)])
				if fnf_record:
					if str(fnf_record.last_working_date) < str(current_date) <= str(fnf_record.fnf_date):
						for node in doc.xpath("//form"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//field"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//button"):
							node.set('invisible',('1'))
							setup_modifiers(node)
					res['arch'] = etree.tostring(doc)
		return res

class HrJob(models.Model):
	_inherit = "hr.job"

	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(HrJob, self).fields_view_get(
			view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		doc = etree.XML(res['arch'])
		current_date = datetime.now().date()
		if self._context.get('uid'):
			uid = self._context.get('uid')
			emp_id = self.env['hr.employee'].search([('user_id','=',uid)])
			if emp_id:
				fnf_record = self.env['fnf.form'].search([('employee_id','=',emp_id.id)])
				if fnf_record:
					if str(fnf_record.last_working_date) < str(current_date) <= str(fnf_record.fnf_date):
						for node in doc.xpath("//form"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//field"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//button"):
							node.set('invisible',('1'))
							setup_modifiers(node)
					res['arch'] = etree.tostring(doc)
		return res

# Recruitment Tab

class HrApplicant(models.Model):
	_inherit = "hr.applicant"

	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(HrApplicant, self).fields_view_get(
			view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		doc = etree.XML(res['arch'])
		current_date = datetime.now().date()
		if self._context.get('uid'):
			uid = self._context.get('uid')
			emp_id = self.env['hr.employee'].search([('user_id','=',uid)])
			if emp_id:
				fnf_record = self.env['fnf.form'].search([('employee_id','=',emp_id.id)])
				if fnf_record:
					if str(fnf_record.last_working_date) < str(current_date) <= str(fnf_record.fnf_date):
						for node in doc.xpath("//form"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//field"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//button"):
							node.set('invisible',('1'))
							setup_modifiers(node)
					res['arch'] = etree.tostring(doc)
		return res

class ServicePortalMaster(models.Model):
	_inherit = "service.portal.master"

	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(ServicePortalMaster, self).fields_view_get(
			view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		doc = etree.XML(res['arch'])
		current_date = datetime.now().date()
		if self._context.get('uid'):
			uid = self._context.get('uid')
			emp_id = self.env['hr.employee'].search([('user_id','=',uid)])
			if emp_id:
				fnf_record = self.env['fnf.form'].search([('employee_id','=',emp_id.id)])
				if fnf_record:
					if str(fnf_record.last_working_date) < str(current_date) <= str(fnf_record.fnf_date):
						for node in doc.xpath("//form"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//field"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//button"):
							node.set('invisible',('1'))
							setup_modifiers(node)
					res['arch'] = etree.tostring(doc)
		return res

class ServiceExperiance(models.Model):
	_inherit = "service.experiance"

	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(ServiceExperiance, self).fields_view_get(
			view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		doc = etree.XML(res['arch'])
		current_date = datetime.now().date()
		if self._context.get('uid'):
			uid = self._context.get('uid')
			emp_id = self.env['hr.employee'].search([('user_id','=',uid)])
			if emp_id:
				fnf_record = self.env['fnf.form'].search([('employee_id','=',emp_id.id)])
				if fnf_record:
					if str(fnf_record.last_working_date) < str(current_date) <= str(fnf_record.fnf_date):
						for node in doc.xpath("//form"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//field"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//button"):
							node.set('invisible',('1'))
							setup_modifiers(node)
					res['arch'] = etree.tostring(doc)
		return res

class ServiceDomain(models.Model):
	_inherit = "service.domain"

	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(ServiceDomain, self).fields_view_get(
			view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		doc = etree.XML(res['arch'])
		current_date = datetime.now().date()
		if self._context.get('uid'):
			uid = self._context.get('uid')
			emp_id = self.env['hr.employee'].search([('user_id','=',uid)])
			if emp_id:
				fnf_record = self.env['fnf.form'].search([('employee_id','=',emp_id.id)])
				if fnf_record:
					if str(fnf_record.last_working_date) < str(current_date) <= str(fnf_record.fnf_date):
						for node in doc.xpath("//form"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//field"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//button"):
							node.set('invisible',('1'))
							setup_modifiers(node)
					res['arch'] = etree.tostring(doc)
		return res

class ServicePfEsicNominee(models.Model):
	_inherit = "service.pf.esic.nominee"

	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(ServicePfEsicNominee, self).fields_view_get(
			view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		doc = etree.XML(res['arch'])
		current_date = datetime.now().date()
		if self._context.get('uid'):
			uid = self._context.get('uid')
			emp_id = self.env['hr.employee'].search([('user_id','=',uid)])
			if emp_id:
				fnf_record = self.env['fnf.form'].search([('employee_id','=',emp_id.id)])
				if fnf_record:
					if str(fnf_record.last_working_date) < str(current_date) <= str(fnf_record.fnf_date):
						for node in doc.xpath("//form"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//field"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//button"):
							node.set('invisible',('1'))
							setup_modifiers(node)
					res['arch'] = etree.tostring(doc)
		return res

# Attendance Tab

# class HrAttendance(models.Model):
# 	_inherit = "hr.attendance"

# 	@api.model
# 	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
# 		res = super(HrAttendance, self).fields_view_get(
# 			view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
# 		doc = etree.XML(res['arch'])
# 		current_date = datetime.now().date()
# 		if self._context.get('uid'):
# 			uid = self._context.get('uid')
# 			emp_id = self.env['hr.employee'].search([('user_id','=',uid)])
# 			if emp_id:
# 				fnf_record = self.env['fnf.form'].search([('employee_id','=',emp_id.id)])
# 				if fnf_record:
# 					if str(fnf_record.last_working_date) < str(current_date) <= str(fnf_record.fnf_date):
# 						for node in doc.xpath("//form"):
# 							node.set('readonly',('1'))
# 							setup_modifiers(node)

# 						for node in doc.xpath("//field"):
# 							node.set('readonly',('1'))
# 							setup_modifiers(node)

# 						for node in doc.xpath("//button"):
# 							node.set('invisible',('1'))
# 							setup_modifiers(node)
# 					res['arch'] = etree.tostring(doc)
# 		return res



class AnnualReview(models.Model):
	_inherit = "annual.review"

	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(AnnualReview, self).fields_view_get(
			view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		doc = etree.XML(res['arch'])
		current_date = datetime.now().date()
		if self._context.get('uid'):
			uid = self._context.get('uid')
			emp_id = self.env['hr.employee'].search([('user_id','=',uid)])
			if emp_id:
				fnf_record = self.env['fnf.form'].search([('employee_id','=',emp_id.id)])
				if fnf_record:
					if str(fnf_record.last_working_date) < str(current_date) <= str(fnf_record.fnf_date):
						for node in doc.xpath("//form"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//field"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//button"):
							node.set('invisible',('1'))
							setup_modifiers(node)
					res['arch'] = etree.tostring(doc)
		return res


class AnnualAppraisal(models.Model):
	_inherit = "annual.appraisal"

	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(AnnualAppraisal, self).fields_view_get(
			view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		doc = etree.XML(res['arch'])
		current_date = datetime.now().date()
		if self._context.get('uid'):
			uid = self._context.get('uid')
			emp_id = self.env['hr.employee'].search([('user_id','=',uid)])
			if emp_id:
				fnf_record = self.env['fnf.form'].search([('employee_id','=',emp_id.id)])
				if fnf_record:
					if str(fnf_record.last_working_date) < str(current_date) <= str(fnf_record.fnf_date):
						for node in doc.xpath("//form"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//field"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//button"):
							node.set('invisible',('1'))
							setup_modifiers(node)
					res['arch'] = etree.tostring(doc)
		return res

class BehaviouralAttributes(models.Model):
	_inherit = "behavioural.attributes"

	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(BehaviouralAttributes, self).fields_view_get(
			view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		doc = etree.XML(res['arch'])
		current_date = datetime.now().date()
		if self._context.get('uid'):
			uid = self._context.get('uid')
			emp_id = self.env['hr.employee'].search([('user_id','=',uid)])
			if emp_id:
				fnf_record = self.env['fnf.form'].search([('employee_id','=',emp_id.id)])
				if fnf_record:
					if str(fnf_record.last_working_date) < str(current_date) <= str(fnf_record.fnf_date):
						for node in doc.xpath("//form"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//field"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//button"):
							node.set('invisible',('1'))
							setup_modifiers(node)
					res['arch'] = etree.tostring(doc)
		return res


class KraQuestions(models.Model):
	_inherit = "kra.questions"

	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(KraQuestions, self).fields_view_get(
			view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		doc = etree.XML(res['arch'])
		current_date = datetime.now().date()
		if self._context.get('uid'):
			uid = self._context.get('uid')
			emp_id = self.env['hr.employee'].search([('user_id','=',uid)])
			if emp_id:
				fnf_record = self.env['fnf.form'].search([('employee_id','=',emp_id.id)])
				if fnf_record:
					if str(fnf_record.last_working_date) < str(current_date) <= str(fnf_record.fnf_date):
						for node in doc.xpath("//form"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//field"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//button"):
							node.set('invisible',('1'))
							setup_modifiers(node)
					res['arch'] = etree.tostring(doc)
		return res


class KraTemplates(models.Model):
	_inherit = "kra.templates"

	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(KraTemplates, self).fields_view_get(
			view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		doc = etree.XML(res['arch'])
		current_date = datetime.now().date()
		if self._context.get('uid'):
			uid = self._context.get('uid')
			emp_id = self.env['hr.employee'].search([('user_id','=',uid)])
			if emp_id:
				fnf_record = self.env['fnf.form'].search([('employee_id','=',emp_id.id)])
				if fnf_record:
					if str(fnf_record.last_working_date) < str(current_date) <= str(fnf_record.fnf_date):
						for node in doc.xpath("//form"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//field"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//button"):
							node.set('invisible',('1'))
							setup_modifiers(node)
					res['arch'] = etree.tostring(doc)
		return res


class AppraisalScale(models.Model):
	_inherit = "appraisal.scale"

	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(AppraisalScale, self).fields_view_get(
			view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		doc = etree.XML(res['arch'])
		current_date = datetime.now().date()
		if self._context.get('uid'):
			uid = self._context.get('uid')
			emp_id = self.env['hr.employee'].search([('user_id','=',uid)])
			if emp_id:
				fnf_record = self.env['fnf.form'].search([('employee_id','=',emp_id.id)])
				if fnf_record:
					if str(fnf_record.last_working_date) < str(current_date) <= str(fnf_record.fnf_date):
						for node in doc.xpath("//form"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//field"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//button"):
							node.set('invisible',('1'))
							setup_modifiers(node)
					res['arch'] = etree.tostring(doc)
		return res


class AnnualKra(models.Model):
	_inherit = "annual.kra"

	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(AnnualKra, self).fields_view_get(
			view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		doc = etree.XML(res['arch'])
		current_date = datetime.now().date()
		if self._context.get('uid'):
			uid = self._context.get('uid')
			emp_id = self.env['hr.employee'].search([('user_id','=',uid)])
			if emp_id:
				fnf_record = self.env['fnf.form'].search([('employee_id','=',emp_id.id)])
				if fnf_record:
					if str(fnf_record.last_working_date) < str(current_date) <= str(fnf_record.fnf_date):
						for node in doc.xpath("//form"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//field"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//button"):
							node.set('invisible',('1'))
							setup_modifiers(node)
					res['arch'] = etree.tostring(doc)
		return res


class AnnualGoalSheet(models.Model):
	_inherit = "annual.goalsheet"

	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(AnnualGoalSheet, self).fields_view_get(
			view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		doc = etree.XML(res['arch'])
		current_date = datetime.now().date()
		if self._context.get('uid'):
			uid = self._context.get('uid')
			emp_id = self.env['hr.employee'].search([('user_id','=',uid)])
			if emp_id:
				fnf_record = self.env['fnf.form'].search([('employee_id','=',emp_id.id)])
				if fnf_record:
					if str(fnf_record.last_working_date) < str(current_date) <= str(fnf_record.fnf_date):
						for node in doc.xpath("//form"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//field"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//button"):
							node.set('invisible',('1'))
							setup_modifiers(node)
					res['arch'] = etree.tostring(doc)
		return res


class AnnualBehaviour(models.Model):
	_inherit = "annual.behaviour"

	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(AnnualBehaviour, self).fields_view_get(
			view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		doc = etree.XML(res['arch'])
		current_date = datetime.now().date()
		if self._context.get('uid'):
			uid = self._context.get('uid')
			emp_id = self.env['hr.employee'].search([('user_id','=',uid)])
			if emp_id:
				fnf_record = self.env['fnf.form'].search([('employee_id','=',emp_id.id)])
				if fnf_record:
					if str(fnf_record.last_working_date) < str(current_date) <= str(fnf_record.fnf_date):
						for node in doc.xpath("//form"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//field"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//button"):
							node.set('invisible',('1'))
							setup_modifiers(node)
					res['arch'] = etree.tostring(doc)
		return res

class AllQuarterKra(models.Model):
	_inherit = "all.quarter.kra"

	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(AllQuarterKra, self).fields_view_get(
			view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		doc = etree.XML(res['arch'])
		current_date = datetime.now().date()
		if self._context.get('uid'):
			uid = self._context.get('uid')
			emp_id = self.env['hr.employee'].search([('user_id','=',uid)])
			if emp_id:
				fnf_record = self.env['fnf.form'].search([('employee_id','=',emp_id.id)])
				if fnf_record:
					if str(fnf_record.last_working_date) < str(current_date) <= str(fnf_record.fnf_date):
						for node in doc.xpath("//form"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//field"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//button"):
							node.set('invisible',('1'))
							setup_modifiers(node)
					res['arch'] = etree.tostring(doc)
		return res

class QrStatusReport(models.Model):
	_inherit = "qr.status.report"

	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(QrStatusReport, self).fields_view_get(
			view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		doc = etree.XML(res['arch'])
		current_date = datetime.now().date()
		if self._context.get('uid'):
			uid = self._context.get('uid')
			emp_id = self.env['hr.employee'].search([('user_id','=',uid)])
			if emp_id:
				fnf_record = self.env['fnf.form'].search([('employee_id','=',emp_id.id)])
				if fnf_record:
					if str(fnf_record.last_working_date) < str(current_date) <= str(fnf_record.fnf_date):
						for node in doc.xpath("//form"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//field"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//button"):
							node.set('invisible',('1'))
							setup_modifiers(node)
					res['arch'] = etree.tostring(doc)
		return res


class QrStatusReportLines(models.Model):
	_inherit = "qr.status.report.lines"

	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(QrStatusReportLines, self).fields_view_get(
			view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		doc = etree.XML(res['arch'])
		current_date = datetime.now().date()
		if self._context.get('uid'):
			uid = self._context.get('uid')
			emp_id = self.env['hr.employee'].search([('user_id','=',uid)])
			if emp_id:
				fnf_record = self.env['fnf.form'].search([('employee_id','=',emp_id.id)])
				if fnf_record:
					if str(fnf_record.last_working_date) < str(current_date) <= str(fnf_record.fnf_date):
						for node in doc.xpath("//form"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//field"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//button"):
							node.set('invisible',('1'))
							setup_modifiers(node)
					res['arch'] = etree.tostring(doc)
		return res

class HolidayMaster(models.Model):
	_inherit = "holiday.master"

	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(HolidayMaster, self).fields_view_get(
			view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		doc = etree.XML(res['arch'])
		current_date = datetime.now().date()
		if self._context.get('uid'):
			uid = self._context.get('uid')
			emp_id = self.env['hr.employee'].search([('user_id','=',uid)])
			if emp_id:
				fnf_record = self.env['fnf.form'].search([('employee_id','=',emp_id.id)])
				if fnf_record:
					if str(fnf_record.last_working_date) < str(current_date) <= str(fnf_record.fnf_date):
						for node in doc.xpath("//form"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//field"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//button"):
							node.set('invisible',('1'))
							setup_modifiers(node)
					res['arch'] = etree.tostring(doc)
		return res

class ReasonResignation(models.Model):
	_inherit = "reason.resignation"

	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(ReasonResignation, self).fields_view_get(
			view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		doc = etree.XML(res['arch'])
		current_date = datetime.now().date()
		if self._context.get('uid'):
			uid = self._context.get('uid')
			emp_id = self.env['hr.employee'].search([('user_id','=',uid)])
			if emp_id:
				fnf_record = self.env['fnf.form'].search([('employee_id','=',emp_id.id)])
				if fnf_record:
					if str(fnf_record.last_working_date) < str(current_date) <= str(fnf_record.fnf_date):
						for node in doc.xpath("//form"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//field"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//button"):
							node.set('invisible',('1'))
							setup_modifiers(node)
					res['arch'] = etree.tostring(doc)
		return res

class Grademaster(models.Model):
	_inherit = "hr.employee.grade"

	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(Grademaster, self).fields_view_get(
			view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		doc = etree.XML(res['arch'])
		current_date = datetime.now().date()
		if self._context.get('uid'):
			uid = self._context.get('uid')
			emp_id = self.env['hr.employee'].search([('user_id','=',uid)])
			if emp_id:
				fnf_record = self.env['fnf.form'].search([('employee_id','=',emp_id.id)])
				if fnf_record:
					if str(fnf_record.last_working_date) < str(current_date) <= str(fnf_record.fnf_date):
						for node in doc.xpath("//form"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//field"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//button"):
							node.set('invisible',('1'))
							setup_modifiers(node)
					res['arch'] = etree.tostring(doc)
		return res

class ResignationType(models.Model):
	_inherit = "hr.employee.resignation.type"

	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(ResignationType, self).fields_view_get(
			view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		doc = etree.XML(res['arch'])
		current_date = datetime.now().date()
		if self._context.get('uid'):
			uid = self._context.get('uid')
			emp_id = self.env['hr.employee'].search([('user_id','=',uid)])
			if emp_id:
				fnf_record = self.env['fnf.form'].search([('employee_id','=',emp_id.id)])
				if fnf_record:
					if str(fnf_record.last_working_date) < str(current_date) <= str(fnf_record.fnf_date):
						for node in doc.xpath("//form"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//field"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//button"):
							node.set('invisible',('1'))
							setup_modifiers(node)
					res['arch'] = etree.tostring(doc)
		return res


class ClearancePointsForm(models.Model):
	_inherit = "clearance.master"

	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(ClearancePointsForm, self).fields_view_get(
			view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		doc = etree.XML(res['arch'])
		current_date = datetime.now().date()
		if self._context.get('uid'):
			uid = self._context.get('uid')
			emp_id = self.env['hr.employee'].search([('user_id','=',uid)])
			if emp_id:
				fnf_record = self.env['fnf.form'].search([('employee_id','=',emp_id.id)])
				if fnf_record:
					if str(fnf_record.last_working_date) < str(current_date) <= str(fnf_record.fnf_date):
						for node in doc.xpath("//form"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//field"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//button"):
							node.set('invisible',('1'))
							setup_modifiers(node)
					res['arch'] = etree.tostring(doc)
		return res


class EmployeeExitTemplate(models.Model):
	_inherit = "hr.employee.template"

	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(EmployeeExitTemplate, self).fields_view_get(
			view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		doc = etree.XML(res['arch'])
		current_date = datetime.now().date()
		if self._context.get('uid'):
			uid = self._context.get('uid')
			emp_id = self.env['hr.employee'].search([('user_id','=',uid)])
			if emp_id:
				fnf_record = self.env['fnf.form'].search([('employee_id','=',emp_id.id)])
				if fnf_record:
					if str(fnf_record.last_working_date) < str(current_date) <= str(fnf_record.fnf_date):
						for node in doc.xpath("//form"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//field"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//button"):
							node.set('invisible',('1'))
							setup_modifiers(node)
					res['arch'] = etree.tostring(doc)
		return res


class AnnualKraWizard(models.TransientModel):
	_inherit = "annual.kra.wizard"

	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(AnnualKraWizard, self).fields_view_get(
			view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		doc = etree.XML(res['arch'])
		current_date = datetime.now().date()
		if self._context.get('uid'):
			uid = self._context.get('uid')
			emp_id = self.env['hr.employee'].search([('user_id','=',uid)])
			if emp_id:
				fnf_record = self.env['fnf.form'].search([('employee_id','=',emp_id.id)])
				if fnf_record:
					if str(fnf_record.last_working_date) < str(current_date) <= str(fnf_record.fnf_date):
						for node in doc.xpath("//form"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//field"):
							node.set('readonly',('1'))
							setup_modifiers(node)

						for node in doc.xpath("//button"):
							node.set('invisible',('1'))
							setup_modifiers(node)
					res['arch'] = etree.tostring(doc)
		return res