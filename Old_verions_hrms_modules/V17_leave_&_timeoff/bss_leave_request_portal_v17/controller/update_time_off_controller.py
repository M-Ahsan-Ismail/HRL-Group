import base64

from odoo import http, fields, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.http import request

from datetime import datetime, time


class UpdateTimeOffController(http.Controller):
    @http.route('/time/off/update/<int:leave_id>', type='http', auth='user', website=True, methods=['GET', 'POST'],
                csrf=True)
    def Update_Time_Off_Data(self, leave_id, **kwargs):
        leave = request.env['hr.leave'].browse(leave_id).exists()
        if not leave or leave.employee_id.user_id.id != request.env.uid:
            raise ValidationError('You do not have permission to update this leave request.')

        if request.httprequest.method == 'POST':
            # Extract form data
            description = kwargs.get('description')
            time_off_type = kwargs.get('time_off_type')
            start_date_raw = kwargs.get('start_date')
            end_date_raw = kwargs.get('end_date')
            request_unit_half = kwargs.get('request_unit_half') == 'on'
            request_unit_hours = kwargs.get('request_unit_hours') == 'on'
            half_morning_or_evening = kwargs.get('half_morning_or_evening')
            request_hour_from = kwargs.get('request_hour_from')  # Now from <select>
            request_hour_to = kwargs.get('request_hour_to')  # Now from <select>

            # Parse start date (required for all leave types)
            if not start_date_raw:
                raise ValidationError('Start Date is required.')
            start_date = datetime.strptime(start_date_raw, '%Y-%m-%d').date()

            # Determine end date based on leave type
            if request_unit_half or request_unit_hours:
                end_date = start_date  # Single-day leave
            else:
                # Full-day leave requires end date
                if not end_date_raw:
                    raise ValidationError('End Date is required for full-day leave.')
                end_date = datetime.strptime(end_date_raw, '%Y-%m-%d').date()

            if leave.state not in ['validate', 'validate1']:
                # Base values for all leave types
                leave_vals = {
                    'name': description,
                    'holiday_status_id': int(time_off_type),
                    'request_date_from': datetime.combine(start_date, time(0, 0)),
                    'request_date_to': datetime.combine(end_date, time(23, 59, 59)),  # End of day for full-day
                    'request_unit_half': request_unit_half,
                    'request_unit_hours': request_unit_hours,
                    'request_date_from_period': False,
                    'request_hour_from': False,
                    'request_hour_to': False,
                }

                if request_unit_half:
                    # Half-day: Set period and rely on Odoo’s computation
                    if not half_morning_or_evening:
                        raise ValidationError('Please specify morning or afternoon for half-day leave.')
                    leave_vals['request_date_from_period'] = half_morning_or_evening

                elif request_unit_hours:
                    # Custom hours: Use selection values directly
                    if not request_hour_from or not request_hour_to:
                        raise ValidationError('From Hour and To Hour are required for custom hours.')
                    try:
                        # Convert string values to float (e.g., '14' or '14.5')
                        hour_from = float(request_hour_from)
                        hour_to = float(request_hour_to)
                        if hour_to <= hour_from:
                            raise ValidationError('To Hour must be after From Hour.')
                        leave_vals['request_hour_from'] = request_hour_from  # Keep as string for Selection field
                        leave_vals['request_hour_to'] = request_hour_to  # Keep as string for Selection field
                    except ValueError:
                        raise ValidationError('Invalid hour selection.')

                # Attachment handling
                def create_attachments(field_name):
                    attachments = []
                    if field_name in request.httprequest.files:
                        files = request.httprequest.files.getlist(field_name)
                        for file in files:
                            if file and file.filename:
                                attachment = request.env['ir.attachment'].sudo().create({
                                    'name': file.filename,
                                    'datas': base64.b64encode(file.read()),
                                    'res_model': 'hr.leave',
                                    'res_field': field_name,
                                    'type': 'binary',
                                })
                                attachments.append(attachment.id)
                    return [(6, 0, attachments)] if attachments else [(6, 0, leave.medical_attachment_ids.ids)]

                new_leave_type = request.env['hr.leave.type'].browse(int(time_off_type))
                clear_attachments = new_leave_type.leave_type != 'sick'
                if clear_attachments:
                    leave_vals['medical_attachment_ids'] = [(5,)]
                else:
                    leave_vals['medical_attachment_ids'] = create_attachments('attachment_file')

                # Update the leave record
                leave.sudo().write(leave_vals)

            return request.redirect('/all/time/off')

        return request.redirect('/all/time/off')


class Cancel_Time_Off_Controller(http.Controller):
    @http.route('/time/off/cancel/<int:leave_id>', type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def Cancel_Time_Off_Data(self, leave_id, **kwargs):
        leave = request.env['hr.leave'].browse(leave_id).exists()
        if not leave or leave.employee_id.user_id.id != request.env.uid:
            raise ValidationError(_('You do not have permission to cancel this leave request.'))

        if leave.state not in ['validate']:  # Allow cancellation if not approved
            leave.sudo().write({
                'state': 'refuse',
            })
        return request.redirect('/all/time/off')
