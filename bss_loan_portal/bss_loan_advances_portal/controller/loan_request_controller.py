from odoo import http, fields
from odoo.exceptions import ValidationError
from odoo.http import request


class LoanRequestController(http.Controller):
    @http.route('/loan/request', type='http', auth="user", website=True, csrf=True, methods=['POST', 'GET'])
    def loan_request(self, **kwargs):
        employee_id = request.env['hr.employee'].search([('user_id', '=', request.env.uid),('company_id','=',request.env.user.company_id.id)], limit=1)
        if not employee_id:
            raise ValidationError('User Must Be Employee...!')
        company_id = employee_id.company_id
        department_name = employee_id.department_id.name

        if int(kwargs.get('no_of_emi', 0)) > 60:
            raise ValidationError('The maximum number of installments allowed is 60.')

        if request.httprequest.method == 'POST':
            vals = {
                'loan_type': 'loan' if kwargs.get('loan_type') == 'loan' else 'advance',
                'loan_amount': kwargs.get('loan_amount'),
                'installment': int(kwargs.get('no_of_emi')),
                'date': fields.Datetime.now(),
                'company_id': company_id.id,
            }

            loan_id = request.env['hr.loan'].create(vals)
            print(f'Loan ID: {loan_id.name}')

            return request.redirect('/fetch/loans')

        return request.render('bss_loan_advances_portal.post_hr_loan_request_id',
                              {'department_name': department_name,
                               'employee_name': employee_id.name})
