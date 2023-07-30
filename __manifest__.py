# -*- coding: utf-8 -*-
{
    'name': "sita_payment_integration",

    'summary': """
       Integration With NBE for MPGS
       """,

    'description': """
        Long description of module's purpose
    """,

    'author': "SITA-EGYPT",
    'website': "https://www.sita-egypt.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','website'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/transaction_sequence.xml',
        'views/account_manager_view.xml',
        'views/transaction_view.xml',
        'views/client_order_view.xml',
        'views/home.xml',
        'views/transaction_actions.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable':True,
    'application':True,
    'images': ['static/description/icon.png'],
}
