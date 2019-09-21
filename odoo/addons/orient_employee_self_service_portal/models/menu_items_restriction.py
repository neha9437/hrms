# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo import SUPERUSER_ID
from lxml import etree
from odoo.exceptions import UserError


class Employee(models.Model):
    _inherit = ['hr.employee']

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(Employee, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        uid = self._context.get('uid')
        doc = etree.XML(res['arch'])
        temp_var = []
        user_data = self.env['res.users'].browse(uid)
        if uid and uid != 1:
            self.env.cr.execute("select name from res_groups where id in (select gid from res_groups_users_rel where uid ="+str(uid)+" and name ilike '%Portal User%')")
            temp_var = self.env.cr.fetchall()
            if temp_var:
                raise UserError(_('Sorry, You are not allowed to access these documents!'))
            if user_data.password_reset == False:
                raise UserError(_('YOU HAVE NOT CHANGED YOUR PASSWORD YET ! \n'
                                  'Please click on your username on upper right hand corner, click on "change password" and follow the instructions. You wont be able to continue using the system unless you change your current default password.'))
        return res


class Resignation(models.Model):
    _inherit = ['hr.resignation']

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(Resignation, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        uid = self._context.get('uid')
        doc = etree.XML(res['arch'])
        temp_var = []
        user_data = self.env['res.users'].browse(uid)
        if uid and uid != 1:
            self.env.cr.execute("select name from res_groups where id in (select gid from res_groups_users_rel where uid ="+str(uid)+" and name ilike '%Portal User%')")
            temp_var = self.env.cr.fetchall()
            if temp_var:
                raise UserError(_('Sorry, You are not allowed to access these documents!'))
            if user_data.password_reset == False:
                raise UserError(_('YOU HAVE NOT CHANGED YOUR PASSWORD YET ! \n'
                                  'Please click on your username on upper right hand corner, click on "change password" and follow the instructions. You wont be able to continue using the system unless you change your current default password.'))
        return res


class EmployeeExit(models.Model):
    _inherit = ['hr.employee.exit']

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(EmployeeExit, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        uid = self._context.get('uid')
        doc = etree.XML(res['arch'])
        temp_var = []
        user_data = self.env['res.users'].browse(uid)
        if uid and uid != 1:
            self.env.cr.execute("select name from res_groups where id in (select gid from res_groups_users_rel where uid ="+str(uid)+" and name ilike '%Portal User%')")
            temp_var = self.env.cr.fetchall()
            if temp_var:
                raise UserError(_('Sorry, You are not allowed to access these documents!'))
            if user_data.password_reset == False:
                raise UserError(_('YOU HAVE NOT CHANGED YOUR PASSWORD YET ! \n'
                                  'Please click on your username on upper right hand corner, click on "change password" and follow the instructions. You wont be able to continue using the system unless you change your current default password.'))
        return res


class FNFForm(models.Model):
    _inherit = ['fnf.form']

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(FNFForm, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        uid = self._context.get('uid')
        doc = etree.XML(res['arch'])
        temp_var = []
        user_data = self.env['res.users'].browse(uid)
        if uid and uid != 1:
            self.env.cr.execute("select name from res_groups where id in (select gid from res_groups_users_rel where uid ="+str(uid)+" and name ilike '%Portal User%')")
            temp_var = self.env.cr.fetchall()
            if temp_var:
                raise UserError(_('Sorry, You are not allowed to access these documents!'))
            if user_data.password_reset == False:
                raise UserError(_('YOU HAVE NOT CHANGED YOUR PASSWORD YET ! \n'
                                  'Please click on your username on upper right hand corner, click on "change password" and follow the instructions. You wont be able to continue using the system unless you change your current default password.'))
        return res


class DepartmentClearance(models.Model):
    _inherit = ['department.clearance']

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(DepartmentClearance, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        uid = self._context.get('uid')
        doc = etree.XML(res['arch'])
        temp_var = []
        user_data = self.env['res.users'].browse(uid)
        if uid and uid != 1:
            self.env.cr.execute("select name from res_groups where id in (select gid from res_groups_users_rel where uid ="+str(uid)+" and name ilike '%Portal User%')")
            temp_var = self.env.cr.fetchall()
            if temp_var:
                raise UserError(_('Sorry, You are not allowed to access these documents!'))
            if user_data.password_reset == False:
                raise UserError(_('YOU HAVE NOT CHANGED YOUR PASSWORD YET ! \n'
                                  'Please click on your username on upper right hand corner, click on "change password" and follow the instructions. You wont be able to continue using the system unless you change your current default password.'))
        return res


class GamificationBadge(models.Model):
    _inherit = ['gamification.badge']

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(GamificationBadge, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        uid = self._context.get('uid')
        doc = etree.XML(res['arch'])
        temp_var = []
        user_data = self.env['res.users'].browse(uid)
        if uid and uid != 1:
            self.env.cr.execute("select name from res_groups where id in (select gid from res_groups_users_rel where uid ="+str(uid)+" and name ilike '%Portal User%')")
            temp_var = self.env.cr.fetchall()
            if temp_var:
                raise UserError(_('Sorry, You are not allowed to access these documents!'))
            if user_data.password_reset == False:
                raise UserError(_('YOU HAVE NOT CHANGED YOUR PASSWORD YET ! \n'
                                  'Please click on your username on upper right hand corner, click on "change password" and follow the instructions. You wont be able to continue using the system unless you change your current default password.'))          
        return res


class KRAMain(models.Model):
    _inherit = ['kra.main']

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(KRAMain, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        uid = self._context.get('uid')
        doc = etree.XML(res['arch'])
        temp_var = []
        user_data = self.env['res.users'].browse(uid)
        if uid and uid != 1:
            self.env.cr.execute("select name from res_groups where id in (select gid from res_groups_users_rel where uid ="+str(uid)+" and name ilike '%Portal User%')")
            temp_var = self.env.cr.fetchall()
            if temp_var:
                raise UserError(_('Sorry, You are not allowed to access these documents!'))
            if user_data.password_reset == False:
                raise UserError(_('YOU HAVE NOT CHANGED YOUR PASSWORD YET ! \n'
                                  'Please click on your username on upper right hand corner, click on "change password" and follow the instructions. You wont be able to continue using the system unless you change your current default password.'))  
        return res


class KraKpiWizard(models.TransientModel):
    _inherit = ['kra.kpi.wizard']

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(KraKpiWizard, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        uid = self._context.get('uid')
        doc = etree.XML(res['arch'])
        temp_var = []
        user_data = self.env['res.users'].browse(uid)
        if uid and uid != 1:
            self.env.cr.execute("select name from res_groups where id in (select gid from res_groups_users_rel where uid ="+str(uid)+" and name ilike '%Portal User%')")
            temp_var = self.env.cr.fetchall()
            if temp_var:
                raise UserError(_('Sorry, You are not allowed to access these documents!'))
            if user_data.password_reset == False:
                raise UserError(_('YOU HAVE NOT CHANGED YOUR PASSWORD YET ! \n'
                                  'Please click on your username on upper right hand corner, click on "change password" and follow the instructions. You wont be able to continue using the system unless you change your current default password.'))  
        return res


class WallPost(models.Model):
    _inherit = ['wall.post']

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(WallPost, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        uid = self._context.get('uid')
        doc = etree.XML(res['arch'])
        temp_var = []
        user_data = self.env['res.users'].browse(uid)
        if uid and uid != 1:
            self.env.cr.execute("select name from res_groups where id in (select gid from res_groups_users_rel where uid ="+str(uid)+" and name ilike '%Portal User%')")
            temp_var = self.env.cr.fetchall()
            if temp_var:
                raise UserError(_('Sorry, You are not allowed to access these documents!'))
            if user_data.password_reset == False:
                raise UserError(_('YOU HAVE NOT CHANGED YOUR PASSWORD YET ! \n'
                                  'Please click on your username on upper right hand corner, click on "change password" and follow the instructions. You wont be able to continue using the system unless you change your current default password.'))  
        return res


class SubordinateKRAView(models.Model):
    _inherit = ['subordinate.kra.view']

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(SubordinateKRAView, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        uid = self._context.get('uid')
        doc = etree.XML(res['arch'])
        temp_var = []
        user_data = self.env['res.users'].browse(uid)
        if uid and uid != 1:
            self.env.cr.execute("select name from res_groups where id in (select gid from res_groups_users_rel where uid ="+str(uid)+" and name ilike '%Portal User%')")
            temp_var = self.env.cr.fetchall()
            if temp_var:
                raise UserError(_('Sorry, You are not allowed to access these documents!'))
            if user_data.password_reset == False:
                raise UserError(_('YOU HAVE NOT CHANGED YOUR PASSWORD YET ! \n'
                                  'Please click on your username on upper right hand corner, click on "change password" and follow the instructions. You wont be able to continue using the system unless you change your current default password.'))  
        return res


class HRHolidays(models.Model):
    _inherit = ['hr.holidays']

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(HRHolidays, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        uid = self._context.get('uid')
        doc = etree.XML(res['arch'])
        temp_var = []
        user_data = self.env['res.users'].browse(uid)
        if uid and uid != 1:
            self.env.cr.execute("select name from res_groups where id in (select gid from res_groups_users_rel where uid ="+str(uid)+" and name ilike '%Portal User%')")
            temp_var = self.env.cr.fetchall()
            if temp_var:
                raise UserError(_('Sorry, You are not allowed to access these documents!'))
            if user_data.password_reset == False:
                raise UserError(_('YOU HAVE NOT CHANGED YOUR PASSWORD YET ! \n'
                                  'Please click on your username on upper right hand corner, click on "change password" and follow the instructions. You wont be able to continue using the system unless you change your current default password.'))       
        return res


class BirthdayReport(models.Model):
    _inherit = ['birthday.report.new']

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(BirthdayReport, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        uid = self._context.get('uid')
        doc = etree.XML(res['arch'])
        temp_var = []
        user_data = self.env['res.users'].browse(uid)
        if uid and uid != 1:
            self.env.cr.execute("select name from res_groups where id in (select gid from res_groups_users_rel where uid ="+str(uid)+" and name ilike '%Portal User%')")
            temp_var = self.env.cr.fetchall()
            if temp_var:
                raise UserError(_('Sorry, You are not allowed to access these documents!'))
            if user_data.password_reset == False:
                raise UserError(_('YOU HAVE NOT CHANGED YOUR PASSWORD YET ! \n'
                                  'Please click on your username on upper right hand corner, click on "change password" and follow the instructions. You wont be able to continue using the system unless you change your current default password.'))       
        return res


# class PaySlip(models.Model):
#     _inherit = ['pay.slip']

#     @api.model
#     def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
#         res = super(PaySlip, self).fields_view_get(
#             view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
#         uid = self._context.get('uid')
#         doc = etree.XML(res['arch'])
#         temp_var = []
#         user_data = self.env['res.users'].browse(uid)
#         if uid and uid != 1:
#             if user_data.password_reset == False:
#                 raise UserError(_('YOU HAVE NOT CHANGED YOUR PASSWORD YET ! \n'
#                                   'Please click on your username on upper right hand corner, click on preferences and change your password. You wont be able to continue using the system unless you change your current default password.'))       
#         #     self.env.cr.execute("select name from res_groups where id in (select gid from res_groups_users_rel where uid ="+str(uid)+" and name ilike '%Portal User%')")
#         #     temp_var = self.env.cr.fetchall()
#         # if temp_var:
#         #     raise UserError(_('Sorry, You are not allowed to access these documents!'))
#         return res

# class TDSSummary(models.Model):
#     _inherit = ['tds.summary']

#     @api.model
#     def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
#         res = super(TDSSummary, self).fields_view_get(
#             view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
#         uid = self._context.get('uid')
#         doc = etree.XML(res['arch'])
#         temp_var = []
#         user_data = self.env['res.users'].browse(uid)
#         if uid and uid != 1:
#             if user_data.password_reset == False:
#                 raise UserError(_('YOU HAVE NOT CHANGED YOUR PASSWORD YET ! \n'
#                                   'Please click on your username on upper right hand corner, click on preferences and change your password. You wont be able to continue using the system unless you change your current default password.'))       
#         #     self.env.cr.execute("select name from res_groups where id in (select gid from res_groups_users_rel where uid ="+str(uid)+" and name ilike '%Portal User%')")
#         #     temp_var = self.env.cr.fetchall()
#         # if temp_var:
#         #     raise UserError(_('Sorry, You are not allowed to access these documents!'))
#         return res


# class Form16(models.Model):
#     _inherit = ['form.16']

#     @api.model
#     def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
#         res = super(Form16, self).fields_view_get(
#             view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
#         uid = self._context.get('uid')
#         doc = etree.XML(res['arch'])
#         temp_var = []
#         user_data = self.env['res.users'].browse(uid)
#         if uid and uid != 1:
#             if user_data.password_reset == False:
#                 raise UserError(_('YOU HAVE NOT CHANGED YOUR PASSWORD YET ! \n'
#                                   'Please click on your username on upper right hand corner, click on preferences and change your password. You wont be able to continue using the system unless you change your current default password.'))       
#         #     self.env.cr.execute("select name from res_groups where id in (select gid from res_groups_users_rel where uid ="+str(uid)+" and name ilike '%Portal User%')")
#         #     temp_var = self.env.cr.fetchall()
#         # if temp_var:
#         #     raise UserError(_('Sorry, You are not allowed to access these documents!'))
#         return res


# class ConveyanceReimbursement(models.Model):
#     _inherit = ['conveyance.reimbursement']

#     @api.model
#     def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
#         res = super(ConveyanceReimbursement, self).fields_view_get(
#             view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
#         uid = self._context.get('uid')
#         doc = etree.XML(res['arch'])
#         temp_var = []
#         user_data = self.env['res.users'].browse(uid)
#         if uid and uid != 1:
#             if user_data.password_reset == False:
#                 raise UserError(_('YOU HAVE NOT CHANGED YOUR PASSWORD YET ! \n'
#                                   'Please click on your username on upper right hand corner, click on preferences and change your password. You wont be able to continue using the system unless you change your current default password.'))       
#         #     self.env.cr.execute("select name from res_groups where id in (select gid from res_groups_users_rel where uid ="+str(uid)+" and name ilike '%Portal User%')")
#         #     temp_var = self.env.cr.fetchall()
#         # if temp_var:
#         #     raise UserError(_('Sorry, You are not allowed to access these documents!'))
#         return res

# class PolicyDocuments(models.Model):
#     _inherit = ['policy.documents']

#     @api.model
#     def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
#         res = super(PolicyDocuments, self).fields_view_get(
#             view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
#         uid = self._context.get('uid')
#         doc = etree.XML(res['arch'])
#         temp_var = []
#         user_data = self.env['res.users'].browse(uid)
#         if uid and uid != 1:
#             if user_data.password_reset == False:
#                 raise UserError(_('YOU HAVE NOT CHANGED YOUR PASSWORD YET ! \n'
#                                   'Please click on your username on upper right hand corner, click on preferences and change your password. You wont be able to continue using the system unless you change your current default password.'))       
#         #     self.env.cr.execute("select name from res_groups where id in (select gid from res_groups_users_rel where uid ="+str(uid)+" and name ilike '%Portal User%')")
#         #     temp_var = self.env.cr.fetchall()
#         # if temp_var:
#         #     raise UserError(_('Sorry, You are not allowed to access these documents!'))
#         return res


# class ApplicationDocuments(models.Model):
#     _inherit = ['application.documents']

#     @api.model
#     def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
#         res = super(ApplicationDocuments, self).fields_view_get(
#             view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
#         uid = self._context.get('uid')
#         doc = etree.XML(res['arch'])
#         temp_var = []
#         user_data = self.env['res.users'].browse(uid)
#         if uid and uid != 1:
#             if user_data.password_reset == False:
#                 raise UserError(_('YOU HAVE NOT CHANGED YOUR PASSWORD YET ! \n'
#                                   'Please click on your username on upper right hand corner, click on preferences and change your password. You wont be able to continue using the system unless you change your current default password.'))       
#         #     self.env.cr.execute("select name from res_groups where id in (select gid from res_groups_users_rel where uid ="+str(uid)+" and name ilike '%Portal User%')")
#         #     temp_var = self.env.cr.fetchall()
#         # if temp_var:
#         #     raise UserError(_('Sorry, You are not allowed to access these documents!'))
#         return res
        

class HrAttendance(models.Model):
    _inherit = ['hr.attendance']

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(HrAttendance, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        uid = self._context.get('uid')
        doc = etree.XML(res['arch'])
        temp_var = []
        user_data = self.env['res.users'].browse(uid)
        if uid and uid != 1:
            self.env.cr.execute("select name from res_groups where id in (select gid from res_groups_users_rel where uid ="+str(uid)+" and name ilike '%Portal User%')")
            temp_var = self.env.cr.fetchall()
            if temp_var:
                raise UserError(_('Sorry, You are not allowed to access these documents!'))
            if user_data.password_reset == False:
                raise UserError(_('YOU HAVE NOT CHANGED YOUR PASSWORD YET ! \n'
                                  'Please click on your username on upper right hand corner, click on "change password" and follow the instructions. You wont be able to continue using the system unless you change your current default password.'))       
        return res