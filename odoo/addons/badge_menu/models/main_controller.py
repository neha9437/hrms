# -*- coding: utf-8 -*-
import logging

from odoo import http, _
from odoo.exceptions import UserError
from odoo.http import request

_logger = logging.getLogger(__name__)

class MyMenu(http.Controller):
    
    @http.route('/web/menu/load_needaction', type='json', auth="user")
    def load_needaction(self, menu_ids):
        """ Loads needaction counters for specific menu ids.

            :return: needaction data
            :rtype: dict(menu_id: {'needaction_enabled': boolean, 'needaction_counter': int})
        """
        return request.env['ir.ui.menu'].get_needaction_data(menu_ids)