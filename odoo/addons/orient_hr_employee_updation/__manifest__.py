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
{
    'name': 'Orient Employee Information Update',
    'version': '11.0.2.0.0',
    'summary': """Added fields in employee form""",
    'description': 'This module helps you to add more information in employee records.',
    'category': 'Generic Modules/Human Resources',
    'author': 'Orient Technologies Pvt Ltd',
    'company': 'Orient Technologies Pvt Ltd',
    'website': "https://hrms.orientindia.net",
    'depends': ['base', 'hr', 'mail', 'hr_gamification'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_view.xml',
        'views/hr_notification.xml',
    ],
    'demo': [],
    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
