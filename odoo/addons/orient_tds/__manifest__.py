# -*- coding: utf-8 -*-
###################################################################################
#    A part of HRMS Project <https://hrms.orientindia.net>
#
#    Orient Technologies Pvt Ltd.
#    Copyright (C) 2018-TODAY Orient Technologies Pvt Ltd..
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
    'name': 'Orient TDS(Tax Deduction Source) Management',
    'version': '11.0.1.0.0',
    'summary': 'Handling the employee TDS',
    'author': 'Orient Technologies Pvt Ltd',
    'company': 'Orient Technologies Pvt Ltd',
    'website': 'https://hrms.orientindia.net',
    'depends': ['hr','base','badge_menu','orient_employee_self_service_portal'],
    'category': 'Human Resources',
    'maintainer': 'Orient Technologies Pvt Ltd',
    'demo': [],
    'data': [
        'views/tds_view.xml',
        # 'views/tds_notification.xml',
        # 'security/security.xml',
        'security/ir.model.access.csv',
        'report/pay_slip_report.xml',
        'report/pay_slip_report_menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': True,
    'images': [],
    'license': 'AGPL-3',
}
