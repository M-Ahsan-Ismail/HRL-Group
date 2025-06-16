{
    'name': 'bss_leave_request_portal_v16',  # Module name
    'author': 'BSS',  # Author name
    'maintainer': 'M.Ahsan',
    'category': 'portal',  # Category displayed in info
    'website': 'https://www.bssuniversal.com',  # Website displayed in info
    'depends': ['base', 'hr_attendance', 'hr', 'hr_holidays', 'website', 'portal'],  # Dependencies
    'installable': True,
    'application': True,
    "license": "LGPL-3",
    'version': '17.0.1.0',
    'data': [
        # 'security/ir.model.access.csv',
        # 'security/security.xml',
        'views/time_off_form_inherit.xml',
        'views/time_off_controller_view.xml',
        'views/time_off_create_from_controller.xml',
    ], 'images': ['static/description/icon.png'],

}
