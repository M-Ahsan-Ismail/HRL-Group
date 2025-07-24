# -*- coding: utf-8 -*-
import base64

from odoo import http
from odoo.http import content_disposition, Controller, request, route
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.tools.mimetypes import guess_mimetype

File_Type = ['application/pdf', 'image/jpeg', 'image/png', 'image/gif']  # allowed file type


class CustomPortalTemplateRender(CustomerPortal):
    MANDATORY_BILLING_FIELDS = []
    OPTIONAL_BILLING_FIELDS = ["zipcode", "state_id", "vat", "company_name", "image_1920", "name", "email",
                               "phone", "city", "country_id"]

    _items_per_page = 20

    @route(['/my/account'], type='http', auth='user', website=True,methods=['POST','GET','PUT','DELETE','PATCH'])
    def account(self, redirect=None, **post):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        values.update({
            'error': {},
            'error_message': [],
        })

        if post and request.httprequest.method == 'POST':
            values = {key: post[key] for key in self.MANDATORY_BILLING_FIELDS}
            values.update({key: post[key] for key in self.OPTIONAL_BILLING_FIELDS if key in post})
            for field in set(['country_id', 'state_id']) & set(values.keys()):
                try:
                    values[field] = int(values[field])
                except:
                    values[field] = False
            values.update({'zip': values.pop('zipcode', '')})
            partner.sudo().write(values)
            if redirect:
                return request.redirect(redirect)
            return request.redirect('/my/home')
        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])
        industries = request.env['res.partner.industry'].sudo().search([])

        values.update({
            'partner': partner,
            'countries': countries,
            'states': states,
            'industries': industries,
            'has_check_vat': hasattr(request.env['res.partner'], 'check_vat'),
            'redirect': redirect,
            'page_name': 'my_details',

        })

        response = request.render("custom_portal_account_page.portal_my_details", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @http.route(['/change/profile/'], type='http', auth="user", methods=['POST'], csrf=False, website=True)
    def change_account_pic(self, **post):
        try:
            partner_id = request.env.user.partner_id
            if post.get('attachment', False):
                file = post.get('attachment')

                # Read the file content
                attachment = file.read()

                # Check if file is not empty
                if not attachment:
                    return request.redirect('/my/account?error=empty_file')

                # Encode to base64 first, then guess mimetype
                attachment_b64 = base64.b64encode(attachment)
                mimetype = guess_mimetype(attachment)

                # Check if mimetype is allowed
                if mimetype in File_Type:
                    partner_id.sudo().write({'image_1920': attachment_b64})
                    return request.redirect('/my/account?success=1')
                else:
                    return request.redirect('/my/account?error=invalid_file_type')
            else:
                return request.redirect('/my/account?error=no_file')

        except Exception as e:
            # Log the error for debugging
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error("Error uploading profile picture: %s", str(e))
            return request.redirect('/my/account?error=upload_failed')

        return request.redirect('/my/account')