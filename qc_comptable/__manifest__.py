# -*- coding: utf-8 -*-
{
    'name': "qc_comptable",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Qualisysconsulting",
    'website': "http://www.qualisysconsulting.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '13.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'base_setup',
        'mail',
        'fetchmail',
        'utm',
        'web_tour',
        'contacts',
        'portal',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/views.xml',
        'views/comptable_portal_templates.xml',
        #'data/data_stage.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    "images": ["static/description/icon.png"],
}