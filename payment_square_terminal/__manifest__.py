{
    "name": "POS Square Terminal Integration (Krunal)",
    "version": "1.0",
    "category": "Point of Sale",
    "summary": "Integrate Square Terminal API with Odoo POS (Krunal)",
    "author": "Your Name",
    "depends": ["point_of_sale", "base"],
    "data": [
        "views/square_config_views.xml",
    ],
    "assets": {
        "point_of_sale.assets": [
            "pos_square_terminal/static/src/js/pos_square_payment.js",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}