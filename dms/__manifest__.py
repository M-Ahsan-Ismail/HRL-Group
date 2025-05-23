{
    'name': 'dms',  # Module name
    'author': 'M.Ahsan',  # Author name
    'maintainer': 'M.Rizwan',
    'category': 'BSS',  # Category displayed in info
    'website': 'https://www.bssuniversal.com',  # Website displayed in info
    'depends': ['base', 'stock', 'hr', 'DMS_Portal'],  # Dependencies
    'installable': True,
    'application': True,
    "license": "LGPL-3",
    'data': [
        'security/ir.model.access.csv',
        'report/agreement_dealer.xml',
        'views/inherit_res_partner.xml',
        'views/menu_items.xml',
        'views/dealer_agreement_view.xml',
        'views/inventory_form_inherit.xml',
        'views/dms_base_views.xml',
        'views/dms_config_views.xml',
    ],
    'images': ['static/description/icon.png'],

}
