# -*- coding: utf-8 -*-
{
    'name': 'Square Payment Terminal',
    'version': '1.0.0',
    'summary': 'Integration for Square Payment terminal for Odoo',
    'category': 'Accounting/Payment',
    'author': 'KrunalC',
    'depends': ['point_of_sale', 'payment'],
    'data': [
        'views/square_views.xml',
        'security/ir.model.access.csv',
    ],
    'assets': {
        'point_of_sale.assets': [
            'payment_square_terminal/static/src/js/square_paymnet.js',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
