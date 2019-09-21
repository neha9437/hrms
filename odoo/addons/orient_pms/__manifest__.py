# -*- coding: utf-8 -*-
{
    'name': "Orient Performance Management System",

    'summary': """
        Measuring Employee Performance""",

    'description': """
        Measure the Performance of Employee on Quarterly/Annual Basis 
    """,

    'author': "Ujwala Pawade, Megha Sirisila",
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
    'depends': ['base','hr'],

    # always loaded
    'data': [
        'views/views.xml',
        'views/templates.xml',
        'views/kra_form.xml',
        'views/annual_review.xml',
        'views/employee_salary_structure_view.xml',
        'wizard/kra_kpi_wizard.xml',
        'data/pms_data.xml',
        'data/master_data.xml',
        'data/pms_notification.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'report/annual_review_form.xml',
        'report/annual_review_report.xml',
        'report/appraisal_report.xml',
        'report/appraisal_report_new.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
