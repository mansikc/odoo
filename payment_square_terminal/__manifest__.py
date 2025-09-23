{
    "name": "POS Square Terminal Integration",
    "version": "1.0",
    "summary": "Add Square Terminal as a POS Terminal provider and send terminal checkouts",
    "category": "Point of Sale",
    "author": "You",
    "depends": ["point_of_sale", "payment"],
    "data": [
        "views/pos_square_views.xml",
        # "data/pos_square_data.xml",  # optional: precreate payment methods
    ],
    "installable": True,
    "application": False,
}
