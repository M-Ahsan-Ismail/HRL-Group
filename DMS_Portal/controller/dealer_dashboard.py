from odoo import http, fields
from odoo.http import request
from dateutil.relativedelta import relativedelta

class DealerDashBoard(http.Controller):
    @http.route('/dealer/dashboard', type='http', auth="user", website=True, methods=['GET'])
    def dealer_dashboard(self, **kwargs):
        dealership_applications = []
        approved_applications = []
        pending_applications = []
        all_dealers = []
        so_list = []
        opportunity_list = []
        res_users = request.env['res.users'].sudo().search_read([], ['id', 'name'])
        request_type = kwargs.get('request_type', 'dealer_applications')
        selected_month = None
        fetch_attempted = False  # Track if a fetch was attempted

        # Dealer Applications Logic
        if request_type in ['dealer_applications', 'approve_applications', 'waiting_applications', 'all_dealer_applications']:
            fetch_attempted = True  # Mark that a fetch was attempted when the endpoint is called

            require_month = kwargs.get('require_month')
            if require_month and request_type != 'all_dealer_applications':
                try:
                    # Ensure require_month is in YYYY-MM-DD format
                    if len(require_month) == 7:  # e.g., "2025-05" from user tampering or old logic
                        require_date = fields.Date.from_string(require_month + '-01')
                    else:
                        require_date = fields.Date.from_string(require_month)
                    selected_month = require_date.strftime("%B %Y")
                    month_start = require_date
                    month_end = require_date + relativedelta(months=1, days=-1)

                    if request_type == 'dealer_applications':
                        dealer_recs = request.env['dms.portal'].with_context(active_test=False).search(
                            [('request_month', '>=', month_start), ('request_month', '<=', month_end)])
                        for x in dealer_recs:
                            dealer_image = x.image_1920
                            if dealer_image and isinstance(dealer_image, bytes):
                                dealer_image = dealer_image.decode('utf-8')
                            elif not dealer_image:
                                dealer_image = None
                            dealership_applications.append({
                                'Application_ID': x.id,
                                'Applicant_Name': f"{x.first_name} {x.last_name}",
                                'Country': x.country_id.name,
                                'Image': dealer_image,
                                'company_name': x.company_name,
                                'business_type': x.business_type,
                            })

                    if request_type == 'approve_applications':
                        approved_recs = request.env['dms.portal'].with_context(active_test=False).search([
                            ('approved_month', '>=', month_start),
                            ('approved_month', '<=', month_end),
                            ('state', '=', 'approved')
                        ])
                        for x in approved_recs:
                            dealer_image = x.image_1920
                            if dealer_image and isinstance(dealer_image, bytes):
                                dealer_image = dealer_image.decode('utf-8')
                            elif not dealer_image:
                                dealer_image = None
                            approved_applications.append({
                                'Application_ID': x.id,
                                'Applicant_Name': f"{x.first_name} {x.last_name}",
                                'Country': x.country_id.name,
                                'Image': dealer_image,
                                'company_name': x.company_name,
                                'business_type': x.business_type,
                            })

                    if request_type == 'waiting_applications':
                        pending_recs = request.env['dms.portal'].with_context(active_test=False).search([
                            ('approved_month', '>=', month_start),
                            ('approved_month', '<=', month_end),
                            ('state', '=', 'under_review')
                        ])
                        for x in pending_recs:
                            dealer_image = x.image_1920
                            if dealer_image and isinstance(dealer_image, bytes):
                                dealer_image = dealer_image.decode('utf-8')
                            elif not dealer_image:
                                dealer_image = None
                            pending_applications.append({
                                'Application_ID': x.id,
                                'Applicant_Name': f"{x.first_name} {x.last_name}",
                                'Country': x.country_id.name,
                                'Image': dealer_image,
                                'company_name': x.company_name,
                                'business_type': x.business_type,
                            })

                except ValueError as e:
                    print(f"Date parsing error: {e}")
                    # Handle invalid date gracefully by skipping the filter
                    pass

            if request_type == 'all_dealer_applications':
                all_dealer_recs = request.env['dms.portal'].with_context(active_test=False).search(
                    [('state', '=', 'approved')])
                for x in all_dealer_recs:
                    dealer_image = x.image_1920
                    if dealer_image and isinstance(dealer_image, bytes):
                        dealer_image = dealer_image.decode('utf-8')
                    elif not dealer_image:
                        dealer_image = None
                    all_dealers.append({
                        'Application_ID': x.id,
                        'Applicant_Name': f"{x.first_name} {x.last_name}",
                        'Country': x.country_id.name,
                        'Image': dealer_image,
                        'company_name': x.company_name,
                        'business_type': x.business_type,
                    })

        # Sale Orders Logic
        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')
        env_user = kwargs.get('env_user')

        if start_date and end_date and env_user:
            try:
                start_date = fields.Date.from_string(start_date)
                end_date = fields.Date.from_string(end_date)
                env_user = int(env_user)

                sale_orders = request.env['sale.order'].sudo().search([
                    ('create_uid', '=', env_user),
                    ('date_order', '>=', start_date),
                    ('date_order', '<=', end_date)
                ])

                so_list = [{
                    'sale_order': so.name,
                    'state': so.state,
                    'total': so.amount_total,
                    'product': so.order_line.mapped('product_template_id.name')
                } for so in sale_orders]
            except (ValueError, TypeError):
                so_list = []

        # Opportunity Logic
        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')
        sales_person = kwargs.get('sales_person')

        if start_date and end_date and sales_person:
            try:
                start_date = fields.Date.from_string(start_date)
                end_date = fields.Date.from_string(end_date)
                sales_person = int(sales_person)

                opportunity_ids = request.env['crm.lead'].sudo().search([
                    ('user_id', '=', sales_person),
                    ('create_date', '>=', start_date),
                    ('create_date', '<=', end_date)
                ])

                opportunity_list = [{
                    'name': x.name,
                    'description': x.description or 'No description',
                    'expected_revenue': x.expected_revenue or 0.0,
                    'stage': x.stage_id.name or 'N/A',
                } for x in opportunity_ids]
            except (ValueError, TypeError):
                opportunity_list = []

        return request.render('DMS_Portal.dealer_ship_admin_dashboard', {
            'dealership_applications': dealership_applications or [],
            'approved_applications': approved_applications or [],
            'pending_applications': pending_applications or [],
            'all_dealers': all_dealers or [],
            'request_type': request_type,
            'selected_month': selected_month,
            'so_list': so_list,
            'res_users': res_users,
            'opportunity_list': opportunity_list,
            'kwargs': kwargs,
            'fetch_attempted': fetch_attempted,
        })