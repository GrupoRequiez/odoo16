# -*- coding: utf-8 -*-
{
    'name': "MRP II",
    'summary': """
    """,
    'description': """
    """,
    'author': "Humanytek",
    'website': "http://www.humanytek.com",
    'category': 'Manufacturing',
    'version': '0.0.1',
    'license': "LGPL-3",
    'depends': ['mrp_workorder', 'sale', 'product_compromise','mrp_sale_info'],
    'data': [
        # security
        "security/ir.model.access.csv",
        # views
        'view/mrp_ii_view.xml',

    ],
    'demo': [
    ],
}
