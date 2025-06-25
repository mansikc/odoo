{
    'name': 'Square Terminal POS Payment',
    'version': '1.0',
    'category': 'Point of Sale',
    'summary': 'Integration with Square Terminal for POS',
    'depends': ['point_of_sale'],
    'data': [
        'views/pos_square_template.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'square_terminal_pos/static/src/js/square_payment.js',
        ],
    },
    'installable': True,
    'application': False,
}
