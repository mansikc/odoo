{
    'name': 'POS Square Terminal',
    'version': '1.0',
    'category': 'Point of Sale',
    'depends': ['point_of_sale'],
    'data': [
        'views/pos_payment_method_views.xml',
    ],
    'qweb': [
        'static/src/xml/pos_square_terminal.xml',
    ],
    'installable': True,
    'application': False,
}
