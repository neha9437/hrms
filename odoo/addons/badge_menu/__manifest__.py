# -*- coding: utf-8 -*-
{
    'name': "Showing a menu notification in Odoo",

    'summary': """
        Showing a menu notification in Odoo
        """,

    'description': """
        Showing a menu notification in Odoo 
    """,

    'author': "shreyaskamath@orientindia.net",
    'website': "",
    'category': 'Tools',
    'version': '0.1',
    "license": "",

    # any module necessary for this one to work correctly
    'images': ['static/description/icon.png'],
    'depends': ['base', 'web'],
    "data": [
        'views/assets.xml',
    ],
    'qweb': [
        'static/src/xml/menu.xml',
    ],
}