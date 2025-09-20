{
    "name": "Square Payment Terminal",
    "version": "18.0.1.0.0",
    "summary": "Integration of Square Terminal with Odoo 18 Payment Providers and POS",
    "category": "Accounting/Payment Providers",
    "author": "Your Company",
    "website": "https://yourcompany.com",
    "depends": ["point_of_sale", "payment"],
    "data": [
        "security/ir.model.access.csv",
        "views/square_views.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
