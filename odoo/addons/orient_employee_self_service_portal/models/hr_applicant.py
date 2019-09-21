# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo import SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError
import re

def is_valid_email(self,email):
    if len(email) > 7:
        return bool(re.match( "^.+@(\[?)[a-zA-Z0-9-.]+.([a-zA-Z]{2,3}|[0-9]{1,3})(]?)$", email))

class Applicant(models.Model):
    _inherit = ['hr.applicant']

    _sql_constraints = [
        ('email_from_uniq', 'unique (email_From)', 'An applicant with this email already exists!'),
    ]    

    def _default_stage_id(self):
        if self._context.get('default_job_id'):
            ids = self.env['hr.recruitment.stage'].search([
                '|',
                ('job_id', '=', False),
                ('job_id', '=', self._context['default_job_id']),
                ('fold', '=', False)
            ], order='sequence asc', limit=1).ids
            if ids:
                return ids[0]
        else:
            initial_qualification_id = self.env['hr.recruitment.stage'].search([('initial_qualification', '=', True)], limit=1).ids
            if initial_qualification_id:
                return initial_qualification_id[0]
        return False

    # offer_letter_generated = fields.Boolean(default=False,string='Offer Letter Generated')
    name = fields.Char("Job Title", required=True)
    offer_letter_sent = fields.Boolean(default=False,string='Offer Letter Sent')
    interview = fields.Boolean(default=False,string='Interview')
    verified = fields.Boolean(default=False,string='Verified')
    employee_created = fields.Boolean(default=False,string='Employee Created')
    stage_id = fields.Many2one('hr.recruitment.stage', 'Stage',
                               domain="['|', ('job_id', '=', False), ('job_id', '=', job_id)]",
                               copy=False, index=True,
                               group_expand='_read_group_stage_ids',
                               default=_default_stage_id)
    portal_id = fields.Many2one('service.portal.master', 'Portal Form')
    salary_proposed = fields.Float("Proposed CTC", group_operator="avg", help="CTC Proposed by the Organisation")
    salary_expected = fields.Float("Expected CTC", group_operator="avg", help="CTC Expected by Applicant")
    years_of_exp = fields.Char(string='Experience')
    reference = fields.Many2one('hr.employee',"Referred By")
    location = fields.Many2one('site.master', string="Site")
    professional_certifications = fields.Text('Professional Certifications')
    hr_spoc = fields.Many2one('hr.employee','HR Spoc',default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1))
    state = fields.Selection([
        ('telephonic', 'Telephonic'),
        ('client', 'Client Interview'),
        ('technical', 'TL Interview'),
        ('director', 'Director'),
        ('hr', 'HR'),
        ('selected', 'Selected'),
        ('verified', 'Verified'),
        ('employee_created', 'Employee Created'),
        ('on_hold', 'On-Hold'),
        ('reject', 'Rejected'),
        ], string='Status', copy=False, index=True, default='telephonic')
    last_state = fields.Selection([
        ('telephonic', 'Telephonic'),
        ('client', 'Client Interview'),
        ('technical', 'TL Interview'),
        ('director', 'Director Interview'),
        ('hr', 'HR Interview'),
        ('selected', 'Selected'),
        ('verified', 'Verified'),
        ('employee_created', 'Employee Created'),
        ('on_hold', 'On-Hold'),
        ('reject', 'Rejected'),
        ], string='Last State')
    resend_offer_link = fields.Boolean(default=False,string='Resend Offer Link?')
    # marked = fields.Boolean(default=False,string='Selection Marked?')


    @api.onchange('resend_offer_link')
    def onchange_resend_offer_link(self):
        data = {}
        if self.resend_offer_link:
            offer_letter_sent = False
            state = 'hr'
        else:
            offer_letter_sent = True
            state = 'hr'
        data['offer_letter_sent'] = offer_letter_sent
        data['state'] = state
        return {'value':data}


    @api.model
    def create(self,vals):
        if vals.get('email_from'):
            email = vals.get('email_from')
            email_l = email.lower()
        else:
            email_l = False
        vals.update({'email_from':email_l})
        return super(Applicant, self).create(vals)

    @api.multi
    def hold_applicant(self):
        self.write({'last_state':self.state,'state': 'on_hold'})

    @api.multi
    def revoke_applicant(self):
        self.write({'state':self.last_state})

    @api.multi
    def archive_applicant(self):
        self.write({'state': 'reject'})

    @api.multi
    def show_offer_letter_wizard(self):
        view_id = self.env.ref('orient_employee_self_service_portal.offer_letter_wizard_view_form').id
        return {
                    'name': _('Send Offer Letter to Candidate'),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'offer.letter.wizard',
                    'view_id': view_id,
                    'views': [(view_id, 'form')],
                    'target': 'new',
                    'context':{'hr_applicant_id': self.id}
                }   

    # @api.multi
    # def generate_offer_letter(self):
    #     res = self.write({'offer_letter_generated':True})
    #     return res
        # return self.env.ref('orient_employee_self_service_portal.action_report_offerletter').report_action(self)


    @api.multi
    def action_portal_selection_send(self):
        #deleting the existing user and partner if exists
        email = self.email_from
        check_valid_email = is_valid_email(self,email)
        if not check_valid_email:
            raise ValidationError(_('Kindly enter valid Email ID!'))
        existing_user_id = self.env['res.users'].search([('login','=',self.email_from)])
        if existing_user_id:
            related_partner_id = existing_user_id.partner_id
            existing_user_id.unlink() 
            related_partner_id.unlink()

        #creating new user for portal login
        service_portal_user_id = self.env['res.users'].create({
            'name': self.partner_name,
            'login':self.email_from
        })
        users = self.env['res.users'].search([('login', '=', self.email_from)])
        if len(users) != 1:
            raise Exception(_('Invalid username or email'))

        #updating user in applicant form
        applicant_id = self.env['hr.applicant'].search([('email_from','=',self.email_from)],limit=1)
        resend_offer_link = False
        self.env.cr.execute("update hr_applicant set user_id=%s, resend_offer_link=%s where id=%s" %(str(service_portal_user_id.id),str(resend_offer_link),str(applicant_id.id)))

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
        template_id = ir_model_data.get_object_reference('orient_employee_self_service_portal', 'selection_portal_login_email_template')[1]
        ctx = {
            'default_model': 'hr.applicant',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    def action_verify_candidate(self):
        if not self.portal_id:
            raise UserError(_('Sorry. Cannot verify as the candidate has not submitted the self service form yet!'))
        # verification_stage_id = self.env['hr.recruitment.stage'].search([('verification','=',True)])
        # res = self.write({'verified':True,'stage_id':verification_stage_id.id})
        res = self.write({'verified':True,'state':'verified'})
        return res

    @api.multi
    def action_clear_interview(self):
        email = self.email_from
        check_valid_email = is_valid_email(self,email)
        if not check_valid_email:
            raise ValidationError(_('Kindly enter valid Email ID!'))
        # interview_stage_id = self.env['hr.recruitment.stage'].search([('interview','=',True)])
        # res = self.write({'interview':True,'stage_id':interview_stage_id.id})
        next_state = None
        if self.state == 'telephonic':
            next_state = 'client'
        elif self.state == 'client':
            next_state = 'technical'
        elif self.state == 'technical':
            next_state = 'director'
        elif self.state == 'director':
            next_state = 'hr'
        res = self.write({'interview':True,'state':next_state})
        return res

    @api.multi
    def create_employee_from_applicant(self):
        """ Create an hr.employee from the hr.applicants """
        context = {}
        employee = False
        for applicant in self:
            contact_name = False
            print("applicant.partner_id",applicant.partner_id)
            if applicant.partner_id:
                address_id = applicant.partner_id.address_get(['contact'])['contact']
                contact_name = applicant.partner_id.name_get()[0][1]
            else:
                new_partner_id = self.env['res.partner'].create({
                    'is_company': False,
                    'name': applicant.partner_name,
                    'email': applicant.email_from,
                    'phone': applicant.partner_phone,
                    'mobile': applicant.partner_mobile
                })
                address_id = new_partner_id.address_get(['contact'])['contact']
            if applicant.job_id and (applicant.partner_name or contact_name):
                applicant.job_id.write({'no_of_hired_employee': applicant.job_id.no_of_hired_employee + 1})
                title = False
                if applicant.portal_id.gender == 'female' or applicant.portal_id.gender == 'other':
                    if applicant.portal_id.marital_status == 'single':
                        title = 'ms'
                    if applicant.portal_id.marital_status == 'married':
                        title = 'mrs'
                    if applicant.portal_id.marital_status == 'divorced':
                        title = 'mrs'
                else:
                    title = 'mr'
                address = ''
                street = applicant.portal_id.street+' '+','
                street2 = applicant.portal_id.street2+' '+','
                city = applicant.portal_id.city+' '+','
                pincode = applicant.portal_id.zip+' '+','
                state = applicant.portal_id.state_id.name+' '+',' if applicant.portal_id.state_id else ' '
                country = applicant.portal_id.country_id.name+' '+','
                address = street+street2+city+state+country
                context.update({'portal_user_true': True})
                emp_vals = {
                    'position_type':'probation',
                    'title': title,
                    'name':applicant.portal_id.first_name+' '+applicant.portal_id.middle_name+' '+applicant.portal_id.last_name,
                    'gender':applicant.portal_id.gender,
                    'age':applicant.portal_id.age,
                    'pan':applicant.portal_id.pan,
                    'aadhar':applicant.portal_id.aadhar,
                    'blood_group':applicant.portal_id.blood_group,
                    'candidate_type1':applicant.portal_id.candidate_type,
                    'previous_company':applicant.portal_id.previous_company,
                    'previous_designation':applicant.portal_id.designation,
                    'current_ctc':applicant.salary_proposed,
                    'experiance_id':applicant.portal_id.experiance_id.id,
                    'highest_qualification':applicant.portal_id.highest_qualification,
                    'address':address,
                    'work_email': applicant.email_from,
                    'mobile_phone': applicant.portal_id.phone_number,
                    'personal_email':applicant.email_from,
                    'personal_mobile':applicant.portal_id.phone_number,
                    # 'emergency_contact':[(0, 0, { 'number':applicant.portal_id.emergency_contact_number})],
                    'emergency_contact_number':applicant.portal_id.emergency_contact_number,
                    'birthday':applicant.portal_id.dob,
                    'first_name':applicant.portal_id.first_name,
                    'middle_name':applicant.portal_id.middle_name,
                    'last_name':applicant.portal_id.last_name,
                    'father_name':applicant.portal_id.father_name,
                    'mother_name':applicant.portal_id.mother_name,
                    'site_master_id':applicant.location.id,
                    # 'guardian_title':,
                    # 'guardian_first_name':,
                    # 'guardian_middle_name':,
                    # 'guardian_last_name':,
                    # 'emp_category'
                    # 'cost_center_id':
                    # 'group_join_date':
                    # 'rate_code':
                    # 'bank_id':
                    # 'branch_name':
                    # 'gl_code':
                    # 'medical_policy_number':
                    # 'union_member':
                    # 'probation_period': 
                    # 'probation_date':
                    # 'notice_period':
                    # 'salary_disbursement_date':
                    # 'confirmation_date':
                    # 'retirement_date':
                    # 'weekly_off':
                    'pf_esic_holder':applicant.portal_id.pf_esic_holder,
                    'pf_uan_no':applicant.portal_id.pf_uan_no, 
                    'pf_nominee_father':applicant.portal_id.pf_nominee_father,
                    'pf_nominee_mother':applicant.portal_id.pf_nominee_mother,
                    'pf_nominee_spouse':applicant.portal_id.pf_nominee_spouse,
                    'pf_nominee_child1':applicant.portal_id.pf_nominee_child1,
                    'pf_nominee_child2':applicant.portal_id.pf_nominee_child1,
                    'pf_father_name':applicant.portal_id.pf_father_name,
                    'pf_mother_name':applicant.portal_id.pf_mother_name,
                    'pf_spouse_name':applicant.portal_id.pf_spouse_name,
                    'pf_first_child':applicant.portal_id.pf_first_child,
                    'pf_second_child':applicant.portal_id.pf_second_child,
                    'pf_dob_father':applicant.portal_id.pf_dob_father,
                    'pf_dob_mother':applicant.portal_id.pf_dob_mother,
                    'pf_dob_spouse':applicant.portal_id.pf_dob_spouse,
                    'pf_dob_child1':applicant.portal_id.pf_dob_child1,
                    'pf_dob_child2':applicant.portal_id.pf_dob_child2,
                    'pf_percent_father':applicant.portal_id.pf_percent_father,
                    'pf_percent_mother':applicant.portal_id.pf_percent_mother,
                    'pf_percent_spouse':applicant.portal_id.pf_percent_spouse,
                    'pf_percent_child1':applicant.portal_id.pf_percent_child1,
                    'pf_percent_child2':applicant.portal_id.pf_percent_child2,
                    'pf_gender_spouse':applicant.portal_id.pf_gender_spouse,
                    'pf_gender_child1':applicant.portal_id.pf_gender_child1,
                    'pf_gender_child2':applicant.portal_id.pf_gender_child2,
                    'esic_uan_no':applicant.portal_id.esic_uan_no,
                    'esic_nominee_father':applicant.portal_id.esic_nominee_father,
                    'esic_nominee_mother':applicant.portal_id.esic_nominee_mother,
                    'esic_nominee_spouse':applicant.portal_id.esic_nominee_spouse,
                    'esic_nominee_child1':applicant.portal_id.esic_nominee_child1,
                    'esic_nominee_child2':applicant.portal_id.esic_nominee_child2,
                    'esic_father_name':applicant.portal_id.esic_father_name, 
                    'esic_mother_name':applicant.portal_id.esic_mother_name,
                    'esic_spouse_name':applicant.portal_id.esic_spouse_name,
                    'esic_first_child':applicant.portal_id.esic_first_child,
                    'esic_second_child':applicant.portal_id.esic_second_child,
                    'esic_dob_father':applicant.portal_id.esic_dob_father,
                    'esic_dob_mother':applicant.portal_id.esic_dob_mother,
                    'esic_dob_spouse':applicant.portal_id.esic_dob_spouse,
                    'esic_dob_child1':applicant.portal_id.esic_dob_child1,
                    'esic_dob_child2':applicant.portal_id.esic_dob_child2,
                    'esic_percent_father':applicant.portal_id.esic_percent_father,
                    'esic_percent_mother':applicant.portal_id.esic_percent_mother,
                    'esic_percent_spouse':applicant.portal_id.esic_percent_spouse,
                    'esic_percent_child1':applicant.portal_id.esic_percent_child1,
                    'esic_percent_child2':applicant.portal_id.esic_percent_child2,
                    'esic_gender_spouse':applicant.portal_id.esic_gender_spouse,
                    'esic_gender_child1':applicant.portal_id.esic_gender_child1,
                    'esic_gender_child2' :applicant.portal_id.esic_gender_child2,
                    'department_id':applicant.department_id.id,
                    'applicant_id':applicant.id,
                    'portal_id':applicant.portal_id.id,
                    'job_id': applicant.job_id.id,
                    'address_home_id': address_id,
                    'department_id': applicant.department_id.id or False,
                    'user_id':applicant.user_id.id,
                    'joining_date':applicant.availability,
                    'country_id':applicant.portal_id.country_id.id,
                    'cv_file':applicant.portal_id.cv_file,
                    'residence_proof':applicant.portal_id.residence_proof,
                    'pan_doc':applicant.portal_id.pan_doc,
                    'aadhar_doc':applicant.portal_id.aadhar_doc,
                    'passport_photo':applicant.portal_id.passport_photo,
                    'birth_cert':applicant.portal_id.birth_cert,
                    'appraisal_doc':applicant.portal_id.appraisal_doc,
                    'appointment_doc':applicant.portal_id.appointment_doc,
                    'payslip':applicant.portal_id.payslip,
                    'qualification_cert':applicant.portal_id.qualification_cert,
                    'leaving_cert':applicant.portal_id.leaving_cert,
                    'skill_cert':applicant.portal_id.skill_cert,
                    'address_id': applicant.company_id and applicant.company_id.partner_id
                            and applicant.company_id.partner_id.id or False,
                }
                employee = self.env['hr.employee'].create(emp_vals).with_context(context)
                applicant.write({'emp_id': employee.id})
                applicant.partner_id.write(
                    {
                        'street':applicant.portal_id.street,
                        'street2':applicant.portal_id.street2,
                        'city':applicant.portal_id.city,
                        'pincode':applicant.portal_id.zip,
                        'state':applicant.portal_id.state_id.id if applicant.portal_id.id else False,
                        'country':applicant.portal_id.country_id.id,
                        'email':applicant.email_from
                    })
                # service_portal_group_id = self.env['res.groups'].search([('name','=','Service Portal User')])
                service_portal_user_id = self.env['res.users'].search([('login','=',applicant.email_from)])
                # group_id = service_portal_group_id.id
                user_id = service_portal_user_id.id
                # self.env.cr.execute("delete from res_users where uid=%s and gid=%s" %(str(user_id),str(group_id)))
                self.env.cr.execute("delete from res_users where id=%s" %(str(user_id)))
                applicant.job_id.message_post(
                    body=_('New Employee %s Hired') % applicant.partner_name if applicant.partner_name else applicant.name,
                    subtype="hr_recruitment.mt_job_applicant_hired")
                employee._broadcast_welcome()
            else:
                raise UserError(_('You must define an Applied Job and a Contact Name for this applicant.'))
        # employee_created_stage_id = self.env['hr.recruitment.stage'].search([('employee_created','=',True)])
        # applicant.write({'stage_id': employee_created_stage_id.id,'employee_created':True})
        applicant.write({'state': 'employee_created','employee_created':True})
        employee_action = self.env.ref('hr.open_view_employee_list')
        dict_act_window = employee_action.read([])[0]
        if employee:
            dict_act_window['res_id'] = employee.id
        dict_act_window['view_mode'] = 'form,tree'
        return dict_act_window


class RecruitmentStage(models.Model):
    _inherit = ['hr.recruitment.stage']

    initial_qualification = fields.Boolean(default=False,string='Initial Qualification')
    interview = fields.Boolean(default=False,string='Interview')
    selection = fields.Boolean(default=False,string='Selection')
    verification = fields.Boolean(default=False,string='Verification')
    employee_created = fields.Boolean(default=False,string='Employee Created')


  
class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'


    @api.multi
    def send_mail(self, auto_commit=False):
        """ Process the wizard content and proceed with sending the related
            email(s), rendering any template patterns on the fly if needed. """
        if self.template_id and self.template_id.name == 'Selection Mail & Portal Login Email Template':
            #updating current application with stage_id, user_id and other booleans
            partner_ids = self.partner_ids
            if len(partner_ids) > 1:
                raise UserError(_('Selection Mail to be sent to only one candidate!'))
            candidate_email = partner_ids[0].email
            service_portal_user_id = self.env['res.users'].search([('login','=',candidate_email)],limit=1)
            # selection_stage_id = self.env['hr.recruitment.stage'].search([('selection','=',True)])
            applicant_id = self.env['hr.applicant'].search([('email_from','=',candidate_email)],limit=1)
            # self.env.cr.execute("update hr_applicant set stage_id=%s, offer_letter_sent=%s, interview=%s where id=%s" %(str(selection_stage_id.id),str(True),str(True),str(applicant_id.id)))
            self.env.cr.execute("update hr_applicant set state='selected', offer_letter_sent=%s, interview=%s where id=%s" %(str(True),str(True),str(applicant_id.id)))
        for wizard in self:
            # Duplicate attachments linked to the email.template.
            # Indeed, basic mail.compose.message wizard duplicates attachments in mass
            # mailing mode. But in 'single post' mode, attachments of an email template
            # also have to be duplicated to avoid changing their ownership.
            if wizard.attachment_ids and wizard.composition_mode != 'mass_mail' and wizard.template_id:
                new_attachment_ids = []
                for attachment in wizard.attachment_ids:
                    if attachment in wizard.template_id.attachment_ids:
                        new_attachment_ids.append(attachment.copy({'res_model': 'mail.compose.message', 'res_id': wizard.id}).id)
                    else:
                        new_attachment_ids.append(attachment.id)
                wizard.write({'attachment_ids': [(6, 0, new_attachment_ids)]})

            # Mass Mailing
            mass_mode = wizard.composition_mode in ('mass_mail', 'mass_post')

            Mail = self.env['mail.mail']
            ActiveModel = self.env[wizard.model if wizard.model else 'mail.thread']
            if wizard.template_id:
                # template user_signature is added when generating body_html
                # mass mailing: use template auto_delete value -> note, for emails mass mailing only
                Mail = Mail.with_context(mail_notify_user_signature=False)
                ActiveModel = ActiveModel.with_context(mail_notify_user_signature=False, mail_auto_delete=wizard.template_id.auto_delete)
            if not hasattr(ActiveModel, 'message_post'):
                ActiveModel = self.env['mail.thread'].with_context(thread_model=wizard.model)
            if wizard.composition_mode == 'mass_post':
                # do not send emails directly but use the queue instead
                # add context key to avoid subscribing the author
                ActiveModel = ActiveModel.with_context(mail_notify_force_send=False, mail_create_nosubscribe=True)
            # wizard works in batch mode: [res_id] or active_ids or active_domain
            if mass_mode and wizard.use_active_domain and wizard.model:
                res_ids = self.env[wizard.model].search(safe_eval(wizard.active_domain)).ids
            elif mass_mode and wizard.model and self._context.get('active_ids'):
                res_ids = self._context['active_ids']
            else:
                res_ids = [wizard.res_id]

            batch_size = int(self.env['ir.config_parameter'].sudo().get_param('mail.batch_size')) or self._batch_size
            sliced_res_ids = [res_ids[i:i + batch_size] for i in range(0, len(res_ids), batch_size)]

            if wizard.composition_mode == 'mass_mail' or wizard.is_log or (wizard.composition_mode == 'mass_post' and not wizard.notify):  # log a note: subtype is False
                subtype_id = False
            elif wizard.subtype_id:
                subtype_id = wizard.subtype_id.id
            else:
                subtype_id = self.sudo().env.ref('mail.mt_comment', raise_if_not_found=False).id

            for res_ids in sliced_res_ids:
                batch_mails = Mail
                all_mail_values = wizard.get_mail_values(res_ids)
                for res_id, mail_values in all_mail_values.items():
                    if wizard.composition_mode == 'mass_mail':
                        batch_mails |= Mail.create(mail_values)
                    else:
                        ActiveModel.browse(res_id).message_post(
                            message_type=wizard.message_type,
                            subtype_id=subtype_id,
                            **mail_values)

                if wizard.composition_mode == 'mass_mail':
                    batch_mails.send(auto_commit=auto_commit)

        return {'type': 'ir.actions.act_window_close'}
