# -*- coding: utf-8 -*-
import datetime
from odoo import api, models, _
from odoo.tools.safe_eval import safe_eval
#
# Use period and Journal for selection or resources
#


class ir_needaction_mixin(models.AbstractModel):
    _name = 'ir.needaction_mixin'
    _needaction = True

    #------------------------------------------------------
    # Addons API
    #------------------------------------------------------

    def _needaction_domain_get(self, cr, uid, context=None):
        """ Returns the domain to filter records that require an action
            :return: domain or False is no action
        """
        return False

    #------------------------------------------------------
    # "Need action" API
    #------------------------------------------------------

    def _needaction_count(self, cr, uid, domain=None, context=None):
        """ Get the number of actions uid has to perform. """
        if context is None:
            context ={}
        dom = self._needaction_domain_get()
        if not dom:
            return 0
        if domain == None:
            domain = []
        res = self.search(dom, limit=100, order='id DESC')
        return len(res)
