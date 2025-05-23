{
    'name': 'hrl_leave_request_portal',  # Module name
    'author': 'M.Ahsan',  # Author name
    'maintainer': 'M.Rizwan',
    'category': 'BSS',  # Category displayed in info
    'website': 'https://www.bssuniversal.com',  # Website displayed in info
    'depends': ['base', 'hr_attendance', 'hr', 'hr_holidays', 'website', 'portal'],  # Dependencies
    'installable': True,
    'application': True,
    "license": "LGPL-3",
    'data': [
        # 'security/ir.model.access.csv',
        'views/time_off_form_inherit.xml',
        'views/time_off_controller_view.xml',
        'views/time_off_create_from_controller.xml',
    ], 'images': ['static/description/icon.png'],

}
