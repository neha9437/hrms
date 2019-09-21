# -*- coding: utf-8 -*-
import datetime
from datetime import datetime, timedelta, date
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
date_format = "%Y-%m-%d"
from odoo import models, api
from lxml import etree
import simplejson
from odoo.osv.orm import setup_modifiers
from dateutil.relativedelta import relativedelta
import base64
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo.tools import config, human_size, ustr, html_escape
from odoo.tools.mimetypes import guess_mimetype
import logging
import os
import csv
import shutil
import os
import base64, urllib
from io import StringIO,BytesIO
import uuid
import calendar
from collections import OrderedDict


import datetime
from datetime import datetime, timedelta
from dateutil import *
from dateutil.relativedelta import relativedelta
from odoo.tools import float_compare
import logging
import math
from odoo.tools.translate import _
from odoo.modules.module import get_module_resource
from dateutil.rrule import rrule, DAILY

# from dateutil.relativedelta import relativedelta
# from lxml import etree
# from openerp.osv.orm import setup_modifiers

_logger = logging.getLogger(__name__)


def get_current_financial_year(self):
    current_date = current_month = current_year = ''
    current_date =  datetime.now().date()
    current_month = datetime.strptime(str(current_date), "%Y-%m-%d").strftime('%B')
    current_year = datetime.strptime(str(current_date), "%Y-%m-%d").strftime('%Y')
    today_date = datetime.now().date()
    year = current_date.year
    year1=current_date.strftime('%y')
    start_year =  end_year = ''
    year = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").year
    month = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").month
    if month > 3:
        start_year = year
        end_year = year+1
        year1 = int(year1)+1
    else:
        start_year = year-1
        end_year = year
        year1 = int(year1)
    financial_start_date = str(start_year)+'-04-01'
    financial_end_date = str(end_year)+'-03-31'
    search_year = self.env['year.master'].search([('start_date','=',financial_start_date),('end_date','=',financial_end_date)])
    if search_year:
        return search_year[0].name
    else:
        return False

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'
    _order = 'attendance_date'

    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        """overriding the __check_validity function for employee attendance."""
        pass

    attendance_date = fields.Date(string="Date", required=True,help='Attendance date of the employee')
    employee_code = fields.Integer('Employee Code')
    department_id_val = fields.Many2one('hr.department',string="Department",help="Employee Department")
    employee_status = fields.Selection([('AB', 'AB'),
                                        ('P', 'P'),
                                        ('WO', 'WO'),
                                        ('PH','PH'),
                                        ('PH+WO','PH+WO'),
                                        ('PL','PL'), 
                                        ('SL/CL','SL/CL'),
                                        ('OD','OD'), 
                                        ('SOD','SOD'),
                                        ('CO','CO'),
                                        ('PA','PA'),
                                        ('MA','MA'),
                                        ('ML','ML'),
                                        ('LWP','LWP'),
                                        ('WFM','WFM'),
                                        ('half_day_p_ab','Half P + Half AB'),
                                        ('half_day_sl','Half Day SL/CL + Half Day P'),
                                        ('half_day_pl','Half Day PL + Half Day P'),
                                        ('P+WO','P+WO'),
                                        ('half_p_half_od','Half P + Half OD'),
                                        ('half_ab_half_od','Half AB + Half OD'),
                                        ('half_pl_half_od','HAlf PL + Half OD'),
                                        ('half_sl_half_od','Half SL/CL + HAlf OD'),
                                        ], string='Employee Status', default='AB')
    remarks = fields.Char(string='Remarks')
    in_time = fields.Char('In Time',size=5)
    out_time = fields.Char('Out Time',size=5)
    early_leaving = fields.Char('Early Leaving',size=5)
    late_coming = fields.Char('Late Coming',size=5)
    in_time_updation = fields.Char('In Time',size=5)
    out_time_updation = fields.Char('Out Time',size=5)
    state = fields.Selection([('draft', 'Draft'),('approval', 'Approval'),('done','Done'),('rejected','Rejected')], string='Status', default='draft')
    reason = fields.Char('Reason')
    shift = fields.Many2one('hr.employee.shift.timing',string="Shift")
    import_status = fields.Selection([('importing', 'Importing'), ('biometric', 'Biometric'), ('quikformz', 'QuikFormz')], string='Data Status(Last Updated From)')
    approve_check = fields.Boolean('Approved record?', default=False)
    remarks = fields.Char('Remarks')
    site_master_id = fields.Many2one('site.master','Site')
    pr = fields.Float('PR')
    c_off = fields.Float('C-OFF')
    sl_cl = fields.Float('SL/CL')
    pa = fields.Float('PA')
    ph = fields.Float('PH')
    ab = fields.Float('AB')
    pl = fields.Float('PL')
    ml = fields.Float('ML')
    ma = fields.Float('MA')
    wo = fields.Float('WO')
    od = fields.Float('OD')
    lwp = fields.Float('LWP')
    worked_days = fields.Float('Paid Days')
    reject_check = fields.Boolean('Rejected record?', default=False)
    select_record = fields.Boolean('Select')
    bulk_approval_id = fields.Many2one('bulk.attendance.approval','Attendance Approval')    
    approved_rejected_date = fields.Date('Approved/Rejected Date')
    created = fields.Boolean('Created?',default=False)
    line_id1 = fields.Many2one('shift.application',string="Line ID",index=True, copy=False)
    hide_assign = fields.Boolean('Hide assign',default=False)

    @api.multi
    def assign(self,access_uid=None):
        if not self.shift:
            raise UserError(_('Kindly assign Shift!!'))
        if self.shift:
            self.write({'shift':self.shift.id,'hide_assign':True})

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        data = {}
        data['employee_code'] = self.employee_id.emp_code
        data['department_id_val'] = self.employee_id.department_id.id if self.employee_id.department_id else None
        data['site_master_id'] = self.employee_id.site_master_id.id if self.employee_id.site_master_id else None
        data['shift'] = self.employee_id.shift_id.id if self.employee_id.shift_id else None
        return {'value':data}

    def oncreate_employee_att(self,emp_id,emp_code,site_master_id,department_id,join_date,shift_id):
        day=1
        month=1
        if join_date:
            split_join_date=join_date.split('-')
            day=split_join_date[2]
            month = split_join_date[1]
        start_date = datetime.now().date().replace(month=int(month), day=int(day))  
        end_date = datetime.now().date().replace(month=12, day=31)
        start_date = datetime.strptime(str(start_date), "%Y-%m-%d").date()
        end_date = datetime.strptime(str(end_date), "%Y-%m-%d").date()
        print (start_date,type(start_date),end_date)
        delta1 = end_date - start_date
        employee_status = ''
        employee_id = emp_id.id
        print (site_master_id,'site_master_id')
        weekoffs = self.env['site.master'].browse(site_master_id).weekoffs
        print (weekoffs)
        sat_list = []
        sun_list = []
        first_list = []
        second_list = []
        third_list = []
        fourth_list = []
        fifth_list = []
        fifth_saturday = ''
        blank = ''
        dates = [str(start_date),str(end_date)]
        print (dates,'dates')
        start, end = [datetime.strptime(_, "%Y-%m-%d") for _ in dates]
        date_range = list(OrderedDict(((start + timedelta(_)).strftime(r"%m-%Y"), None) for _ in range((end - start).days)).keys())

        for i in range(delta1.days + 1):
            dates = start_date + timedelta(i)
            day_name = calendar.day_name[dates.weekday()]
            if day_name == 'Saturday':
                sat_list.append(dates)
            if day_name == 'Sunday':
                sun_list.append(dates)

        
        for y in date_range:
            split_range = y.split('-')
            c = calendar.Calendar(firstweekday=calendar.SUNDAY)
            monthcal = c.monthdatescalendar(int(split_range[1]),int(split_range[0]))
            second_saturday = [day for week in monthcal for day in week if day.weekday() == calendar.SATURDAY and day.month == int(split_range[0])][1]
            fourth_saturday = [day for week in monthcal for day in week if day.weekday() == calendar.SATURDAY and day.month == int(split_range[0])][3]
            first_saturday = [day for week in monthcal for day in week if day.weekday() == calendar.SATURDAY and day.month == int(split_range[0])][0]
            third_saturday = [day for week in monthcal for day in week if day.weekday() == calendar.SATURDAY and day.month == int(split_range[0])][2]
            if first_saturday in sat_list:
                if first_saturday not in first_list:
                    first_list.append(first_saturday)
            if third_saturday in sat_list:
                if third_saturday not in third_list:
                    third_list.append(third_saturday)
            ix = [day for week in monthcal for day in week if day.weekday() == calendar.SATURDAY and day.month == int(split_range[0])]
            if len(ix) > 4:
                fifth_saturday = [day for week in monthcal for day in week if day.weekday() == calendar.SATURDAY and day.month == int(split_range[0])][4]
                if fifth_saturday in sat_list:
                    if fifth_saturday not in fifth_list:
                        fifth_list.append(fifth_saturday)
            if second_saturday in sat_list:
                if second_saturday not in second_list:
                    second_list.append(second_saturday)
            if fourth_saturday in sat_list:
                if fourth_saturday not in fourth_list:
                    fourth_list.append(fourth_saturday)
        for i in range(delta1.days + 1):
            employee_status=''
            dates = start_date + timedelta(i)
            que = self.env.cr.execute('insert into hr_attendance(shift,employee_id,check_in,check_out,attendance_date,employee_code,department_id_val,site_master_id,employee_status,state) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(shift_id,employee_id,dates,dates,dates,emp_code,department_id,site_master_id,employee_status,'draft'))
            self.env.cr.commit()
            holiday_rec = self.env['holiday.master'].search([('holiday_date','=',dates)])
            if holiday_rec:
                site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s' % holiday_rec.id)
                result = self.env.cr.fetchall()
                if result:
                    for site in result:
                        if site[0] == site_master_id:
                            employee_status = 'PH'
                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',dates),('employee_code','=',emp_code)])
                            if search_attendance:
                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_code=%s', (employee_status,dates,emp_code))
                                self.env.cr.commit()


        employee_status = ''
        if weekoffs == '2_4':
            for sun in list(set(sun_list)):
                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s', ('WO',datetime.strptime(str(sun), "%Y-%m-%d").date(),employee_id))
            for x in first_list:
                holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                if holiday_rec:
                    site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                    if result:
                        for site in result:
                            if site[0] == site_master_id:                                   
                                employee_status = 'PH'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
            for x in third_list:
                holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                if holiday_rec:
                    site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                    result = self.env.cr.fetchall()
                    if result:
                        for site in result:
                            if site[0] == site_master_id:                                   
                                employee_status = 'PH'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
            for x in fifth_list:
                holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                if holiday_rec:
                    site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                    result = self.env.cr.fetchall()
                    if result:
                        for site in result:
                            if site[0] == site_master_id:
                                employee_status = 'PH'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
            for x in second_list:
                employee_status = 'WO'
                holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                if holiday_rec:
                    site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                    result = self.env.cr.fetchall()
                    if result:
                        for site in result:
                            if site[0] == site_master_id:                                   
                                employee_status = 'PH+WO'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                                else:
                                    employee_status = 'PH'
                                    search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                    if search_attendance:
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
                    else:
                        employee_status = 'WO'
                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                        if search_attendance:
                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                            self.env.cr.commit()
                else:
                    employee_status = 'WO'
                    search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                    if search_attendance:  
                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                        self.env.cr.commit()
            for x in fourth_list:
                employee_status = 'WO'
                holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                if holiday_rec:
                    site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                    result = self.env.cr.fetchall()
                    if result:
                        for site in result:
                            if site[0] == site_master_id:                                   
                                employee_status = 'PH+WO'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                                else:
                                    employee_status = 'PH'
                                    search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                    if search_attendance:
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
                    else:
                        employee_status = 'WO'
                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                        if search_attendance:
                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                            self.env.cr.commit()
                else:
                    employee_status = 'WO'
                    search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                    if search_attendance:
                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                        self.env.cr.commit()
        if weekoffs == '1_3_5':
            for sun in list(set(sun_list)):
                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s', ('WO',datetime.strptime(str(sun), "%Y-%m-%d").date(),employee_id))
            for x in second_list:
                holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                if holiday_rec:
                    site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                    result = self.env.cr.fetchall()
                    if result:
                        for site in result:
                            if site[0] == site_master_id:                                   
                                employee_status = 'PH'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
            for x in fourth_list:
                holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                if holiday_rec:
                    site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                    result = self.env.cr.fetchall()
                    if result:
                        for site in result:
                            if site[0] == site_master_id:                                   
                                employee_status = 'PH'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:
                                    if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
            for x in first_list:
                employee_status = 'WO'
                holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                if holiday_rec:
                    site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                    result = self.env.cr.fetchall()
                    if result:
                        for site in result:
                            if site[0] == site_master_id:                                   
                                employee_status = 'PH+WO'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:                                        
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                                else:
                                    employee_status = 'PH'
                                    search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                    if search_attendance:                                            
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
                    else:
                        employee_status = 'WO'
                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                        if search_attendance:                                
                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                            self.env.cr.commit()
                else:
                    employee_status = 'WO'
                    search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                    if search_attendance:
                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                        self.env.cr.commit()
            for x in third_list:
                employee_status = 'WO'
                holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                if holiday_rec:
                    site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                    result = self.env.cr.fetchall()
                    if result:
                        for site in result:
                            if site[0] == site_master_id:                                   
                                employee_status = 'PH+WO'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                                else:
                                    employee_status = 'PH'
                                    search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                    if search_attendance:                                            
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
                    else:
                        employee_status = 'WO'
                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                        if search_attendance:
                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                            self.env.cr.commit()

                else:
                    employee_status = 'WO'
                    search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                    if search_attendance:
                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                        self.env.cr.commit()
            for x in fifth_list:
                employee_status = 'WO'
                holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                if holiday_rec:
                    site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                    result = self.env.cr.fetchall()
                    if result:
                        for site in result:
                            if site[0] == site_master_id:                                   
                                employee_status = 'PH+WO'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                                else:
                                    employee_status = 'PH'
                                    search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                    if search_attendance:
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
                    else:
                        employee_status = 'WO'
                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                        if search_attendance:
                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                            self.env.cr.commit()
                else:
                    employee_status = 'WO'
                    search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                    if search_attendance:
                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                        self.env.cr.commit()
        if weekoffs == 'all':
            for sun in list(set(sun_list)):
                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s', ('WO',datetime.strptime(str(sun), "%Y-%m-%d").date(),employee_id))
            new_list = first_list + second_list + third_list + fourth_list + fifth_list
            for x in new_list:
                holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                if holiday_rec:
                    site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                    result = self.env.cr.fetchall()
                    if result:
                        for site in result:
                            if site[0] == site_master_id:                                   
                                employee_status = 'PH+WO'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                    else:
                        employee_status = 'WO'
                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                        if search_attendance:
                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                            self.env.cr.commit()
                else:
                    employee_status = 'WO'
                    search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                    if search_attendance:
                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                        self.env.cr.commit()
        if weekoffs == 'no':
            for sun in list(set(sun_list)):
                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s', ('WO',datetime.strptime(str(sun), "%Y-%m-%d").date(),employee_id))
            new_list = first_list + second_list + third_list + fourth_list + fifth_list
            for x in new_list:
                holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                if holiday_rec:
                    site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                    result = self.env.cr.fetchall()
                    if result:
                        for site in result:
                            if site[0] == site_master_id:                                   
                                employee_status = 'PH'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:                                        
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                    else:
                        employee_status = ''
                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                        if search_attendance:                                
                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                            self.env.cr.commit()
                else:
                    employee_status = ''
                    search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                    if search_attendance:                            
                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                        self.env.cr.commit()
        if weekoffs == 'saturday_weekoff':
            print (employee_status,'11111111')
            for sun in list(set(sun_list)):
                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s', (blank,datetime.strptime(str(sun), "%Y-%m-%d").date(),employee_id))
                employee_status = ''
                holiday_rec = self.env['holiday.master'].search([('holiday_date','=',sun)])
                if holiday_rec:
                    site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                    result = self.env.cr.fetchall()
                    if result:
                        for site in result:
                            if site[0] == site_master_id:                                   
                                employee_status = 'PH'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',sun),('employee_code','=',emp_code)],limit=1)
                                if search_attendance:
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(sun), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',sun),('employee_code','=',emp_code)],limit=1)
                if search_attendance:                    
                    employee_status = ''
                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(sun), "%Y-%m-%d").date(),employee_id))
                    self.env.cr.commit()
            employee_status=''                
            new_list = first_list + second_list + third_list + fourth_list + fifth_list
            for x in new_list:
                holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                if holiday_rec:
                    site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                    result = self.env.cr.fetchall()
                    if result:
                        for site in result:
                            if site[0] == site_master_id:                                   
                                employee_status = 'PH+WO'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                    else:
                        employee_status = 'WO'
                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                        if search_attendance:
                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                            self.env.cr.commit()
                else:
                    employee_status = 'WO'
                    search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                    if search_attendance:                    
                        employee_status = 'WO'
                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                        self.env.cr.commit()
        return True

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if 'employee_code' in fields:
            fields.remove('employee_code')
        if 'worked_hours' in fields:
            fields.remove('worked_hours')
        return super(HrAttendance, self.with_context(virtual_id=False)).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

    def save_attendance(self):
        flag = False
        flag1 = False
        site_master_id = self.site_master_id.id if self.site_master_id else self.employee_id.site_master_id.id
        if not self.in_time_updation or not self.out_time_updation:
            raise ValidationError(_('Please Enter proper In/Out Time'))
        if self.in_time_updation:
            in_time_updation = self.in_time_updation
            if ':' not in in_time_updation:
                raise ValidationError(_('Please Enter proper In Time'))
            if not self.out_time_updation:
                raise ValidationError(_('Please Enter Out Time'))
            in_time_split = in_time_updation.split(':')
            if in_time_split:
                in_time_hour = in_time_split[0]
                in_time_minute = in_time_split[1]
                if int(in_time_hour) > 23 or int(in_time_minute) > 59:
                    raise ValidationError(_('Please Enter proper In Time'))
            if len(in_time_split) != 2:
                raise ValidationError(_('Please Enter proper In Time'))
            main_id =self.id
            self.state = 'approval'
            flag = True
            if self.in_time_updation != self.in_time:
                flag1 =True
        if self.out_time_updation:
            out_time_updation = self.out_time_updation
            if not self.in_time_updation:
                raise ValidationError(_('Please Enter In Time'))
            if ':' not in out_time_updation:
                raise ValidationError(_('Please Enter proper Out Time'))
            out_time_split = out_time_updation.split(':')
            if out_time_split:
                out_time_hour = out_time_split[0]
                out_time_minute = out_time_split[1]
                if int(out_time_hour) > 23 or int(out_time_minute) > 59:
                    raise ValidationError(_('Please Enter proper Out Time'))
            if len(out_time_split) != 2:
                raise ValidationError(_('Please Enter proper Out Time'))
            main_id =self.id
            self.state = 'approval'
            flag = True
            if self.out_time_updation != self.out_time:
                flag1 =True
        if self.in_time or self.out_time:
            attendance_date = self.attendance_date
            in_time_updation = self.in_time
            out_time_updation = self.out_time
            if ':' not in in_time_updation:
                raise ValidationError(_('Please Enter proper In Time'))
            if ':' not in out_time_updation:
                raise ValidationError(_('Please Enter proper Out Time'))
            in_time_split = in_time_updation.split(':')
            out_time_split = out_time_updation.split(':')
            if in_time_split:
                in_time_hour = in_time_split[0]
                in_time_minute = in_time_split[1]
                if int(in_time_hour) > 23 or int(in_time_minute) > 59:
                    raise ValidationError(_('Please Enter proper In Time'))
            if out_time_split:
                out_time_hour = out_time_split[0]
                out_time_minute = out_time_split[1]
                if int(in_time_hour) > 23 or int(in_time_minute) > 59:
                    raise ValidationError(_('Please Enter proper Out Time'))
            if len(in_time_split) != 2:
                raise ValidationError(_('Please Enter proper In Time'))
            if len(in_time_split) != 2:
                raise ValidationError(_('Please Enter proper Out Time'))
            check_in = str(attendance_date)+' '+str(in_time_updation)
            check_out = str(attendance_date)+' '+str(out_time_updation)
            check_in_time = datetime.strptime(str(check_in), "%Y-%m-%d %H:%M") - timedelta(hours=5)
            check_out_time = datetime.strptime(str(check_out), "%Y-%m-%d %H:%M")- timedelta(hours=5)
            check_in_min = check_in_time - timedelta(minutes=30)
            check_out_min = check_out_time - timedelta(minutes=30)
            tdiff =  check_out_time - check_in_time
            tdiff_string = str(tdiff)
            tdiff_split = tdiff_string.split(':')
            tdiff_split_val = tdiff_split[0]+'.'+tdiff_split[1]
            if ',' in tdiff_split_val:
                tdiff_split_comma = tdiff_split_val.split(',')
                tdiff_split_comma_val = tdiff_split_comma[1]
                tdiff_split_val = tdiff_split_comma_val
            worked_hours = float(tdiff_split_val)
            day = check_in_time.strftime('%A')
            holiday_master = self.env['holiday.master'].search([('holiday_date','=',attendance_date)])
            if holiday_master:
                site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s' % holiday_master.id)
                result = self.env.cr.fetchall()
                if result:
                    for site in result:
                        if site[0] == site_master_id:                            
                            employee_status = 'PH'
                        else:
                            if day in ('Saturday','Sunday'):
                                if worked_hours >=3.5:
                                    employee_status = 'P'
                                    diff_out_time_replace=None
                                    diff_in_time_replace =None
                                if worked_hours < 3.5:
                                    employee_status = 'AB'
                                    diff_out_time_replace=None
                                    diff_in_time_replace =None
                            elif day not in ('Saturday','Sunday'):
                                if worked_hours > 6.5:
                                    employee_status = 'P'
                                elif worked_hours >=4.5 and worked_hours <= 6.5:
                                    employee_status = 'half_day_p_ab'
                                else:
                                    employee_status = 'AB'
                                    diff_out_time_replace=None
                                    diff_in_time_replace =None
                else:
                    if day in ('Saturday','Sunday'):
                        if worked_hours >=3.5:
                            employee_status = 'P'
                            diff_out_time_replace=None
                            diff_in_time_replace =None
                        if worked_hours < 3.5:
                            employee_status = 'AB'
                            diff_out_time_replace=None
                            diff_in_time_replace =None
                    elif day not in ('Saturday','Sunday'):
                        if worked_hours > 6.5:
                            employee_status = 'P'
                        elif worked_hours >=4.5 and worked_hours <= 6.5:
                            employee_status = 'half_day_p_ab'
                        else:
                            employee_status = 'AB'
                            diff_out_time_replace=None
                            diff_in_time_replace =None
                    flag = True
            else:
                if day in ('Saturday','Sunday'):
                    if worked_hours >=3.5:
                        employee_status = 'P'
                        diff_out_time_replace=None
                        diff_in_time_replace =None
                    if worked_hours < 3.5:
                        employee_status = 'AB'
                        diff_out_time_replace=None
                        diff_in_time_replace =None
                elif day not in ('Saturday','Sunday'):
                    if worked_hours > 6.5:
                        employee_status = 'P'
                    elif worked_hours >=4.5 and worked_hours <= 6.5:
                        employee_status = 'half_day_p_ab'
                    else:
                        employee_status = 'AB'
                        diff_out_time_replace=None
                        diff_in_time_replace =None
                flag = True
            self.worked_hours = worked_hours
            self.employee_status = employee_status
            self.approve_check = True
            self.state = 'approval'
        if not flag1:
            raise ValidationError(_('You have not Updated either In Time or Out Time'))
        if flag:
            template_id = self.env.ref('orient_hr_attendance_import.email_template_employeeattendance_approval', False)
            self.env['mail.template'].browse(template_id.id).send_mail(self.id, force_send=True)
        return True

    @api.model
    def create(self, vals):
        site_master_id = vals.get('site_master_id')
        shift_id = vals.get('shift')
        worked_hours = 0
        diff_out_time_replace = None
        diff_in_time_replace = None
        if vals.get('attendance_date'):
            existing_attendance_id = self.search([('employee_id','=',vals.get('employee_id')),('attendance_date','=',vals.get('attendance_date'))])
            if existing_attendance_id:
                raise UserError(_('Attendance creation error!\nThe attendance for this employee already exists for the given date!'))
            if vals.get('in_time') or vals.get('out_time'):
                attendance_date = vals.get('attendance_date')
                in_time_updation = vals.get('in_time')
                out_time_updation = vals.get('out_time')
                diff_out_time_replace = None
                diff_in_time_replace = None
                if ':' not in in_time_updation:
                    raise ValidationError(_('Please Enter proper In Time'))
                if ':' not in out_time_updation:
                    raise ValidationError(_('Please Enter proper Out Time'))
                in_time_split = in_time_updation.split(':')
                out_time_split = out_time_updation.split(':')
                if in_time_split:
                    in_time_hour = in_time_split[0]
                    in_time_minute = in_time_split[1]
                    if int(in_time_hour) > 23 or int(in_time_minute) > 59:
                        raise ValidationError(_('Please Enter proper In Time'))
                if out_time_split:
                    out_time_hour = out_time_split[0]
                    out_time_minute = out_time_split[1]
                    if int(in_time_hour) > 23 or int(in_time_minute) > 59:
                        raise ValidationError(_('Please Enter proper Out Time'))
                if len(in_time_split) != 2:
                    raise ValidationError(_('Please Enter proper In Time'))
                if len(in_time_split) != 2:
                    raise ValidationError(_('Please Enter proper Out Time'))
                shift = self.env['hr.employee.shift.timing'].browse(shift_id)
                shift_in_time = shift.in_time
                shift_out_time = shift.out_time
                shift_out_var = shift.out_time_select
                shift_in_time_split = shift_in_time.replace(':','.')
                shift_out_time_split = shift_out_time.replace(':','.')
                cutoff_in_time = float(shift_in_time_split)+1.00
                cutoff_out_time = float(shift_out_time_split)
                if shift_out_var == 'pm':
                    if cutoff_out_time == 1.0:
                        cutoff_out_time = 13.0
                    elif cutoff_out_time == 2.0:
                        cutoff_out_time = 14.0
                    elif cutoff_out_time == 3.0:
                        cutoff_out_time = 15.0
                    elif cutoff_out_time == 4.0:
                        cutoff_out_time = 16.0
                    elif cutoff_out_time == 5.0:
                        cutoff_out_time = 17.0
                    elif cutoff_out_time == 6.0:
                        cutoff_out_time = 18.0
                    elif cutoff_out_time == 7.0:
                        cutoff_out_time = 19.0
                    elif cutoff_out_time == 8.0:
                        cutoff_out_time = 20.0
                    elif cutoff_out_time == 9.0:
                        cutoff_out_time = 21.0
                    elif cutoff_out_time == 10.0:
                        cutoff_out_time = 22.0
                    elif cutoff_out_time == 11.0:
                        cutoff_out_time = 23.0
                in_time_split = in_time_updation.replace(':','.')
                out_time_split = out_time_updation.replace(':','.')
                in_time_float = float(in_time_split)
                out_time_float = float(out_time_split)
                if in_time_float > cutoff_in_time:
                    diff_in_time = in_time_float - cutoff_in_time
                    diff_in_time_replace = str('%.2f' % diff_in_time).replace('.',':')
                if out_time_float < cutoff_out_time:
                    diff_out_time = cutoff_out_time - out_time_float
                    diff_out_time_val = str(diff_out_time).split('.')
                    diff_out_time_val_one = diff_out_time_val[1]
                    if int(diff_out_time_val_one) > 60:
                        diff_out_time = diff_out_time - 0.40
                    diff_out_time_replace = str('%.2f' % diff_out_time).replace('.',':')
                in_time = in_time_updation
                out_time = out_time_updation

                check_in = str(attendance_date)+' '+str(in_time)
                check_out = str(attendance_date)+' '+str(out_time)
                check_in_time = datetime.strptime(str(check_in), "%Y-%m-%d %H:%M") - timedelta(hours=5)
                check_out_time = datetime.strptime(str(check_out), "%Y-%m-%d %H:%M")- timedelta(hours=5)
                check_in_min = check_in_time - timedelta(minutes=30)
                check_out_min = check_out_time - timedelta(minutes=30)
                tdiff =  check_out_time - check_in_time
                tdiff_string = str(tdiff)
                tdiff_split = tdiff_string.split(':')
                tdiff_split_val = tdiff_split[0]+'.'+tdiff_split[1]
                if ',' in tdiff_split_val:
                    tdiff_split_comma = tdiff_split_val.split(',')
                    tdiff_split_comma_val = tdiff_split_comma[1]
                    tdiff_split_val = tdiff_split_comma_val
                worked_hours = float(tdiff_split_val)
                day = check_in_time.strftime('%A')
                holiday_master = self.env['holiday.master'].search([('holiday_date','=',attendance_date)])
                if holiday_master:
                    site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s' % holiday_master.id)
                    result = self.env.cr.fetchall()
                    if result:
                        for site in result:
                            if site[0] == site_master_id:                            
                                employee_status = 'PH'
                            else:
                                if day in ('Saturday','Sunday'):
                                    if worked_hours >=3.5:
                                        employee_status = 'P'
                                        diff_out_time_replace=None
                                        diff_in_time_replace =None
                                    if worked_hours < 3.5:
                                        employee_status = 'AB'
                                        diff_out_time_replace=None
                                        diff_in_time_replace =None
                                elif day not in ('Saturday','Sunday'):
                                    if worked_hours > 6.5:
                                        employee_status = 'P'
                                    elif worked_hours >=4.5 and worked_hours <= 6.5:
                                        employee_status = 'half_day_p_ab'
                                    else:
                                        employee_status = 'AB'
                                        diff_out_time_replace=None
                                        diff_in_time_replace =None
                    else:
                        if day in ('Saturday','Sunday'):
                            if worked_hours >=3.5:
                                employee_status = 'P'
                                diff_out_time_replace=None
                                diff_in_time_replace =None
                            if worked_hours < 3.5:
                                employee_status = 'AB'
                                diff_out_time_replace=None
                                diff_in_time_replace =None
                        elif day not in ('Saturday','Sunday'):
                            if worked_hours > 6.5:
                                employee_status = 'P'
                            elif worked_hours >=4.5 and worked_hours <= 6.5:
                                employee_status = 'half_day_p_ab'
                            else:
                                employee_status = 'AB'
                                diff_out_time_replace=None
                                diff_in_time_replace =None
                else:
                    if day in ('Saturday','Sunday'):
                        if worked_hours >=3.5:
                            employee_status = 'P'
                            diff_out_time_replace=None
                            diff_in_time_replace =None
                        if worked_hours < 3.5:
                            employee_status = 'AB'
                            diff_out_time_replace=None
                            diff_in_time_replace =None
                    elif day not in ('Saturday','Sunday'):
                        if worked_hours > 6.5:
                            employee_status = 'P'
                        elif worked_hours >=4.5 and worked_hours <= 6.5:
                            employee_status = 'half_day_p_ab'
                        else:
                            employee_status = 'AB'
                            diff_out_time_replace=None
                            diff_in_time_replace =None
                if vals.get('employee_status') and vals.get('employee_status') == 'WO':
                    employee_status = 'WO'
                vals['worked_hours'] = worked_hours
                vals['employee_status'] = employee_status
                vals['early_leaving'] = diff_out_time_replace
                vals['late_coming'] = diff_in_time_replace
        vals['created'] = True
        attendance = super(HrAttendance, self).create(vals)
        self.env.cr.execute("update hr_attendance set worked_hours=%s where id=%s" %(str(worked_hours),str(attendance.id)))
        return attendance

    @api.multi
    def write(self, vals):
        res = super(HrAttendance, self).write(vals)
        in_time_updation = 0.0
        out_time_updation = False
        diff_out_time_replace = None
        diff_in_time_replace = None
        site_master_id = self.site_master_id.id if self.site_master_id else self.employee_id.site_master_id.id
        shift_id = self.shift.id if self.shift else self.employee_id.shift_id.id
        shift = self.shift if self.shift else self.employee_id.shift_id
        if 'in_time_updation' in vals:
            in_time_updation = vals.get('in_time_updation')
            if ':' not in in_time_updation:
                raise ValidationError(_('Please Enter proper In Time'))
            in_time_split = in_time_updation.split(':')
            if in_time_split:
                in_time_hour = in_time_split[0]
                in_time_minute = in_time_split[1]
                if int(in_time_hour) > 23 or int(in_time_minute) > 59:
                    raise ValidationError(_('Please Enter proper In Time'))
            if len(in_time_split) != 2:
                raise ValidationError(_('Please Enter proper In Time'))
            main_id =self.id
            self.state = 'approval'

        if 'out_time_updation' in vals:
            out_time_updation = vals.get('out_time_updation')
            if ':' not in out_time_updation:
                raise ValidationError(_('Please Enter proper Out Time'))
            out_time_split = out_time_updation.split(':')
            if out_time_split:
                out_time_hour = out_time_split[0]
                out_time_minute = out_time_split[1]
                if int(out_time_hour) > 23 or int(out_time_minute) > 59:
                    raise ValidationError(_('Please Enter proper Out Time'))
            if len(out_time_split) != 2:
                raise ValidationError(_('Please Enter proper Out Time'))
            main_id =self.id
            self.state = 'approval'

        if 'in_time' in vals or 'out_time' in vals:
            attendance_date = self.attendance_date
            in_time_updation = vals.get('in_time')
            out_time_updation = vals.get('out_time')
            if not in_time_updation:
                in_time_updation = self.in_time
            if not out_time_updation:
                out_time_updation = self.out_time
            if ':' not in in_time_updation:
                raise ValidationError(_('Please Enter proper In Time'))
            if ':' not in out_time_updation:
                raise ValidationError(_('Please Enter proper Out Time'))
            in_time_split = in_time_updation.split(':')
            out_time_split = out_time_updation.split(':')
            if in_time_split:
                in_time_hour = in_time_split[0]
                in_time_minute = in_time_split[1]
                if int(in_time_hour) > 23 or int(in_time_minute) > 59:
                    raise ValidationError(_('Please Enter proper In Time'))
            if out_time_split:
                out_time_hour = out_time_split[0]
                out_time_minute = out_time_split[1]
                if int(in_time_hour) > 23 or int(in_time_minute) > 59:
                    raise ValidationError(_('Please Enter proper Out Time'))
            if len(in_time_split) != 2:
                raise ValidationError(_('Please Enter proper In Time'))
            if len(in_time_split) != 2:
                raise ValidationError(_('Please Enter proper Out Time'))

            shift_in_time = shift.in_time
            shift_out_time = shift.out_time
            shift_out_var = shift.out_time_select
            shift_in_time_split = shift_in_time.replace(':','.')
            shift_out_time_split = shift_out_time.replace(':','.')
            cutoff_in_time = float(shift_in_time_split)+1.00
            cutoff_out_time = float(shift_out_time_split)
            if shift_out_var == 'pm':
                if cutoff_out_time == 1.0:
                    cutoff_out_time = 13.0
                elif cutoff_out_time == 2.0:
                    cutoff_out_time = 14.0
                elif cutoff_out_time == 3.0:
                    cutoff_out_time = 15.0
                elif cutoff_out_time == 4.0:
                    cutoff_out_time = 16.0
                elif cutoff_out_time == 5.0:
                    cutoff_out_time = 17.0
                elif cutoff_out_time == 6.0:
                    cutoff_out_time = 18.0
                elif cutoff_out_time == 7.0:
                    cutoff_out_time = 19.0
                elif cutoff_out_time == 8.0:
                    cutoff_out_time = 20.0
                elif cutoff_out_time == 9.0:
                    cutoff_out_time = 21.0
                elif cutoff_out_time == 10.0:
                    cutoff_out_time = 22.0
                elif cutoff_out_time == 11.0:
                    cutoff_out_time = 23.0
            in_time_split = in_time_updation.replace(':','.')
            out_time_split = out_time_updation.replace(':','.')
            in_time_float = float(in_time_split)
            out_time_float = float(out_time_split)
            if in_time_float > cutoff_in_time:
                diff_in_time = in_time_float - cutoff_in_time
                diff_in_time_replace = str('%.2f' % diff_in_time).replace('.',':')
            if out_time_float < cutoff_out_time:
                diff_out_time = cutoff_out_time - out_time_float
                diff_out_time_val = str(diff_out_time).split('.')
                diff_out_time_val_one = diff_out_time_val[1]
                if int(diff_out_time_val_one) > 60:
                    diff_out_time = diff_out_time - 0.40
                diff_out_time_replace = str('%.2f' % diff_out_time).replace('.',':')
            in_time = in_time_updation
            out_time = out_time_updation
            check_in = str(attendance_date)+' '+str(in_time)
            check_out = str(attendance_date)+' '+str(out_time)
            check_in_time = datetime.strptime(str(check_in), "%Y-%m-%d %H:%M") - timedelta(hours=5)
            check_out_time = datetime.strptime(str(check_out), "%Y-%m-%d %H:%M")- timedelta(hours=5)
            check_in_min = check_in_time - timedelta(minutes=30)
            check_out_min = check_out_time - timedelta(minutes=30)
            tdiff =  check_out_time - check_in_time
            tdiff_string = str(tdiff)
            tdiff_split = tdiff_string.split(':')
            tdiff_split_val = tdiff_split[0]+'.'+tdiff_split[1]
            if ',' in tdiff_split_val:
                tdiff_split_comma = tdiff_split_val.split(',')
                tdiff_split_comma_val = tdiff_split_comma[1]
                tdiff_split_val = tdiff_split_comma_val
            worked_hours = float(tdiff_split_val)           
            day = check_in_time.strftime('%A')
            holiday_master = self.env['holiday.master'].search([('holiday_date','=',attendance_date)])
            #--------------------------------------------------------------------------------------------------------
            if holiday_master:
                site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s' % holiday_master.id)
                result = self.env.cr.fetchall()
                print (result,'ppppppp')
                if result:
                    for site in result:
                        print (site,'siteeee')
                        if site[0] == site_master_id:                            
                            employee_status = 'PH'
                        else:
                            if day in ('Saturday','Sunday'):
                                if worked_hours >=3.5:
                                    employee_status = 'P'
                                    diff_out_time_replace=None
                                    diff_in_time_replace =None
                                if worked_hours < 3.5:
                                    employee_status = 'AB'
                                    diff_out_time_replace=None
                                    diff_in_time_replace =None
                            elif day not in ('Saturday','Sunday'):
                                if worked_hours > 6.5:
                                    employee_status = 'P'
                                elif worked_hours >=4.3 and worked_hours <= 6.3:
                                    employee_status = 'half_day_p_ab'
                                else:
                                    employee_status = 'AB'
                                    diff_out_time_replace=None
                                    diff_in_time_replace =None
                else:
                    if day in ('Saturday','Sunday'):
                        if worked_hours >=3.5:
                            employee_status = 'P'
                            diff_out_time_replace=None
                            diff_in_time_replace =None
                        if worked_hours < 3.5:
                            employee_status = 'AB'
                            diff_out_time_replace=None
                            diff_in_time_replace =None
                    elif day not in ('Saturday','Sunday'):
                        if worked_hours > 6.5:
                            employee_status = 'P'
                        elif worked_hours >=4.5 and worked_hours <= 6.5:
                            employee_status = 'half_day_p_ab'
                        else:
                            employee_status = 'AB'
                            diff_out_time_replace=None
                            diff_in_time_replace =None
            else:
                if day in ('Saturday','Sunday'):
                    if worked_hours >=3.3:
                        employee_status = 'P'
                        diff_out_time_replace=None
                        diff_in_time_replace =None
                    if worked_hours < 3.3:
                        employee_status = 'AB'
                        diff_out_time_replace=None
                        diff_in_time_replace =None
                elif day not in ('Saturday','Sunday'):
                    if worked_hours > 6.3:
                        employee_status = 'P'
                    elif worked_hours >=4.3 and worked_hours <= 6.3:
                        employee_status = 'half_day_p_ab'
                    else:
                        employee_status = 'AB'
                        diff_out_time_replace=None
                        diff_in_time_replace =None
            print("worked_hours in write",worked_hours)
            self.worked_hours = worked_hours
            self.employee_status = employee_status
            self.approve_check = True
            self.early_leaving = diff_out_time_replace
            self.late_coming = diff_in_time_replace
            # self.in_time_updation = self.in_time_updation
            # self.out_time_updation = self.out_time_updation
            main_id =self.id
            # self.state = 'approval'
            # template_id = self.env.ref('orient_hr_attendance_import.email_template_employeeattendance_approval', False)
            # self.env['mail.template'].browse(template_id.id).send_mail(self.id, force_send=True)
        return res

    @api.multi
    def update_time(self):
        todays_date = datetime.now().date()
        print (self.attendance_date,todays_date,'date')
        if str(self.attendance_date) > str(todays_date):
            raise ValidationError(_('You cannot update the time for Future Date!!'))
        if self.attendance_date >= '2019-06-01' and self.attendance_date <= '2019-06-30':
            raise ValidationError(_('Attendance Update is freezed. Kindly contact Administrator!!'))
        view_id = self.env.ref('orient_hr_attendance_import.hr_attendance_wizard_view_form').id
        return {
            'type': 'ir.actions.act_window',
            'name': _('Update Time'),
            'view_mode': 'form',
            'res_model': 'hr.attendance',
            'target': 'new',
            'res_id':self.id,
            'views': [[view_id, 'form']],
            'context':{}
        }

    @api.multi
    def update_time_admin(self):
        view_id = self.env.ref('orient_hr_attendance_import.hr_attendance_admin_wizard_view_form').id
        return {
            'type': 'ir.actions.act_window',
            'name': _('Update Time'),
            'view_mode': 'form',
            'res_model': 'hr.attendance',
            'target': 'new',
            'res_id':self.id,
            'views': [[view_id, 'form']],
            'context':{}
        }

    @api.multi
    def reset_state(self):
        self.write({'state':'approval'})

    @api.multi
    def approve_time(self):
        diff_in_time_replace = None
        diff_out_time_replace = None
        in_time_updation = 0.0
        out_time_updation = 0.0
        for rec in self:
            attendance_date = rec.attendance_date
            if self.in_time_updation:
                in_time_updation = self.in_time_updation
                if not self.out_time_updation:
                    raise ValidationError(_("Out time is not filled by Employee '%s'. Kindly ask Employee to update it and then proceed!\nIf you still want to proceed kindly deselect that record!")%(self.employee_id.name))
            if self.out_time_updation:
                out_time_updation = self.out_time_updation
                if not self.in_time_updation:
                    raise ValidationError(_("In time is not filled by Employee '%s'. Kindly ask Employee to update it and then proceed!\nIf you still want to proceed kindly deselect that record!")%(self.employee_id.name))
            in_time_split = 0.00
            out_time_split = 0.00
            in_time_split = in_time_updation.replace(':','.')
            out_time_split = out_time_updation.replace(':','.')
            shift_id = rec.shift.id
            shift = rec.shift
            site_master_id = rec.site_master_id.id
            if not shift_id:
                shift_id = rec.employee_id.shift_id.id
                shift = rec.employee_id.shift
                if not shift_id:
                    raise ValidationError(_('No shift is assigned to this user. Please ask the administrator to update it and then proceed!'))
            if not site_master_id:
                site_master_id = rec.employee_id.site_master_id.id
                if not site_master_id:
                    raise ValidationError(_("No site is assigned to employee '%s' in the attendance records!")%(self.employee_id.name))
            shift_in_time = shift.in_time
            shift_out_time = shift.out_time
            shift_out_var = shift.out_time_select
            shift_in_time_split = shift_in_time.replace(':','.')
            shift_out_time_split = shift_out_time.replace(':','.')
            cutoff_in_time = float(shift_in_time_split)+1.00
            cutoff_out_time = float(shift_out_time_split)
            if shift_out_var == 'pm':
                if cutoff_out_time == 1.0:
                    cutoff_out_time = 13.0
                elif cutoff_out_time == 2.0:
                    cutoff_out_time = 14.0
                elif cutoff_out_time == 3.0:
                    cutoff_out_time = 15.0
                elif cutoff_out_time == 4.0:
                    cutoff_out_time = 16.0
                elif cutoff_out_time == 5.0:
                    cutoff_out_time = 17.0
                elif cutoff_out_time == 6.0:
                    cutoff_out_time = 18.0
                elif cutoff_out_time == 7.0:
                    cutoff_out_time = 19.0
                elif cutoff_out_time == 8.0:
                    cutoff_out_time = 20.0
                elif cutoff_out_time == 9.0:
                    cutoff_out_time = 21.0
                elif cutoff_out_time == 10.0:
                    cutoff_out_time = 22.0
                elif cutoff_out_time == 11.0:
                    cutoff_out_time = 23.0
            in_time_float= 0.0
            out_time_float = 0.0
            if in_time_split:
                in_time_float = float(in_time_split)
            if out_time_split:
                out_time_float = float(out_time_split)
            if in_time_float > cutoff_in_time:
                diff_in_time = in_time_float - cutoff_in_time
                diff_in_time_replace = str('%.2f' % diff_in_time).replace('.',':')
            if out_time_float < cutoff_out_time:
                diff_out_time = cutoff_out_time - out_time_float
                diff_out_time_val = str(diff_out_time).split('.')
                diff_out_time_val_one = diff_out_time_val[1]
                if int(diff_out_time_val_one) > 60:
                    diff_out_time = diff_out_time - 0.40
                diff_out_time_replace = str('%.2f' % diff_out_time).replace('.',':')
            in_time = in_time_updation
            out_time = out_time_updation
            check_in = str(attendance_date)+' '+str(in_time)
            check_out = str(attendance_date)+' '+str(out_time)
            check_in_time = datetime.strptime(str(check_in), "%Y-%m-%d %H:%M") - timedelta(hours=5)
            check_out_time = datetime.strptime(str(check_out), "%Y-%m-%d %H:%M")- timedelta(hours=5)
            check_in_min = check_in_time - timedelta(minutes=30)
            check_out_min = check_out_time - timedelta(minutes=30)
            tdiff =  check_out_time - check_in_time
            tdiff_string = str(tdiff)
            tdiff_split = tdiff_string.split(':')
            tdiff_split_val = tdiff_split[0]+'.'+tdiff_split[1]
            if ',' in tdiff_split_val:
                tdiff_split_comma = tdiff_split_val.split(',')
                tdiff_split_comma_val = tdiff_split_comma[1]
                tdiff_split_val = tdiff_split_comma_val
            worked_hours = float(tdiff_split_val)
            day = check_in_time.strftime('%A')
            holiday_master = self.env['holiday.master'].search([('holiday_date','=',attendance_date)])
            if holiday_master:
                site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s' % holiday_master.id)
                result = self.env.cr.fetchall()
                print (result,'ppppppp')
                if result:
                    for site in result:
                        print (site,'siteeee')
                        if site[0] == site_master_id:                            
                            employee_status = 'PH'
                        else:
                            if day in ('Saturday','Sunday'):
                                if worked_hours >=3.5:
                                    employee_status = 'P'
                                    diff_out_time_replace=None
                                    diff_in_time_replace =None
                                if worked_hours < 3.5:
                                    employee_status = 'AB'
                                    diff_out_time_replace=None
                                    diff_in_time_replace =None
                            elif day not in ('Saturday','Sunday'):
                                if worked_hours > 6.5:
                                    employee_status = 'P'
                                elif worked_hours >=4.5 and worked_hours <= 6.5:
                                    employee_status = 'half_day_p_ab'
                                else:
                                    employee_status = 'AB'
                                    diff_out_time_replace=None
                                    diff_in_time_replace =None
                else:
                    if day in ('Saturday','Sunday'):
                        if worked_hours >=3.5:
                            employee_status = 'P'
                            diff_out_time_replace=None
                            diff_in_time_replace =None
                        if worked_hours < 3.5:
                            employee_status = 'AB'
                            diff_out_time_replace=None
                            diff_in_time_replace =None
                    elif day not in ('Saturday','Sunday'):
                        if worked_hours > 6.5:
                            employee_status = 'P'
                        elif worked_hours >=4.5 and worked_hours <= 6.5:
                            employee_status = 'half_day_p_ab'
                        else:
                            employee_status = 'AB'
                            diff_out_time_replace=None
                            diff_in_time_replace =None
            else:
                if day in ('Saturday','Sunday'):
                    if worked_hours >=3.5:
                        employee_status = 'P'
                        diff_out_time_replace=None
                        diff_in_time_replace =None
                    if worked_hours < 3.5:
                        employee_status = 'AB'
                        diff_out_time_replace=None
                        diff_in_time_replace =None
                elif day not in ('Saturday','Sunday'):
                    if worked_hours > 6.5:
                        employee_status = 'P'
                    elif worked_hours >=4.5 and worked_hours <= 6.5:
                        employee_status = 'half_day_p_ab'
                    else:
                        employee_status = 'AB'
                        diff_out_time_replace=None
                        diff_in_time_replace =None
            update_query = self.env.cr.execute('update hr_attendance set in_time=%s,out_time=%s,worked_hours=%s,early_leaving=%s,late_coming=%s,check_in=%s,check_out=%s,state=%s,employee_status=%s,approve_check=%s where id=%s' ,(in_time_updation,out_time_updation,float(tdiff_split_val),diff_out_time_replace,diff_in_time_replace,check_in_min,check_out_min,'done',employee_status,'t',rec.id))
            self.env.cr.commit()
            template_id = self.env.ref('orient_hr_attendance_import.email_template_employeeattendance_approvalsuccess', False)
            self.env['mail.template'].browse(template_id.id).sudo().send_mail(self.id, force_send=True)

    @api.multi
    def bulk_approve_time(self):
        diff_in_time_replace = None
        diff_out_time_replace = None
        in_time_updation = 0.0
        out_time_updation = 0.0
        for rec in self:
            attendance_date = rec.attendance_date
            if self.in_time_updation:
                in_time_updation = self.in_time_updation
                if not self.out_time_updation:
                    raise ValidationError(_("Out time is not filled by employee '%s'. Kindly ask Employee to update it and then proceed!")%(self.employee_id.name))
            if self.out_time_updation:
                out_time_updation = self.out_time_updation
                if not self.in_time_updation:
                    raise ValidationError(_("In time is not filled by employee '%s'. Kindly ask Employee to update it and then proceed!")%(self.employee_id.name))
            if not self.in_time_updation:
                raise ValidationError(_("In time is not filled by employee '%s'. Kindly ask Employee to update it and then proceed!")%(self.employee_id.name))
            if not self.out_time_updation:
                raise ValidationError(_("Out time is not filled by employee '%s'. Kindly ask Employee to update it and then proceed!")%(self.employee_id.name))
            in_time_split = 0.00
            out_time_split = 0.00
            if self.in_time_updation:
                in_time_split = in_time_updation.replace(':','.')
            if self.out_time_updation:
                out_time_split = out_time_updation.replace(':','.')
            shift_id = rec.shift.id
            shift = rec.shift
            site_master_id = rec.site_master_id.id
            if not shift_id:
                shift_id = rec.employee_id.shift_id.id
                shift = rec.employee_id.shift_id
                if not shift_id:
                    raise ValidationError(_("No shift is assigned to employee '%s'. Please ask the administrator to update it and then proceed!")%(self.employee_id.name))
            if not site_master_id:
                site_master_id = rec.employee_id.site_master_id.id
                if not site_master_id:
                    raise ValidationError(_("No site is assigned to employee '%s' in the attendance records!")%(self.employee_id.name))
            shift_in_time = shift.in_time
            shift_out_time = shift.out_time
            shift_out_var = shift.out_time_select
            shift_in_time_split = shift_in_time.replace(':','.')
            shift_out_time_split = shift_out_time.replace(':','.')
            cutoff_in_time = float(shift_in_time_split)+1.00
            cutoff_out_time = float(shift_out_time_split)
            if shift_out_var == 'pm':
                if cutoff_out_time == 1.0:
                    cutoff_out_time = 13.0
                elif cutoff_out_time == 2.0:
                    cutoff_out_time = 14.0
                elif cutoff_out_time == 3.0:
                    cutoff_out_time = 15.0
                elif cutoff_out_time == 4.0:
                    cutoff_out_time = 16.0
                elif cutoff_out_time == 5.0:
                    cutoff_out_time = 17.0
                elif cutoff_out_time == 6.0:
                    cutoff_out_time = 18.0
                elif cutoff_out_time == 7.0:
                    cutoff_out_time = 19.0
                elif cutoff_out_time == 8.0:
                    cutoff_out_time = 20.0
                elif cutoff_out_time == 9.0:
                    cutoff_out_time = 21.0
                elif cutoff_out_time == 10.0:
                    cutoff_out_time = 22.0
                elif cutoff_out_time == 11.0:
                    cutoff_out_time = 23.0
            in_time_float= 0.0
            out_time_float = 0.0
            if in_time_split:
                in_time_float = float(in_time_split)
            if out_time_split:
                out_time_float = float(out_time_split)
            if in_time_float > cutoff_in_time:
                diff_in_time = in_time_float - cutoff_in_time
                diff_in_time_replace = str('%.2f' % diff_in_time).replace('.',':')
            if out_time_float < cutoff_out_time:
                diff_out_time = cutoff_out_time - out_time_float
                diff_out_time_val = str(diff_out_time).split('.')
                diff_out_time_val_one = diff_out_time_val[1]
                if int(diff_out_time_val_one) > 60:
                    diff_out_time = diff_out_time - 0.40
                diff_out_time_replace = str('%.2f' % diff_out_time).replace('.',':')
            in_time = in_time_updation
            out_time = out_time_updation
            check_in = str(attendance_date)+' '+str(in_time)
            check_out = str(attendance_date)+' '+str(out_time)
            check_in_time = datetime.strptime(str(check_in), "%Y-%m-%d %H:%M") - timedelta(hours=5)
            check_out_time = datetime.strptime(str(check_out), "%Y-%m-%d %H:%M")- timedelta(hours=5)
            check_in_min = check_in_time - timedelta(minutes=30)
            check_out_min = check_out_time - timedelta(minutes=30)
            tdiff =  check_out_time - check_in_time
            tdiff_string = str(tdiff)
            tdiff_split = tdiff_string.split(':')
            tdiff_split_val = tdiff_split[0]+'.'+tdiff_split[1]
            if ',' in tdiff_split_val:
                tdiff_split_comma = tdiff_split_val.split(',')
                tdiff_split_comma_val = tdiff_split_comma[1]
                tdiff_split_val = tdiff_split_comma_val
            worked_hours = float(tdiff_split_val)
            day = check_in_time.strftime('%A')
            holiday_master = self.env['holiday.master'].search([('holiday_date','=',attendance_date)])
            if holiday_master:
                site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s' % holiday_master.id)
                result = self.env.cr.fetchall()
                print (result,'ppppppp')
                if result:
                    for site in result:
                        print (site,'siteeee')
                        if site[0] == site_master_id:                            
                            employee_status = 'PH'
                        else:
                            if day in ('Saturday','Sunday'):
                                if worked_hours >=3.5:
                                    employee_status = 'P'
                                    diff_out_time_replace=None
                                    diff_in_time_replace =None
                                if worked_hours < 3.5:
                                    employee_status = 'AB'
                                    diff_out_time_replace=None
                                    diff_in_time_replace =None
                            elif day not in ('Saturday','Sunday'):
                                if worked_hours > 6.5:
                                    employee_status = 'P'
                                elif worked_hours >=4.5 and worked_hours <= 6.5:
                                    employee_status = 'half_day_p_ab'
                                else:
                                    employee_status = 'AB'
                                    diff_out_time_replace=None
                                    diff_in_time_replace =None
                else:
                    if day in ('Saturday','Sunday'):
                        if worked_hours >=3.5:
                            employee_status = 'P'
                            diff_out_time_replace=None
                            diff_in_time_replace =None
                        if worked_hours < 3.5:
                            employee_status = 'AB'
                            diff_out_time_replace=None
                            diff_in_time_replace =None
                    elif day not in ('Saturday','Sunday'):
                        if worked_hours > 6.5:
                            employee_status = 'P'
                        elif worked_hours >=4.5 and worked_hours <= 6.5:
                            employee_status = 'half_day_p_ab'
                        else:
                            employee_status = 'AB'
                            diff_out_time_replace=None
                            diff_in_time_replace =None
            else:
                if day in ('Saturday','Sunday'):
                    if worked_hours >=3.5:
                        employee_status = 'P'
                        diff_out_time_replace=None
                        diff_in_time_replace =None
                    if worked_hours < 3.5:
                        employee_status = 'AB'
                        diff_out_time_replace=None
                        diff_in_time_replace =None
                elif day not in ('Saturday','Sunday'):
                    if worked_hours > 6.5:
                        employee_status = 'P'
                    elif worked_hours >=4.5 and worked_hours <= 6.5:
                        employee_status = 'half_day_p_ab'
                    else:
                        employee_status = 'AB'
                        diff_out_time_replace=None
                        diff_in_time_replace =None
            update_query = self.env.cr.execute('update hr_attendance set in_time=%s,out_time=%s,worked_hours=%s,early_leaving=%s,late_coming=%s,check_in=%s,check_out=%s,state=%s,employee_status=%s,approve_check=%s where id=%s' ,(in_time_updation,out_time_updation,float(tdiff_split_val),diff_out_time_replace,diff_in_time_replace,check_in_min,check_out_min,'done',employee_status,'t',rec.id))
            self.env.cr.commit()

    @api.multi
    def reject_time(self):
        for rec in self:
            update_query = self.env.cr.execute('update hr_attendance set state=%s,reject_check=%s,approved_rejected_date=%s where id=%s' ,('rejected','t',datetime.now().date(),rec.id))
            # update_query = self.env.cr.execute("update hr_attendance set reject_check=%s, state=%s where id=%s" %(str(True),str(state),str(rec.id)))
            self.env.cr.commit()
            template_id = self.env.ref('orient_hr_attendance_import.email_template_employeeattendance_reject', False)
            self.env['mail.template'].browse(template_id.id).sudo().send_mail(self.id, force_send=True)


    @api.multi
    def cron_check_absent(self):
        todays_date =datetime.now().date()
        search_employee = self.env['hr.employee'].search([('active','=',True)])
        for recs in search_employee:
            search_attendance = self.search([('employee_id','=',recs.id),('attendance_date','=',todays_date)],limit=1)
            shift=''
            if search_attendance:
                shift = search_attendance.shift.name
            else:
                hr_employee_shift = self.env['hr.employee'].search([('emp_code','=',employee_code)])
                shift = hr_employee_shift.shift_id.name
            if search_attendance:
                for rec in search_attendance:
                    if shift=='WO':
                        rec.write({'employee_status':'WO'})
                    if rec.employee_status==' ' and rec.in_time==False and rec.out_time==False and shift!='WO':
                        rec.write({'employee_status':'AB'})
                    if rec.employee_status==False and rec.in_time==False and rec.out_time==False and shift!='WO':
                        rec.write({'employee_status':'AB'})
        return True


    @api.multi
    def cron_import_data_absent(self):
        todays_date =datetime.now().date()
        month = datetime.today().month
        if month == 1:
               current_month = 'jan'
        if month == 2:
               current_month = 'feb'
        if month == 3:
               current_month = 'march'
        if month == 4:
               current_month = 'april'
        if month == 5:
               current_month = 'may'
        if month == 6:
               current_month = 'june'
        if month == 7:
               current_month = 'july'
        if month == 8:
               current_month = 'aug'
        if month == 9:
               current_month = 'sept'
        if month == 10:
               current_month = 'oct'
        if month == 11:
               current_month = 'nov'
        if month == 12:
               current_month = 'dec'
        financial_year_id = False
        year = datetime.today().year
        year_master_ids = self.env['year.master'].search([('name','ilike',year)])
        for each_year_master_id in year_master_ids:
           if each_year_master_id.start_date:
               start_date_year = datetime.strptime(each_year_master_id.start_date,'%Y-%m-%d').year
               if start_date_year == year:
                   financial_year_id = each_year_master_id.id
        CO = self.env['hr.holidays.status'].search([('code','=','CO')])
        compoff_id = CO.id
        search_employee = self.env['hr.employee'].search([('active','=',True)])
        for search_employee_id in search_employee:
            emp_code = search_employee_id.emp_code
            department_id = search_employee_id.department_id.id
            parent_id = search_employee_id.parent_id.id
            if not parent_id:
                parent_id = None
            if not department_id:
                department_id=None
            employee_id = search_employee_id.id
            shift_application_line = self.env['shift.application.line'].search([('employee_code','=',emp_code),('date','=',todays_date)])
            if shift_application_line:
                shift = shift_application_line.shift.name
                shift_id = shift_application_line.shift.id
            else:
                hr_employee_shift = self.env['hr.employee'].search([('emp_code','=',emp_code)])
                shift = hr_employee_shift.shift_id.name
                shift_id = hr_employee_shift.shift_id.id
            if not shift_id:
                shift_id=None
            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',todays_date),('employee_code','=',emp_code)])
            print(search_attendance,emp_code,'---------------------')
            if not search_attendance:
                que = self.env.cr.execute('insert into hr_attendance(shift,employee_id,check_in,check_out,attendance_date,employee_code,department_id_val,employee_status,state) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)',(shift_id,employee_id,todays_date,todays_date,todays_date,emp_code,department_id,'AB','draft'))
                self.env.cr.commit()

            # comp off logic based on worked hours during public holidays or extra worked hours
            if search_attendance:
                worked_hours = float(search_attendance.worked_hours)
                employee_status = search_attendance.employee_status
                if employee_status in ('WO','PH') and worked_hours >=6:
                    total_days =1.0
                    string = self.env.cr.execute('insert into hr_holidays(name,code,holiday_type,employee_id,holiday_status_id,manager_id,total_days,balanced_days,department_id,type,state,approved_by,current_month,financial_year_id,comp_off_date,allocated) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',('Leave Allocation','CO','employee',employee_id,compoff_id,parent_id,total_days,total_days,department_id,'add','allocated',1,current_month,financial_year_id,todays_date,True))
                    self.env.cr.commit()
                elif worked_hours >= 15:
                    total_days =1.0
                    string = self.env.cr.execute('insert into hr_holidays(name,code,holiday_type,employee_id,holiday_status_id,manager_id,total_days,balanced_days,department_id,type,state,approved_by,current_month,financial_year_id,comp_off_date,allocated) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',('Leave Allocation','CO','employee',employee_id,compoff_id,parent_id,total_days,total_days,department_id,'add','allocated',1,current_month,financial_year_id,todays_date,True))
                    self.env.cr.commit()

    @api.multi
    def cron_yearly_scheduler(self):

        start_date = datetime.now().date().replace(month=1, day=1)    
        end_date = datetime.now().date().replace(month=12, day=31)
        # print(start_date,end_date,'--------')

        delta1 = end_date - start_date
        # print(delta1,'delta1')

        emp_recs = self.env['hr.employee'].search([('active','=',True)])
        # emp_recs = self.env['hr.employee'].search([('id','in',(18643,16617))])
        # emp_recs = self.env['hr.employee'].search([('id','=',16617)])
        # print(emp_recs,'emp_recs')

        for search_employee_id in emp_recs:
            emp_code = search_employee_id.emp_code
            department_id = search_employee_id.department_id.id
            parent_id = search_employee_id.parent_id.id
            if not parent_id:
                parent_id = None
            if not department_id:
                department_id=None
            employee_id = search_employee_id.id
            # shift_application_line = self.env['shift.application.line'].search([('employee_code','=',emp_code),('date','=',todays_date)])
            # if shift_application_line:
            #     shift = shift_application_line.shift.name
            #     shift_id = shift_application_line.shift.id
            # else:
            #     hr_employee_shift = self.env['hr.employee'].search([('emp_code','=',emp_code)])
            shift = search_employee_id.shift_id.name if search_employee_id.shift_id.name else ''
            shift_id = search_employee_id.shift_id.id if search_employee_id.shift_id.id else None
            # if not shift_id:
            #     shift_id=None
            site_master_id = search_employee_id.site_master_id.id
            if not site_master_id:
                site_master_id = None
            # print(site_master_id,'site_master_id')
            for i in range(delta1.days + 1):
                # print(starting_day_of_current_year + timedelta(i),'-----')
                print("*******************************************************************")
                dates = start_date + timedelta(i)
                day_name = calendar.day_name[dates.weekday()]
                # print(day_name,'day_name')

                if day_name == 'Sunday':
                    weekend = True
                else:
                    weekend = False

                print(dates,search_employee_id,'dates  ===============')

                holiday_rec = self.env['holiday.master'].search([('holiday_date','=',dates)])
                if holiday_rec and not weekend:
                    # print(holiday_rec)
                    print("holiday_rec and not weekend")
                    site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s' % holiday_rec.id)
                    result = self.env.cr.fetchall()
                    # print(result,'result')
                    if result:
                        for site in result:
                            print(site,site_master_id)
                            if site[0] == site_master_id:
                                employee_status = 'PH'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',dates),('employee_code','=',emp_code)])
                                if search_attendance:
                                    if not search_attendance.employee_status in ('PL','SL/CL','PA','MA','ML'):
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_code=%s', (employee_status,dates,emp_code))
                                        self.env.cr.commit()
                                else:
                                    que = self.env.cr.execute('insert into hr_attendance(shift,employee_id,check_in,check_out,attendance_date,employee_code,department_id_val,site_master_id,employee_status,state) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(shift_id,employee_id,dates,dates,dates,emp_code,department_id,site_master_id,employee_status,'draft'))
                                    self.env.cr.commit()
                            else:
                                employee_status = ' '
                                print("else of holiday")
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',dates),('employee_code','=',emp_code)])
                                if search_attendance:  
                                    if not search_attendance.employee_status in ('PL','SL/CL','PA','MA','ML'):
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_code=%s', (employee_status,dates,emp_code))
                                        self.env.cr.commit()
                                else:
                                    que = self.env.cr.execute('insert into hr_attendance(shift,employee_id,check_in,check_out,attendance_date,employee_code,department_id_val,site_master_id,employee_status,state) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(shift_id,employee_id,dates,dates,dates,emp_code,department_id,site_master_id,employee_status,'draft'))
                                    self.env.cr.commit()

                elif weekend and holiday_rec:
                    print("weekend and holiday_rec")

                    site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s' % holiday_rec.id)
                    result = self.env.cr.fetchall()

                    if result:
                        for site in result:
                            print(site,site_master_id)
                            if site[0] == site_master_id:
                                employee_status = 'PH+WO'

                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',dates),('employee_code','=',emp_code)])
                                if search_attendance:
                                    if not search_attendance.employee_status in ('PL','SL/CL','PA','MA','ML'):
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_code=%s', (employee_status,dates,emp_code))
                                        self.env.cr.commit()
                                else:
                                    que = self.env.cr.execute('insert into hr_attendance(shift,employee_id,check_in,check_out,attendance_date,employee_code,department_id_val,site_master_id,employee_status,state) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(shift_id,employee_id,dates,dates,dates,emp_code,department_id,site_master_id,employee_status,'draft'))
                                    self.env.cr.commit()
                            else:
                                employee_status = 'WO'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',dates),('employee_code','=',emp_code)])
                                if search_attendance:  
                                    if not search_attendance.employee_status in ('PL','SL/CL','PA','MA','ML'):
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_code=%s', (employee_status,dates,emp_code))
                                        self.env.cr.commit()
                                else:
                                    que = self.env.cr.execute('insert into hr_attendance(shift,employee_id,check_in,check_out,attendance_date,employee_code,department_id_val,site_master_id,employee_status,state) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(shift_id,employee_id,dates,dates,dates,emp_code,department_id,site_master_id,employee_status,'draft'))
                                    self.env.cr.commit()                     

                elif weekend and not holiday_rec:
                    employee_status = 'WO'
                    que = self.env.cr.execute('insert into hr_attendance(shift,employee_id,check_in,check_out,attendance_date,employee_code,department_id_val,site_master_id,employee_status,state) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(shift_id,employee_id,dates,dates,dates,emp_code,department_id,site_master_id,employee_status,'draft'))
                    self.env.cr.commit() 

                elif not weekend and not holiday_rec:
                    employee_status = ' '
                    search_attendance = self.env['hr.attendance'].search([('attendance_date','=',dates),('employee_code','=',emp_code)])
                    if search_attendance:
                        if not search_attendance.employee_status in ('PL','SL/CL','PA','MA','ML'):
                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_code=%s', (employee_status,dates,emp_code))
                            self.env.cr.commit()
                    else:
                        # print("insert record")
                        que = self.env.cr.execute('insert into hr_attendance(shift,employee_id,check_in,check_out,attendance_date,employee_code,department_id_val,site_master_id,employee_status,state) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(shift_id,employee_id,dates,dates,dates,emp_code,department_id,site_master_id,employee_status,'draft'))
                        self.env.cr.commit()
                else:
                    employee_status = ''
                    search_attendance = self.env['hr.attendance'].search([('attendance_date','=',dates),('employee_code','=',emp_code)])
                    if search_attendance:
                        if not search_attendance.employee_status in ('PL','SL/CL','PA','MA','ML'):
                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_code=%s', (employee_status,dates,emp_code))
                            self.env.cr.commit()
                    else:
                        # print("insert record")
                        que = self.env.cr.execute('insert into hr_attendance(shift,employee_id,check_in,check_out,attendance_date,employee_code,department_id_val,site_master_id,employee_status,state) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(shift_id,employee_id,dates,dates,dates,emp_code,department_id,site_master_id,employee_status,'draft'))
                        self.env.cr.commit()


    @api.multi
    def muster_calculation(self):

        print(self.attendance_date,'====')
        month = datetime.strptime(self.attendance_date, "%Y-%m-%d").month
        year = datetime.strptime(self.attendance_date, "%Y-%m-%d").year
        print(month,year)

        last_day = calendar.monthrange(int(year),int(month))[1]

        start_date = str(year) + '-' + str(month) + '-' + '01'
        end_date = str(year) + '-' + str(month) + '-' + str(last_day)
        print(start_date,end_date)

        employee_id = self.employee_id.id

        att_recs = self.env['hr.attendance'].search([('attendance_date','>=',start_date),('attendance_date','<=',end_date),('employee_id','=',employee_id)])
        print(att_recs,'att_recs')

        employee_stat = []

        for each in att_recs:
            employee_status = each.employee_status
            employee_stat.append(employee_status)
        # print(employee_stat,'employee_stat')

        for i in employee_stat:
            if 'PH' in employee_stat:
                employee_stat.count('PH')
                self.ph = float(employee_stat.count('PH'))
            if 'P' in employee_stat:
                employee_stat.count('P')
                self.pr = float(employee_stat.count('P'))
            if 'WO' in employee_stat:
                employee_stat.count('WO')
                self.wo = float(employee_stat.count('WO'))
            if 'AB' in employee_stat:
                employee_stat.count('AB')
                self.ab = float(employee_stat.count('AB'))
            if 'PL' in employee_stat:
                employee_stat.count('PL')
                self.pl = float(employee_stat.count('PL'))
            if 'PA' in employee_stat:
                employee_stat.count('PA')
                self.pa = float(employee_stat.count('PA'))
            if 'SL/CL' in employee_stat:
                employee_stat.count('SL/CL')
                self.sl_cl = float(employee_stat.count('SL/CL'))
            if 'OD' in employee_stat:
                employee_stat.count('OD')
                self.od = float(employee_stat.count('OD'))
            if 'ML' in employee_stat:
                employee_stat.count('ML')
                self.ml = float(employee_stat.count('ML'))
            if 'MA' in employee_stat:
                employee_stat.count('MA')
                self.ma = float(employee_stat.count('MA'))
            if 'LWP' in employee_stat:
                employee_stat.count('LWP')
                self.lwp = float(employee_stat.count('LWP'))
            if 'CO' in employee_stat:
                employee_stat.count('CO')
                self.c_off = float(employee_stat.count('CO'))


            # print(self.ab,'aaaaaaaaaaaabbbbbbbbbbb')
            self.worked_days = self.ph + self.pr + self.wo + self.pa + self.c_off + self.ma + self.ml + self.od + self.sl_cl + self.pl

        return True
    
class HrAttendanceImport(models.Model):
    _name = 'hr.attendance.import'
    _description = "Attendance Import"


    @api.model
    def _file_read(self, full_path, fname, bin_size=False):
        import_config = self.env['import.config'].search([],limit=1)
        source_path = str(import_config.source_path)
        destination_path = str(import_config.destination_path)
        full_path = source_path
        r = ''
        try:
            if bin_size:
                r = human_size(os.path.getsize(full_path))
            else:
                r = base64.b64encode(open(full_path,'rb').read())
        except (IOError, OSError):
            _logger.info("_read_file reading %s", full_path, exc_info=True)
        return r


    @api.depends('datas_fname','db_datas')
    def _compute_datas(self):
        bin_size = self._context.get('bin_size')
        result ={}
        for attach in self:
            if attach.datas_fname:
                result[attach.id]= self._file_read(attach.file_url,attach.datas_fname, bin_size)
            else:
                result[attach.id] = attach.db_datas


    @api.model
    def _file_write(self, value, file_name):
        db_datas = value
        bin_value = base64.b64decode(value)
        fname = file_name
        import_config = self.env['import.config'].search([],limit=1)
        source_path = str(import_config.source_path)
        destination_path = str(import_config.destination_path)
        full_path = source_path+fname
        if not os.path.exists(full_path):
            try:
                with open(full_path, 'wb') as fp:
                    fp.write(bin_value)
                    os.chmod(full_path,0o777)
                    # shutil.chown(full_path, user='odoouser', group='odoouser')
            except IOError:
                _logger.info("_file_write writing %s", full_path, exc_info=True)
        return full_path


    def _inverse_datas(self):
        for attach in self:
            # compute the fields that depend on datas
            file_name = attach.datas_fname
            if not file_name:
                raise ValidationError(_('Kindly select file for import!!'))
            value = attach.datas
            bin_data = base64.b64decode(value) if value else b''
            if file_name.endswith('.csv'):
                fname = self._file_write(value,file_name)
            vals={'file_url':fname}
            # write as superuser, as user probably does not have write access
            super(HrAttendanceImport, attach.sudo()).write(vals)

    file_url = fields.Char('Url', index=True, size=1024)
    datas_fname = fields.Char('File Name')
    datas = fields.Binary(string='File Content', compute='_compute_datas', inverse='_inverse_datas')
    db_datas = fields.Binary('Database Data')
    state = fields.Selection([('draft', 'Draft'),('done', 'Done'),('failed','Failed')], string='Status', default='draft')


    @api.multi
    def import_data(self):
        todays_date = datetime.now()
        append_data=[]
        attendance_date_val =[]
        quikform_boolean = False
        qf_next_date = False
        qf_next_date_24_hr = False
        attendance_in_qf = False
        attendance_out_qf = False
        for rec in self:
            if not rec.datas_fname:
                raise ValidationError(_('Kindly select file for import!!'))
            datas_fname = str(rec.datas_fname)
            import_config = self.env['import.config'].search([],limit=1)
            source_path = str(import_config.source_path)
            destination_path = str(import_config.destination_path)
            failed_path = str(import_config.failed_path)
            file_path = source_path+datas_fname
            with open(file_path, 'r') as f:
                reader = csv.reader(f)
                try:
                    count = 0
                    for row in reader:
                        diff_out_time_replace=None
                        diff_in_time_replace =None
                        append_data_var = row[4]
                        if append_data_var == 'Import Data':
                            variable_diff = 'importing'
                        if append_data_var == 'BiometricDate':
                            variable_diff = 'biometric'
                        if append_data_var == 'QuikFormz Data':
                            variable_diff = 'quikformz'
                            quikform_boolean = True
                        append_data.append(variable_diff)
                        if count != 0:
                            attendance_date = row[0]
                            employee_code = row[1]
                            variable_diff = row[4]
                            if quikform_boolean == True:
                                qf_next_date = False
                                qf_next_date_24_hr = False
                                # print (row[2],row[3])
                                if row[2]:
                                    rows_in = row[2]
                                    in_t = rows_in.split(' ')
                                    # print (in_t,'lllll')
                                    row[2] = in_t[1][0:5]
                                    attendance_in_qf = in_t[0]
                                if row[3]:
                                    rows_out = row[3]
                                    out_t = rows_out.split(' ')
                                    row[3] = out_t[1][0:5]
                                    attendance_out_qf = out_t[0]
                                if str(attendance_in_qf)!=str(attendance_out_qf):
                                    if row[2] > row[3]:
                                        qf_next_date=True
                                    if row[2] <= row[3]:
                                        qf_next_date_24_hr=True
                            attendance_date_split = attendance_date.split('-')
                            attendance_date = attendance_date_split[2]+'-'+attendance_date_split[1]+'-'+attendance_date_split[0]
                            hr_employee_id = self.env['hr.employee'].search([('emp_code','=',employee_code)])
                            employee_id = hr_employee_id.id
                            department_id = hr_employee_id.department_id.id
                            if not department_id:
                                department_id=None
                            site_master_id = hr_employee_id.site_master_id.id
                            if not site_master_id:
                                site_master_id=None
                            fms_ids = []
                            mumbai_id = self.env['site.master'].search([('name','=','Mumbai HO')])
                            pune_id = self.env['site.master'].search([('name','=','PUNE BRANCH')])
                            ahmedabad_id = self.env['site.master'].search([('name','=','Ahmedabad Branch')])
                            bangalore_id = self.env['site.master'].search([('name','=','BANGLORE BRANCH')])
                            chennai_id = self.env['site.master'].search([('name','=','CHENNAI BRANCH')])
                            delhi_id = self.env['site.master'].search([('name','=','Delhi Branch')])
                            kolkata_id = self.env['site.master'].search([('name','=','KOLKATA BRANCH')])
                            hr_id = self.env['site.master'].search([('name','=','Human Resource - Mumbai')])
                            if mumbai_id:
                                fms_ids.append(mumbai_id.id)
                            if pune_id:
                                fms_ids.append(pune_id.id)
                            if ahmedabad_id:
                                fms_ids.append(ahmedabad_id.id)
                            if bangalore_id:
                                fms_ids.append(bangalore_id.id)
                            if chennai_id:
                                fms_ids.append(chennai_id.id)
                            if delhi_id:
                                fms_ids.append(delhi_id.id)
                            if kolkata_id:
                                fms_ids.append(kolkata_id.id)
                            if hr_id:
                                fms_ids.append(hr_id.id)
                            # shift_application_line = self.env['shift.application.line'].search([('employee_code','=',employee_code),('date','=',attendance_date)])
                            shift_attendance_line = self.env['hr.attendance'].search([('employee_code','=',employee_code),('attendance_date','=',attendance_date)])
                            # if shift_application_line:
                            #     shift = shift_application_line.shift.name
                            if shift_attendance_line:
                                shift = shift_attendance_line.shift.name
                            else:
                                hr_employee_shift = self.env['hr.employee'].search([('emp_code','=',employee_code)])
                                shift = hr_employee_shift.shift_id.name
                            if shift:
                                search_att = self.env['hr.attendance'].search([('employee_code','=',employee_code),('attendance_date','=',str(attendance_date))],limit=1)
                                if search_att:
                                    update_in_time = search_att.in_time
                                    update_out_time = search_att.out_time
                                else:
                                    update_in_time = ''
                                    update_out_time = ''
                                if qf_next_date:
                                    update_in_time = row[2]
                                    update_out_time = row[3]
                                shift_search = self.env['hr.employee.shift.timing'].search([('name','=',shift)])
                                shift_browse = self.env['hr.employee.shift.timing'].browse(shift_search.id)
                                shift_id = shift_browse.id
                                shift_in_time = shift_search.in_time
                                shift_out_time = shift_search.out_time
                                shift_out_var = shift_search.out_time_select
                                shift_in_time_split = shift_in_time.replace(':','.')
                                shift_out_time_split = shift_out_time.replace(':','.') 
                                # to keep the same in time as the first insert to get the correct working hours
                                if update_in_time:
                                    #  if a file that has least in time is synced later
                                    if float(update_in_time.replace(':','.')) < float(row[2].replace(':','.')):
                                        in_time_split = update_in_time.replace(':','.')
                                    else:
                                        in_time_split = row[2].replace(':','.')
                                else:
                                    in_time_split = row[2].replace(':','.')
                                # to keep the most out time 
                                if update_out_time:
                                    if float(update_out_time.replace(':','.')) > float(row[3].replace(':','.')):
                                        out_time_split = update_out_time.replace(':','.')
                                    else:
                                        out_time_split = row[3].replace(':','.')
                                else:
                                    out_time_split = row[3].replace(':','.')
                                if shift_in_time_split:
                                    cutoff_in_time = float(shift_in_time_split)+1.00
                                if shift_out_time_split:
                                    cutoff_out_time = float(shift_out_time_split)
                                if shift_out_var == 'pm':
                                    if cutoff_out_time == 1.0:
                                        cutoff_out_time = 13.0
                                    elif cutoff_out_time == 2.0:
                                        cutoff_out_time = 14.0
                                    elif cutoff_out_time == 3.0:
                                        cutoff_out_time = 15.0
                                    elif cutoff_out_time == 4.0:
                                        cutoff_out_time = 16.0
                                    elif cutoff_out_time == 5.0:
                                        cutoff_out_time = 17.0
                                    elif cutoff_out_time == 6.0:
                                        cutoff_out_time = 18.0
                                    elif cutoff_out_time == 7.0:
                                        cutoff_out_time = 19.0
                                    elif cutoff_out_time == 8.0:
                                        cutoff_out_time = 20.0
                                    elif cutoff_out_time == 9.0:
                                        cutoff_out_time = 21.0
                                    elif cutoff_out_time == 10.0:
                                        cutoff_out_time = 22.0
                                    elif cutoff_out_time == 11.0:
                                        cutoff_out_time = 23.0
                                in_time_float = 0.0
                                out_time_float = 0.0
                                if in_time_split:
                                    in_time_float = float(in_time_split)
                                if out_time_split:
                                    out_time_float = float(out_time_split)
                                if in_time_float and cutoff_in_time:
                                    if in_time_float > cutoff_in_time:
                                        diff_in_time = in_time_float - cutoff_in_time
                                        diff_in_time_val = str(diff_in_time).split('.')
                                        # diff_in_time_val_one = diff_in_time_val[1]
                                        # if diff_in_time_val_one > 60:
                                        #     diff_in_time_var = diff_in_time_val_one-60
                                        #     diff_in_time = diff_in_time +1
                                        diff_in_time_replace = str('%.2f' % diff_in_time).replace('.',':')
                                if out_time_float and cutoff_out_time:
                                    if out_time_float < cutoff_out_time:
                                        diff_out_time = cutoff_out_time - out_time_float
                                        diff_out_time_val = str(diff_out_time).split('.')
                                        diff_out_time_val_one = diff_out_time_val[1]
                                        print(diff_out_time,out_time_float,cutoff_out_time,diff_out_time_val,int(diff_out_time_val_one))
                                        if int(diff_out_time_val_one) > 60:
                                            diff_out_time = diff_out_time - 0.40
                                        diff_out_time_replace = str('%.2f' % diff_out_time).replace('.',':')
                                # to keep the same in time as the first insert to get the correct working hours
                                # if in_time_split:
                                #     #  if a file that has least in time that is synced later
                                #     if in_time_split < row[2]:
                                #         in_time = in_time_split
                                #     else:
                                #         in_time = row[2]
                                # else:
                                #     in_time = row[2]
                                # # to have the greater out time 
                                # if out_time_split:
                                #     #  if a file that has max out time that is synced later
                                #     if out_time_split > row[3]:
                                #         out_time = out_time_split
                                #     else:
                                #         out_time = row[3]
                                # else:
                                #     out_time = row[3]
                                
                                if in_time_split:
                                    #  if a file that has least in time is synced later
                                    if float(in_time_split.replace(':','.')) < float(row[2].replace(':','.')):
                                        in_time = in_time_split.replace('.',':')
                                    else:
                                        in_time = row[2].replace('.',':')
                                else:
                                    in_time = row[2].replace('.',':')
                                # to keep the most out time 
                                if out_time_split:
                                    if float(out_time_split.replace(':','.')) > float(row[3].replace(':','.')):
                                        out_time = out_time_split.replace('.',':')
                                    else:
                                        out_time = row[3].replace('.',':')
                                else:
                                    out_time = row[3].replace('.',':')
                                attendance_date_split = attendance_date.split('-')
                                attendance_date = attendance_date_split[0]+'-'+attendance_date_split[1]+'-'+attendance_date_split[2]
                                if in_time:
                                    check_in = str(attendance_date)+' '+str(in_time)
                                if out_time:
                                    check_out = str(attendance_date)+' '+str(out_time)
                                check_in_time = False
                                check_out_time = False
                                check_in_min = False
                                check_out_min = False
                                if check_in:
                                    check_in_time = datetime.strptime(str(check_in), "%Y-%m-%d %H:%M") - timedelta(hours=5)
                                if check_out:
                                    check_out_time = datetime.strptime(str(check_out), "%Y-%m-%d %H:%M")- timedelta(hours=5)
                                # print(check_in_time,check_out_time,'gggggg---1111')
                                if check_in_time:
                                    check_in_min = check_in_time - timedelta(minutes=30)
                                if check_out_time:
                                    check_out_min = check_out_time - timedelta(minutes=30)
                                tdiff =  check_out_time - check_in_time
                                tdiff_string = str(tdiff)
                                tdiff_split = tdiff_string.split(':')
                                tdiff_split_val = tdiff_split[0]+'.'+tdiff_split[1]
                                # print(tdiff_split_val,'tdiff_split_val')
                                if ',' in tdiff_split_val:
                                    tdiff_split_comma = tdiff_split_val.split(',')
                                    tdiff_split_comma_val = tdiff_split_comma[1]
                                    tdiff_split_val = tdiff_split_comma_val
                                worked_hours = float(tdiff_split_val)
                                day = check_in_time.strftime('%A')
                                if site_master_id and site_master_id not in fms_ids:
                                    # below line is commented as of now because fms employees should not have early early_leaving or late_coming remark
                                    # if append_data[0] == 'importing' or not append_data[0]:
                                        diff_out_time_replace=None
                                        diff_in_time_replace =None
                                holiday_master = self.env['holiday.master'].search([('holiday_date','=',attendance_date)])
                                if holiday_master:
                                    site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s' % holiday_master.id)
                                    result = self.env.cr.fetchall()
                                    print (result,'ppppppp')
                                    if result:
                                        for site in result:
                                            print (site,'siteeee')
                                            if site[0] == site_master_id:                            
                                                employee_status = 'PH'
                                            else:
                                                if day in ('Saturday','Sunday'):
                                                    if worked_hours >=3.3:
                                                        employee_status = 'P'
                                                        diff_out_time_replace=None
                                                        diff_in_time_replace =None
                                                    if worked_hours < 3.3:
                                                        employee_status = 'AB'
                                                        diff_out_time_replace=None
                                                        diff_in_time_replace =None
                                                elif day not in ('Saturday','Sunday'):
                                                    if worked_hours > 8.0:
                                                        employee_status = 'P'
                                                    elif worked_hours >=4.3 and worked_hours <= 8.0:
                                                        employee_status = 'half_day_p_ab'
                                                    else:
                                                        employee_status = 'AB'
                                                        diff_out_time_replace=None
                                                        diff_in_time_replace =None
                                    else:
                                        if day in ('Saturday','Sunday'):
                                            if worked_hours >=3.3:
                                                employee_status = 'P'
                                                diff_out_time_replace=None
                                                diff_in_time_replace =None
                                            if worked_hours < 3.3:
                                                employee_status = 'AB'
                                                diff_out_time_replace=None
                                                diff_in_time_replace =None
                                        elif day not in ('Saturday','Sunday'):
                                            if worked_hours >= 8.0:
                                                employee_status = 'P'
                                            elif worked_hours >=4.3 and worked_hours < 8.0:
                                                employee_status = 'half_day_p_ab'
                                            else:
                                                employee_status = 'AB'
                                                diff_out_time_replace=None
                                                diff_in_time_replace =None
                                else:
                                    if day in ('Saturday','Sunday'):
                                        if worked_hours >=3.3:
                                            employee_status = 'P'
                                            diff_out_time_replace=None
                                            diff_in_time_replace =None
                                        if worked_hours < 3.3:
                                            employee_status = 'AB'
                                            diff_out_time_replace=None
                                            diff_in_time_replace =None
                                    elif day not in ('Saturday','Sunday'):
                                        if worked_hours >= 8.0:
                                            employee_status = 'P'
                                        elif worked_hours >=4.3 and worked_hours < 8.0:
                                            employee_status = 'half_day_p_ab'
                                        else:
                                            employee_status = 'AB'
                                            diff_out_time_replace=None
                                            diff_in_time_replace =None
                                if (worked_hours=='' or worked_hours == 0.0) and shift=='WO':
                                    employee_status = 'WO'
                                    diff_out_time_replace=None
                                    diff_in_time_replace =None
                                if qf_next_date_24_hr:
                                    worked_hours=worked_hours+24.0
                                    diff_out_time_replace=None
                                    diff_in_time_replace =None
                                if qf_next_date:
                                    diff_out_time_replace=None
                                search_attendance = self.env['hr.attendance'].search([('employee_code','=',employee_code),('attendance_date','=',str(attendance_date))],limit=1)
                                if search_attendance:
                                    if search_attendance.employee_status not in ('half_p_half_od','half_ab_half_od','half_pl_half_od','half_sl_half_od'):
                                        update_query = self.env.cr.execute('update hr_attendance set write_date=%s,early_leaving=%s,late_coming=%s,check_out=%s,out_time_updation=%s,worked_hours=%s,employee_status=%s,out_time=%s,check_in=%s,in_time_updation=%s,in_time=%s,import_status=%s where id=%s' ,(todays_date,diff_out_time_replace,diff_in_time_replace,check_out_min,out_time,worked_hours,employee_status,out_time,check_in_min,in_time,in_time,append_data[0],search_attendance.id))
                                        self.env.cr.commit()
                                else:
                                    que = self.env.cr.execute('insert into hr_attendance(create_date,import_status,shift,early_leaving,late_coming,employee_id,check_in,check_out,in_time_updation,out_time_updation,worked_hours,attendance_date,employee_code,department_id_val,site_master_id,employee_status,in_time,out_time,state) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(todays_date,append_data[0],shift_id,(diff_out_time_replace),(diff_in_time_replace),employee_id,check_in_min,check_out_min,in_time,out_time,worked_hours,attendance_date,employee_code,department_id,site_master_id,employee_status,in_time,out_time,'draft'))
                                    self.env.cr.commit()
                        count+=1
                    destination_file_name = datas_fname.split('.')
                    main_file_name = destination_file_name[0]+'_'+str(todays_date)+'.'+destination_file_name[1]
                    destination_path = destination_path+main_file_name
                    # shutil.move(file_path,destination_path+main_file_name)
                    # rec.state = 'done'
                    state = 'done'
                except Exception  as exc:
                    destination_file_name = datas_fname.split('.')
                    main_file_name = destination_file_name[0]+'_'+str(todays_date)+'.'+destination_file_name[1]
                    destination_path = failed_path+main_file_name
                    # shutil.move(file_path,failed_path+main_file_name)
                    state = 'failed'
            rec.state = state
            shutil.move(file_path,destination_path)

    # @api.multi
    # def import_data(self):
    #     todays_date = datetime.now()
    #     append_data=[]
    #     attendance_date_val =[]
    #     for rec in self:
    #         datas_fname = str(rec.datas_fname)
    #         import_config = self.env['import.config'].search([],limit=1)
    #         source_path = str(import_config.source_path)
    #         destination_path = str(import_config.destination_path)
    #         file_path = source_path+datas_fname
    #         print(file_path)
    #         with open(file_path, 'r') as f:
    #             reader = csv.reader(f)
    #             count =0   
    #             for row in reader:
    #                 diff_out_time_replace=''
    #                 diff_in_time_replace =''
    #                 append_data_var = row[9]
    #                 if append_data_var == 'Import Data':
    #                     variable_diff = 'importing'
    #                 if append_data_var == 'Biometric Data':
    #                     variable_diff = 'biometric'
    #                 if append_data_var == 'QuickFormz Data':
    #                     variable_diff = 'quickformz'
    #                 append_data.append(variable_diff)
    #                 if count != 0:
    #                     attendance_date = row[0]
    #                     employee_code = row[1]
    #                     variable_diff = row[9]
    #                     hr_employee_id = self.env['hr.employee'].search([('emp_code','=',employee_code)])
    #                     employee_id = hr_employee_id.id
    #                     department_name = row[3]
    #                     shift = row[4]
    #                     department_search = self.env['hr.department'].search([('name','=',str(department_name))])
    #                     shift_search = self.env['hr.employee.shift.timing'].search([('name','=',shift)])
    #                     shift_browse = self.env['hr.employee.shift.timing'].browse(shift_search.id)
    #                     shift_id = shift_browse.id
    #                     shift_in_time = shift_search.in_time
    #                     shift_out_time =shift_search.out_time
    #                     shift_out_var = shift_search.out_time_select
    #                     shift_in_time_split = shift_in_time.replace(':','.')
    #                     shift_out_time_split = shift_out_time.replace(':','.')                        
    #                     department_id =department_search.id
    #                     in_time_split = row[5].replace(':','.')
    #                     out_time_split = row[6].replace(':','.')
    #                     cutoff_in_time = float(shift_in_time_split)+1.00
    #                     cutoff_out_time = float(shift_out_time_split)
    #                     if shift_out_var == 'pm':
    #                         if cutoff_out_time == 1.0:
    #                             cutoff_out_time = 13.0
    #                         elif cutoff_out_time == 2.0:
    #                             cutoff_out_time = 14.0
    #                         elif cutoff_out_time == 3.0:
    #                             cutoff_out_time = 15.0
    #                         elif cutoff_out_time == 4.0:
    #                             cutoff_out_time = 16.0
    #                         elif cutoff_out_time == 5.0:
    #                             cutoff_out_time = 17.0
    #                         elif cutoff_out_time == 6.0:
    #                             cutoff_out_time = 18.0
    #                         elif cutoff_out_time == 7.0:
    #                             cutoff_out_time = 19.0
    #                         elif cutoff_out_time == 8.0:
    #                             cutoff_out_time = 20.0
    #                         elif cutoff_out_time == 9.0:
    #                             cutoff_out_time = 21.0
    #                         elif cutoff_out_time == 10.0:
    #                             cutoff_out_time = 22.0
    #                         elif cutoff_out_time == 11.0:
    #                             cutoff_out_time = 23.0
    #                     in_time_float = float(in_time_split)
    #                     out_time_float = float(out_time_split)
    #                     if in_time_float > cutoff_in_time:
    #                         diff_in_time = in_time_float - cutoff_in_time
    #                         diff_in_time_val = str(diff_in_time).split('.')
    #                         # diff_in_time_val_one = diff_in_time_val[1]
    #                         # if diff_in_time_val_one > 60:
    #                         #     diff_in_time_var = diff_in_time_val_one-60
    #                         #     diff_in_time = diff_in_time +1
    #                         diff_in_time_replace = str('%.2f' % diff_in_time).replace('.',':')
    #                     if out_time_float < cutoff_out_time:
    #                         diff_out_time = cutoff_out_time - out_time_float
    #                         diff_out_time_val = str(diff_out_time).split('.')
    #                         diff_out_time_val_one = diff_out_time_val[1]
    #                         if int(diff_out_time_val_one) > 60:
    #                             diff_out_time = diff_out_time - 0.40
    #                         diff_out_time_replace = str('%.2f' % diff_out_time).replace('.',':')
    #                     in_time = row[5]
    #                     out_time = row[6]
    #                     worked_hours = row[7]
    #                     employee_status = row[8]
    #                     attendance_date_split = attendance_date.split('-')
    #                     attendance_date = attendance_date_split[2]+'-'+attendance_date_split[1]+'-'+attendance_date_split[0]
    #                     check_in = str(attendance_date)+' '+str(in_time)
    #                     check_out = str(attendance_date)+' '+str(out_time)
    #                     check_in_time = datetime.strptime(str(check_in), "%Y-%m-%d %H:%M") - timedelta(hours=5)
    #                     check_out_time = datetime.strptime(str(check_out), "%Y-%m-%d %H:%M")- timedelta(hours=5)
    #                     check_in_min = check_in_time - timedelta(minutes=30)
    #                     check_out_min = check_out_time - timedelta(minutes=30)
    #                     que = self.env.cr.execute('insert into hr_attendance(import_status,shift,early_leaving,late_coming,employee_id,check_in,check_out,in_time_updation,out_time_updation,worked_hours,attendance_date,employee_code,department_id_val,employee_status,in_time,out_time,state) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(append_data[0],shift_id,(diff_out_time_replace),(diff_in_time_replace),employee_id,check_in_min,check_out_min,in_time,out_time,worked_hours,attendance_date,employee_code,department_id,employee_status,in_time,out_time,'draft'))
    #                     self.env.cr.commit()
    #                 count+=1
    #                 destination_file_name = datas_fname.split('.')
    #                 main_file_name = destination_file_name[0]+'_'+str(todays_date)+'.'+destination_file_name[1]
    #         shutil.move(file_path,destination_path+main_file_name)
    #         rec.state = 'done'

    @api.model
    def cron_import_data(self):
        import_config = self.env['import.config'].search([],limit=1)
        source_path = str(import_config.source_path)
        destination_path = str(import_config.destination_path)
        listOfFiles = os.listdir(source_path)
        for f in listOfFiles:
            if f.endswith('.csv'):
                datas_fname = str(f)
                file_url = source_path+datas_fname
                vals = {'datas_fname':datas_fname,'file_url':file_url,'state':'draft'}
                create_id = self.env['hr.attendance.import'].create(vals)
                for machine in create_id:
                    machine.import_data()


class ImportConfig(models.Model):
    _name = 'import.config'
    _description = "Import Configuration"

    source_path = fields.Char(string='Source Path')
    destination_path = fields.Char(string='Destination Path')
    failed_path = fields.Char(string='Failed File Path')


class HrAttendanceExport(models.Model):
    _name = 'hr.attendance.export'
    _description = "Attendance Export"

    def _get_default_access_token(self):
        return str(uuid.uuid4())

    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    access_token = fields.Char('Security Token', copy=False,default=_get_default_access_token)


    @api.multi
    def generate_excel(self,access_uid=None):
        self.ensure_one()
        return {
        'type': 'ir.actions.act_url',
        'url': '/web/pivot/attendance_export_xls/%s?access_token=%s' % (self.id, self.access_token),
        'target': 'new',
        }

class AttendanceReports(models.Model):
    _name = 'attendance.reports'

    def _get_default_access_token(self):
        return str(uuid.uuid4())

    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    access_token = fields.Char('Security Token', copy=False,default=_get_default_access_token)
    site_master_id = fields.Many2one('site.master','Site')
    department_id = fields.Many2one('hr.department','Department')
    time_period = fields.Selection([('daily','Daily'),('month','Monthly'),('year','Yearly')], string="Period")
    employee_id = fields.Many2one('hr.employee','Employee')
    emp_code = fields.Char('Employee Code')
    month_sel = fields.Selection([('01','January'),('02','February'),('03','March'),('04','April'),
                                        ('05','May'),('06','June'),('07','July'),('08','August'),
                                        ('09','September'),('10','October'),('11','November'),
                                        ('12','December')], string="Month")
    year_sel = fields.Many2one('year.master.annual','Year')

    @api.onchange('employee_id')
    def onchange_emp_code(self):
        if self.employee_id:
            self.emp_code = self.employee_id.emp_code
        else:
            pass

    @api.multi
    def generate_excelreport(self,access_uid=None):
        print(self.employee_id,self.emp_code,'------')
        self.get_dates()
        self.ensure_one()
        return {
        'type': 'ir.actions.act_url',
        'url': '/web/pivot/attendance_exportreport_xls/%s?access_token=%s' % (self.id, self.access_token),
        'target': 'new',
        }

    @api.multi
    def generate_month_excelreport(self,access_uid=None):
        if self.department_id:
            raise ValidationError(_('Department wise report is not available'))
        if not self.employee_id and not self.site_master_id:
            raise ValidationError(_('Kindly select Site or Employee!'))
        if self.employee_id and not self.employee_id.emp_code:
            raise ValidationError(_('Employee does not have an employee code!!!'))

        # print(self.employee_id,self.emp_code,'------')
        self.get_dates()
        self.ensure_one()
        return {
        'type': 'ir.actions.act_url',
        'url': '/web/pivot/attendance_month_exportreport_xls/%s?access_token=%s' % (self.id, self.access_token),
        'target': 'new',
        }

    @api.multi
    def generate_attendance_summary(self,access_uid=None):
        # if self.department_id:
        #     raise ValidationError(_('Department wise report is not available'))
        # if not self.employee_id and not self.site_master_id:
        #     raise ValidationError(_('Kindly select Site or Employee!'))
        # if self.employee_id and not self.employee_id.emp_code:
        #     raise ValidationError(_('Employee does not have an employee code!!!'))

        # print(self.employee_id,self.emp_code,'------')
        self.get_dates()
        self.ensure_one()
        return {
        'type': 'ir.actions.act_url',
        'url': '/web/pivot/attendance_summaryreport_xls/%s?access_token=%s' % (self.id, self.access_token),
        'target': 'new',
        }

    @api.multi
    def get_dates(self):
        current_date = datetime.now().date()
        # current_month = datetime.strptime(str(current_date), "%Y-%m-%d").strftime('%B')
        # current_year = datetime.strptime(str(current_date), "%Y-%m-%d").strftime('%Y')
        month = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").month
        year = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").year
        if self.time_period:
            abc = self.time_period
            print(abc,'***********88')
            if self.time_period == 'daily':
                self.from_date = datetime.now().date()
                self.to_date = datetime.now().date()
                
            elif self.time_period == 'month':
                date_list = []
                month = self.month_sel
                year = self.year_sel.name

                date_list = []
                date_list = calendar.monthrange(int(year),int(month))
                first_day = 1
                last_day = date_list[1]
                start_date = year + '-' + month + '-' + '01'
                end_date = year + '-' + month + '-' + str(last_day)

                from_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                to_date = datetime.strptime(end_date, "%Y-%m-%d").date()

                self.from_date = from_date
                self.to_date = to_date

            elif self.time_period == 'year':
                starting_day_of_current_year = datetime.now().date().replace(month=1, day=1)    
                ending_day_of_current_year = datetime.now().date().replace(month=12, day=31)
                print(starting_day_of_current_year,'wwwwww')
                print(ending_day_of_current_year,'dsds')
                self.from_date = starting_day_of_current_year
                self.to_date = ending_day_of_current_year
        return True


class HrAttendanceUtility(models.Model):
    _name = "hr.attendance.utility"

    site_id = fields.Many2one('site.master','Site Name')
    employee_ids = fields.Many2many('hr.employee','employee_site_rel','att_id','employee','Employee List')
    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')

    # weekoffs = fields.Selection([('2_4', 'Second & Forth'),('1_3_5', 'Frist, Third & Fifth'),('all', 'All Saturdays')], string='Saturday Weekoffs',default='2_4')
    effective_from = fields.Date('Effective From Date')
    effective_to = fields.Date('Effective To Date')


    @api.multi
    def create_yearly_scheduler(self):
        employee_ids = self.env['hr.employee'].search([('active','=',True),('name','not in',('Administrator','Test   User'))])
        for search_employee_id in employee_ids:
            emp_code = search_employee_id.emp_code
            department_id = search_employee_id.department_id.id
            parent_id = search_employee_id.parent_id.id
            if not parent_id:
                parent_id = None
            if not department_id:
                department_id=None
            employee_id = search_employee_id.id

            shift = search_employee_id.shift_id.name if search_employee_id.shift_id.name else ''
            shift_id = search_employee_id.shift_id.id if search_employee_id.shift_id.id else None

            site_master_id = search_employee_id.site_master_id.id
            if not site_master_id:
                site_master_id = None

            weekoffs = self.env['site.master'].browse(site_master_id).weekoffs
            print (weekoffs)
            sat_list = []
            sun_list = []
            first_list = []
            second_list = []
            third_list = []
            fourth_list = []
            fifth_list = []
            fifth_saturday = ''
            blank = ''
            if str(search_employee_id.joining_date) > '2019-04-01':
                split_join_date=search_employee_id.joining_date.split('-')
                day=split_join_date[2]
                month = split_join_date[1]
                start_date = datetime.now().date().replace(month=int(month), day=int(day))  
                end_date = datetime.now().date().replace(month=12, day=31)
                start_date = datetime.strptime(str(start_date), "%Y-%m-%d").date()
                end_date = datetime.strptime(str(end_date), "%Y-%m-%d").date()
            else:
                start_date = datetime.now().date().replace(month=4, day=1)  
                end_date = datetime.now().date().replace(month=12, day=31)
                start_date = datetime.strptime(str(start_date), "%Y-%m-%d").date()
                end_date = datetime.strptime(str(end_date), "%Y-%m-%d").date()
            print (start_date,type(start_date),end_date)
            delta1 = end_date - start_date
            dates = [str(start_date),str(end_date)]
            print (dates,'dates',emp_code)
            start, end = [datetime.strptime(_, "%Y-%m-%d") for _ in dates]
            date_range = list(OrderedDict(((start + timedelta(_)).strftime(r"%m-%Y"), None) for _ in range((end - start).days)).keys())

            for i in range(delta1.days + 1):
                dates = start_date + timedelta(i)
                day_name = calendar.day_name[dates.weekday()]
                if day_name == 'Saturday':
                    sat_list.append(dates)
                if day_name == 'Sunday':
                    sun_list.append(dates)

            
            for y in date_range:
                split_range = y.split('-')
                c = calendar.Calendar(firstweekday=calendar.SUNDAY)
                monthcal = c.monthdatescalendar(int(split_range[1]),int(split_range[0]))
                second_saturday = [day for week in monthcal for day in week if day.weekday() == calendar.SATURDAY and day.month == int(split_range[0])][1]
                fourth_saturday = [day for week in monthcal for day in week if day.weekday() == calendar.SATURDAY and day.month == int(split_range[0])][3]
                first_saturday = [day for week in monthcal for day in week if day.weekday() == calendar.SATURDAY and day.month == int(split_range[0])][0]
                third_saturday = [day for week in monthcal for day in week if day.weekday() == calendar.SATURDAY and day.month == int(split_range[0])][2]
                if first_saturday in sat_list:
                    if first_saturday not in first_list:
                        first_list.append(first_saturday)
                if third_saturday in sat_list:
                    if third_saturday not in third_list:
                        third_list.append(third_saturday)
                ix = [day for week in monthcal for day in week if day.weekday() == calendar.SATURDAY and day.month == int(split_range[0])]
                if len(ix) > 4:
                    fifth_saturday = [day for week in monthcal for day in week if day.weekday() == calendar.SATURDAY and day.month == int(split_range[0])][4]
                    if fifth_saturday in sat_list:
                        if fifth_saturday not in fifth_list:
                            fifth_list.append(fifth_saturday)
                if second_saturday in sat_list:
                    if second_saturday not in second_list:
                        second_list.append(second_saturday)
                if fourth_saturday in sat_list:
                    if fourth_saturday not in fourth_list:
                        fourth_list.append(fourth_saturday)
            for i in range(delta1.days + 1):
                employee_status=''
                dates = start_date + timedelta(i)
                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',dates),('employee_code','=',emp_code)])
                if not search_attendance:
                    que = self.env.cr.execute('insert into hr_attendance(shift,employee_id,check_in,check_out,attendance_date,employee_code,department_id_val,site_master_id,employee_status,state) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(shift_id,employee_id,dates,dates,dates,emp_code,department_id,site_master_id,employee_status,'draft'))
                    self.env.cr.commit()
                holiday_rec = self.env['holiday.master'].search([('holiday_date','=',dates)])
                if holiday_rec:
                    site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s' % holiday_rec.id)
                    result = self.env.cr.fetchall()
                    if result:
                        for site in result:
                            if site[0] == site_master_id:
                                employee_status = 'PH'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',dates),('employee_code','=',emp_code)])
                                if search_attendance:
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_code=%s', (employee_status,dates,emp_code))
                                    self.env.cr.commit()
            employee_status = ''
            if weekoffs == '2_4':
                for sun in list(set(sun_list)):
                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s', ('WO',datetime.strptime(str(sun), "%Y-%m-%d").date(),employee_id))
                for x in first_list:
                    holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                    if holiday_rec:
                        site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                        if result:
                            for site in result:
                                if site[0] == site_master_id:                                   
                                    employee_status = 'PH'
                                    search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                    if search_attendance:
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
                for x in third_list:
                    holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                    if holiday_rec:
                        site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                        result = self.env.cr.fetchall()
                        if result:
                            for site in result:
                                if site[0] == site_master_id:                                   
                                    employee_status = 'PH'
                                    search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                    if search_attendance:
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
                for x in fifth_list:
                    holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                    if holiday_rec:
                        site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                        result = self.env.cr.fetchall()
                        if result:
                            for site in result:
                                if site[0] == site_master_id:
                                    employee_status = 'PH'
                                    search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                    if search_attendance:
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
                for x in second_list:
                    employee_status = 'WO'
                    holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                    if holiday_rec:
                        site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                        result = self.env.cr.fetchall()
                        if result:
                            for site in result:
                                if site[0] == site_master_id:                                   
                                    employee_status = 'PH+WO'
                                    search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                    if search_attendance:
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
                                    else:
                                        employee_status = 'PH'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                            self.env.cr.commit()
                        else:
                            employee_status = 'WO'
                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                            if search_attendance:
                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                self.env.cr.commit()
                    else:
                        employee_status = 'WO'
                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                        if search_attendance:  
                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                            self.env.cr.commit()
                for x in fourth_list:
                    employee_status = 'WO'
                    holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                    if holiday_rec:
                        site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                        result = self.env.cr.fetchall()
                        if result:
                            for site in result:
                                if site[0] == site_master_id:                                   
                                    employee_status = 'PH+WO'
                                    search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                    if search_attendance:
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
                                    else:
                                        employee_status = 'PH'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                            self.env.cr.commit()
                        else:
                            employee_status = 'WO'
                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                            if search_attendance:
                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                self.env.cr.commit()
                    else:
                        employee_status = 'WO'
                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                        if search_attendance:
                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                            self.env.cr.commit()
            if weekoffs == '1_3_5':
                for sun in list(set(sun_list)):
                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s', ('WO',datetime.strptime(str(sun), "%Y-%m-%d").date(),employee_id))
                for x in second_list:
                    holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                    if holiday_rec:
                        site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                        result = self.env.cr.fetchall()
                        if result:
                            for site in result:
                                if site[0] == site_master_id:                                   
                                    employee_status = 'PH'
                                    search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                    if search_attendance:
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
                for x in fourth_list:
                    holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                    if holiday_rec:
                        site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                        result = self.env.cr.fetchall()
                        if result:
                            for site in result:
                                if site[0] == site_master_id:                                   
                                    employee_status = 'PH'
                                    search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                    if search_attendance:
                                        if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                            self.env.cr.commit()
                for x in first_list:
                    employee_status = 'WO'
                    holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                    if holiday_rec:
                        site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                        result = self.env.cr.fetchall()
                        if result:
                            for site in result:
                                if site[0] == site_master_id:                                   
                                    employee_status = 'PH+WO'
                                    search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                    if search_attendance:                                        
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
                                    else:
                                        employee_status = 'PH'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:                                            
                                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                            self.env.cr.commit()
                        else:
                            employee_status = 'WO'
                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                            if search_attendance:                                
                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                self.env.cr.commit()
                    else:
                        employee_status = 'WO'
                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                        if search_attendance:
                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                            self.env.cr.commit()
                for x in third_list:
                    employee_status = 'WO'
                    holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                    if holiday_rec:
                        site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                        result = self.env.cr.fetchall()
                        if result:
                            for site in result:
                                if site[0] == site_master_id:                                   
                                    employee_status = 'PH+WO'
                                    search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                    if search_attendance:
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
                                    else:
                                        employee_status = 'PH'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:                                            
                                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                            self.env.cr.commit()
                        else:
                            employee_status = 'WO'
                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                            if search_attendance:
                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                self.env.cr.commit()

                    else:
                        employee_status = 'WO'
                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                        if search_attendance:
                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                            self.env.cr.commit()
                for x in fifth_list:
                    employee_status = 'WO'
                    holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                    if holiday_rec:
                        site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                        result = self.env.cr.fetchall()
                        if result:
                            for site in result:
                                if site[0] == site_master_id:                                   
                                    employee_status = 'PH+WO'
                                    search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                    if search_attendance:
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
                                    else:
                                        employee_status = 'PH'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                            self.env.cr.commit()
                        else:
                            employee_status = 'WO'
                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                            if search_attendance:
                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                self.env.cr.commit()
                    else:
                        employee_status = 'WO'
                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                        if search_attendance:
                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                            self.env.cr.commit()
            if weekoffs == 'all':
                for sun in list(set(sun_list)):
                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s', ('WO',datetime.strptime(str(sun), "%Y-%m-%d").date(),employee_id))
                new_list = first_list + second_list + third_list + fourth_list + fifth_list
                for x in new_list:
                    holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                    if holiday_rec:
                        site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                        result = self.env.cr.fetchall()
                        if result:
                            for site in result:
                                if site[0] == site_master_id:                                   
                                    employee_status = 'PH+WO'
                                    search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                    if search_attendance:
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
                        else:
                            employee_status = 'WO'
                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                            if search_attendance:
                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                self.env.cr.commit()
                    else:
                        employee_status = 'WO'
                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                        if search_attendance:
                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                            self.env.cr.commit()
            if weekoffs == 'no':
                for sun in list(set(sun_list)):
                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s', ('WO',datetime.strptime(str(sun), "%Y-%m-%d").date(),employee_id))
                new_list = first_list + second_list + third_list + fourth_list + fifth_list
                for x in new_list:
                    holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                    if holiday_rec:
                        site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                        result = self.env.cr.fetchall()
                        if result:
                            for site in result:
                                if site[0] == site_master_id:                                   
                                    employee_status = 'PH'
                                    search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                    if search_attendance:                                        
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
                        else:
                            employee_status = ''
                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                            if search_attendance:                                
                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                self.env.cr.commit()
                    else:
                        employee_status = ''
                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                        if search_attendance:                            
                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                            self.env.cr.commit()
            if weekoffs == 'saturday_weekoff':
                print (employee_status,'11111111')
                for sun in list(set(sun_list)):
                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s', (blank,datetime.strptime(str(sun), "%Y-%m-%d").date(),employee_id))
                    employee_status = ''
                    holiday_rec = self.env['holiday.master'].search([('holiday_date','=',sun)])
                    if holiday_rec:
                        site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                        result = self.env.cr.fetchall()
                        if result:
                            for site in result:
                                if site[0] == site_master_id:                                   
                                    employee_status = 'PH'
                                    search_attendance = self.env['hr.attendance'].search([('attendance_date','=',sun),('employee_code','=',emp_code)],limit=1)
                                    if search_attendance:
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(sun), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
                    search_attendance = self.env['hr.attendance'].search([('attendance_date','=',sun),('employee_code','=',emp_code)],limit=1)
                    if search_attendance:                    
                        employee_status = ''
                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(sun), "%Y-%m-%d").date(),employee_id))
                        self.env.cr.commit()
                employee_status=''                
                new_list = first_list + second_list + third_list + fourth_list + fifth_list
                for x in new_list:
                    holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                    if holiday_rec:
                        site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                        result = self.env.cr.fetchall()
                        if result:
                            for site in result:
                                if site[0] == site_master_id:                                   
                                    employee_status = 'PH+WO'
                                    search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                    if search_attendance:
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
                        else:
                            employee_status = 'WO'
                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                            if search_attendance:
                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                self.env.cr.commit()
                    else:
                        employee_status = 'WO'
                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                        if search_attendance:                    
                            employee_status = 'WO'
                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                            self.env.cr.commit()

    @api.multi
    def create_attendance_schedule(self):

        start_date = datetime.strptime(str(self.from_date), "%Y-%m-%d").date()
        end_date = datetime.strptime(str(self.to_date), "%Y-%m-%d").date()

        delta1 = end_date - start_date
        print(delta1,'delta1')

        if self.site_id and not self.employee_ids:
            emp_recs = self.env['hr.employee'].search([('site_master_id','=',self.site_id.id)])
            print(emp_recs,'emp_recs')

            for search_employee_id in emp_recs:
                emp_code = search_employee_id.emp_code
                department_id = search_employee_id.department_id.id
                parent_id = search_employee_id.parent_id.id
                if not parent_id:
                    parent_id = None
                if not department_id:
                    department_id=None
                employee_id = search_employee_id.id

                shift = search_employee_id.shift_id.name if search_employee_id.shift_id.name else ''
                shift_id = search_employee_id.shift_id.id if search_employee_id.shift_id.id else None

                site_master_id = search_employee_id.site_master_id.id
                if not site_master_id:
                    site_master_id = None

                weekoffs = self.env['site.master'].browse(site_master_id).weekoffs
                print (weekoffs)
                sat_list = []
                sun_list = []
                first_list = []
                second_list = []
                third_list = []
                fourth_list = []
                fifth_list = []
                fifth_saturday = ''
                blank = ''
                if str(search_employee_id.joining_date) > '2019-04-01':
                    split_join_date=search_employee_id.joining_date.split('-')
                    day=split_join_date[2]
                    month = split_join_date[1]
                    start_date = datetime.now().date().replace(month=int(month), day=int(day))  
                    end_date = datetime.now().date().replace(month=12, day=31)
                    start_date = datetime.strptime(str(start_date), "%Y-%m-%d").date()
                    end_date = datetime.strptime(str(end_date), "%Y-%m-%d").date()
                else:
                    start_date = datetime.now().date().replace(month=4, day=1)  
                    end_date = datetime.now().date().replace(month=12, day=31)
                    start_date = datetime.strptime(str(start_date), "%Y-%m-%d").date()
                    end_date = datetime.strptime(str(end_date), "%Y-%m-%d").date()
                print (start_date,type(start_date),end_date)
                delta1 = end_date - start_date
                dates = [str(start_date),str(end_date)]
                print (dates,'dates')
                start, end = [datetime.strptime(_, "%Y-%m-%d") for _ in dates]
                date_range = list(OrderedDict(((start + timedelta(_)).strftime(r"%m-%Y"), None) for _ in range((end - start).days)).keys())

                for i in range(delta1.days + 1):
                    dates = start_date + timedelta(i)
                    day_name = calendar.day_name[dates.weekday()]
                    if day_name == 'Saturday':
                        sat_list.append(dates)
                    if day_name == 'Sunday':
                        sun_list.append(dates)

                for y in date_range:
                    split_range = y.split('-')
                    c = calendar.Calendar(firstweekday=calendar.SUNDAY)
                    monthcal = c.monthdatescalendar(int(split_range[1]),int(split_range[0]))
                    second_saturday = [day for week in monthcal for day in week if day.weekday() == calendar.SATURDAY and day.month == int(split_range[0])][1]
                    fourth_saturday = [day for week in monthcal for day in week if day.weekday() == calendar.SATURDAY and day.month == int(split_range[0])][3]
                    first_saturday = [day for week in monthcal for day in week if day.weekday() == calendar.SATURDAY and day.month == int(split_range[0])][0]
                    third_saturday = [day for week in monthcal for day in week if day.weekday() == calendar.SATURDAY and day.month == int(split_range[0])][2]
                    if first_saturday in sat_list:
                        if first_saturday not in first_list:
                            first_list.append(first_saturday)
                    if third_saturday in sat_list:
                        if third_saturday not in third_list:
                            third_list.append(third_saturday)
                    ix = [day for week in monthcal for day in week if day.weekday() == calendar.SATURDAY and day.month == int(split_range[0])]
                    if len(ix) > 4:
                        fifth_saturday = [day for week in monthcal for day in week if day.weekday() == calendar.SATURDAY and day.month == int(split_range[0])][4]
                        if fifth_saturday in sat_list:
                            if fifth_saturday not in fifth_list:
                                fifth_list.append(fifth_saturday)
                    if second_saturday in sat_list:
                        if second_saturday not in second_list:
                            second_list.append(second_saturday)
                    if fourth_saturday in sat_list:
                        if fourth_saturday not in fourth_list:
                            fourth_list.append(fourth_saturday)
                for i in range(delta1.days + 1):
                    employee_status=''
                    dates = start_date + timedelta(i)
                    search_attendance = self.env['hr.attendance'].search([('attendance_date','=',dates),('employee_code','=',emp_code)])
                    if not search_attendance:
                        que = self.env.cr.execute('insert into hr_attendance(shift,employee_id,check_in,check_out,attendance_date,employee_code,department_id_val,site_master_id,employee_status,state) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(shift_id,employee_id,dates,dates,dates,emp_code,department_id,site_master_id,employee_status,'draft'))
                        self.env.cr.commit()
                    holiday_rec = self.env['holiday.master'].search([('holiday_date','=',dates)])
                    if holiday_rec:
                        site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s' % holiday_rec.id)
                        result = self.env.cr.fetchall()
                        if result:
                            for site in result:
                                if site[0] == site_master_id:
                                    employee_status = 'PH'
                                    search_attendance = self.env['hr.attendance'].search([('attendance_date','=',dates),('employee_code','=',emp_code)])
                                    if search_attendance:
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_code=%s', (employee_status,dates,emp_code))
                                        self.env.cr.commit()
                employee_status = ''
                if weekoffs == '2_4':
                    for sun in list(set(sun_list)):
                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s', ('WO',datetime.strptime(str(sun), "%Y-%m-%d").date(),employee_id))
                    for x in first_list:
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                            self.env.cr.commit()
                    for x in third_list:
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                            self.env.cr.commit()
                    for x in fifth_list:
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:
                                        employee_status = 'PH'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                            self.env.cr.commit()
                    for x in second_list:
                        employee_status = 'WO'
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH+WO'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                            self.env.cr.commit()
                                        else:
                                            employee_status = 'PH'
                                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                            if search_attendance:
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                            else:
                                employee_status = 'WO'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                        else:
                            employee_status = 'WO'
                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                            if search_attendance:  
                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                self.env.cr.commit()
                    for x in fourth_list:
                        employee_status = 'WO'
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH+WO'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                            self.env.cr.commit()
                                        else:
                                            employee_status = 'PH'
                                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                            if search_attendance:
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                            else:
                                employee_status = 'WO'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                        else:
                            employee_status = 'WO'
                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                            if search_attendance:
                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                self.env.cr.commit()
                if weekoffs == '1_3_5':
                    for sun in list(set(sun_list)):
                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s', ('WO',datetime.strptime(str(sun), "%Y-%m-%d").date(),employee_id))
                    for x in second_list:
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                            self.env.cr.commit()
                    for x in fourth_list:
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                    for x in first_list:
                        employee_status = 'WO'
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH+WO'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:                                        
                                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                            self.env.cr.commit()
                                        else:
                                            employee_status = 'PH'
                                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                            if search_attendance:                                            
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                            else:
                                employee_status = 'WO'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:                                
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                        else:
                            employee_status = 'WO'
                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                            if search_attendance:
                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                self.env.cr.commit()
                    for x in third_list:
                        employee_status = 'WO'
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH+WO'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                            self.env.cr.commit()
                                        else:
                                            employee_status = 'PH'
                                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                            if search_attendance:                                            
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                            else:
                                employee_status = 'WO'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()

                        else:
                            employee_status = 'WO'
                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                            if search_attendance:
                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                self.env.cr.commit()
                    for x in fifth_list:
                        employee_status = 'WO'
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH+WO'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                            self.env.cr.commit()
                                        else:
                                            employee_status = 'PH'
                                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                            if search_attendance:
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                            else:
                                employee_status = 'WO'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                        else:
                            employee_status = 'WO'
                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                            if search_attendance:
                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                self.env.cr.commit()
                if weekoffs == 'all':
                    for sun in list(set(sun_list)):
                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s', ('WO',datetime.strptime(str(sun), "%Y-%m-%d").date(),employee_id))
                    new_list = first_list + second_list + third_list + fourth_list + fifth_list
                    for x in new_list:
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH+WO'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                            self.env.cr.commit()
                            else:
                                employee_status = 'WO'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                        else:
                            employee_status = 'WO'
                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                            if search_attendance:
                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                self.env.cr.commit()
                if weekoffs == 'no':
                    for sun in list(set(sun_list)):
                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s', ('WO',datetime.strptime(str(sun), "%Y-%m-%d").date(),employee_id))
                    new_list = first_list + second_list + third_list + fourth_list + fifth_list
                    for x in new_list:
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:                                        
                                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                            self.env.cr.commit()
                            else:
                                employee_status = ''
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:                                
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                        else:
                            employee_status = ''
                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                            if search_attendance:                            
                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                self.env.cr.commit()
                if weekoffs == 'saturday_weekoff':
                    print (employee_status,'11111111')
                    for sun in list(set(sun_list)):
                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s', (blank,datetime.strptime(str(sun), "%Y-%m-%d").date(),employee_id))
                        employee_status = ''
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',sun)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',sun),('employee_code','=',emp_code)],limit=1)
                                        if search_attendance:
                                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(sun), "%Y-%m-%d").date(),employee_id))
                                            self.env.cr.commit()
                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',sun),('employee_code','=',emp_code)],limit=1)
                        if search_attendance:                    
                            employee_status = ''
                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(sun), "%Y-%m-%d").date(),employee_id))
                            self.env.cr.commit()
                    employee_status=''                
                    new_list = first_list + second_list + third_list + fourth_list + fifth_list
                    for x in new_list:
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH+WO'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                            self.env.cr.commit()
                            else:
                                employee_status = 'WO'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                        else:
                            employee_status = 'WO'
                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                            if search_attendance:                    
                                employee_status = 'WO'
                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                self.env.cr.commit()

        elif self.employee_ids:
            for search_employee_id in self.employee_ids:
                emp_code = search_employee_id.emp_code
                department_id = search_employee_id.department_id.id
                parent_id = search_employee_id.parent_id.id
                if not parent_id:
                    parent_id = None
                if not department_id:
                    department_id=None
                employee_id = search_employee_id.id

                shift = search_employee_id.shift_id.name if search_employee_id.shift_id.name else ''
                shift_id = search_employee_id.shift_id.id if search_employee_id.shift_id.id else None

                site_master_id = search_employee_id.site_master_id.id
                if not site_master_id:
                    site_master_id = None

                weekoffs = self.env['site.master'].browse(site_master_id).weekoffs
                print (weekoffs)
                sat_list = []
                sun_list = []
                first_list = []
                second_list = []
                third_list = []
                fourth_list = []
                fifth_list = []
                fifth_saturday = ''
                blank = ''
                dates = [str(start_date),str(end_date)]
                print (dates,'dates')
                start, end = [datetime.strptime(_, "%Y-%m-%d") for _ in dates]
                date_range = list(OrderedDict(((start + timedelta(_)).strftime(r"%m-%Y"), None) for _ in range((end - start).days)).keys())

                for i in range(delta1.days + 1):
                    dates = start_date + timedelta(i)
                    day_name = calendar.day_name[dates.weekday()]
                    if day_name == 'Saturday':
                        sat_list.append(dates)
                    if day_name == 'Sunday':
                        sun_list.append(dates)

                
                for y in date_range:
                    split_range = y.split('-')
                    c = calendar.Calendar(firstweekday=calendar.SUNDAY)
                    monthcal = c.monthdatescalendar(int(split_range[1]),int(split_range[0]))
                    second_saturday = [day for week in monthcal for day in week if day.weekday() == calendar.SATURDAY and day.month == int(split_range[0])][1]
                    fourth_saturday = [day for week in monthcal for day in week if day.weekday() == calendar.SATURDAY and day.month == int(split_range[0])][3]
                    first_saturday = [day for week in monthcal for day in week if day.weekday() == calendar.SATURDAY and day.month == int(split_range[0])][0]
                    third_saturday = [day for week in monthcal for day in week if day.weekday() == calendar.SATURDAY and day.month == int(split_range[0])][2]
                    if first_saturday in sat_list:
                        if first_saturday not in first_list:
                            first_list.append(first_saturday)
                    if third_saturday in sat_list:
                        if third_saturday not in third_list:
                            third_list.append(third_saturday)
                    ix = [day for week in monthcal for day in week if day.weekday() == calendar.SATURDAY and day.month == int(split_range[0])]
                    if len(ix) > 4:
                        fifth_saturday = [day for week in monthcal for day in week if day.weekday() == calendar.SATURDAY and day.month == int(split_range[0])][4]
                        if fifth_saturday in sat_list:
                            if fifth_saturday not in fifth_list:
                                fifth_list.append(fifth_saturday)
                    if second_saturday in sat_list:
                        if second_saturday not in second_list:
                            second_list.append(second_saturday)
                    if fourth_saturday in sat_list:
                        if fourth_saturday not in fourth_list:
                            fourth_list.append(fourth_saturday)
                for i in range(delta1.days + 1):
                    employee_status=''
                    dates = start_date + timedelta(i)
                    search_attendance = self.env['hr.attendance'].search([('attendance_date','=',dates),('employee_code','=',emp_code)])
                    if not search_attendance:
                        que = self.env.cr.execute('insert into hr_attendance(shift,employee_id,check_in,check_out,attendance_date,employee_code,department_id_val,site_master_id,employee_status,state) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(shift_id,employee_id,dates,dates,dates,emp_code,department_id,site_master_id,employee_status,'draft'))
                        self.env.cr.commit()
                    holiday_rec = self.env['holiday.master'].search([('holiday_date','=',dates)])
                    if holiday_rec:
                        site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s' % holiday_rec.id)
                        result = self.env.cr.fetchall()
                        if result:
                            for site in result:
                                if site[0] == site_master_id:
                                    employee_status = 'PH'
                                    search_attendance = self.env['hr.attendance'].search([('attendance_date','=',dates),('employee_code','=',emp_code)])
                                    if search_attendance:
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_code=%s', (employee_status,dates,emp_code))
                                        self.env.cr.commit()
                employee_status = ''
                if weekoffs == '2_4':
                    for sun in list(set(sun_list)):
                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s', ('WO',datetime.strptime(str(sun), "%Y-%m-%d").date(),employee_id))
                    for x in first_list:
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                            self.env.cr.commit()
                    for x in third_list:
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                            self.env.cr.commit()
                    for x in fifth_list:
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:
                                        employee_status = 'PH'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                            self.env.cr.commit()
                    for x in second_list:
                        employee_status = 'WO'
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH+WO'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                            self.env.cr.commit()
                                        else:
                                            employee_status = 'PH'
                                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                            if search_attendance:
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                            else:
                                employee_status = 'WO'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                        else:
                            employee_status = 'WO'
                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                            if search_attendance:  
                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                self.env.cr.commit()
                    for x in fourth_list:
                        employee_status = 'WO'
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH+WO'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                            self.env.cr.commit()
                                        else:
                                            employee_status = 'PH'
                                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                            if search_attendance:
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                            else:
                                employee_status = 'WO'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                        else:
                            employee_status = 'WO'
                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                            if search_attendance:
                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                self.env.cr.commit()
                if weekoffs == '1_3_5':
                    for sun in list(set(sun_list)):
                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s', ('WO',datetime.strptime(str(sun), "%Y-%m-%d").date(),employee_id))
                    for x in second_list:
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                            self.env.cr.commit()
                    for x in fourth_list:
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                    for x in first_list:
                        employee_status = 'WO'
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH+WO'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:                                        
                                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                            self.env.cr.commit()
                                        else:
                                            employee_status = 'PH'
                                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                            if search_attendance:                                            
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                            else:
                                employee_status = 'WO'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:                                
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                        else:
                            employee_status = 'WO'
                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                            if search_attendance:
                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                self.env.cr.commit()
                    for x in third_list:
                        employee_status = 'WO'
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH+WO'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                            self.env.cr.commit()
                                        else:
                                            employee_status = 'PH'
                                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                            if search_attendance:                                            
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                            else:
                                employee_status = 'WO'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()

                        else:
                            employee_status = 'WO'
                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                            if search_attendance:
                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                self.env.cr.commit()
                    for x in fifth_list:
                        employee_status = 'WO'
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH+WO'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                            self.env.cr.commit()
                                        else:
                                            employee_status = 'PH'
                                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                            if search_attendance:
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                            else:
                                employee_status = 'WO'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                        else:
                            employee_status = 'WO'
                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                            if search_attendance:
                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                self.env.cr.commit()
                if weekoffs == 'all':
                    for sun in list(set(sun_list)):
                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s', ('WO',datetime.strptime(str(sun), "%Y-%m-%d").date(),employee_id))
                    new_list = first_list + second_list + third_list + fourth_list + fifth_list
                    for x in new_list:
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH+WO'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                            self.env.cr.commit()
                            else:
                                employee_status = 'WO'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                        else:
                            employee_status = 'WO'
                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                            if search_attendance:
                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                self.env.cr.commit()
                if weekoffs == 'no':
                    for sun in list(set(sun_list)):
                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s', ('WO',datetime.strptime(str(sun), "%Y-%m-%d").date(),employee_id))
                    new_list = first_list + second_list + third_list + fourth_list + fifth_list
                    for x in new_list:
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:                                        
                                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                            self.env.cr.commit()
                            else:
                                employee_status = ''
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:                                
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                        else:
                            employee_status = ''
                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                            if search_attendance:                            
                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                self.env.cr.commit()
                if weekoffs == 'saturday_weekoff':
                    print (employee_status,'11111111')
                    for sun in list(set(sun_list)):
                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s', (blank,datetime.strptime(str(sun), "%Y-%m-%d").date(),employee_id))
                        employee_status = ''
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',sun)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',sun),('employee_code','=',emp_code)],limit=1)
                                        if search_attendance:
                                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(sun), "%Y-%m-%d").date(),employee_id))
                                            self.env.cr.commit()
                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',sun),('employee_code','=',emp_code)],limit=1)
                        if search_attendance:                    
                            employee_status = ''
                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(sun), "%Y-%m-%d").date(),employee_id))
                            self.env.cr.commit()
                    employee_status=''                
                    new_list = first_list + second_list + third_list + fourth_list + fifth_list
                    for x in new_list:
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH+WO'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                            self.env.cr.commit()
                            else:
                                employee_status = 'WO'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                        else:
                            employee_status = 'WO'
                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                            if search_attendance:                    
                                employee_status = 'WO'
                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                self.env.cr.commit()

        return True


    @api.multi
    def weekoff_leave_assignment(self):
        if self.effective_from == '':
            raise ValidationError(_("Kindly enter Effective from Date"))
        if self.effective_to == '':
            raise ValidationError(_("Kindly enter Effective to Date"))
        from_date = self.effective_from
        to_date = self.effective_to
        start_date = datetime.strptime(from_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(to_date, "%Y-%m-%d").date()
        delta1 = end_date - start_date
        emp_recs = self.env['hr.employee'].search([('site_master_id','=',self.id)])
        sat_list = []
        sun_list = []
        # weekoffs = self.weekoffs
        result = []
        first_list = []
        second_list = []
        third_list = []
        fourth_list = []
        fifth_list = []
        fifth_saturday = ''
        dates = [from_date,to_date]
        start, end = [datetime.strptime(_, "%Y-%m-%d") for _ in dates]
        date_range = list(OrderedDict(((start + timedelta(_)).strftime(r"%m-%Y"), None) for _ in range((end - start).days)).keys())
        
        if self.site_id and not self.employee_ids:

            emp_recs = self.env['hr.employee'].search([('site_master_id','=',self.site_id.id)])
            print(emp_recs,'emp_recs')

            for search_employee_id in emp_recs:
                site_master_id = search_employee_id.site_master_id.id
                emp_code = search_employee_id.emp_code
                department_id = search_employee_id.department_id.id
                parent_id = search_employee_id.parent_id.id
                if not parent_id:
                    parent_id = None
                if not department_id:
                    department_id=None

                weekoffs = search_employee_id.site_master_id.weekoffs
                print(weekoffs,'weekoffs')

                employee_id = search_employee_id.id

                shift = search_employee_id.shift_id.name if search_employee_id.shift_id.name else ''
                shift_id = search_employee_id.shift_id.id if search_employee_id.shift_id.id else None

                # site_master_id = self.id

                for i in range(delta1.days + 1):
                    dates = start_date + timedelta(i)
                    day_name = calendar.day_name[dates.weekday()]

                    if day_name == 'Saturday':
                        sat_list.append(dates)
                        weekend = True
                    else:
                        weekend = False
                    if day_name == 'Sunday':
                        sun_list.append(dates)
                blank = ''
                for sat in list(set(sat_list)):
                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s', (blank,datetime.strptime(str(sat), "%Y-%m-%d").date(),employee_id))
                for y in date_range:
                    split_range = y.split('-')
                    c = calendar.Calendar(firstweekday=calendar.SUNDAY)
                    monthcal = c.monthdatescalendar(int(split_range[1]),int(split_range[0]))
                    second_saturday = [day for week in monthcal for day in week if day.weekday() == calendar.SATURDAY and day.month == int(split_range[0])][1]
                    fourth_saturday = [day for week in monthcal for day in week if day.weekday() == calendar.SATURDAY and day.month == int(split_range[0])][3]
                    first_saturday = [day for week in monthcal for day in week if day.weekday() == calendar.SATURDAY and day.month == int(split_range[0])][0]
                    third_saturday = [day for week in monthcal for day in week if day.weekday() == calendar.SATURDAY and day.month == int(split_range[0])][2]
                    if first_saturday in sat_list:
                        if first_saturday not in first_list:
                            first_list.append(first_saturday)
                    if third_saturday in sat_list:
                        if third_saturday not in third_list:
                            third_list.append(third_saturday)
                    ix = [day for week in monthcal for day in week if day.weekday() == calendar.SATURDAY and day.month == int(split_range[0])]
                    if len(ix) > 4:
                        fifth_saturday = [day for week in monthcal for day in week if day.weekday() == calendar.SATURDAY and day.month == int(split_range[0])][4]
                        if fifth_saturday in sat_list:
                            if fifth_saturday not in fifth_list:
                                fifth_list.append(fifth_saturday)
                    if second_saturday in sat_list:
                        if second_saturday not in second_list:
                            second_list.append(second_saturday)
                    if fourth_saturday in sat_list:
                        if fourth_saturday not in fourth_list:
                            fourth_list.append(fourth_saturday)
                if weekoffs == '2_4':
                    for x in first_list:
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                                worked_hours=search_attendance.worked_hours
                                                day = x.strftime('%A')
                                                if day in ('Saturday','Sunday'):
                                                    if worked_hours >=3.5:
                                                        employee_status = 'P'
                                                    if worked_hours < 3.5:
                                                        employee_status = 'AB'
                                                elif day not in ('Saturday','Sunday'):
                                                    if worked_hours > 6.5:
                                                        employee_status = 'P'
                                                    elif worked_hours >=4.5 and worked_hours <= 6.5:
                                                        employee_status = 'half_day_p_ab'
                                                    else:
                                                        employee_status = 'AB'
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                                            else:
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                    for x in third_list:
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                                worked_hours=search_attendance.worked_hours
                                                day = x.strftime('%A')
                                                if day in ('Saturday','Sunday'):
                                                    if worked_hours >=3.5:
                                                        employee_status = 'P'
                                                    if worked_hours < 3.5:
                                                        employee_status = 'AB'
                                                elif day not in ('Saturday','Sunday'):
                                                    if worked_hours > 6.5:
                                                        employee_status = 'P'
                                                    elif worked_hours >=4.5 and worked_hours <= 6.5:
                                                        employee_status = 'half_day_p_ab'
                                                    else:
                                                        employee_status = 'AB'
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                                            else:
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                    for x in fifth_list:
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:
                                        employee_status = 'PH'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                                worked_hours=search_attendance.worked_hours
                                                day = x.strftime('%A')
                                                if day in ('Saturday','Sunday'):
                                                    if worked_hours >=3.5:
                                                        employee_status = 'P'
                                                    if worked_hours < 3.5:
                                                        employee_status = 'AB'
                                                elif day not in ('Saturday','Sunday'):
                                                    if worked_hours > 6.5:
                                                        employee_status = 'P'
                                                    elif worked_hours >=4.5 and worked_hours <= 6.5:
                                                        employee_status = 'half_day_p_ab'
                                                    else:
                                                        employee_status = 'AB'
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                                            else:
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                    for x in second_list:
                        employee_status = 'WO'
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH+WO'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                                worked_hours=search_attendance.worked_hours
                                                day = x.strftime('%A')
                                                if day in ('Saturday','Sunday'):
                                                    if worked_hours >=3.5:
                                                        employee_status = 'P'
                                                    if worked_hours < 3.5:
                                                        employee_status = 'AB'
                                                elif day not in ('Saturday','Sunday'):
                                                    if worked_hours > 6.5:
                                                        employee_status = 'P'
                                                    elif worked_hours >=4.5 and worked_hours <= 6.5:
                                                        employee_status = 'half_day_p_ab'
                                                    else:
                                                        employee_status = 'AB'
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                                            else:
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                                        else:
                                            employee_status = 'PH'
                                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                            if search_attendance:
                                                if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                                    worked_hours=search_attendance.worked_hours
                                                    day = x.strftime('%A')
                                                    if day in ('Saturday','Sunday'):
                                                        if worked_hours >=3.5:
                                                            employee_status = 'P'
                                                        if worked_hours < 3.5:
                                                            employee_status = 'AB'
                                                    elif day not in ('Saturday','Sunday'):
                                                        if worked_hours > 6.5:
                                                            employee_status = 'P'
                                                        elif worked_hours >=4.5 and worked_hours <= 6.5:
                                                            employee_status = 'half_day_p_ab'
                                                        else:
                                                            employee_status = 'AB'
                                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                    self.env.cr.commit()
                                                else:
                                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                    self.env.cr.commit()
                            else:
                                employee_status = 'WO'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:
                                    if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                        worked_hours=search_attendance.worked_hours
                                        day = x.strftime('%A')
                                        if day in ('Saturday','Sunday'):
                                            if worked_hours >=3.5:
                                                employee_status = 'P'
                                            if worked_hours < 3.5:
                                                employee_status = 'AB'
                                        elif day not in ('Saturday','Sunday'):
                                            if worked_hours > 6.5:
                                                employee_status = 'P'
                                            elif worked_hours >=4.5 and worked_hours <= 6.5:
                                                employee_status = 'half_day_p_ab'
                                            else:
                                                employee_status = 'AB'
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
                                    else:
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
                        else:
                            employee_status = 'WO'
                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                            if search_attendance:
                                if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                    worked_hours=search_attendance.worked_hours
                                    day = x.strftime('%A')
                                    if day in ('Saturday','Sunday'):
                                        if worked_hours >=3.5:
                                            employee_status = 'P'
                                        if worked_hours < 3.5:
                                            employee_status = 'AB'
                                    elif day not in ('Saturday','Sunday'):
                                        if worked_hours > 6.5:
                                            employee_status = 'P'
                                        elif worked_hours >=4.5 and worked_hours <= 6.5:
                                            employee_status = 'half_day_p_ab'
                                        else:
                                            employee_status = 'AB'
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                                else:   
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                    for x in fourth_list:
                        employee_status = 'WO'
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH+WO'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                                worked_hours=search_attendance.worked_hours
                                                day = x.strftime('%A')
                                                if day in ('Saturday','Sunday'):
                                                    if worked_hours >=3.5:
                                                        employee_status = 'P'
                                                    if worked_hours < 3.5:
                                                        employee_status = 'AB'
                                                elif day not in ('Saturday','Sunday'):
                                                    if worked_hours > 6.5:
                                                        employee_status = 'P'
                                                    elif worked_hours >=4.5 and worked_hours <= 6.5:
                                                        employee_status = 'half_day_p_ab'
                                                    else:
                                                        employee_status = 'AB'
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                                            else:
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                                        else:
                                            employee_status = 'PH'
                                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                            if search_attendance:
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                            else:
                                employee_status = 'WO'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:
                                    if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                        worked_hours=search_attendance.worked_hours
                                        day = x.strftime('%A')
                                        if day in ('Saturday','Sunday'):
                                            if worked_hours >=3.5:
                                                employee_status = 'P'
                                            if worked_hours < 3.5:
                                                employee_status = 'AB'
                                        elif day not in ('Saturday','Sunday'):
                                            if worked_hours > 6.5:
                                                employee_status = 'P'
                                            elif worked_hours >=4.5 and worked_hours <= 6.5:
                                                employee_status = 'half_day_p_ab'
                                            else:
                                                employee_status = 'AB'
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
                                    else:
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
                        else:
                            employee_status = 'WO'
                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                            if search_attendance:
                                if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                    worked_hours=search_attendance.worked_hours
                                    day = x.strftime('%A')
                                    if day in ('Saturday','Sunday'):
                                        if worked_hours >=3.5:
                                            employee_status = 'P'
                                        if worked_hours < 3.5:
                                            employee_status = 'AB'
                                    elif day not in ('Saturday','Sunday'):
                                        if worked_hours > 6.5:
                                            employee_status = 'P'
                                        elif worked_hours >=4.5 and worked_hours <= 6.5:
                                            employee_status = 'half_day_p_ab'
                                        else:
                                            employee_status = 'AB'
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                                else:
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                if weekoffs == '1_3_5':
                    for x in second_list:
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                                worked_hours=search_attendance.worked_hours
                                                day = x.strftime('%A')
                                                if day in ('Saturday','Sunday'):
                                                    if worked_hours >=3.5:
                                                        employee_status = 'P'
                                                    if worked_hours < 3.5:
                                                        employee_status = 'AB'
                                                elif day not in ('Saturday','Sunday'):
                                                    if worked_hours > 6.5:
                                                        employee_status = 'P'
                                                    elif worked_hours >=4.5 and worked_hours <= 6.5:
                                                        employee_status = 'half_day_p_ab'
                                                    else:
                                                        employee_status = 'AB'
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                                        else:
                                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                            self.env.cr.commit()
                    for x in fourth_list:
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                                worked_hours=search_attendance.worked_hours
                                                day = x.strftime('%A')
                                                if day in ('Saturday','Sunday'):
                                                    if worked_hours >=3.5:
                                                        employee_status = 'P'
                                                    if worked_hours < 3.5:
                                                        employee_status = 'AB'
                                                elif day not in ('Saturday','Sunday'):
                                                    if worked_hours > 6.5:
                                                        employee_status = 'P'
                                                    elif worked_hours >=4.5 and worked_hours <= 6.5:
                                                        employee_status = 'half_day_p_ab'
                                                    else:
                                                        employee_status = 'AB'
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                                            else:
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                    for x in first_list:
                        employee_status = 'WO'
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH+WO'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                                worked_hours=search_attendance.worked_hours
                                                day = x.strftime('%A')
                                                if day in ('Saturday','Sunday'):
                                                    if worked_hours >=3.5:
                                                        employee_status = 'P'
                                                    if worked_hours < 3.5:
                                                        employee_status = 'AB'
                                                elif day not in ('Saturday','Sunday'):
                                                    if worked_hours > 6.5:
                                                        employee_status = 'P'
                                                    elif worked_hours >=4.5 and worked_hours <= 6.5:
                                                        employee_status = 'half_day_p_ab'
                                                    else:
                                                        employee_status = 'AB'
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                                            else:
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                                        else:
                                            employee_status = 'PH'
                                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                            if search_attendance:
                                                if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                                    worked_hours=search_attendance.worked_hours
                                                    day = x.strftime('%A')
                                                    if day in ('Saturday','Sunday'):
                                                        if worked_hours >=3.5:
                                                            employee_status = 'P'
                                                        if worked_hours < 3.5:
                                                            employee_status = 'AB'
                                                    elif day not in ('Saturday','Sunday'):
                                                        if worked_hours > 6.5:
                                                            employee_status = 'P'
                                                        elif worked_hours >=4.5 and worked_hours <= 6.5:
                                                            employee_status = 'half_day_p_ab'
                                                        else:
                                                            employee_status = 'AB'
                                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                    self.env.cr.commit()
                                                else:
                                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                    self.env.cr.commit()
                            else:
                                employee_status = 'WO'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:
                                    if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                        worked_hours=search_attendance.worked_hours
                                        day = x.strftime('%A')
                                        if day in ('Saturday','Sunday'):
                                            if worked_hours >=3.5:
                                                employee_status = 'P'
                                            if worked_hours < 3.5:
                                                employee_status = 'AB'
                                        elif day not in ('Saturday','Sunday'):
                                            if worked_hours > 6.5:
                                                employee_status = 'P'
                                            elif worked_hours >=4.5 and worked_hours <= 6.5:
                                                employee_status = 'half_day_p_ab'
                                            else:
                                                employee_status = 'AB'
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
                                    else:
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
                        else:
                            employee_status = 'WO'
                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                            if search_attendance:
                                if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                    worked_hours=search_attendance.worked_hours
                                    day = x.strftime('%A')
                                    if day in ('Saturday','Sunday'):
                                        if worked_hours >=3.5:
                                            employee_status = 'P'
                                        if worked_hours < 3.5:
                                            employee_status = 'AB'
                                    elif day not in ('Saturday','Sunday'):
                                        if worked_hours > 6.5:
                                            employee_status = 'P'
                                        elif worked_hours >=4.5 and worked_hours <= 6.5:
                                            employee_status = 'half_day_p_ab'
                                        else:
                                            employee_status = 'AB'
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                                else:
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                    for x in third_list:
                        employee_status = 'WO'
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH+WO'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                                worked_hours=search_attendance.worked_hours
                                                day = x.strftime('%A')
                                                if day in ('Saturday','Sunday'):
                                                    if worked_hours >=3.5:
                                                        employee_status = 'P'
                                                    if worked_hours < 3.5:
                                                        employee_status = 'AB'
                                                elif day not in ('Saturday','Sunday'):
                                                    if worked_hours > 6.5:
                                                        employee_status = 'P'
                                                    elif worked_hours >=4.5 and worked_hours <= 6.5:
                                                        employee_status = 'half_day_p_ab'
                                                    else:
                                                        employee_status = 'AB'
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                                            else:
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                                        else:
                                            employee_status = 'PH'
                                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                            if search_attendance:
                                                if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                                    worked_hours=search_attendance.worked_hours
                                                    day = x.strftime('%A')
                                                    if day in ('Saturday','Sunday'):
                                                        if worked_hours >=3.5:
                                                            employee_status = 'P'
                                                        if worked_hours < 3.5:
                                                            employee_status = 'AB'
                                                    elif day not in ('Saturday','Sunday'):
                                                        if worked_hours > 6.5:
                                                            employee_status = 'P'
                                                        elif worked_hours >=4.5 and worked_hours <= 6.5:
                                                            employee_status = 'half_day_p_ab'
                                                        else:
                                                            employee_status = 'AB'
                                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                    self.env.cr.commit()
                                                else:
                                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                    self.env.cr.commit()
                            else:
                                employee_status = 'WO'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:
                                    if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                        worked_hours=search_attendance.worked_hours
                                        day = x.strftime('%A')
                                        if day in ('Saturday','Sunday'):
                                            if worked_hours >=3.5:
                                                employee_status = 'P'
                                            if worked_hours < 3.5:
                                                employee_status = 'AB'
                                        elif day not in ('Saturday','Sunday'):
                                            if worked_hours > 6.5:
                                                employee_status = 'P'
                                            elif worked_hours >=4.5 and worked_hours <= 6.5:
                                                employee_status = 'half_day_p_ab'
                                            else:
                                                employee_status = 'AB'
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
                                    else:
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()

                        else:
                            employee_status = 'WO'
                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                            if search_attendance:
                                if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                    worked_hours=search_attendance.worked_hours
                                    day = x.strftime('%A')
                                    if day in ('Saturday','Sunday'):
                                        if worked_hours >=3.5:
                                            employee_status = 'P'
                                        if worked_hours < 3.5:
                                            employee_status = 'AB'
                                    elif day not in ('Saturday','Sunday'):
                                        if worked_hours > 6.5:
                                            employee_status = 'P'
                                        elif worked_hours >=4.5 and worked_hours <= 6.5:
                                            employee_status = 'half_day_p_ab'
                                        else:
                                            employee_status = 'AB'
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                                else:
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                    for x in fifth_list:
                        employee_status = 'WO'
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH+WO'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                                worked_hours=search_attendance.worked_hours
                                                day = x.strftime('%A')
                                                if day in ('Saturday','Sunday'):
                                                    if worked_hours >=3.5:
                                                        employee_status = 'P'
                                                    if worked_hours < 3.5:
                                                        employee_status = 'AB'
                                                elif day not in ('Saturday','Sunday'):
                                                    if worked_hours > 6.5:
                                                        employee_status = 'P'
                                                    elif worked_hours >=4.5 and worked_hours <= 6.5:
                                                        employee_status = 'half_day_p_ab'
                                                    else:
                                                        employee_status = 'AB'
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                                            else:
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                                        else:
                                            employee_status = 'PH'
                                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                            if search_attendance:
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                            else:
                                employee_status = 'WO'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:
                                    if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                        worked_hours=search_attendance.worked_hours
                                        day = x.strftime('%A')
                                        if day in ('Saturday','Sunday'):
                                            if worked_hours >=3.5:
                                                employee_status = 'P'
                                            if worked_hours < 3.5:
                                                employee_status = 'AB'
                                        elif day not in ('Saturday','Sunday'):
                                            if worked_hours > 6.5:
                                                employee_status = 'P'
                                            elif worked_hours >=4.5 and worked_hours <= 6.5:
                                                employee_status = 'half_day_p_ab'
                                            else:
                                                employee_status = 'AB'
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
                                    else:
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
                        else:
                            employee_status = 'WO'
                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                            if search_attendance:
                                if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                    worked_hours=search_attendance.worked_hours
                                    day = x.strftime('%A')
                                    if day in ('Saturday','Sunday'):
                                        if worked_hours >=3.5:
                                            employee_status = 'P'
                                        if worked_hours < 3.5:
                                            employee_status = 'AB'
                                    elif day not in ('Saturday','Sunday'):
                                        if worked_hours > 6.5:
                                            employee_status = 'P'
                                        elif worked_hours >=4.5 and worked_hours <= 6.5:
                                            employee_status = 'half_day_p_ab'
                                        else:
                                            employee_status = 'AB'
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                                else:
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                if weekoffs == 'all':
                    new_list = first_list + second_list + third_list + fourth_list + fifth_list
                    for x in new_list:
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH+WO'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                                worked_hours=search_attendance.worked_hours
                                                day = x.strftime('%A')
                                                if day in ('Saturday','Sunday'):
                                                    if worked_hours !=0.0 and worked_hours>0.0:
                                                        employee_status = 'P'
                                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                        self.env.cr.commit()
                                                    else:
                                                        employee_status = 'WO'
                                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                        self.env.cr.commit()
                                            else:
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                            else:
                                employee_status = 'WO'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:
                                    if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                        worked_hours=search_attendance.worked_hours
                                        day = x.strftime('%A')
                                        if day in ('Saturday','Sunday'):
                                            if worked_hours !=0.0 and worked_hours>0.0:
                                                employee_status = 'P'
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                                            else:
                                                employee_status = 'WO'
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                                    else:
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
                        else:
                            employee_status = 'WO'
                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                            if search_attendance:
                                if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                    worked_hours=search_attendance.worked_hours
                                    day = x.strftime('%A')
                                    if day in ('Saturday','Sunday'):
                                        if worked_hours !=0.0 and worked_hours>0.0:
                                            employee_status = 'P'
                                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                            self.env.cr.commit()
                                        else:
                                            employee_status = 'WO'
                                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                            self.env.cr.commit()
                                else:
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                if weekoffs == 'no':
                    new_list = first_list + second_list + third_list + fourth_list + fifth_list
                    for x in new_list:
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                                worked_hours=search_attendance.worked_hours
                                                day = x.strftime('%A')
                                                if day in ('Saturday','Sunday'):
                                                    if worked_hours >=3.5:
                                                        employee_status = 'P'
                                                    if worked_hours < 3.5:
                                                        employee_status = 'AB'
                                                elif day not in ('Saturday','Sunday'):
                                                    if worked_hours > 6.5:
                                                        employee_status = 'P'
                                                    elif worked_hours >=4.5 and worked_hours <= 6.5:
                                                        employee_status = 'half_day_p_ab'
                                                    else:
                                                        employee_status = 'AB'
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                                            else:
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                            else:
                                employee_status = ''
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:
                                    if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                        worked_hours=search_attendance.worked_hours
                                        day = x.strftime('%A')
                                        if day in ('Saturday','Sunday'):
                                            if worked_hours >=3.5:
                                                employee_status = 'P'
                                            if worked_hours < 3.5:
                                                employee_status = 'AB'
                                        elif day not in ('Saturday','Sunday'):
                                            if worked_hours > 6.5:
                                                employee_status = 'P'
                                            elif worked_hours >=4.5 and worked_hours <= 6.5:
                                                employee_status = 'half_day_p_ab'
                                            else:
                                                employee_status = 'AB'
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
                                    else:
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
                        else:
                            employee_status = ''
                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                            if search_attendance:
                                if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                    worked_hours=search_attendance.worked_hours
                                    day = x.strftime('%A')
                                    if day in ('Saturday','Sunday'):
                                        if worked_hours >=3.5:
                                            employee_status = 'P'
                                        if worked_hours < 3.5:
                                            employee_status = 'AB'
                                    elif day not in ('Saturday','Sunday'):
                                        if worked_hours > 6.5:
                                            employee_status = 'P'
                                        elif worked_hours >=4.5 and worked_hours <= 6.5:
                                            employee_status = 'half_day_p_ab'
                                        else:
                                            employee_status = 'AB'
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                                else:
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                if weekoffs == 'saturday_weekoff':
                    for sun in list(set(sun_list)):
                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s', (blank,datetime.strptime(str(sun), "%Y-%m-%d").date(),employee_id))
                        employee_status = ''
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',sun)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',sun),('employee_code','=',emp_code)],limit=1)
                                        if search_attendance:
                                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(sun), "%Y-%m-%d").date(),employee_id))
                                            self.env.cr.commit()
                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',sun),('employee_code','=',emp_code)],limit=1)
                        if search_attendance:
                            if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                worked_hours=search_attendance.worked_hours
                                day = sun.strftime('%A')
                                if day in ('Sunday'):
                                    if worked_hours > 6.5:
                                        employee_status = 'P'
                                    elif worked_hours >=4.5 and worked_hours <= 6.5:
                                        employee_status = 'half_day_p_ab'
                                    else:
                                        employee_status = 'AB'
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(sun), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                                else:
                                    employee_status = ''
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(sun), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                            else:
                                employee_status = ''
                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(sun), "%Y-%m-%d").date(),employee_id))
                                self.env.cr.commit()
                                    
                    new_list = first_list + second_list + third_list + fourth_list + fifth_list
                    for x in new_list:
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH+WO'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                                worked_hours=search_attendance.worked_hours
                                                day = x.strftime('%A')
                                                if day in ('Saturday'):
                                                    if worked_hours !=0.0 and worked_hours>0.0:
                                                        employee_status = 'P+WO'
                                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                        self.env.cr.commit()
                                                    else:
                                                        employee_status = 'WO'
                                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                        self.env.cr.commit()
                                            else:
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                            else:
                                employee_status = 'WO'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:
                                    if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                        worked_hours=search_attendance.worked_hours
                                        day = x.strftime('%A')
                                        if day in ('Saturday'):
                                            if worked_hours !=0.0 and worked_hours>0.0:
                                                employee_status = 'P+WO'
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                                            else:
                                                employee_status = 'WO'
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                                    else:
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
                        else:
                            employee_status = 'WO'
                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                            if search_attendance:
                                if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                    worked_hours=search_attendance.worked_hours
                                    day = x.strftime('%A')
                                    if day in ('Saturday'):
                                        if worked_hours !=0.0 and worked_hours>0.0:
                                            employee_status = 'P+WO'
                                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                            self.env.cr.commit()
                                        else:
                                            employee_status = 'WO'
                                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                            self.env.cr.commit()
                                else:
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()


        elif self.employee_ids:
            for search_employee_id in self.employee_ids:
                site_master_id = search_employee_id.site_master_id.id
                emp_code = search_employee_id.emp_code
                department_id = search_employee_id.department_id.id
                parent_id = search_employee_id.parent_id.id
                if not parent_id:
                    parent_id = None
                if not department_id:
                    department_id=None

                weekoffs = search_employee_id.site_master_id.weekoffs
                print(weekoffs,'weekoffs')

                employee_id = search_employee_id.id

                shift = search_employee_id.shift_id.name if search_employee_id.shift_id.name else ''
                shift_id = search_employee_id.shift_id.id if search_employee_id.shift_id.id else None

                # site_master_id = self.id

                for i in range(delta1.days + 1):
                    dates = start_date + timedelta(i)
                    day_name = calendar.day_name[dates.weekday()]

                    if day_name == 'Saturday':
                        sat_list.append(dates)
                        weekend = True
                    else:
                        weekend = False
                    if day_name == 'Sunday':
                        sun_list.append(dates)
                blank = ''
                for sat in list(set(sat_list)):
                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s', (blank,datetime.strptime(str(sat), "%Y-%m-%d").date(),employee_id))
                for sun in list(set(sun_list)):
                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s', ('WO',datetime.strptime(str(sun), "%Y-%m-%d").date(),employee_id))
                for y in date_range:
                    split_range = y.split('-')
                    c = calendar.Calendar(firstweekday=calendar.SUNDAY)
                    monthcal = c.monthdatescalendar(int(split_range[1]),int(split_range[0]))
                    second_saturday = [day for week in monthcal for day in week if day.weekday() == calendar.SATURDAY and day.month == int(split_range[0])][1]
                    fourth_saturday = [day for week in monthcal for day in week if day.weekday() == calendar.SATURDAY and day.month == int(split_range[0])][3]
                    first_saturday = [day for week in monthcal for day in week if day.weekday() == calendar.SATURDAY and day.month == int(split_range[0])][0]
                    third_saturday = [day for week in monthcal for day in week if day.weekday() == calendar.SATURDAY and day.month == int(split_range[0])][2]
                    if first_saturday in sat_list:
                        if first_saturday not in first_list:
                            first_list.append(first_saturday)
                    if third_saturday in sat_list:
                        if third_saturday not in third_list:
                            third_list.append(third_saturday)
                    ix = [day for week in monthcal for day in week if day.weekday() == calendar.SATURDAY and day.month == int(split_range[0])]
                    if len(ix) > 4:
                        fifth_saturday = [day for week in monthcal for day in week if day.weekday() == calendar.SATURDAY and day.month == int(split_range[0])][4]
                        if fifth_saturday in sat_list:
                            if fifth_saturday not in fifth_list:
                                fifth_list.append(fifth_saturday)
                    if second_saturday in sat_list:
                        if second_saturday not in second_list:
                            second_list.append(second_saturday)
                    if fourth_saturday in sat_list:
                        if fourth_saturday not in fourth_list:
                            fourth_list.append(fourth_saturday)
                if weekoffs == '2_4':
                    for x in first_list:
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                                worked_hours=search_attendance.worked_hours
                                                day = x.strftime('%A')
                                                if day in ('Saturday','Sunday'):
                                                    if worked_hours >=3.5:
                                                        employee_status = 'P'
                                                    if worked_hours < 3.5:
                                                        employee_status = 'AB'
                                                elif day not in ('Saturday','Sunday'):
                                                    if worked_hours > 6.5:
                                                        employee_status = 'P'
                                                    elif worked_hours >=4.5 and worked_hours <= 6.5:
                                                        employee_status = 'half_day_p_ab'
                                                    else:
                                                        employee_status = 'AB'
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                                            else:
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                    for x in third_list:
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                                worked_hours=search_attendance.worked_hours
                                                day = x.strftime('%A')
                                                if day in ('Saturday','Sunday'):
                                                    if worked_hours >=3.5:
                                                        employee_status = 'P'
                                                    if worked_hours < 3.5:
                                                        employee_status = 'AB'
                                                elif day not in ('Saturday','Sunday'):
                                                    if worked_hours > 6.5:
                                                        employee_status = 'P'
                                                    elif worked_hours >=4.5 and worked_hours <= 6.5:
                                                        employee_status = 'half_day_p_ab'
                                                    else:
                                                        employee_status = 'AB'
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                                            else:
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                    for x in fifth_list:
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:
                                        employee_status = 'PH'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                                worked_hours=search_attendance.worked_hours
                                                day = x.strftime('%A')
                                                if day in ('Saturday','Sunday'):
                                                    if worked_hours >=3.5:
                                                        employee_status = 'P'
                                                    if worked_hours < 3.5:
                                                        employee_status = 'AB'
                                                elif day not in ('Saturday','Sunday'):
                                                    if worked_hours > 6.5:
                                                        employee_status = 'P'
                                                    elif worked_hours >=4.5 and worked_hours <= 6.5:
                                                        employee_status = 'half_day_p_ab'
                                                    else:
                                                        employee_status = 'AB'
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                                            else:
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                    for x in second_list:
                        employee_status = 'WO'
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH+WO'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                                worked_hours=search_attendance.worked_hours
                                                day = x.strftime('%A')
                                                if day in ('Saturday','Sunday'):
                                                    if worked_hours >=3.5:
                                                        employee_status = 'P'
                                                    if worked_hours < 3.5:
                                                        employee_status = 'AB'
                                                elif day not in ('Saturday','Sunday'):
                                                    if worked_hours > 6.5:
                                                        employee_status = 'P'
                                                    elif worked_hours >=4.5 and worked_hours <= 6.5:
                                                        employee_status = 'half_day_p_ab'
                                                    else:
                                                        employee_status = 'AB'
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                                            else:
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                                        else:
                                            employee_status = 'PH'
                                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                            if search_attendance:
                                                if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                                    worked_hours=search_attendance.worked_hours
                                                    day = x.strftime('%A')
                                                    if day in ('Saturday','Sunday'):
                                                        if worked_hours >=3.5:
                                                            employee_status = 'P'
                                                        if worked_hours < 3.5:
                                                            employee_status = 'AB'
                                                    elif day not in ('Saturday','Sunday'):
                                                        if worked_hours > 6.5:
                                                            employee_status = 'P'
                                                        elif worked_hours >=4.5 and worked_hours <= 6.5:
                                                            employee_status = 'half_day_p_ab'
                                                        else:
                                                            employee_status = 'AB'
                                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                    self.env.cr.commit()
                                                else:
                                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                    self.env.cr.commit()
                            else:
                                employee_status = 'WO'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:
                                    if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                        worked_hours=search_attendance.worked_hours
                                        day = x.strftime('%A')
                                        if day in ('Saturday','Sunday'):
                                            if worked_hours >=3.5:
                                                employee_status = 'P'
                                            if worked_hours < 3.5:
                                                employee_status = 'AB'
                                        elif day not in ('Saturday','Sunday'):
                                            if worked_hours > 6.5:
                                                employee_status = 'P'
                                            elif worked_hours >=4.5 and worked_hours <= 6.5:
                                                employee_status = 'half_day_p_ab'
                                            else:
                                                employee_status = 'AB'
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
                                    else:
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
                        else:
                            employee_status = 'WO'
                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                            if search_attendance:
                                if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                    worked_hours=search_attendance.worked_hours
                                    day = x.strftime('%A')
                                    if day in ('Saturday','Sunday'):
                                        if worked_hours >=3.5:
                                            employee_status = 'P'
                                        if worked_hours < 3.5:
                                            employee_status = 'AB'
                                    elif day not in ('Saturday','Sunday'):
                                        if worked_hours > 6.5:
                                            employee_status = 'P'
                                        elif worked_hours >=4.5 and worked_hours <= 6.5:
                                            employee_status = 'half_day_p_ab'
                                        else:
                                            employee_status = 'AB'
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                                else:   
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                    for x in fourth_list:
                        employee_status = 'WO'
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH+WO'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                                worked_hours=search_attendance.worked_hours
                                                day = x.strftime('%A')
                                                if day in ('Saturday','Sunday'):
                                                    if worked_hours >=3.5:
                                                        employee_status = 'P'
                                                    if worked_hours < 3.5:
                                                        employee_status = 'AB'
                                                elif day not in ('Saturday','Sunday'):
                                                    if worked_hours > 6.5:
                                                        employee_status = 'P'
                                                    elif worked_hours >=4.5 and worked_hours <= 6.5:
                                                        employee_status = 'half_day_p_ab'
                                                    else:
                                                        employee_status = 'AB'
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                                            else:
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                                        else:
                                            employee_status = 'PH'
                                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                            if search_attendance:
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                            else:
                                employee_status = 'WO'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:
                                    if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                        worked_hours=search_attendance.worked_hours
                                        day = x.strftime('%A')
                                        if day in ('Saturday','Sunday'):
                                            if worked_hours >=3.5:
                                                employee_status = 'P'
                                            if worked_hours < 3.5:
                                                employee_status = 'AB'
                                        elif day not in ('Saturday','Sunday'):
                                            if worked_hours > 6.5:
                                                employee_status = 'P'
                                            elif worked_hours >=4.5 and worked_hours <= 6.5:
                                                employee_status = 'half_day_p_ab'
                                            else:
                                                employee_status = 'AB'
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
                                    else:
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
                        else:
                            employee_status = 'WO'
                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                            if search_attendance:
                                if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                    worked_hours=search_attendance.worked_hours
                                    day = x.strftime('%A')
                                    if day in ('Saturday','Sunday'):
                                        if worked_hours >=3.5:
                                            employee_status = 'P'
                                        if worked_hours < 3.5:
                                            employee_status = 'AB'
                                    elif day not in ('Saturday','Sunday'):
                                        if worked_hours > 6.5:
                                            employee_status = 'P'
                                        elif worked_hours >=4.5 and worked_hours <= 6.5:
                                            employee_status = 'half_day_p_ab'
                                        else:
                                            employee_status = 'AB'
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                                else:
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                if weekoffs == '1_3_5':
                    for x in second_list:
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                                worked_hours=search_attendance.worked_hours
                                                day = x.strftime('%A')
                                                if day in ('Saturday','Sunday'):
                                                    if worked_hours >=3.5:
                                                        employee_status = 'P'
                                                    if worked_hours < 3.5:
                                                        employee_status = 'AB'
                                                elif day not in ('Saturday','Sunday'):
                                                    if worked_hours > 6.5:
                                                        employee_status = 'P'
                                                    elif worked_hours >=4.5 and worked_hours <= 6.5:
                                                        employee_status = 'half_day_p_ab'
                                                    else:
                                                        employee_status = 'AB'
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                                        else:
                                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                            self.env.cr.commit()
                    for x in fourth_list:
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                                worked_hours=search_attendance.worked_hours
                                                day = x.strftime('%A')
                                                if day in ('Saturday','Sunday'):
                                                    if worked_hours >=3.5:
                                                        employee_status = 'P'
                                                    if worked_hours < 3.5:
                                                        employee_status = 'AB'
                                                elif day not in ('Saturday','Sunday'):
                                                    if worked_hours > 6.5:
                                                        employee_status = 'P'
                                                    elif worked_hours >=4.5 and worked_hours <= 6.5:
                                                        employee_status = 'half_day_p_ab'
                                                    else:
                                                        employee_status = 'AB'
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                                            else:
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                    for x in first_list:
                        employee_status = 'WO'
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH+WO'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                                worked_hours=search_attendance.worked_hours
                                                day = x.strftime('%A')
                                                if day in ('Saturday','Sunday'):
                                                    if worked_hours >=3.5:
                                                        employee_status = 'P'
                                                    if worked_hours < 3.5:
                                                        employee_status = 'AB'
                                                elif day not in ('Saturday','Sunday'):
                                                    if worked_hours > 6.5:
                                                        employee_status = 'P'
                                                    elif worked_hours >=4.5 and worked_hours <= 6.5:
                                                        employee_status = 'half_day_p_ab'
                                                    else:
                                                        employee_status = 'AB'
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                                            else:
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                                        else:
                                            employee_status = 'PH'
                                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                            if search_attendance:
                                                if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                                    worked_hours=search_attendance.worked_hours
                                                    day = x.strftime('%A')
                                                    if day in ('Saturday','Sunday'):
                                                        if worked_hours >=3.5:
                                                            employee_status = 'P'
                                                        if worked_hours < 3.5:
                                                            employee_status = 'AB'
                                                    elif day not in ('Saturday','Sunday'):
                                                        if worked_hours > 6.5:
                                                            employee_status = 'P'
                                                        elif worked_hours >=4.5 and worked_hours <= 6.5:
                                                            employee_status = 'half_day_p_ab'
                                                        else:
                                                            employee_status = 'AB'
                                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                    self.env.cr.commit()
                                                else:
                                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                    self.env.cr.commit()
                            else:
                                employee_status = 'WO'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:
                                    if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                        worked_hours=search_attendance.worked_hours
                                        day = x.strftime('%A')
                                        if day in ('Saturday','Sunday'):
                                            if worked_hours >=3.5:
                                                employee_status = 'P'
                                            if worked_hours < 3.5:
                                                employee_status = 'AB'
                                        elif day not in ('Saturday','Sunday'):
                                            if worked_hours > 6.5:
                                                employee_status = 'P'
                                            elif worked_hours >=4.5 and worked_hours <= 6.5:
                                                employee_status = 'half_day_p_ab'
                                            else:
                                                employee_status = 'AB'
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
                                    else:
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
                        else:
                            employee_status = 'WO'
                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                            if search_attendance:
                                if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                    worked_hours=search_attendance.worked_hours
                                    day = x.strftime('%A')
                                    if day in ('Saturday','Sunday'):
                                        if worked_hours >=3.5:
                                            employee_status = 'P'
                                        if worked_hours < 3.5:
                                            employee_status = 'AB'
                                    elif day not in ('Saturday','Sunday'):
                                        if worked_hours > 6.5:
                                            employee_status = 'P'
                                        elif worked_hours >=4.5 and worked_hours <= 6.5:
                                            employee_status = 'half_day_p_ab'
                                        else:
                                            employee_status = 'AB'
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                                else:
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                    for x in third_list:
                        employee_status = 'WO'
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH+WO'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                                worked_hours=search_attendance.worked_hours
                                                day = x.strftime('%A')
                                                if day in ('Saturday','Sunday'):
                                                    if worked_hours >=3.5:
                                                        employee_status = 'P'
                                                    if worked_hours < 3.5:
                                                        employee_status = 'AB'
                                                elif day not in ('Saturday','Sunday'):
                                                    if worked_hours > 6.5:
                                                        employee_status = 'P'
                                                    elif worked_hours >=4.5 and worked_hours <= 6.5:
                                                        employee_status = 'half_day_p_ab'
                                                    else:
                                                        employee_status = 'AB'
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                                            else:
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                                        else:
                                            employee_status = 'PH'
                                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                            if search_attendance:
                                                if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                                    worked_hours=search_attendance.worked_hours
                                                    day = x.strftime('%A')
                                                    if day in ('Saturday','Sunday'):
                                                        if worked_hours >=3.5:
                                                            employee_status = 'P'
                                                        if worked_hours < 3.5:
                                                            employee_status = 'AB'
                                                    elif day not in ('Saturday','Sunday'):
                                                        if worked_hours > 6.5:
                                                            employee_status = 'P'
                                                        elif worked_hours >=4.5 and worked_hours <= 6.5:
                                                            employee_status = 'half_day_p_ab'
                                                        else:
                                                            employee_status = 'AB'
                                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                    self.env.cr.commit()
                                                else:
                                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                    self.env.cr.commit()
                            else:
                                employee_status = 'WO'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:
                                    if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                        worked_hours=search_attendance.worked_hours
                                        day = x.strftime('%A')
                                        if day in ('Saturday','Sunday'):
                                            if worked_hours >=3.5:
                                                employee_status = 'P'
                                            if worked_hours < 3.5:
                                                employee_status = 'AB'
                                        elif day not in ('Saturday','Sunday'):
                                            if worked_hours > 6.5:
                                                employee_status = 'P'
                                            elif worked_hours >=4.5 and worked_hours <= 6.5:
                                                employee_status = 'half_day_p_ab'
                                            else:
                                                employee_status = 'AB'
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
                                    else:
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()

                        else:
                            employee_status = 'WO'
                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                            if search_attendance:
                                if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                    worked_hours=search_attendance.worked_hours
                                    day = x.strftime('%A')
                                    if day in ('Saturday','Sunday'):
                                        if worked_hours >=3.5:
                                            employee_status = 'P'
                                        if worked_hours < 3.5:
                                            employee_status = 'AB'
                                    elif day not in ('Saturday','Sunday'):
                                        if worked_hours > 6.5:
                                            employee_status = 'P'
                                        elif worked_hours >=4.5 and worked_hours <= 6.5:
                                            employee_status = 'half_day_p_ab'
                                        else:
                                            employee_status = 'AB'
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                                else:
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                    for x in fifth_list:
                        employee_status = 'WO'
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH+WO'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                                worked_hours=search_attendance.worked_hours
                                                day = x.strftime('%A')
                                                if day in ('Saturday','Sunday'):
                                                    if worked_hours >=3.5:
                                                        employee_status = 'P'
                                                    if worked_hours < 3.5:
                                                        employee_status = 'AB'
                                                elif day not in ('Saturday','Sunday'):
                                                    if worked_hours > 6.5:
                                                        employee_status = 'P'
                                                    elif worked_hours >=4.5 and worked_hours <= 6.5:
                                                        employee_status = 'half_day_p_ab'
                                                    else:
                                                        employee_status = 'AB'
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                                            else:
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                                        else:
                                            employee_status = 'PH'
                                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                            if search_attendance:
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                            else:
                                employee_status = 'WO'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:
                                    if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                        worked_hours=search_attendance.worked_hours
                                        day = x.strftime('%A')
                                        if day in ('Saturday','Sunday'):
                                            if worked_hours >=3.5:
                                                employee_status = 'P'
                                            if worked_hours < 3.5:
                                                employee_status = 'AB'
                                        elif day not in ('Saturday','Sunday'):
                                            if worked_hours > 6.5:
                                                employee_status = 'P'
                                            elif worked_hours >=4.5 and worked_hours <= 6.5:
                                                employee_status = 'half_day_p_ab'
                                            else:
                                                employee_status = 'AB'
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
                                    else:
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
                        else:
                            employee_status = 'WO'
                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                            if search_attendance:
                                if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                    worked_hours=search_attendance.worked_hours
                                    day = x.strftime('%A')
                                    if day in ('Saturday','Sunday'):
                                        if worked_hours >=3.5:
                                            employee_status = 'P'
                                        if worked_hours < 3.5:
                                            employee_status = 'AB'
                                    elif day not in ('Saturday','Sunday'):
                                        if worked_hours > 6.5:
                                            employee_status = 'P'
                                        elif worked_hours >=4.5 and worked_hours <= 6.5:
                                            employee_status = 'half_day_p_ab'
                                        else:
                                            employee_status = 'AB'
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                                else:
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                if weekoffs == 'all':
                    new_list = first_list + second_list + third_list + fourth_list + fifth_list
                    for x in new_list:
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH+WO'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                                worked_hours=search_attendance.worked_hours
                                                day = x.strftime('%A')
                                                if day in ('Saturday','Sunday'):
                                                    if worked_hours !=0.0 and worked_hours>0.0:
                                                        employee_status = 'P'
                                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                        self.env.cr.commit()
                                                    else:
                                                        employee_status = 'WO'
                                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                        self.env.cr.commit()
                                            else:
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                            else:
                                employee_status = 'WO'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:
                                    if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                        worked_hours=search_attendance.worked_hours
                                        day = x.strftime('%A')
                                        if day in ('Saturday','Sunday'):
                                            if worked_hours !=0.0 and worked_hours>0.0:
                                                employee_status = 'P'
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                                            else:
                                                employee_status = 'WO'
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                                    else:
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
                        else:
                            employee_status = 'WO'
                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                            if search_attendance:
                                if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                    worked_hours=search_attendance.worked_hours
                                    day = x.strftime('%A')
                                    if day in ('Saturday','Sunday'):
                                        if worked_hours !=0.0 and worked_hours>0.0:
                                            employee_status = 'P'
                                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                            self.env.cr.commit()
                                        else:
                                            employee_status = 'WO'
                                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                            self.env.cr.commit()
                                else:
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                if weekoffs == 'no':
                    new_list = first_list + second_list + third_list + fourth_list + fifth_list
                    for x in new_list:
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                                worked_hours=search_attendance.worked_hours
                                                day = x.strftime('%A')
                                                if day in ('Saturday','Sunday'):
                                                    if worked_hours >=3.5:
                                                        employee_status = 'P'
                                                    if worked_hours < 3.5:
                                                        employee_status = 'AB'
                                                elif day not in ('Saturday','Sunday'):
                                                    if worked_hours > 6.5:
                                                        employee_status = 'P'
                                                    elif worked_hours >=4.5 and worked_hours <= 6.5:
                                                        employee_status = 'half_day_p_ab'
                                                    else:
                                                        employee_status = 'AB'
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                                            else:
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                            else:
                                employee_status = ''
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:
                                    if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                        worked_hours=search_attendance.worked_hours
                                        day = x.strftime('%A')
                                        if day in ('Saturday','Sunday'):
                                            if worked_hours >=3.5:
                                                employee_status = 'P'
                                            if worked_hours < 3.5:
                                                employee_status = 'AB'
                                        elif day not in ('Saturday','Sunday'):
                                            if worked_hours > 6.5:
                                                employee_status = 'P'
                                            elif worked_hours >=4.5 and worked_hours <= 6.5:
                                                employee_status = 'half_day_p_ab'
                                            else:
                                                employee_status = 'AB'
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
                                    else:
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
                        else:
                            employee_status = ''
                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                            if search_attendance:
                                if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                    worked_hours=search_attendance.worked_hours
                                    day = x.strftime('%A')
                                    if day in ('Saturday','Sunday'):
                                        if worked_hours >=3.5:
                                            employee_status = 'P'
                                        if worked_hours < 3.5:
                                            employee_status = 'AB'
                                    elif day not in ('Saturday','Sunday'):
                                        if worked_hours > 6.5:
                                            employee_status = 'P'
                                        elif worked_hours >=4.5 and worked_hours <= 6.5:
                                            employee_status = 'half_day_p_ab'
                                        else:
                                            employee_status = 'AB'
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                                else:
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                if weekoffs == 'saturday_weekoff':
                    for sun in list(set(sun_list)):
                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s', (blank,datetime.strptime(str(sun), "%Y-%m-%d").date(),employee_id))
                        employee_status = ''
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',sun)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',sun),('employee_code','=',emp_code)],limit=1)
                                        if search_attendance:
                                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(sun), "%Y-%m-%d").date(),employee_id))
                                            self.env.cr.commit()
                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',sun),('employee_code','=',emp_code)],limit=1)
                        if search_attendance:
                            if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                worked_hours=search_attendance.worked_hours
                                day = sun.strftime('%A')
                                if day in ('Sunday'):
                                    if worked_hours > 6.5:
                                        employee_status = 'P'
                                    elif worked_hours >=4.5 and worked_hours <= 6.5:
                                        employee_status = 'half_day_p_ab'
                                    else:
                                        employee_status = 'AB'
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(sun), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                                else:
                                    employee_status = ''
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(sun), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()
                            else:
                                employee_status = ''
                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(sun), "%Y-%m-%d").date(),employee_id))
                                self.env.cr.commit()
                                    
                    new_list = first_list + second_list + third_list + fourth_list + fifth_list
                    for x in new_list:
                        holiday_rec = self.env['holiday.master'].search([('holiday_date','=',x)])
                        if holiday_rec:
                            site_master = self.env.cr.execute('select site_id from site_holiday_rel where holiday_id=%s and site_id=%s',(holiday_rec.id,site_master_id))
                            result = self.env.cr.fetchall()
                            if result:
                                for site in result:
                                    if site[0] == site_master_id:                                   
                                        employee_status = 'PH+WO'
                                        search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                        if search_attendance:
                                            if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                                worked_hours=search_attendance.worked_hours
                                                day = x.strftime('%A')
                                                if day in ('Saturday'):
                                                    if worked_hours !=0.0 and worked_hours>0.0:
                                                        employee_status = 'P+WO'
                                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                        self.env.cr.commit()
                                                    else:
                                                        employee_status = 'WO'
                                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                        self.env.cr.commit()
                                            else:
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                            else:
                                employee_status = 'WO'
                                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                                if search_attendance:
                                    if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                        worked_hours=search_attendance.worked_hours
                                        day = x.strftime('%A')
                                        if day in ('Saturday'):
                                            if worked_hours !=0.0 and worked_hours>0.0:
                                                employee_status = 'P+WO'
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                                            else:
                                                employee_status = 'WO'
                                                self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                                self.env.cr.commit()
                                    else:
                                        self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                        self.env.cr.commit()
                        else:
                            employee_status = 'WO'
                            search_attendance = self.env['hr.attendance'].search([('attendance_date','=',x),('employee_code','=',emp_code)])
                            if search_attendance:
                                if search_attendance.worked_hours>0.0 and search_attendance.worked_hours!=0.0:
                                    worked_hours=search_attendance.worked_hours
                                    day = x.strftime('%A')
                                    if day in ('Saturday'):
                                        if worked_hours !=0.0 and worked_hours>0.0:
                                            employee_status = 'P+WO'
                                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                            self.env.cr.commit()
                                        else:
                                            employee_status = 'WO'
                                            self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                            self.env.cr.commit()
                                else:
                                    self.env.cr.execute('update hr_attendance set employee_status=%s where attendance_date=%s and employee_id=%s',(employee_status,datetime.strptime(str(x), "%Y-%m-%d").date(),employee_id))
                                    self.env.cr.commit()

        return True


class BulkAttendanceApproval(models.Model):
    _name = 'bulk.attendance.approval'

    name = fields.Char('Name',default='Attendance Approval')
    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    employee_id = fields.Many2one('hr.employee','Employee')
    emp_code = fields.Char('Employee Code')
    attendance_lines = fields.One2many('hr.attendance','bulk_approval_id','Attendance')
    select_all = fields.Boolean('Select All',default=False)
    check_exists = fields.Boolean('Exists',default=False)
    done = fields.Boolean('Done',default=False)
    reject = fields.Boolean('Reject',default=False)

    @api.onchange('select_all')
    def _onchange_select_all(self):
        if self.select_all:
            if self.attendance_lines:
                for m in self.attendance_lines:
                    m.update({'select_record':True})
        else:
            if self.attendance_lines:
                for m in self.attendance_lines:
                    m.update({'select_record':False})

    def approve_attendance_records(self):
        if self.attendance_lines:
            check_rec=False
            for recs in self.attendance_lines:
                if recs.select_record:
                    check_rec=True
                    break
            if check_rec==False:
                raise ValidationError(_("Select atleast one record to Approve!!"))
            for recs in self.attendance_lines:
                if recs.select_record:
                    recs.bulk_approve_time()
                    recs.write({'state':'done','approved_rejected_date':datetime.now().date()})
        self.write({'check_exists':False,'done':True})


    def reject_attendance_records(self):
        if self.attendance_lines:
            check_rec=False
            for recs in self.attendance_lines:
                if recs.select_record:
                    check_rec=True
                    break
            if check_rec==False:
                raise ValidationError(_("Select atleast one record to Reject!!"))
            for recs in self.attendance_lines:
                if recs.select_record:
                    recs.reject_time()
                    recs.write({'state':'rejected','approved_rejected_date':datetime.now().date()})
        self.write({'check_exists':False,'reject':True})

    def search_attendance_records(self):
        self.write({'done':False,'reject':False,'check_exists':False})
        if self.attendance_lines:
            for i in self.attendance_lines:
                if i.bulk_approval_id.id:
                    i.write({'bulk_approval_id':None})
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        if res_user.id==1:
            if self.emp_code and self.from_date and self.to_date:
                search_attendance = self.env['hr.attendance'].search([('employee_code','=',str(self.emp_code)),('state','=','approval'),('attendance_date','>=',self.from_date),('attendance_date','<=',self.to_date)])
                if search_attendance:
                    for recs in search_attendance:
                        recs.write({'bulk_approval_id':self.id,'select_record':False})
                    self.write({'check_exists':True})
            elif self.emp_code:
                search_attendance = self.env['hr.attendance'].search([('employee_code','=',str(self.emp_code)),('state','=','approval')])
                if search_attendance:
                    for recs in search_attendance:
                        recs.write({'bulk_approval_id':self.id,'select_record':False})
                    self.write({'check_exists':True})
            elif self.from_date and self.to_date:
                search_attendance = self.env['hr.attendance'].search([('state','=','approval'),('attendance_date','>=',self.from_date),('attendance_date','<=',self.to_date)])
                if search_attendance:
                    for recs in search_attendance:
                        recs.write({'bulk_approval_id':self.id,'select_record':False})
                    self.write({'check_exists':True})
            else:
                res_user = self.env['res.users'].search([('id', '=', self._uid)])
                emp_id = self.env['hr.employee'].search([('user_id', '=', res_user.id)])
                search_employee = self.env['hr.employee'].search([('parent_id', '=', emp_id.id)])
                if search_employee:
                    for rec in search_employee:
                        search_attendance = self.env['hr.attendance'].search([('employee_id','=',rec.id),('state','=','approval')])
                        if search_attendance:
                            for recs in search_attendance:
                                recs.write({'bulk_approval_id':self.id,'select_record':False})
                            self.write({'check_exists':True})
        else:
            if self.employee_id:
                search_attendance = self.env['hr.attendance'].search([('employee_id','=',self.employee_id.id),('state','=','approval')])
                if search_attendance:
                    for recs in search_attendance:
                        recs.write({'bulk_approval_id':self.id,'select_record':False})
                    self.write({'check_exists':True})
            elif self.employee_id and self.from_date and self.to_date:
                search_attendance = self.env['hr.attendance'].search([('employee_id','=',self.employee_id.id),('state','=','approval'),('attendance_date','>=',self.from_date),('attendance_date','<=',self.to_date)])
                if search_attendance:
                    for recs in search_attendance:
                        recs.write({'bulk_approval_id':self.id,'select_record':False})
                    self.write({'check_exists':True})
            elif self.emp_code and self.from_date and self.to_date:
                search_attendance = self.env['hr.attendance'].search([('employee_code','=',str(self.emp_code)),('state','=','approval'),('attendance_date','>=',self.from_date),('attendance_date','<=',self.to_date)])
                if search_attendance:
                    for recs in search_attendance:
                        recs.write({'bulk_approval_id':self.id,'select_record':False})
                    self.write({'check_exists':True})
            elif self.emp_code:
                search_attendance = self.env['hr.attendance'].search([('employee_code','=',str(self.emp_code)),('state','=','approval')])
                if search_attendance:
                    for recs in search_attendance:
                        recs.write({'bulk_approval_id':self.id,'select_record':False})
                    self.write({'check_exists':True})
            elif self.from_date and self.to_date:
                res_user = self.env['res.users'].search([('id', '=', self._uid)])
                emp_id = self.env['hr.employee'].search([('user_id', '=', res_user.id)])
                search_employee = self.env['hr.employee'].search([('parent_id', '=', emp_id.id)])
                if search_employee:
                    for rec in search_employee:
                        search_attendance = self.env['hr.attendance'].search([('employee_id','=',rec.id),('state','=','approval'),('attendance_date','>=',self.from_date),('attendance_date','<=',self.to_date)])
                        if search_attendance:
                            for recs in search_attendance:
                                recs.write({'bulk_approval_id':self.id,'select_record':False})
                            self.write({'check_exists':True})
            else:
                res_user = self.env['res.users'].search([('id', '=', self._uid)])
                emp_id = self.env['hr.employee'].search([('user_id', '=', res_user.id)])
                search_employee = self.env['hr.employee'].search([('parent_id', '=', emp_id.id)])
                if search_employee:
                    for rec in search_employee:
                        search_attendance = self.env['hr.attendance'].search([('employee_id','=',rec.id),('state','=','approval')])
                        if search_attendance:
                            for recs in search_attendance:
                                recs.write({'bulk_approval_id':self.id,'select_record':False})
                            self.write({'check_exists':True})
        return True

class ShiftApplications(models.Model):
    _name = 'shift.application'
    _description = "Shift Application"

    name = fields.Char('Shift Application',default="Change Shift Application")
    year = fields.Selection([('2018', '2018'),('2019', '2019'),('2020', '2020'),('2021','2021'),('2022', '2022'),('2023','2023'),('2024', '2024'),('2025','2025'),('2026', '2026'),('2027','2027'),('2028', '2028'),('2029','2029'),('2030', '2030'),('2031','2031'),('2032', '2032'),('2033','2033'),('2034', '2034'),('2035','2035')],default='2019',string='Year')
    month = fields.Selection([('1', 'January'),('2', 'February'),('3', 'March'),('4','April'),('5', 'May'),('6','June'),('7', 'July'),('8','August'),('9', 'September'),('10','October'),('11', 'November'),('12','December')], string='Month', default='1')
    employee_code = fields.Char('Employee Code',size=10)
    employee_id = fields.Many2one('hr.employee', string="Employee Name",help='Name of the Employee', index=True, copy=False)
    shift_line = fields.One2many('shift.application.line', 'line_id', string='', auto_join=True)
    attendance_line = fields.One2many('hr.attendance', 'line_id1', string='', auto_join=True)
    line_visible = fields.Boolean('Tree View Visible',default=False)
    from_date =fields.Date('From Date')
    to_date = fields.Date('To Date')

    @api.onchange('employee_id')
    def set_join_date(self):
        self.employee_code = str(self.employee_id.emp_code) if self.employee_id.emp_code else 0

    def search_list(self):
        for rec in self:
            search_attendance = self.env['hr.attendance'].search([('attendance_date','>=',self.from_date),('attendance_date','<=',self.to_date),('employee_id','=',self.employee_id.id)])
            if search_attendance:
                for x in search_attendance:
                    x.write({'line_id1':rec.id,'hide_assign':False})
            rec.line_visible = True

    # def search_list(self):
    #     for rec in self:
    #         main_id = rec.id
    #         employee_code = rec.employee_code
    #         month = rec.month
    #         year = rec.year
    #         hr_employee_id =self.env['hr.employee'].search([('emp_code','=',int(employee_code))])
    #         employee_id = hr_employee_id.id
    #         search_shift_application_line = self.env['shift.application.line'].search([('employee_id','=',employee_id),('month','=',month),('year','=',year)])
    #         if search_shift_application_line:
    #             browse_shift_application_line = self.env['shift.application.line'].browse(search_shift_application_line)
    #             for search_id in search_shift_application_line:
    #                 shift_time = search_id.shift.id
    #                 main_line_id = search_id.line_id.id
    #                 search_id.shift = shift_time
    #                 search_id.line_id = main_id
    #             shift_application_obj = self.env['shift.application'].search([('id','=',main_line_id)])
    #             if shift_application_obj:
    #                 shift_application_obj.sudo().unlink()
    #         else:
    #             shift_time = hr_employee_id.shift_id.id
    #             first_last_day = calendar.monthrange(int(year),int(month))
    #             last_day = first_last_day[1]
    #             d1 = date(int(year), int(month), 1)
    #             d2 = date(int(year), int(month), last_day)
    #             delta = d2 - d1
    #             for i in range(delta.days + 1):
    #                 date_var = d1 + timedelta(i)
    #                 b = date_var.strftime('%A')
    #                 if b == 'Saturday' or b == 'Sunday':
    #                     search_shift_time = self.env['hr.employee.shift.timing'].search([('name','=','WO')])
    #                     shift_time= search_shift_time.id
    #                 else:
    #                     shift_time = hr_employee_id.shift_id.id
    #                 hr_attendance_id = self.env['hr.attendance'].search([('employee_code','=',int(employee_code)),('attendance_date','=',str(date_var))])
    #                 in_time = hr_attendance_id.in_time
    #                 out_time = hr_attendance_id.out_time
    #                 vals ={'employee_id':employee_id,'year':year,'month':month,'employee_code':employee_code,'date':str(date_var),'shift':shift_time,'in_time':in_time,'out_time':out_time,'line_id':main_id}
    #                 shift_application_create = self.env['shift.application.line'].create(vals)
    #         rec.line_visible = True

    @api.one
    def assign_list(self):
        self.env.cr.commit()

    

class ShiftApplicationsLines(models.Model):
    _name = 'shift.application.line'
    _description = "Shift Application Line"


    date = fields.Date(string='Date')
    shift = fields.Many2one('hr.employee.shift.timing',string="Shift",ondelete='cascade',index=True, copy=False)
    in_time = fields.Char('In Time',size=5)
    out_time = fields.Char('Out Time',size=5)
    line_id = fields.Many2one('shift.application',string="Line ID",ondelete='cascade',index=True, copy=False)
    employee_id = fields.Many2one('hr.employee', string="Employee Name",help='Name of the Employee', index=True, copy=False)
    year = fields.Selection([('2018', '2018'),('2019', '2019'),('2020', '2020'),('2021','2021'),('2022', '2022'),('2023','2023'),('2024', '2024'),('2025','2025'),('2026', '2026'),('2027','2027'),('2028', '2028'),('2029','2029'),('2030', '2030'),('2031','2031'),('2032', '2032'),('2033','2033'),('2034', '2034'),('2035','2035')],string='Year')
    month = fields.Selection([('1', 'January'),('2', 'February'),('3', 'March'),('4','April'),('5', 'May'),('6','June'),('7', 'July'),('8','August'),('9', 'September'),('10','October'),('11', 'November'),('12','December')], string='Month', default='1')
    employee_code = fields.Char('Employee Code',size=10)