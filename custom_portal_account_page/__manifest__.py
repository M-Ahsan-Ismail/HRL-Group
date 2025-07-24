# -*- coding: utf-8 -*-
{
    'name': "Custom My Account Portal Page",
    'summary': """
        Enhances the Odoo portal account page with a modern layout and profile picture upload functionality.
    """,
    'description': """
                   
                           This module customizes the Odoo portal's "My Account" page by introducing a redesigned user interface
                                              and adding a feature to upload and change the user's profile picture. It improves user experience with
                                              a responsive design, form validation, and seamless integration with the Odoo portal framework.

                                              Key Features:
                                              - Modernized account page layout with Bootstrap styling
                                              - Profile picture upload with preview and validation
                                              - Support for editing user details (name, email, phone, city, country, state)
                                              - Responsive design for mobile and desktop compatibility
                                          """,
    'author': "Muhammad Ahsan Ismail",
    'website': "https://ahsan-developer.netlify.app",
    'category': 'Website/Portal',
    'version': '18.0.1.0.0',
    'license': 'LGPL-3',
    'depends': ['base', 'portal', 'website'],
    'data': [
        'views/templates.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
