{
    "name": "Square Payment Terminal",
    "version": "19.0.1.0.0",
    "summary": "Integration of Square Terminal with Odoo 18 Payment Providers and POS",
    "category": "Accounting/Payment Providers",
    "author": "Your Company",
    "website": "https://yourcompany.com",
    "depends": ["point_of_sale", "payment"],
    "data": [
        "security/ir.model.access.csv",
        "views/square_views.xml",
        "views/assets.xml", // asset
       	'data/payment_method_data.xml', 
    	'data/payment_provider_data.xml'
    ],
    "assets": {
        "point_of_sale.assets": [
            "payment_square_terminal/static/src/js/square_payment.js"
        ]
    },
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
