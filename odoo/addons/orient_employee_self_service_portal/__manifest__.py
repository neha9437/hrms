# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Candidate Self Service Portal',
    'version': '1.1',
    'category': 'Human Resources',
    'summary': 'Self service portal for potential candidates to fill in all the details and attach the documents.',
    'description': "Candidate self service portal",
    'author': 'Orient Technologies Pvt Ltd',
    'images': [
    ],
    'depends': [
        'base','hr_recruitment','mail','orient_hr_resignation'
    ],
    'data': [
        'security/orient_employee_self_service_portal_security.xml',
        'security/ir.model.access.csv',
        'views/hr_applicant_view.xml',
        'views/service_portal_master_view.xml',
        'views/service_config_view.xml',
        'views/hr_employee_view.xml',
        # 'views/report_template.xml',
        'wizard/offer_letter_wizard_view.xml',
        # 'report/offer_letter.xml',
        # 'report/employee_offerletter.xml',
        'data/portal_configuration_data.xml',
        # 'data/portal_document_configuration_data.xml',
        'data/portal_login_email_data.xml',
        'data/recruitment_stages_data.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': True,
    'qweb': [],
}