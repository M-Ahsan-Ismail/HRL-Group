{
    'name': 'bss_attendance_portal_v17',  # Module name
    'author': 'BSS',  # Author name
    'maintainer': 'M.Ahsan',
    'category': 'portal',  # Category displayed in info
    'website': 'https://www.bssuniversal.com',  # Website displayed in info
    'depends': ['base', 'web', 'hr_attendance', 'hr', 'hr_holidays', 'website', 'portal'],  # Dependencies
    'installable': True,
    'application': True,
    "license": "LGPL-3",
    'data': [
        # 'security/ir.model.access.csv',
        'views/attendance_history_fetcher_controller_view.xml',

    ], 'images': ['static/description/icon.png'],

}
