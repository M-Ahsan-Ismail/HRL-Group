{
    'name': 'mrp_portal_dashboard',  # Module name
    'author': 'M.Ahsan Ismail',  # Author name
    'maintainer': 'M.Rizwan',
    'category': 'Manufacturing/Repair',  # Category displayed in info
    'website': 'https://ahsan-developer.ntelify.app',  # Website displayed in info
    'depends': ['base','mrp','mrp_workorder','website','portal'],  # Dependencies
    'installable': True,
    'application': True,
    "license": "LGPL-3",
    'data': [
        # 'security/ir.model.access.csv',
        'views/mrp_orders_dashboard_controller_views.xml',
        'views/mrp_work_orders_detail_views.xml',

    ],
    'images': ['static/description/icon.png'],

}
