{
    'name': 'DMS_Portal',  # Module name
    'author': 'M.Ahsan',  # Author name
    'maintainer': 'M.Rizwan',
    'category': 'BSS',  # Category displayed in info
    'website': 'https://www.bssuniversal.com',  # Website displayed in info
    'depends': ['base', 'portal', 'website','hr','sale','crm'],  # Dependencies
    'installable': True,
    'application': True,
    "license": "LGPL-3",
    'data': [
        'security/ir.model.access.csv',
        'views/dms_portal_view.xml',
        'views/dms_customer_portal.xml',
        'views/dealer_dashboard_portal.xml',
        'views/model_views.xml',

    ], 'images': ['static/description/icon.png'],

}
