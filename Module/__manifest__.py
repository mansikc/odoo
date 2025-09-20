# -*- coding: utf-8 -*-
{
    'name': 'Square Payment Integration',
    'version': '16.0.1.0.0',
    'summary': 'Starter integration for Square (sandbox + production) for Odoo',
    'category': 'Accounting/Payment',
    'author': 'You',
    'website': 'https://ever-wild-outdoors.odoo.com/',
    'depends': ['payment'],
    'data': [
        'views/square_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
