# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################
{
    'name': 'POS : Square - Payment Terminal',
    'version': '19.0.0.0',
    'category': 'POS',
    "license": "OPL-1",
    'summary': 'POS : Square - Payment Terminal',
    'description': """

""",
    'author': 'Sitaram',
    'depends': ['point_of_sale'],
    "data": [
            "security/ir.model.access.csv",
            "views/pos_payment_method_view.xml",
            "views/pos_payment_view.xml"
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            "sr_pos_square_payment_terminal/static/src/js/payment_screen.js",
        ],
    },
    'website':'https://www.sitaramsolutions.in',
    'installable': True,
    'auto_install': False,
}
