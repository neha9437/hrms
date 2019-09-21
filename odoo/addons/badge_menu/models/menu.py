# -*- coding: utf-8 -*-
from odoo import models

class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    def get_needaction_data(self, ids):
        """ Return for each menu entry of ids :
            - if it uses the needaction mechanism (needaction_enabled)
            - the needaction counter of the related action, taking into account
              the action domain
        """
        res = {}
        menu_item = ['My Attendances','New Leave Request','Pending Leave Requests','Approved Leave Requests','Refused Leave Requests','All Leave Requests','Allocated Leaves','Leaves Approved','Leaves Refused']
        for menu in self.browse(ids):
            res[menu.id] = {
                'needaction_enabled': False,
                'needaction_counter': False,
            }
            if menu.action and menu.action.type in ('ir.actions.act_window', 'ir.actions.client') and menu.action.res_model:
                if menu.action.res_model in self.env:
                    obj = self.env[menu.action.res_model]
                    if obj._needaction:
                        if menu.action.type == 'ir.actions.act_window':
                            dom = menu.action.domain and eval(menu.action.domain, {'uid': self.env.uid}) or []
                        else:
                            dom = eval(menu.action.params_store or '{}', {'uid': uid}).get('domain')
                        if menu.name not in menu_item:
                            res[menu.id]['needaction_enabled'] = obj._needaction
                            res[menu.id]['needaction_counter'] = obj._needaction_count(self.env.uid,dom)
        return res