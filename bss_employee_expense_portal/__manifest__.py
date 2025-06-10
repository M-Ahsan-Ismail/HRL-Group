{
    'name': 'bss_employee_expense_portal',  # Module name
    'author': 'BSS',  # Author name
    'maintainer': 'M.Ahsan',
    'category': 'portal',  # Category displayed in info
    'website': 'https://www.bssuniversal.com',  # Website displayed in info
    'depends': ['base', 'hr_expense', 'website', 'portal'],  # Dependencies
    'installable': True,
    'application': True,
    "license": "LGPL-3",
    'data': [
        'views/employee_expense_controller_view.xml',
        'views/employee_expense_create_controller_view.xml',

    ], 'images': ['static/description/icon.png'],

}
