{
    'name': 'bss_salary_slip_portal',  # Module name
    'author': 'Business Solutions & Services',  # Author name
    'maintainer': 'M.Ahsan Ismail',
    'category': 'BSS',  # Category displayed in info
    'website': 'https://www.bssuniversal.com',  # Website displayed in info
    'depends': ['base', 'hr_payroll', 'hr_payroll_account', 'website', 'portal'],  # Dependencies
    'installable': True,
    'application': True,
    "license": "LGPL-3",
    'data': [
        # 'security/ir.model.access.csv',
        'views/payslip_fatcher_controller_view.xml',

    ],
    'images': ['static/description/icon.png'],

}
