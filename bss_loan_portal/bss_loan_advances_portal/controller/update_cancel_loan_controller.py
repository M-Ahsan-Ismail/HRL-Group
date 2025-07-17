from odoo import http, fields, _
from odoo.exceptions import ValidationError
from odoo.http import request


class UpdateLoanController(http.Controller):
    @http.route('/update/loan/request/<int:loan_id>', type='http', auth='user', csrf=True, methods=['POST', 'GET'])
    def update_loan_request(self, loan_id, **kwargs):
        loan_rec = request.env['hr.loan'].browse(loan_id)
        if loan_rec.exists() and loan_rec.state == 'draft':
            employee_id = request.env['hr.employee'].search(
                [('user_id', '=', request.env.uid), ('company_id', '=', request.env.user.company_id.id)], limit=1)
            if not employee_id:
                raise ValidationError('User Must Be Employee...!')
            company_id = employee_id.company_id

            if int(kwargs.get('no_of_emi', 0)) > 60:
                raise ValidationError('Maximum number of installments allowed is 60.')

            if request.httprequest.method == 'POST':
                vals = {
                    'loan_type': 'loan' if kwargs.get('loan_type') == 'loan' else 'advance',
                    'loan_amount': kwargs.get('loan_amount'),
                    'installment': int(kwargs.get('no_of_emi')),
                    'date': fields.Datetime.now(),
                    'company_id': company_id.id,
                }

                updated_loan_id = loan_rec.sudo().write(vals)
                print(f'Updated Loan ID: {updated_loan_id}')

                return request.redirect('/fetch/loans')


class CancelLoanController(http.Controller):
    @http.route('/cancel/loan/request/<int:loan_id>', type='http', auth='user', csrf=True, methods=['POST', 'GET'])
    def cancel_loan_request(self, loan_id):
        loan_rec = request.env['hr.loan'].browse(loan_id)
        print(f'Loan: {loan_rec} Hit')
        if loan_rec.exists() and loan_rec.state == 'draft':
            loan_rec.sudo().write({'state': 'cancel'})
            print(f'Loan: {loan_rec} Cancelled')

            return request.redirect('/fetch/loans')
