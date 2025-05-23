{
    'name': 'Empty',  # Module name
    'author': 'M.Ahsan',  # Author name
    'maintainer': 'M.Rizwan',
    'category': 'BSS',  # Category displayed in info
    'website': 'https://www.bssuniversal.com',  # Website displayed in info
    'depends': ['base', 'hr', 'portal', 'website'],  # Dependencies
    'installable': True,
    'application': True,
    "license": "LGPL-3",
    'data': [
        'security/ir.model.access.csv',
        'views/menuitems_view.xml',
        'views/employee_grievance.xml',
        'views/employee_grievance_portal_view.xml',
        'views/track_grievance_status_portal.xml',

    ], 'images': ['static/description/icon.png'],

}
