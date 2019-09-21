# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Orient Leave Management',
    'version': '1.1',
    'category': 'Human Resources',
    'summary': 'Handling Employee Leaves',
    'description': "Leave management system",
    'author': 'Orient Technologies Pvt Ltd',
    'images': [
    ],
    'depends': [
        'base','hr_holidays','orient_pms','orient_hr_resignation'
    ],
    'data': [
        'data/leaves_data.xml',
        'data/leaves_notification.xml',
        'data/leaves_schedular.xml',
        'security/orient_leave_security.xml',
        'security/ir.model.access.csv',
        'views/hr_holidays_view.xml',
        'views/site_holidays_view.xml',
        'views/holiday_allocation_view.xml',
        'wizard/sandwich_leaves_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': True,
    'qweb': [],
}
