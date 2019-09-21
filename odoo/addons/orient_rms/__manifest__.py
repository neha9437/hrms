# -*- coding: utf-8 -*-
{
    'name': "Orient Recruitment Management System",

    'summary': """
        Handling the recruitment processes""",

    'description': """ Recruitment Management System
        
    """,

    'author': 'Orient Technologies Pvt Ltd',
    'website': "http://www.orientindia.com",
    'images': [
        'static/src/img/default_image.png',
    ],
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'HRMS',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','orient_employee_self_service_portal'],

    # always loaded
    'data': [
        'security/orient_rms_security.xml',
        'views/recruitment_view.xml',
        'views/quik_recruitments_view.xml',
        'security/ir.model.access.csv',
        'data/hr_recruitment_data.xml',
        'data/portal_login_email_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': [],
    'license': 'AGPL-3',
}
