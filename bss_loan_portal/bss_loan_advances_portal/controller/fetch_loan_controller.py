from odoo import http
from odoo.http import request
from datetime import datetime, timedelta


class FetchLoans(http.Controller):
    @http.route('/fetch/loans', type='http', auth="user", website=True, methods=['POST', 'GET'], csrf=False)
    def fetch_loans(self, **kwargs):
        today = datetime.today().date()
        employee_id = request.env['hr.employee'].search([('user_id', '=', request.env.uid),('company_id','=',request.env.user.company_id.id)], limit=1)

        if not employee_id:
            return request.render('bss_loan_advances_portal.loan_history_fetcher_id', {
                'Loans': [],
                'error': 'Employee not found'
            })

        company_id = employee_id.company_id
        Loans = []
        Loan_lines = []

        # Get filter parameters with proper defaults
        filter_by = kwargs.get('filter_by', 'all')
        group_by = kwargs.get('group_by', 'all')
        sort_by = kwargs.get('sort_by', 'all')
        search_query = kwargs.get('search', '').strip()

        # Base domain for all queries
        domain = [('employee_id', '=', employee_id.id),('employee_id.company_id', '=', company_id.id)]

        # Apply date filters - only if filter_by is not 'all'
        if filter_by and filter_by != 'all':
            if filter_by == 'today':
                domain.append(('date', '=', today))
            elif filter_by == 'last_7_days':
                domain.append(('date', '>=', today - timedelta(days=7)))
                domain.append(('date', '<=', today))
            elif filter_by == 'last_week':
                last_week_start = today - timedelta(days=today.weekday() + 7)
                last_week_end = last_week_start + timedelta(days=6)
                domain.append(('date', '>=', last_week_start))
                domain.append(('date', '<=', last_week_end))
            elif filter_by == 'this_month':
                month_start = today.replace(day=1)
                domain.append(('date', '>=', month_start))
                domain.append(('date', '<=', today))
            elif filter_by == 'last_30_days':
                domain.append(('date', '>=', today - timedelta(days=30)))
                domain.append(('date', '<=', today))
            elif filter_by == 'last_month':
                last_month = today.replace(day=1) - timedelta(days=1)
                last_month_start = last_month.replace(day=1)
                domain.append(('date', '>=', last_month_start))
                domain.append(('date', '<', today.replace(day=1)))
            elif filter_by == 'last_year':
                last_year_start = today.replace(year=today.year - 1, month=1, day=1)
                last_year_end = today.replace(year=today.year - 1, month=12, day=31)
                domain.append(('date', '>=', last_year_start))
                domain.append(('date', '<=', last_year_end))

        # Apply search filter
        if search_query:
            search_domain = [
                '|', '|', '|',
                ('name', 'ilike', search_query),
                ('employee_id.name', 'ilike', search_query),
                ('loan_type', 'ilike', search_query),
                ('state', 'ilike', search_query)
            ]
            domain = ['&'] + domain + search_domain

        # Determine order for database query
        # For grouped results, we'll sort in memory, so use a consistent order from DB
        if group_by != 'all':
            order = 'date desc'  # Default order for fetching, we'll sort in memory
        else:
            # For non-grouped results, apply sorting at database level
            if sort_by and sort_by != 'all':
                order = f"{sort_by} desc" if sort_by in ['date', 'loan_amount'] else 'date desc'
            else:
                order = 'date desc'

        # Fetch loans
        loan_ids = request.env['hr.loan'].search(domain, order=order)

        # Process loan data
        for rec in loan_ids:
            loan_lines = []
            for line in rec.loan_line_ids:
                loan_lines.append({
                    'next_installment_payment_date': line.date,
                    'amount': line.amount,
                    'paid': line.paid,
                })

            Loans.append({
                'loan_name': rec.name,
                'request_date': rec.date,
                'employee_name': rec.employee_id.name,
                'loan_type': rec.loan_type,
                'loan_amount': rec.loan_amount,
                'total_paid_amount': rec.total_paid_amount,
                'balance_amount': rec.loan_amount - rec.total_paid_amount,
                'state': rec.state,
                'id': rec.id,
                'installment': rec.installment,
                'remaining_installment': rec.installment - sum(1 for x in rec.loan_line_ids if x.paid == True),
                'state_label': dict(rec._fields['state'].selection).get(rec.state, rec.state),
                'loan_lines': loan_lines,
            })

        # Group loans if required
        grouped_loans = {}
        if group_by and group_by != 'all':
            for loan in Loans:
                if group_by == 'state':
                    key = loan['state_label']
                elif group_by == 'loan_type':
                    key = 'Loan' if loan['loan_type'] == 'loan' else 'Advance'
                elif group_by == 'month':
                    key = loan['request_date'].strftime('%B %Y') if loan['request_date'] else 'Unknown'
                else:
                    key = 'All'

                if key not in grouped_loans:
                    grouped_loans[key] = []
                grouped_loans[key].append(loan)

            # Apply sorting within each group - FIXED LOGIC
            if sort_by and sort_by != 'all':
                for group_key in grouped_loans:
                    if sort_by == 'date':
                        grouped_loans[group_key].sort(
                            key=lambda x: x['request_date'] or datetime.min.date(),
                            reverse=True
                        )
                    elif sort_by == 'loan_amount':
                        grouped_loans[group_key].sort(
                            key=lambda x: x['loan_amount'],
                            reverse=True
                        )
        else:
            # For non-grouped results, apply sorting if needed and not already applied at DB level
            if sort_by and sort_by != 'all':
                # If we didn't apply sorting at DB level, apply it here
                if sort_by not in ['date', 'loan_amount']:
                    # Handle any future sort options
                    pass
                else:
                    # This is redundant if we already sorted at DB level, but keeping for safety
                    if sort_by == 'date':
                        Loans.sort(key=lambda x: x['request_date'] or datetime.min.date(), reverse=True)
                    elif sort_by == 'loan_amount':
                        Loans.sort(key=lambda x: x['loan_amount'], reverse=True)

        # Get filter options for template
        filter_options = [
            ('today', 'Today'),
            ('last_7_days', 'Last 7 Days'),
            ('last_week', 'Last Week'),
            ('this_month', 'This Month'),
            ('last_30_days', 'Last 30 Days'),
            ('last_month', 'Last Month'),
            ('last_year', 'Last Year'),
        ]

        group_options = [
            ('state', 'State'),
            ('loan_type', 'Loan Type'),
            ('month', 'Month'),
        ]

        sort_options = [
            ('date', 'Date'),
            ('loan_amount', 'Amount'),
        ]

        return request.render('bss_loan_advances_portal.loan_history_fetcher_id', {
            'Loans': Loans,
            'Loan_lines': Loan_lines,
            'grouped_loans': grouped_loans,
            'filter_by': filter_by,
            'group_by': group_by,
            'search_query': search_query,
            'sort_by': sort_by,
            'filter_options': filter_options,
            'group_options': group_options,
            'sort_options': sort_options,
            'total_loans': len(Loans),
            'employee_name': employee_id.name,
        })
#
# class FetchLoans(http.Controller):
#     @http.route('/fetch/loans', type='http', auth="user", website=True, methods=['POST', 'GET'], csrf=False)
#     def fetch_loans(self, **kwargs):
#         today = datetime.today().date()
#         employee_id = request.env['hr.employee'].search([('user_id', '=', request.env.uid)], limit=1)
#
#         if not employee_id:
#             return request.render('bss_loan_advances_portal.loan_history_fetcher_id', {
#                 'Loans': [],
#                 'error': 'Employee not found'
#             })
#
#         company_id = employee_id.company_id
#         Loans = []
#         Loan_lines = []
#
#         # Get filter parameters with proper defaults
#         filter_by = kwargs.get('filter_by', 'all')
#         group_by = kwargs.get('group_by', 'all')
#         sort_by = kwargs.get('sort_by', 'all')
#         search_query = kwargs.get('search', '').strip()
#
#         # Base domain for all queries
#         domain = [('employee_id', '=', employee_id.id)]
#
#         # Apply date filters - only if filter_by is not 'all'
#         if filter_by and filter_by != 'all':
#             if filter_by == 'today':
#                 domain.append(('date', '=', today))
#             elif filter_by == 'last_7_days':
#                 domain.append(('date', '>=', today - timedelta(days=7)))
#                 domain.append(('date', '<=', today))
#             elif filter_by == 'last_week':
#                 last_week_start = today - timedelta(days=today.weekday() + 7)
#                 last_week_end = last_week_start + timedelta(days=6)
#                 domain.append(('date', '>=', last_week_start))
#                 domain.append(('date', '<=', last_week_end))
#             elif filter_by == 'this_month':
#                 month_start = today.replace(day=1)
#                 domain.append(('date', '>=', month_start))
#                 domain.append(('date', '<=', today))
#             elif filter_by == 'last_30_days':
#                 domain.append(('date', '>=', today - timedelta(days=30)))
#                 domain.append(('date', '<=', today))
#             elif filter_by == 'last_month':
#                 last_month = today.replace(day=1) - timedelta(days=1)
#                 last_month_start = last_month.replace(day=1)
#                 domain.append(('date', '>=', last_month_start))
#                 domain.append(('date', '<', today.replace(day=1)))
#             elif filter_by == 'last_year':
#                 last_year_start = today.replace(year=today.year - 1, month=1, day=1)
#                 last_year_end = today.replace(year=today.year - 1, month=12, day=31)
#                 domain.append(('date', '>=', last_year_start))
#                 domain.append(('date', '<=', last_year_end))
#
#         # Apply search filter
#         if search_query:
#             search_domain = [
#                 '|', '|', '|',
#                 ('name', 'ilike', search_query),
#                 ('employee_id.name', 'ilike', search_query),
#                 ('loan_type', 'ilike', search_query),
#                 ('state', 'ilike', search_query)
#             ]
#             domain = ['&'] + domain + search_domain
#
#         # Apply sorting
#         order = f"{sort_by} desc" if sort_by in ['date', 'loan_amount'] else 'date desc'
#
#         # Fetch loans
#         loan_ids = request.env['hr.loan'].search(domain, order=order)
#
#         # Process loan data
#         for rec in loan_ids:
#             loan_lines = []
#             for line in rec.loan_line_ids:
#                 loan_lines.append({
#                     'next_installment_payment_date': line.date,
#                     'amount': line.amount,
#                     'paid': line.paid,
#                 })
#
#             Loans.append({
#                 'loan_name': rec.name,
#                 'request_date': rec.date,
#                 'employee_name': rec.employee_id.name,
#                 'loan_type': rec.loan_type,
#                 'loan_amount': rec.loan_amount,
#                 'total_paid_amount': rec.total_paid_amount,
#                 'balance_amount': rec.loan_amount - rec.total_paid_amount,
#                 'state': rec.state,
#                 'id': rec.id,
#                 'installment': rec.installment,
#                 'remaining_installment' : rec.installment - sum(1 for x in rec.loan_line_ids if x.paid == True) ,
#                 'state_label': dict(rec._fields['state'].selection).get(rec.state, rec.state),
#                 'loan_lines': loan_lines,  # ✅ Attach here
#             })
#
#         # Group loans if required
#         grouped_loans = {}
#         if group_by and group_by != 'all':
#             for loan in Loans:
#                 if group_by == 'state':
#                     key = loan['state_label']
#                 elif group_by == 'loan_type':
#                     # Fix: Use consistent, user-friendly labels
#                     key = 'Loan' if loan['loan_type'] == 'loan' else 'Advance'
#                 elif group_by == 'month':
#                     key = loan['request_date'].strftime('%B %Y') if loan['request_date'] else 'Unknown'
#                 else:
#                     key = 'All'
#
#                 if key not in grouped_loans:
#                     grouped_loans[key] = []
#                 grouped_loans[key].append(loan)
#
#         # Get filter options for template
#         filter_options = [
#             ('today', 'Today'),
#             ('last_7_days', 'Last 7 Days'),
#             ('last_week', 'Last Week'),
#             ('this_month', 'This Month'),
#             ('last_30_days', 'Last 30 Days'),
#             ('last_month', 'Last Month'),
#             ('last_year', 'Last Year'),
#         ]
#
#         group_options = [
#             ('state', 'State'),
#             ('loan_type', 'Loan Type'),
#             ('month', 'Month'),
#         ]
#
#         sort_options = [
#             ('date', 'Date'),
#             ('loan_amount', 'Amount'),
#         ]
#
#         return request.render('bss_loan_advances_portal.loan_history_fetcher_id', {
#             'Loans': Loans,
#             'Loan_lines': Loan_lines,
#             'grouped_loans': grouped_loans,
#             'filter_by': filter_by,
#             'group_by': group_by,
#             'search_query': search_query,
#             'sort_by': sort_by,
#             'filter_options': filter_options,
#             'group_options': group_options,
#             'sort_options': sort_options,
#             'total_loans': len(Loans),
#             'employee_name': employee_id.name,
#         })
