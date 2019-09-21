# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from ast import literal_eval
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.misc import ustr
from odoo.addons.base.ir.ir_mail_server import MailDeliveryException
from odoo.addons.auth_signup.models.res_partner import SignupError, now
_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'


    @api.multi
    def action_reset_password_custom(self):
        """ create signup token for each user, and send their signup url by email """
        # prepare reset password signup
        create_mode = bool(self.env.context.get('create_user'))
        # no time limit for initial invitation, only for reset password
        expiration = False if create_mode else now(days=+1)
        signup_url = self.mapped('partner_id').signup_prepare(signup_type="reset", expiration=expiration)