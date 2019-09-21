# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class OfferLetterWizard(models.TransientModel):
    _name = 'offer.letter.wizard'
    _description = 'Wizard for attaching and sending offer and portal link'

    @api.model
    def default_get(self, fields):
        rec = super(OfferLetterWizard, self).default_get(fields)
        context = dict(self._context or {})
        active_id = context.get('active_id', False)

        rec['hr_applicant_id'] = active_id
        applicant_name = self.env['hr.applicant'].browse(active_id).partner_name
        rec['applicant_name'] = applicant_name
        #     inv = self.env['account.invoice'].browse(active_id)
        #     return inv.name
        return rec

    hr_applicant_id = fields.Many2one('hr.applicant',string="Application") 
    applicant_name = fields.Char(string='Applicant', copy=False)

    # delivery_packaging_id = fields.Many2one(
    #     'product.packaging',
    #     default=lambda self: self._default_delivery_packaging_id()
    # )
    # shipping_weight = fields.Float(
    #     string='Shipping Weight',
    #     default=lambda self: self._default_shipping_weight()
    # )


    def send_offer_letter(self):
        # partner_id = self.env['res.partner'].create({
        #         'is_company': False,
        #         'name':self.hr_applicant_id.partner_name,
        #         'email':self.hr_applicant_id.email_from,
        #     })
        # print(partner_id)
        # service_portal_group_id = self.env['res.groups'].search([('name','=','Service Portal User')])
        # portal_wizard_user_ids = []
        # portal_wizard_user_ids.append(portal_wizard_user_id.id)
        # print(service_portal_group_id)
        # portal_wizard_id = self.env['portal.wizard'].create({
        #         'portal_id': group_id.id,
        #         'welcome_message':"hello how are you?",
        #         # 'user_ids':[(6,0,portal_wizard_user_ids)]
        #     })
        # portal_wizard_user_id = self.env['portal.wizard.user'].create({
        #         'wizard_id':portal_wizard_id.id,
        #         'partner_id':partner_id.id,
        #         'email':self.hr_applicant_id.email_from,
        #         'in_portal':True,
        #     })
        # portal_wizard_user_id.write({'wizard_id':portal_wizard_id})
        service_portal_user_id = self.env['res.users'].create({
                'name': self.hr_applicant_id.partner_name,
                'login':self.hr_applicant_id.email_from
            })
        service_portal_group_id = self.env['res.groups'].search([('name','=','Service Portal User')])
        employee_group_id = self.env['res.groups'].search([('name','=','Employee')])
        group_id = service_portal_group_id.id
        user_id = service_portal_user_id.id
        que = self.env.cr.execute('insert into res_groups_users_rel (gid,uid) values (%s,%s)',(group_id,user_id))
        self.env.cr.commit()
        service_portal_user_id.partner_id.write({'email':self.hr_applicant_id.email_from})
        self.env.cr.commit()
        # group_user_rel_ids = self.env['res.groups.users.rel'].search([('uid','=',user_id),('gid','!=',group_id)])
        # print(group_user_rel_ids)
        # asdfasd
        # self.env.cr.execute('delete from res_groups_users_rel where uid in %s',(tuple(group_user_rel_ids.ids),))
        self.env.cr.execute("delete from res_groups_users_rel where uid=%s and gid!=%s and gid!=%s" %(str(user_id),str(group_id),str(employee_group_id.id)))
        self.env.cr.commit()
        contract_proposed_stage_id = self.env['hr.recruitment.stage'].search([('name','=','Contract Proposed')])
        self.hr_applicant_id.write({'stage_id':contract_proposed_stage_id.id,'offer_letter_sent':True})
        users = self.env['res.users'].search([('login', '=', self.hr_applicant_id.email_from)])
        if len(users) != 1:
            raise Exception(_('Reset password: invalid username or email'))
        return users.action_reset_password_custom()
        # offer_letter_email_template = self.env.ref('hr_selfservice_portal.offer_letter_email_template')
        # self.env['mail.template'].browse(offer_letter_email_template.id).send_mail(self.id)
        # return True