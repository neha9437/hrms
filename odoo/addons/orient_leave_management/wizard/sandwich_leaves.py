# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.http import request
from datetime import datetime, timedelta
from dateutil.rrule import rrule, DAILY
from odoo.exceptions import UserError, AccessError, ValidationError


class HolidaysSandwich(models.Model):
    _name = "hr.holidays.status.sandwich"

    # def _get_no_of_days(self):
    #     if self._context.get('active_id'):
    #         holiday_id = self._context.get('active_id')
    #     holiday = request.env['hr.holidays'].browse([holiday_id])
    #     dfn = datetime.strptime(holiday.date_from_new, '%Y-%m-%d')
    #     fri_leave_id = None
    #     mon_leave_id = None
    #     for dt2 in rrule(DAILY, dtstart=dfn, until=dfn):
    #         # if friday
    #         if dt2.weekday() == 4:
    #             sun = dt2+timedelta(days=2)
    #             date_from_new = holiday.date_from_new
    #         # if monday
    #         if dt2.weekday() == 0:
    #             sun = dt2-timedelta(days=2)
    #             date_from_new = sun
    #     return date_from_new

    sandwich_id = fields.Many2one('sandwich.leaves', string='Sandwich')
    # holiday_id = fields.Many2one('hr.holidays', string='Holiday')
    hr_holiday_status_id = fields.Many2one('hr.holidays.status', domain=[('sandwich', '=', True)], required=True, string='Leave Type',track_visibility='onchange')
    no_of_days = fields.Float('Number of days', required=True, copy=False, default=1.00)
    comp_off_date = fields.Date('Comp Off Date')
    code = fields.Char('Code', required=True, readonly=True, translate=True)


    @api.onchange('hr_holiday_status_id')
    def onchange_hr_holiday_status_id(self):
        data = {}
        if self.hr_holiday_status_id:
            data['code'] = self.hr_holiday_status_id.code
        else:
            data['code'] = None
        return {'value':data}



class SandwichLeaves(models.Model):
    _name = 'sandwich.leaves'
    _description = 'Wizard for sandwich leaves'


    def _default_employee(self):
        if self._context.get('active_id'):
            holiday_id = self._context.get('active_id')
        holiday = request.env['hr.holidays'].browse([holiday_id])
        return holiday.employee_id.id

    def _get_date_from_new(self):
        return self._context.get('date_from_new')

    def _get_date_to_new(self):
        return self._context.get('date_to_new')


    # def _default_total_days(self):
    #     if self._context.get('active_id'):
    #         holiday_id = self._context.get('active_id')
    #     holiday = request.env['hr.holidays'].browse([holiday_id])
    #     return holiday.total_days+2

    def _default_total_days(self):
        if self._context.get('date_from_new') and self._context.get('date_to_new'):
            dfn = datetime.strptime(self._context.get('date_from_new'), '%Y-%m-%d')
            dtn = datetime.strptime(self._context.get('date_to_new'), '%Y-%m-%d')
            total_days = abs((dfn - dtn).days)+1
            return total_days


    date_from_new = fields.Date('From', readonly=True, index=True, copy=False, default=_get_date_from_new)
    date_to_new = fields.Date('To', readonly=True, index=True, copy=False, default=_get_date_to_new)
    # date_from_new = fields.Date('From', readonly=True, index=True, copy=False)
    # date_to_new = fields.Date('To', readonly=True, index=True, copy=False)
    total_days = fields.Float('Allocation', readonly=True, copy=False, help='Number of days of the leave request according to your working schedule.',default=_default_total_days)
    holiday_sandwich_ids = fields.One2many('hr.holidays.status.sandwich', 'sandwich_id', string='Select leave types')
    employee_id = fields.Many2one('hr.employee','Employee')
    manager_id = fields.Many2one('hr.employee','manager')
    hr_manager_id = fields.Many2one('hr.employee','HR Manager')


    @api.multi
    def action_proceed_sandwich_leaves(self):
        holiday_id = None
        if self._context.get('active_id'):
            holiday_id = self._context.get('active_id')
        holiday = request.env['hr.holidays'].browse([holiday_id])
        if not self.holiday_sandwich_ids:
            raise ValidationError(_('Please select the leave types !'))
        dfn = datetime.strptime(self.date_from_new, '%Y-%m-%d')
        for dt2 in rrule(DAILY, dtstart=dfn, until=dfn):
            new_day = dt2 
        days = 0
        wizard_pl_days = 0
        wizard_sl_days = 0
        wizard_co_days = 0
        
        self.employee_id = holiday.employee_id.id
        self.manager_id = holiday.manager_id.id
        self.hr_manager_id = holiday.hr_manager_id.id

        total_no_of_days = 0

        for each_holiday_sandwich_id in self.holiday_sandwich_ids:
            if each_holiday_sandwich_id.no_of_days == 0:
               raise UserError(_('Number of days cannot be 0 !'))
            if each_holiday_sandwich_id.code == 'CO':
                applied_co_ids = self.env['hr.holidays'].search([('code', '=', 'CO'),('employee_id', '=', holiday.employee_id.id),('comp_off_date', '=', each_holiday_sandwich_id.comp_off_date),('state', 'in', ['confirm','validate'])])
                if applied_co_ids:
                    raise UserError(_('You have already applied for Compensatory off on %s!') % (each_holiday_sandwich_id.comp_off_date))
                comp_off_dates = []
                allocated_co_ids = self.env['hr.holidays'].search([('code', '=', 'CO'),('employee_id', '=', holiday.employee_id.id),('allocated', '=', True)])
                if allocated_co_ids:
                    for allocated_co_id in allocated_co_ids:
                        comp_off_dates.append(allocated_co_id.comp_off_date)
                    if comp_off_dates:
                        if each_holiday_sandwich_id.comp_off_date not in comp_off_dates:
                            raise UserError(_('Available Compensatory dates for you are : %s !') % (comp_off_dates))
            total_no_of_days = total_no_of_days + each_holiday_sandwich_id.no_of_days
            if each_holiday_sandwich_id.code == 'PL':
                wizard_pl_days = wizard_pl_days + each_holiday_sandwich_id.no_of_days
            elif each_holiday_sandwich_id.code == 'SL/CL':
                wizard_sl_days = wizard_sl_days + each_holiday_sandwich_id.no_of_days
            elif each_holiday_sandwich_id.code == 'CO':
                wizard_co_days = wizard_co_days + each_holiday_sandwich_id.no_of_days
        if total_no_of_days < self.total_days:
            raise UserError(_('Total number of days should sum up to %s !') % (self.total_days))
        if total_no_of_days > self.total_days:
            raise UserError(_('Total number of days cannot exceed %s !') % (self.total_days))

        
        for each_holiday_sandwich_id in self.holiday_sandwich_ids:
            r = 1
            test = []
            while r < each_holiday_sandwich_id.no_of_days+1:
                test.append(r)
                r = r+1
            for each in test:
                vals = {
                            'name':holiday.name, 
                            'code': each_holiday_sandwich_id.hr_holiday_status_id.code,
                            'holiday_type':'employee',
                            'employee_id':holiday.employee_id.id,
                            'holiday_status_id':each_holiday_sandwich_id.hr_holiday_status_id.id, 
                            'manager_id':holiday.manager_id.id,
                            'total_days':1, 
                            'balanced_days':0,
                            'department_id':holiday.department_id.id,
                            'type':'remove',
                            'state':'confirm',
                            'current_month':holiday.current_month,
                            'financial_year_id':holiday.financial_year_id.id,
                            'payslip_status': False,
                            'user_id': self.env.uid,
                            'date_from_new': new_day+timedelta(days=days),
                            'date_to_new': new_day+timedelta(days=days),
                            'holiday_type': 'employee',
                            'manager_user_id': holiday.manager_user_id.id,
                            'leave_manager_id': holiday.leave_manager_id.id,
                            'allocated': False,
                            'half_day_applicable': False,
                            'sandwich': True
                }
                if each_holiday_sandwich_id.hr_holiday_status_id.code == 'CO':
                    dcof = datetime.strptime(each_holiday_sandwich_id.comp_off_date, '%Y-%m-%d')
                    difference =  abs((new_day+timedelta(days=days) - dcof).days)
                    if difference > 30:
                        raise UserError(_('Sorry you cannot apply for this leave ! The Comp Off selected is either already lapsed or will lapse for the selected duration!'))
                    pre1 = new_day+timedelta(days=days)-timedelta(days=1)
                    pre2 = new_day+timedelta(days=days)-timedelta(days=2)
                    pre1_id = self.env['hr.holidays'].search([('code', '=', 'CO'),('employee_id', '=', holiday.employee_id.id),('state', 'in', ['confirm','validate']),('date_from_new', '=', pre1)])
                    pre2_id = self.env['hr.holidays'].search([('code', '=', 'CO'),('employee_id', '=', holiday.employee_id.id),('state', 'in', ['confirm','validate']),('date_from_new', '=', pre2)])
                    if pre1_id and pre2_id:
                        raise UserError(_('You cannot apply for 3 consecutive compensatory leaves!'))
                    vals.update({'comp_off':True ,'comp_off_date':each_holiday_sandwich_id.comp_off_date})
                else:
                    vals.update({'comp_off':False ,'comp_off_date':None})
                new_sandwich_holiday_id = self.env['hr.holidays'].create(vals)
                days = days + 1

        print("wizard_pl_days",wizard_pl_days)
        print("wizard_sl_days",wizard_sl_days)
        
        if wizard_pl_days:
            pl_allocated_leave_id = request.env['hr.holidays'].search([('employee_id', '=', holiday.employee_id.id),('type', '=', 'add'),('code', '=', 'PL')])
            pl_balanced_days = pl_allocated_leave_id.balanced_days-wizard_pl_days
            self.env.cr.execute("update hr_holidays set balanced_days=%s where id=%s" %(pl_balanced_days,str(pl_allocated_leave_id.id)))
        
        if wizard_sl_days:
            sl_allocated_leave_id = request.env['hr.holidays'].search([('employee_id', '=', holiday.employee_id.id),('type', '=', 'add'),('code', '=', 'SL/CL')])
            sl_balanced_days = sl_allocated_leave_id.balanced_days-wizard_sl_days
            self.env.cr.execute("update hr_holidays set balanced_days=%s where id=%s" %(sl_balanced_days,str(sl_allocated_leave_id.id)))
        
        if wizard_co_days:
            co_allocated_leave_id = request.env['hr.holidays'].search([('employee_id', '=', holiday.employee_id.id),('type', '=', 'add'),('code', '=', 'CO')])
            co_balanced_days = co_allocated_leave_id.balanced_days-wizard_co_days
            self.env.cr.execute("update hr_holidays set balanced_days=%s where id=%s" %(co_balanced_days,str(co_allocated_leave_id.id)))

        template_id = self.env.ref('orient_leave_management.email_template_for_leavessandwich', False)
        self.env['mail.template'].browse(template_id.id).send_mail(self.id, force_send=True)

        return {
            'name': _('Sandwich Leaves Applied'),
            'domain': [('sandwich', '=', True),('state', '=', 'confirm'),('name', '=', holiday.name)],
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.holidays',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }