import base64
from odoo import http, fields, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta, time
from dateutil.relativedelta import relativedelta
from odoo.http import request


class CreateTimeOffController(http.Controller):
    @http.route('/create/time/off', type='http', auth='user', website=True, methods=['GET', 'POST'], csrf=True)
    def create_Time_Off_Data(self, **kwargs):
        # Fetch leave types for the employee
        all_types = []
        employee_id = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.uid)], limit=1)
        allocated_recs = request.env['hr.leave.allocation'].sudo().search(
            [('employee_id', '=', employee_id.id), ('state', 'in', ['validate'])])
        for x in allocated_recs:
            all_types.append({
                'name': x.holiday_status_id.name,
                'id': x.holiday_status_id.id,
                'type': x.holiday_status_id.leave_type,
            })

        # Add Unpaid leave type if not already present
        unpaid_leave_id = request.env['hr.leave.type'].sudo().search([('leave_type', '=', 'unpaid')], limit=1)
        if not unpaid_leave_id:
            unpaid_leave_id = request.env['hr.leave.type'].sudo().create({'leave_type': 'unpaid', 'name': 'unpaid'})

        if not any(x['id'] == unpaid_leave_id.id for x in all_types):
            all_types.append(
                {'id': unpaid_leave_id.id, 'name': unpaid_leave_id.name, 'type': unpaid_leave_id.leave_type})

        # Define hour options for the template
        hour_options = [
            ('0', '12:00 AM'), ('0.5', '12:30 AM'),
            ('1', '1:00 AM'), ('1.5', '1:30 AM'),
            ('2', '2:00 AM'), ('2.5', '2:30 AM'),
            ('3', '3:00 AM'), ('3.5', '3:30 AM'),
            ('4', '4:00 AM'), ('4.5', '4:30 AM'),
            ('5', '5:00 AM'), ('5.5', '5:30 AM'),
            ('6', '6:00 AM'), ('6.5', '6:30 AM'),
            ('7', '7:00 AM'), ('7.5', '7:30 AM'),
            ('8', '8:00 AM'), ('8.5', '8:30 AM'),
            ('9', '9:00 AM'), ('9.5', '9:30 AM'),
            ('10', '10:00 AM'), ('10.5', '10:30 AM'),
            ('11', '11:00 AM'), ('11.5', '11:30 AM'),
            ('12', '12:00 PM'), ('12.5', '12:30 PM'),
            ('13', '1:00 PM'), ('13.5', '1:30 PM'),
            ('14', '2:00 PM'), ('14.5', '2:30 PM'),
            ('15', '3:00 PM'), ('15.5', '3:30 PM'),
            ('16', '4:00 PM'), ('16.5', '4:30 PM'),
            ('17', '5:00 PM'), ('17.5', '5:30 PM'),
            ('18', '6:00 PM'), ('18.5', '6:30 PM'),
            ('19', '7:00 PM'), ('19.5', '7:30 PM'),
            ('20', '8:00 PM'), ('20.5', '8:30 PM'),
            ('21', '9:00 PM'), ('21.5', '9:30 PM'),
            ('22', '10:00 PM'), ('22.5', '10:30 PM'),
            ('23', '11:00 PM'), ('23.5', '11:30 PM')
        ]

        if request.httprequest.method == 'POST':
            if not employee_id:
                raise ValidationError(_('No employee record found for the current user.'))

            # Parse date fields (date-only input)
            from_date_str = kwargs.get('from_date')
            to_date_str = kwargs.get('to_date')
            if not from_date_str:
                raise ValidationError(_('From Date is required.'))
            from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date() if to_date_str else from_date

            # Validate dates
            current_date = datetime.now().date()
            if from_date < current_date:
                raise ValidationError(_('Start date cannot be in the past.'))
            if to_date < from_date:
                raise ValidationError(_('End date must be after start date.'))

            # Get form inputs
            request_unit_half = kwargs.get('request_unit_half') == 'on'
            request_unit_hours = kwargs.get('request_unit_hours') == 'on'
            half_morning_or_evening = kwargs.get('half_morning_or_evening')
            request_hour_from = kwargs.get('request_hour_from')
            request_hour_to = kwargs.get('request_hour_to')
            description = kwargs.get('description')
            time_off_type = int(kwargs.get('time_off_type'))
            department = employee_id.department_id.id

            # Default datetime values for full-day leaves
            request_date_from = datetime.combine(from_date, time(0, 0))
            request_date_to = datetime.combine(to_date, time(23, 59, 59))

            # Handle Half Day
            if request_unit_half:
                if not half_morning_or_evening:
                    raise ValidationError(_('Please select Morning or Afternoon for half-day leave.'))
                if half_morning_or_evening == 'am':
                    request_date_from = datetime.combine(from_date, time(0, 0))
                    request_date_to = datetime.combine(from_date, time(12, 0))
                else:  # 'pm'
                    request_date_from = datetime.combine(from_date, time(12, 0))
                    request_date_to = datetime.combine(from_date, time(23, 59, 59))
                to_date = from_date  # Ensure half-day is on a single day

            # Handle Custom Hours
            if request_unit_hours:
                if not request_hour_from or not request_hour_to:
                    raise ValidationError(_('From Hour and To Hour are required for custom hours.'))

                try:
                    # Convert string values to float for time calculations
                    hour_from_float = float(request_hour_from)
                    hour_to_float = float(request_hour_to)

                    if hour_to_float <= hour_from_float:
                        raise ValidationError(_('To Hour must be after From Hour.'))

                    # Convert float hours to time objects for datetime fields
                    from_hour = int(hour_from_float)
                    from_minute = int((hour_from_float - from_hour) * 60)
                    to_hour = int(hour_to_float)
                    to_minute = int((hour_to_float - to_hour) * 60)

                    request_date_from = datetime.combine(from_date, time(from_hour, from_minute))
                    # request_date_to = datetime.combine(from_date, time(to_hour, to_minute))
                    # to_date = from_date  # Custom hours are on a single day

                except (ValueError, TypeError):
                    raise ValidationError(_('Invalid hour selection.'))

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
                return [(6, 0, attachments)] if attachments else False

            # Prepare leave values
            leave_vals = {
                'employee_id': employee_id.id,
                'department_id': department,
                'name': description,
                'holiday_status_id': time_off_type,
                'request_date_from': request_date_from,
                'request_date_to': request_date_to,
                'medical_attachment_ids': create_attachments('attachment_file'),
                'request_unit_half': request_unit_half,
                'request_date_from_period': half_morning_or_evening if request_unit_half else False,
                'request_unit_hours': request_unit_hours,
            }

            # Set custom hours fields if applicable (keep as STRING values for Selection fields)
            if request_unit_hours and request_hour_from and request_hour_to:
                leave_vals['request_hour_from'] = request_hour_from  # Keep as string
                leave_vals['request_hour_to'] = request_hour_to      # Keep as string

            # Create the leave record
            request.env['hr.leave'].sudo().create(leave_vals)

            return request.redirect('/all/time/off')

        return request.render('bss_leave_request_portal_v17.time_off_create_form_template', {
            'all_types': all_types,
            'hour_options': hour_options
        })