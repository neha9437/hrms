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

class JobPosting(models.Model):
	_name = "job.posting"

	manpower_req = fields.Selection([('in_house','In House'),('site','Client')], string="Manpower Requisition", default="in_house")
	posting_type = fields.Selection([('new','New'),('replacement','Replacement')], string="Job Posting Type", default="new")
	freshers = fields.Boolean('Allow freshers to apply?')

	req_min_exp = fields.Integer(string='Mininum Experience')
	req_max_exp = fields.Integer(string='Maximum Experience')
	ctc_min = fields.Float('Minimum CTC')
	ctc_max = fields.Float('Maximum CTC')

	opening_date = fields.Date('Opening Date')
	closing_date = fields.Date('Closing Date')
	process = fields.Many2one('interview.round','Process')
	skills = fields.One2many('skillset.child','skill','Skills and Competencies')
	replacement_emp = fields.One2many('replacement.child','replacement_id','Replacement Employees')
	jobprocessone2many = fields.One2many('job.process.child','process_id','')
	job_visible = fields.Boolean('Job')
	upload_po = fields.Binary('Upload PO', attachment=True)
	designation = fields.Many2one('hr.job', string="Designation")
	location = fields.Many2one('site.master', string="Site")
	no_of_openings = fields.Integer('No of Openings')
	department_id = fields.Many2one('hr.department', string="Department")
	job_description = fields.Text("Job Description(JD)")
	client_name = fields.Char(string="Client Name")
	client_location = fields.Many2one('site.master', string="Client Location")
	client_city = fields.Char(string="Client City")
	project_name = fields.Char(string="Project Name")
	project_duration = fields.Char('Project Duration')
	no_of_replacement = fields.Integer('No. Of Replacement')
	client_address = fields.Text('Client Address')
	client_mail_id = fields.Char('Client Mail ID')
	hr_access = fields.Boolean('HR Access')
	hr_manager = fields.Many2one('hr.employee','HR Manager',default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1))
	hr_spoc_id = fields.Many2one('hr.employee','HR Spoc',track_visibility='onchange')
	spoc_user_id = fields.Many2one('res.users','Spoc User')
	status = fields.Selection([('draft','Draft'),('open','Requisition'),('initiate','Pending'),('done','Closed')], string="Status", default="draft")
	initiated = fields.Boolean('initiated')


	@api.multi
	def view_rounds(self):
		if self.process:
			self.write({'job_visible':True})
			search_record = self.env['round.child'].search([('round_id','=',self.process.id)])
			if not search_record:
				raise ValidationError(_("Kindly add rounds against this Process!"))
			if self.jobprocessone2many:
				for i in self.jobprocessone2many:
					i.unlink()
			for each in search_record:
				self.env['job.process.child'].create({'name':each.name,'stage_id':each.stage_id.id,'process_id':self.id})
		return True


	@api.onchange('hr_spoc_id')
	def onchange_hr_spoc_id(self):
		data = {}
		if self.hr_spoc_id:
			data['spoc_user_id'] = self.hr_spoc_id.user_id.id
		else:
			data['spoc_user_id'] = None
		return {'value':data}


	@api.onchange('opening_date')
	def onchange_opening_date(self):
		if self.opening_date:
			date_object = datetime.strptime(self.opening_date, '%Y-%m-%d')
			self.closing_date = date_object + timedelta(days=24)


	def submit_manpower_requisition(self):
		if not self.no_of_openings or self.no_of_openings < 1:
			raise ValidationError("Please enter the number of openings for this request !")
		self.write({'status': 'open'})
		return True
			

	@api.multi
	def initiate_manpower_requisition(self):
		if self.location:
			location = self.location.id if self.location else None
		else:
			location = self.client_location.id if self.client_location else None
		no_of_openings = self.no_of_openings
		manpower_req = self.manpower_req
		designation = self.designation.id if self.designation else None
		opening_date = self.opening_date
		hr_manager = self.hr_manager.id if self.hr_manager else None
		spoc_user_id = self.spoc_user_id.id if self.spoc_user_id else None
		status = self.status
		inv_id = self.env['interview.list'].create(
			{
				'location':location,
				'no_of_openings':no_of_openings,
				'manpower_req':manpower_req,
				'designation':designation,
				'opening_date':opening_date,
				'hr_manager': hr_manager,
				'spoc_user_id': spoc_user_id,
				'status': status,
				'job_posting':self.id
			})
		self.write({'status': 'initiate','initiated':True})
		return True

	@api.multi
	def complete_job(self):
		self.status = 'done'
		return True

	@api.model
	def create(self,vals):
		job_id = super(JobPosting, self).create(vals)
		# location = vals.get('location') if vals.get('location') else vals.get('client_location')
		# no_of_openings = vals.get('no_of_openings')
		# manpower_req = vals.get('manpower_req')
		# designation = vals.get('designation')
		# opening_date = vals.get('opening_date')
		# hr_manager = vals.get('hr_manager')
		# status = vals.get('status')
		if not job_id.skills:
			raise ValidationError(_("Please add skills!!"))
		# if job_id:
		# 	self.env['interview.list'].create({'location':location,
		# 										'no_of_openings':no_of_openings,
		# 										'manpower_req':manpower_req,
		# 										'designation':designation,
		# 										'opening_date':opening_date,
		# 										'job_posting':job_id.id})	
		return job_id

class InterviewRound(models.Model):
	_name = "interview.round"

	name = fields.Char('Process')
	round_one2many = fields.One2many('round.child','round_id','')

class RoundChild(models.Model):
	_name = "round.child"

	name = fields.Char('Round Type')
	stage_id = fields.Many2one('hr.recruitment.stage')
	round_id = fields.Many2one('interview.round','')


class JobProcessChild(models.Model):
	_name ="job.process.child"

	process_id = fields.Many2one('job.posting','')
	name = fields.Char('Round Type')
	stage_id = fields.Many2one('hr.recruitment.stage','Stage')

class ReplacementChild(models.Model):
	_name = "replacement.child"

	employee = fields.Many2one('hr.employee','Employee Name')
	replacement_id = fields.Many2one('job.posting','')

class SkillsetChild(models.Model):
	_name = "skillset.child"

	name = fields.Many2one('skillset','Skill Name')
	version = fields.Char('Version')
	experience = fields.Integer('Experience in months')
	skill = fields.Many2one('job.posting','Skill')


class InterviewList(models.Model):
	_name = "interview.list"


	location = fields.Many2one('site.master', string="Site")
	no_of_openings = fields.Integer('No of Openings')
	manpower_req = fields.Selection([('in_house','In House'),('site','Site')], string="Manpower Requisition", default="in_house")
	designation = fields.Many2one('hr.job', string="Designation")
	opening_date = fields.Date('Opening Date')
	hr_manager = fields.Many2one('hr.employee','HR Manager',default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1))
	spoc_user_id = fields.Many2one('res.users','Spoc User')
	status = fields.Selection([('open','Open'),('done','Done')], string="Status", default="open")
	job_posting = fields.Many2one('job.posting','Job Posting')
	user_id = fields.Many2one('res.users', default=lambda self: self.env.user)

	# @api.multi
	# def add_candidate_details(self):
	# 	view_id = self.env.ref('orient_rms.view_rmscandidate_details_form', False)
	# 	print(view_id,'view_id')
	# 	context = {
	# 			'interview_id':self.id,
	# 	}
	# 	return {
 #            'type': 'ir.actions.act_window',
 #            'name': _('Candidate details'),
 #            'view_mode': 'form',
 #            'res_model': 'candidate.details',
 #            'target': 'new',
 #            'views': [[view_id.id, 'form']],
 #            'context':context
	# 	}

	@api.multi
	def add_candidate_details(self):
		view_id = self.env.ref('hr_recruitment.crm_case_form_view_job', False)
		context = {
				'interview_id':self.id,
		}
		return {
			'type': 'ir.actions.act_window',
			'name': _('HR Applicant'),
			'view_mode': 'form',
			'res_model' : 'hr.applicant',
			'target' : 'new',
			'views' : [[view_id.id, 'form']],
			'context' : context
		}


class CandidateDetails(models.Model):
	_name = "candidate.details"

	name = fields.Char('Candidate Name')
	email = fields.Char('Email')
	mobile_no= fields.Char('Mobile Number', size=10)
	exp_in_months = fields.Integer('Experience in Months')
	upload_resume = fields.Binary('Upload Resume')
	designation = fields.Many2one('hr.job', string="Designation")
	job_posting = fields.Many2one('job.posting','Job Posting')

	@api.model
	def create(self, vals):
		can_id =super(CandidateDetails, self).create(vals)
		if self._context.get('interview_id'):
			interview_id = self._context.get('interview_id')
			int_id = self.env['interview.list'].search([('id','=',interview_id)])
			job_posting = int_id.job_posting.id
			designation = int_id.designation.id
			can_id.update({'job_posting':job_posting,'designation':designation})
		return can_id


class CandidateDocuments(models.Model):
	_name = "candidate.documents"

	name = fields.Char('Name')
	document = fields.Binary('Document')
	current_date = fields.Date('Upload Date',default=datetime.today())


class Applicant(models.Model):
    _inherit = ['hr.applicant']

    quik_recruitment_id = fields.Many2one('quik.recruitment', 'Quik Recruitment')