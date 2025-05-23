import base64
from odoo import http, fields, _
from odoo.exceptions import ValidationError
from odoo.http import request
from datetime import date


class WarrantyPortal(http.Controller):
    @http.route('/warranty/check', type='http', auth='public', website=True, methods=['GET'])
    def warranty_check(self, **kwargs):
        remaining_value = 0
        data = []
        warranty_to_check = kwargs.get('warranty_id')
        if warranty_to_check and isinstance(warranty_to_check, str):
            res = request.env['sales.warranty'].sudo().with_context(active_test=False).search(
                [('name', '=', warranty_to_check)], limit=1)
            if res:
                for x in res:
                    remaining_months = x.remaining_months if x.remaining_months else 0
                    # calculating remaining warranty a percetnage from 1 to 100 scale.
                    if x.warranty_end_date and x.date_of_purchase:
                        today_date = fields.Date.today()
                        total_duration = (x.warranty_end_date - x.date_of_purchase).days
                        remaining_duration = (x.warranty_end_date - today_date).days
                        if total_duration > 0:
                            remaining_value = max(1, min(100, (remaining_duration * 100) // total_duration))
                        else:
                            remaining_value = 100

                    data.append({
                        'name': x.name,
                        'status': x.state,
                        'date_of_purchase': x.date_of_purchase,
                        'warranty_end_date': x.warranty_end_date,
                        'remaining_months': f'{remaining_months} Months',
                        'remaining_value': int(remaining_value),
                        'product_name': x.product_id.name,
                        'sale_order_number': x.sale_order_id.name,
                    })
                print(data)
            else:
                return """
                        <div style="text-align:center; margin-top:50px;">
                            <h2 style="color:#c00;">Warranty not found</h2>
                            <p>The requested tracking id <strong>{}</strong> does not exist or is invalid.</p>
                            <a href="/warranty/check" style="text-decoration:none; padding:10px 20px; background-color:#007bff; color:white; border-radius:5px;">
                                Go Back
                            </a>
                        </div>
                        """.format(warranty_to_check)
        return request.render('sales_warranty.WarrantyCheckTemplate', {'data': data})


class Warranty_Claim_Controller(http.Controller):
    @http.route('/warranty/claim/request', type='http', auth='public', website=True, methods=['GET', 'POST'])
    def warranty_claim_request(self, **kwargs):
        # Fetch products and customers for the form
        # products = []
        # res = request.env['product.template'].sudo().search([('warranty_eligibility', '=', True)])
        # for product in res:
        #     products.append({'product_name': product.name, 'product_id': product.id})
        #
        # customers = []
        # res = request.env['res.partner'].sudo().search([])
        # for customer in res:
        #     customers.append({'name': customer.name, 'id': customer.id})

        if kwargs:
            image_file = request.httprequest.files.get('image_1920')
            image_base64 = False
            if image_file:
                image_base64 = base64.b64encode(image_file.read())

            claim_date = kwargs.get('claim_date')
            if claim_date:
                claim_date = fields.Date.from_string(claim_date)
                if claim_date < date.today():
                    raise ValidationError(_("Claim date must not be in the past."))

            # # Handle multiple attachment files
            # def create_attachments(field_name):
            #     attachments = []
            #     if field_name in request.httprequest.files:
            #         files = request.httprequest.files.getlist(field_name)
            #         for file in files:
            #             if file and file.filename:
            #                 attachment = request.env['ir.attachment'].sudo().create({
            #                     'name': file.filename,
            #                     'datas': base64.b64encode(file.read()),
            #                     'res_model': 'warranty.claim',
            #                     'type': 'binary',
            #                     'mimetype': file.content_type,
            #                 })
            #                 attachments.append(attachment.id)
            #     return [(6, 0, attachments)] if attachments else False

            # Create warranty claim record with attachments
            warranty_number_id = request.env['sales.warranty'].search(
                [('name', '=', kwargs.get('warranty_number_id'))], limit=1
            ).id or False

            warranty_claim_vals = {
                # 'customer_id': int(kwargs.get('customer_id')) if kwargs.get('customer_id') else False,
                # 'product_id': int(kwargs.get('product_id')) if kwargs.get('product_id') else False,
                'image_1920': image_base64,
                'description': kwargs.get('description'),
                'claim_date': claim_date,
                'warranty_number_id': warranty_number_id,
                # 'attachment_ids': create_attachments('attachment_file'),  # Link attachments
            }
            warranty_claim_id = request.env['warranty.claim'].sudo().create(warranty_claim_vals)

            # Update Record According to Warranty Status
            if warranty_claim_id.warranty_number_id and warranty_claim_id.warranty_number_id.warranty_end_date > date.today():
                warranty_claim_id.write({
                    'state': 'draft',
                    'active': True,
                    'warranty_end_date': warranty_claim_id.warranty_number_id.warranty_end_date,
                    'customer_id': warranty_claim_id.warranty_number_id.customer_id.id,
                    'product_id': warranty_claim_id.warranty_number_id.product_id.id,
                })
            elif warranty_claim_id.warranty_number_id:
                warranty_claim_id.write({
                    'state': 'rejected',
                    'active': False,
                    'warranty_end_date': warranty_claim_id.warranty_number_id.warranty_end_date,
                    'customer_id': warranty_claim_id.warranty_number_id.customer_id.id,
                    'product_id': warranty_claim_id.warranty_number_id.product_id.id,
                })

            # Return success message
            return """
                <div style="margin:0; padding:0; background-color:#ffffff; height:100vh; display:flex; align-items:center; justify-content:center;">
                    <div style="
                        background: rgba(255, 255, 255, 0.15);
                        backdrop-filter: blur(12px);
                        -webkit-backdrop-filter: blur(12px);
                        border-radius: 16px;
                        padding: 40px 30px;
                        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
                        text-align: center;
                        max-width: 500px;
                        width: 90%;
                        color: #333;
                    ">
                        <h2 style="color: #1a73e8; margin-bottom: 15px;">Claim Request Submitted Successfully</h2>
                        <p style="color: #444; font-size: 16px; margin-bottom: 20px;">
                            Tracking ID <strong style="color:#111;">{}</strong>
                        </p>
                        <a href="/warranty/claim/request" style="
                            text-decoration: none;
                            padding: 10px 25px;
                            background-color: #1a73e8;
                            color: white;                                                                                   
                            border-radius: 8px;
                            font-weight: 500;
                            transition: all 0.3s ease;
                            display: inline-block;
                        " onmouseover="this.style.backgroundColor='#0c5ccd'" onmouseout="this.style.backgroundColor='#1a73e8'">
                            Go Back
                        </a>
                    </div>
                </div>
                """.format(warranty_claim_id.name)

        return request.render('sales_warranty.warranty_claim_portal_form', {
            # 'products': products,
            # 'customers': customers,
        })


class Warranty_Claim_Status(http.Controller):
    @http.route('/warranty/claim/status', type='http', auth='public', website=True, methods=['GET'])
    def warranty_claim_status(self, **kwargs):
        claim_status = []
        claim_warranty_id = kwargs.get('claim_warranty_id')
        if claim_warranty_id and isinstance(claim_warranty_id, str):
            res = request.env['warranty.claim'].sudo().with_context(active_test=False).search(
                [('name', '=', claim_warranty_id)])
            if res:
                for x in res:
                    dealer_image = x.customer_id.image_1920
                    if dealer_image and isinstance(dealer_image, bytes):
                        dealer_image = dealer_image.decode('utf-8')
                    elif not dealer_image:
                        dealer_image = None
                    claim_status.append({
                        'state': x.state,
                        'claim_id': x.name,
                        'rejection_reason': x.decision_note,
                        'warranty_end_date': x.warranty_end_date,
                        'customer_id': x.customer_id.name,
                        'product_id': x.product_id.name,
                        'claim_date': x.claim_date,
                        'warranty_number_name': x.warranty_number_id.name,
                        'image_1920': dealer_image,
                        'service_center': x.service_center,
                    })
            else:
                return """
                                <div style="margin:0; padding:0; background-color:#ffffff; height:100vh; display:flex; align-items:center; justify-content:center;">
                                    <div style="
                                        background: rgba(255, 255, 255, 0.15);
                                        backdrop-filter: blur(12px);
                                        -webkit-backdrop-filter: blur(12px);
                                        border-radius: 16px;
                                        padding: 40px 30px;
                                        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
                                        text-align: center;
                                        max-width: 500px;
                                        width: 90%;
                                        color: #333;
                                    ">
                                        <h2 style="color: #1a73e8; margin-bottom: 15px;">Tracking Id Is Invalid</h2>
                                        <a href="/warranty/claim/status" style="
                                            text-decoration: none;
                                            padding: 10px 25px;
                                            background-color: #1a73e8;
                                            color: white;                                                                                   
                                            border-radius: 8px;
                                            font-weight: 500;
                                            transition: all 0.3s ease;
                                            display: inline-block;
                                        " onmouseover="this.style.backgroundColor='#0c5ccd'" onmouseout="this.style.backgroundColor='#1a73e8'">
                                            Go Back
                                        </a>
                                    </div>
                                </div>
                                """.format(claim_warranty_id)

        return request.render('sales_warranty.warranty_claim_status_id', {'data': claim_status})
