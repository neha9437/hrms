# -*- coding: utf-8 -*-
###################################################################################
#    A part of Open HRMS Project <https://hrms.orientindia.net>
#
#    Orient Technologies Pvt Ltd.
#    Copyright (C) 2018-TODAY Orient Technologies Pvt Ltd.
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################
from datetime import datetime, timedelta
from odoo import api, fields, models, tools, _
from odoo import SUPERUSER_ID
from odoo.exceptions import UserError, AccessError, ValidationError
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
import calendar
from collections import OrderedDict

GENDER_SELECTION = [('male', 'Male'),
                    ('female', 'Female'),
                    ('other', 'Other')]


class HrEmployeeContractName(models.Model):
    """This class is to add emergency contact table"""

    _name = 'hr.emergency.contact'
    _description = 'HR Emergency Contact'

    number = fields.Char(string='Number', help='Contact Number')
    relation = fields.Char(string='Contact', help='Relation with employee')
    employee_obj = fields.Many2one('hr.employee', invisible=1)


class HrEmployeeFamilyInfo(models.Model):
    """Table for keep employee family information"""

    _name = 'hr.employee.family'
    _description = 'HR Employee Family'

    member_name = fields.Char(string='Name', related='employee_ref.name', store=True)
    employee_ref = fields.Many2one(string="Is Employee",
                                   help='If family member currently is an employee of same company, '
                                        'then please tick this field',
                                   comodel_name='hr.employee')
    employee_id = fields.Many2one(string="Employee", help='Select corresponding Employee', comodel_name='hr.employee',
                                  invisible=1)
    relation = fields.Selection([('father', 'Father'),
                                 ('mother', 'Mother'),
                                 ('daughter', 'Daughter'),
                                 ('son', 'Son'),
                                 ('wife', 'Wife')], string='Relationship', help='Relation with employee')
    member_contact = fields.Char(string='Contact No', related='employee_ref.personal_mobile', store=True)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def mail_reminder(self):
        """Sending expiry date notification for ID and Passport"""

        now = datetime.now() + timedelta(days=1)
        date_now = now.date()
        match = self.search([])
        for i in match:
            if i.id_expiry_date:
                exp_date = fields.Date.from_string(i.id_expiry_date) - timedelta(days=14)
                if date_now >= exp_date:
                    mail_content = "  Hello  " + i.name + ",<br>Your ID " + i.identification_id + "is going to expire on " + \
                                   str(i.id_expiry_date) + ". Please renew it before expiry date"
                    main_content = {
                        'subject': _('ID-%s Expired On %s') % (i.identification_id, i.id_expiry_date),
                        'author_id': self.env.user.partner_id.id,
                        'body_html': mail_content,
                        'email_to': i.work_email,
                    }
                    self.env['mail.mail'].sudo().create(main_content).send()
        match1 = self.search([])
        for i in match1:
            if i.passport_expiry_date:
                exp_date1 = fields.Date.from_string(i.passport_expiry_date) - timedelta(days=180)
                if date_now >= exp_date1:
                    mail_content = "  Hello  " + i.name + ",<br>Your Passport " + i.passport_id + "is going to expire on " + \
                                   str(i.passport_expiry_date) + ". Please renew it before expiry date"
                    main_content = {
                        'subject': _('Passport-%s Expired On %s') % (i.passport_id, i.passport_expiry_date),
                        'author_id': self.env.user.partner_id.id,
                        'body_html': mail_content,
                        'email_to': i.work_email,
                    }
                    self.env['mail.mail'].sudo().create(main_content).send()
    personal_mobile = fields.Char(string='Mobile', related='address_home_id.mobile', store=True)
    emergency_contact = fields.One2many('hr.emergency.contact', 'employee_obj', string='Emergency Contact')
    joining_date = fields.Date(string='Joining Date')
    id_expiry_date = fields.Date(string='Expiry Date', help='Expiry date of Identification ID')
    passport_expiry_date = fields.Date(string='Expiry Date', help='Expiry date of Passport ID')
    id_attachment_id = fields.Many2many('ir.attachment', 'id_attachment_rel', 'id_ref', 'attach_ref',
                                        string="Attachment", help='You can attach the copy of your Id')
    passport_attachment_id = fields.Many2many('ir.attachment', 'passport_attachment_rel', 'passport_ref', 'attach_ref1',
                                              string="Attachment",
                                              help='You can attach the copy of Passport')
    fam_ids = fields.One2many('hr.employee.family', 'employee_id', string='Family', help='Family Information')

class EmployeeTransfer(models.Model):
    _name = 'employee.transfer'

    name = fields.Char('Name',default='Employee Transfer')
    company_id = fields.Many2one('res.company','Company Name',default=1)
    location_name = fields.Many2one('site.master','Location Name*')
    employee_id = fields.Many2one('hr.employee','Select Employee*')
    employee_code = fields.Char('Employee Code*')
    department_name = fields.Many2one('hr.department','Department Name*')
    employee_status = fields.Selection([('probation', 'Probation'),('confirm','Permanent')], string='Employee Status*')
    salutation = fields.Selection([('mr','Mr'),('mrs','Mrs'),('ms','Ms')],string='Salutation')
    first_name = fields.Char('First Name')
    middle_name = fields.Char('Middle Name')
    last_name = fields.Char('Last Name')
    designation_name = fields.Many2one('hr.job','Designation Name')
    transfer = fields.Selection([('Transfer', 'Transfer')], default="Transfer", string='Transfer')
    transfer_date = fields.Date('Transfer Date*')
    transfer_reason = fields.Char('Transfer Reason')
    transfered = fields.Boolean('Transfered',default=False)
    old_site = fields.Many2one('site.master','Old Location Name*')
    old_site_name = fields.Char('Old Location Name')
    new_site_name = fields.Char('New Location Name')


    @api.onchange('employee_id')
    def onchange_employee_id(self):
        data = {}
        data['employee_code'] = self.employee_id.emp_code
        data['department_name'] = self.employee_id.department_id.id if self.employee_id.department_id else None
        data['location_name'] = self.employee_id.site_master_id.id if self.employee_id.site_master_id else None
        data['employee_status'] = self.employee_id.position_type
        data['salutation'] = self.employee_id.title
        data['first_name'] = self.employee_id.first_name
        data['last_name'] = self.employee_id.last_name
        data['middle_name'] = self.employee_id.middle_name
        data['designation_name'] = self.employee_id.job_id.id
        return {'value':data}

    def clear_form(self):
        self.write({'employee_id':None,'employee_code':None,
            'department_name':None,'location_name':None,
            'employee_status':None,
            'salutation':None,
            'first_name':None,'last_name':None,
            'middle_name':None,'designation_name':None,
            'transfer':None,'transfer_date':None,'transfer_reason':None})

    def search_by_emp_code(self):
        if self.employee_code:
            search_rec = self.env['hr.employee'].search([('emp_code','=',self.employee_code)])
            if search_rec:
                for x in search_rec:
                    self.write({'employee_id':x.id,'employee_code':x.emp_code,
                    'department_name':x.department_id.id,'location_name':x.site_master_id.id,
                    'employee_status':x.position_type,
                    'salutation':x.title,
                    'first_name':x.first_name,'last_name':x.last_name,
                    'middle_name':x.middle_name,'designation_name':x.job_id.id})
            else:
                raise ValidationError(_("Employee not found!!"))

    def update_site(self):
        if not self.employee_code:
            raise ValidationError(_("Kindly enter Employee code!!"))
        if not self.location_name:
            raise ValidationError(_("Kindly enter Location Name!!"))
        if not self.employee_status:
            raise ValidationError(_("Kindly enter Employee Status!!"))
        if not self.designation_name:
            raise ValidationError(_("Kindly enter Designation!!"))
        if not self.department_name:
            raise ValidationError(_("Kindly enter Department Name!!"))
        if not self.transfer_date:
            raise ValidationError(_("Kindly enter Transfer Date!!"))
        if not self.transfer_reason:
            raise ValidationError(_("Kindly enter Transfer Reason!!"))
        if self.employee_id:
            old_site = self.employee_id.site_master_id.id
            old_site_name = self.employee_id.site_master_id.name
            if old_site==self.location_name.id:
                raise ValidationError(_("Kindly select new Site to be transfered!!"))
        if self.transfer_date:
            site_master_id = self.location_name.id
            emp_code = self.employee_code
            department_id = self.department_name.id
            parent_id = self.employee_id.parent_id.id
            if not parent_id:
                parent_id = None
            if not department_id:
                department_id=None

            weekoffs = self.location_name.weekoffs
            print(weekoffs,'weekoffs')

            employee_id = self.employee_id.id

            shift = self.employee_id.shift_id.name if self.employee_id.shift_id.name else ''
            shift_id = self.employee_id.shift_id.id if self.employee_id.shift_id.id else None

            split_join_date=self.transfer_date.split('-')
            day=split_join_date[2]
            month = split_join_date[1]
            start_date = datetime.now().date().replace(month=int(month), day=int(day))  
            end_date = datetime.now().date().replace(month=12, day=31)
            start_date = datetime.strptime(str(start_date), "%Y-%m-%d").date()
            end_date = datetime.strptime(str(end_date), "%Y-%m-%d").date()
            print (start_date,type(start_date),end_date)
            delta1 = end_date - start_date
            employee_status = ''
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
                dates = start_date + timedelta(i)
                search_attendance = self.env['hr.attendance'].search([('attendance_date','=',dates),('employee_code','=',emp_code)])
                if search_attendance:
                    self.env.cr.execute('update hr_attendance set site_master_id=%s where attendance_date=%s and employee_code=%s', (site_master_id,dates,emp_code))
                    self.env.cr.commit()
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
            search_employee = self.env['hr.employee'].search([('id','=',self.employee_id.id)])
            if search_employee:
                search_employee.write({'department_id':self.department_name.id,
                                        'position_type':self.employee_status,
                                        'title':self.salutation,
                                        'first_name':self.first_name,
                                        'middle_name':self.middle_name,
                                        'last_name':self.last_name,
                                        'job_id':self.designation_name.id,
                                        'site_master_id':self.location_name.id})
            create_id = self.env['employee.transfer.history'].create({'old_site':old_site,
                                                        'old_site_name':old_site_name,
                                                        'employee_id':self.employee_id.id,
                                                        'employee_code':self.employee_code,
                                                        'new_site':self.location_name.id,
                                                        'new_site_name':self.location_name.name,
                                                        'transfer_date':self.transfer_date,
                                                        'transfer_reason':self.transfer_reason})
            self.write({'transfered':True,'old_site':old_site,
                        'old_site_name':old_site_name,
                        'new_site_name':self.location_name.name})

class EmployeeTransferHistory(models.Model):
    _name = 'employee.transfer.history'

    name = fields.Char('Name',default='Employee Transfer')
    old_site = fields.Many2one('site.master','Old Location Name*')
    old_site_name = fields.Char('Old Location Name')
    employee_id = fields.Many2one('hr.employee','Employee*')
    employee_code = fields.Char('Employee Code*')
    new_site = fields.Many2one('site.master','New Location Name*')
    new_site_name = fields.Char('New Location Name')
    transfer_date = fields.Date('Transfer Date*')
    transfer_reason = fields.Char('Transfer Reason')