import base64
from odoo import http, fields, _
from odoo.exceptions import ValidationError, UserError
from odoo.http import request
from odoo.tools.safe_eval import datetime
import logging

_logger = logging.getLogger(__name__)

class Fetch_Payslip(http.Controller):
    @http.route('/fetch/payslip', type='http', auth='user', website=True, methods=['GET'], csrf=False)
    def fetch_payslip(self, **kw):
        employee_id = request.env.user.employee_id.id

        payslip_list = []
        today_date = fields.Date.today()
        payslip_rec_ids = request.env['hr.payslip'].sudo().search(
            [('employee_id', '=', employee_id), ('date_from', '<=', today_date),('state','=','done')])
        for pay in payslip_rec_ids:
            payslip_list.append({
                'employee_id': pay.employee_id.id,
                'employee_name': pay.employee_id.name,
                'date_from': pay.date_from,
                'date_to': pay.date_to,
                'reference': pay.name,
                'payslip_id': pay.id,
                'number' : pay.number,
            })
        return request.render('bss_salary_slip_portal.payslip_fetcher_id', {'payslip_list': payslip_list})


    @http.route('/fetch/payslip/<int:payslip_id>', type='http', auth='user', website=True, methods=['GET'], csrf=False)
    def fetch_payslip_detail(self, payslip_id, **kw):
        employee_id = request.env.user.employee_id.id
        action = kw.get('action')

        payslip = request.env['hr.payslip'].sudo().search([
            ('id', '=', payslip_id),
            ('employee_id', '=', employee_id)
        ], limit=1)

        if not payslip:
            return request.redirect('/fetch/payslip')

        if action == 'download':
            try:
                available_reports = request.env['ir.actions.report'].search([]).mapped('report_name')
                _logger.info("Available report names: %s", available_reports)

                report = request.env['ir.actions.report'].search(
                    [('report_name', '=', 'hr_payroll.report_payslip_lang')],  # Updated report name
                    limit=1
                )
                if not report:
                    raise UserError("Payslip report not found. Available reports: %s" % available_reports)

                pdf_content = report._render_qweb_pdf(report.report_name, res_ids=[payslip.id])[0]
                if not pdf_content:
                    raise Exception("PDF content is empty")

                attachment = request.env['ir.attachment'].sudo().create({
                    'name': f'Payslip_{payslip.name or str(payslip.id)}.pdf',
                    'type': 'binary',
                    'datas': base64.b64encode(pdf_content),
                    'res_model': 'hr.payslip',
                    'res_id': payslip.id,
                    'mimetype': 'application/pdf',
                })

                return request.make_response(
                    base64.b64decode(attachment.datas),
                    headers=[
                        ('Content-Type', 'application/pdf'),
                        ('Content-Disposition', f'attachment; filename={attachment.name}'),
                    ]
                )
            except Exception as e:
                raise ValidationError(f"Error generating PDF: {str(e)}")

        payslip_data = {
            'payslip': payslip,
            'employee_name': payslip.employee_id.name,
            'date_from': payslip.date_from,
            'date_to': payslip.date_to,
            'reference': payslip.name,
            'payslip_id': payslip.id,
            'line_ids': payslip.line_ids,
        }
        return request.render('bss_salary_slip_portal.payslip_detail_id', payslip_data)