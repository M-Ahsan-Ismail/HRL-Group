import base64
from odoo import http, fields, _
from odoo.exceptions import ValidationError, UserError
from odoo.http import request
from datetime import date


class EmployeeGrievancePortal(http.Controller):
    @http.route('/employee/grievance/portal', type='http', auth="user", website=True, methods=['GET', 'POST'],
                csrf=True)
    def submit_grievance(self, **post):
        grievance_types = []

        obj = request.env['emp.grievance.type'].search([])
        if obj:
            for x in obj:
                grievance_types.append({'id': x.id, 'name': x.name})

        if post:
            employee = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.uid)], limit=1)
            if not employee:
                raise UserError("Error: No employee linked to this user.")

            complaint_type = post.get('complaint_type')
            description = post.get('description')
            if not complaint_type or not description:
                raise UserError(_('Please enter complaint type and description'))

            def create_attachments(field_name):
                attachments = []
                if field_name in request.httprequest.files:
                    files = request.httprequest.files.getlist(field_name)
                    for file in files:
                        if file and file.filename:
                            attachment = request.env['ir.attachment'].sudo().create({
                                'name': file.filename,
                                'datas': base64.b64encode(file.read()),
                                'res_model': 'emp.grievance',
                                'res_field': field_name,
                                'type': 'binary',
                            })
                            attachments.append(attachment.id)
                return [(6, 0, attachments)] if attachments else False

            emp_grievance_id = request.env['emp.grievance'].sudo().create({
                'complainant_id': employee.id,
                'complaint_type_id': complaint_type,
                'description': description,
                'attachment_ids': create_attachments('attachment_file'),
            })
            return f"""
                <div style="text-align:center; margin-top:50px;">
                    <h2 style="color:#28a745;">Grievance Submitted Successfully</h2>
                    <p>Your grievance <strong>{emp_grievance_id.name}</strong> has been recorded.</p>
                    <a href="/employee/grievance/portal" style="text-decoration:none; padding:10px 20px; background-color:#007bff; color:white; border-radius:5px;">
                        Submit Another
                    </a>
                </div>
            """

        return request.render('employee_grievance_management.employee_grievance_portal_form_id',
                              {'grievance_types': grievance_types})

    @http.route('/employee/grievance/portal/status', type='http', auth="user", website=True, methods=['GET'],
                csrf=False)
    def get_status(self, **post):
        grievance_data = []
        if post:
            grievance_id = post.get('grievance_id')
            if grievance_id and isinstance(grievance_id, str):
                grievance_rec = request.env['emp.grievance'].sudo().search([('name', '=', grievance_id)], limit=1)
                if grievance_rec:
                    complainant_image = grievance_rec.complainant_id.image_1920
                    if complainant_image and isinstance(complainant_image, bytes):
                        complainant_image = complainant_image.decode('utf-8')
                    elif not complainant_image:
                        complainant_image = None

                    for grievance in grievance_rec:
                        grievance_data.append({
                            'type': grievance.complaint_type_id.name,
                            'description': grievance.description,
                            'date': grievance.submission_date,
                            'name': grievance.name,
                            'status': grievance.status,
                            'image_1920': complainant_image,
                            'complainant_name': grievance.complainant_id.name,
                        })
                else:
                    return """
                        <div style="text-align:center; margin-top:50px;">
                                  <h2 style="color:#28a745;">Grievance Not Found</h2>
                                <p>The grievance ID <strong>{}</strong> does not exist.</p>
                                     <a href="/employee/grievance/portal/status" style="text-decoration:none; padding:10px 20px; background-color:#007bff; color:white; border-radius:5px;">
                                Check Another
                              </a>
                            </div>
                    """.format(grievance_id)
        return request.render('employee_grievance_management.grievance_status_tracking_id',
                              {'grievance_data': grievance_data})
