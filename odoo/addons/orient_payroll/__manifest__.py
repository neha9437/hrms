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
    'name': 'Orient Payroll',
    'version': '11.0.1.0.0',
    'summary': 'Exporting the data for payroll calculation',
    'author': 'Orient Technologies Pvt Ltd',
    'company': 'Orient Technologies Pvt Ltd',
    'website': 'https://hrms.orientindia.net',
    'depends': ['hr','base','orient_pms','orient_tds'],
    'category': 'Human Resources',
    'maintainer': 'Orient Technologies Pvt Ltd',
    'demo': [],
    'data': [
        'data/months_data.xml',
        'security/ir.model.access.csv',
        'views/payroll_view.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': True,
    'images': [],
    'license': 'AGPL-3',
}
