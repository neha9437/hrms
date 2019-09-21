# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    signup_token = fields.Char(copy=False,groups="base.group_erp_manager,hr_recruitment.group_hr_recruitment_manager,hr.group_hr_user,hr.group_hr_manager")
    signup_type = fields.Char(string='Signup Token Type', copy=False, groups="base.group_erp_manager,hr_recruitment.group_hr_recruitment_manager,hr.group_hr_user,hr.group_hr_manager")
    signup_expiration = fields.Datetime(copy=False, groups="base.group_erp_manager,hr_recruitment.group_hr_recruitment_manager,hr.group_hr_user,hr.group_hr_manager")
    signup_valid = fields.Boolean(compute='_compute_signup_valid', string='Signup Token is Valid')
    signup_url = fields.Char(compute='_compute_signup_url', string='Signup URL')