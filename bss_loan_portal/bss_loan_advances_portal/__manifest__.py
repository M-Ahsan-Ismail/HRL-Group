{
    'name': 'bss_loan_advances_portal',  # Module name
    'author': 'BSS',  # Author name
    'maintainer': 'M.Ahsan Ismail',
    'category': 'portal',  # Category displayed in info
    'website': 'https://www.bssuniversal.com',  # Website displayed in info
    'depends': ['base', 'hr', 'ent_loan_accounting', 'ent_ohrms_loan', 'portal', 'website'],  # Dependencies
    'installable': True,
    'application': True,
    "license": "LGPL-3",
    'data': [
        # 'security/ir.model.access.csv',
        'views/fetch_loan_controller_view.xml',
        'views/loan_request_controller_view.xml',

    ], 'images': ['static/description/icon.png'],

}
