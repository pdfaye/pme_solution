# -*- coding:utf-8 -*-

{
    'name': 'PME et Cabinet',
    'category': 'Human Resources',
    'version': '13',
    'sequence': 1,
    'author': 'Papa Daouda Faye, Odoo QC',
    'summary': 'Cabinets et PMe',
    'description': "Ce module offre la liste des PME, cabinet et des services offerts ",
    'website': 'http://odoomates.tech',
    'depends': [
        'hr_contract',
        'hr_holidays',
    ],
    'data': [
        'security/pme_cabinet_securite.xml',
        'security/ir.model.access.csv',
        'views/cabinet.xml',
        'views/pme.xml',
    ],
    'images': ['static/description/banner.gif'],
    'application': True,
}
