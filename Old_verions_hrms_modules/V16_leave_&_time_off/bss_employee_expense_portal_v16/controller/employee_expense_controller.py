from werkzeug.utils import redirect
from odoo import http, fields, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from odoo.http import request


class EmployeeExpenseController(http.Controller):
    @http.route('/view/employee/expense', type='http', auth="user", website=True, methods=['GET'], csrf=False)
    def get_employee_expense(self, **post):
        user_id = request.env.user.employee_id.id
        all_products = []
        all_expenses = []
        filter_expense = []
        today = datetime.now().date()

        product_recs = request.env['product.product'].search([])
        for product in product_recs:
            all_products.append({
                'name': product.name,
                'id': product.id,
            })

        # Fetch all expenses for the user
        expense_recs = request.env['hr.expense'].sudo().search([('employee_id', '=', user_id)])
        for expense in expense_recs:
            all_expenses.append({
                'name': expense.name,
                'product': expense.product_id.name,
                'expense_date': expense.date,
                'total_amount': expense.total_amount,
                'state': expense.state,
                'payment_mode': 'Company' if expense.payment_mode == 'company_account' else 'Employee',
                'id': expense.id,
            })
        print(f'Expense: {all_expenses}')

        filter_by = post.get('filter_by', '')
        group_by = post.get('group_by', 'none')
        grouped_data = {}

        if user_id:
            # Group the records
            if group_by != 'none':
                for group in all_expenses:
                    key = group[group_by] if group_by in group else 'Unknown'
                    if key not in grouped_data:
                        grouped_data[key] = []
                    grouped_data[key].append(group)
            else:
                grouped_data = {'none': all_expenses}
            print(f'Grouped data: {grouped_data}')
            domain = [('employee_id', '=', user_id)]

            if filter_by == 'last_week':
                last_week_start = today - timedelta(days=today.weekday() + 7)
                last_week_end = last_week_start + timedelta(days=6)
                domain.append(('date', '>=', last_week_start))
                domain.append(('date', '<=', last_week_end))
            elif filter_by == 'last_month':
                last_month = today.replace(day=1) - timedelta(days=1)
                last_month_start = last_month.replace(day=1)
                domain.append(('date', '>=', last_month_start))
                domain.append(('date', '<', today.replace(day=1)))
                print('Called')
            elif filter_by == 'last_year':
                last_year_start = today.replace(year=today.year - 1, month=1, day=1)
                last_year_end = today.replace(year=today.year - 1, month=12, day=31)
                domain.append(('date', '>=', last_year_start))
                domain.append(('date', '<=', last_year_end))

            filter_expense_recs = request.env['hr.expense'].search(domain)
            for expense in filter_expense_recs:
                filter_expense.append({
                    'name': expense.name,
                    'product': expense.product_id.name,
                    'expense_date': expense.date,
                    'total_amount': expense.total_amount,
                    'state': expense.state,
                    'payment_mode': 'Company' if expense.payment_mode == 'company_account' else 'Employee',
                    'id': expense.id,
                })
            print(f'Filter: {filter_expense_recs}')

        return request.render('bss_employee_expense_portal_v16.employee_expense_portal_id',
                              {'all_products': all_products,
                               'all_expenses': all_expenses,
                               'filter_expense': filter_expense,
                               'grouped_data': grouped_data,  # Pass grouped_data explicitly
                               'group_by': group_by,
                               'filter_by': filter_by,
                               })

    @http.route('/update/expense/<int:expense_id>', type='http', auth="user", website=True, methods=['GET', 'POST'],
                csrf=True)
    def http_update_employee_expense(self, expense_id, **post):
        expense = request.env['hr.expense'].browse(expense_id).exists()
        if not expense:
            raise ValidationError(_('Expense record does not exist or Invalid'))

        if expense.state in ['draft', 'reported']:
            update_vals = {
                'name': post.get('name'),
                'product_id': int(post.get('product')) if post.get('product') else None,
                'date': post.get('expense_date'),
                'total_amount': float(post.get('total_amount')) if post.get('total_amount') else 0.0,
                'payment_mode': post.get('payment_mode'),
            }
            print(f'Update: {update_vals}')
            expense.write(update_vals)

        return request.redirect('/view/employee/expense')

    @http.route('/create/expense', type='http', auth="user", website=True, methods=['GET', 'POST'], csrf=True)
    def http_create_expense(self, **post):
        user_id = request.env.user.employee_id.id
        al_categories = []
        category_recs = request.env['product.product'].search([])
        for rec in category_recs:
            al_categories.append({
                'name': rec.name,
                'id': rec.id,
            })

        if post:
            expense_date = fields.Date.from_string(post.get('expense_date'))
            category_id = int(post.get('category_id'))
            name_desc = post.get('description')
            amount = float(post.get('amount'))
            paid_by = post.get(
                'paid_by')  # selection field on model hr.expense: own_account: employee , company_account : company

            if not expense_date:
                raise ValidationError('Expense date is required')
            if not category_id:
                raise ValidationError('Category  is required')
            if not name_desc:
                raise ValidationError('Description is required')
            if not amount or amount < 0:
                raise ValidationError('Amount required and can not be in _ve')
            if not paid_by:
                raise ValidationError('Paid By is required')

            expense_id = request.env['hr.expense'].create({
                'employee_id': user_id,
                'name': name_desc,
                'date': expense_date,
                'product_id': category_id,
                'payment_mode': 'own_account' if post.get('paid_by') == 'Employee' else 'company_account',
                'total_amount': amount,
            })
            print(f'Expense ID: {expense_id}')

            return redirect('/view/employee/expense')

        return request.render('bss_employee_expense_portal_v16.employee__create_expense_controller_id',
                              {'al_categories': al_categories})
