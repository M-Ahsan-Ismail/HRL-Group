import base64

from odoo import http, fields, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.http import request


class TimeOffController(http.Controller):
    @http.route('/all/time/off', type='http', auth='user', website=True, methods=['GET', 'POST'], csrf=True)
    def Retrive_Time_Off_Data(self, **kwargs):
        all_types = []
        employee_id = request.env['hr.employee'].search([('user_id', '=', request.env.uid)], limit=1)
        allocated_recs = request.env['hr.leave.allocation'].search([('employee_id', '=', employee_id.id)])
        for x in allocated_recs:
            all_types.append({
                'name': x.holiday_status_id.name,
                'id': x.holiday_status_id.id,
            })
        unpaid_leave_id = request.env['hr.leave.type'].search([('name', 'ilike', 'Unpaid')], limit=1)
        if any(x['id'] == unpaid_leave_id.id for x in all_types):
            print('Already unpaid leave')
        else:
            all_types.append({'id': unpaid_leave_id.id, 'name': unpaid_leave_id.name})
        print(f'Leave: {all_types} ')

        env_user = request.env.uid
        time_offs = []
        grouped_data = {}
        today = datetime.now().date()

        # Get filter, sort, and group parameters with "None" as default
        filter_by = kwargs.get('filter_by', '')
        sort_by = kwargs.get('sort_by', '')  # Default to no sort
        group_by = kwargs.get('group_by', 'none')

        if env_user:
            # Base domain for time off records
            domain = [('employee_id.user_id', '=', env_user)]

            # Apply date filter based on filter_by
            if filter_by == 'last_week':
                last_week_start = today - timedelta(days=today.weekday() + 7)
                last_week_end = last_week_start + timedelta(days=6)
                domain.append(('request_date_from', '>=', last_week_start))
                domain.append(('request_date_from', '<=', last_week_end))
            elif filter_by == 'last_month':
                last_month = today.replace(day=1) - timedelta(days=1)
                last_month_start = last_month.replace(day=1)
                domain.append(('request_date_from', '>=', last_month_start))
                domain.append(('request_date_from', '<', today.replace(day=1)))
            elif filter_by == 'last_year':
                last_year_start = today.replace(year=today.year - 1, month=1, day=1)
                last_year_end = today.replace(year=today.year - 1, month=12, day=31)
                domain.append(('request_date_from', '>=', last_year_start))
                domain.append(('request_date_from', '<=', last_year_end))
            # Empty filter_by means no filtering (equivalent to "All")

            # Fetch time off records
            time_off_recs = request.env['hr.leave'].search(domain)

            if time_off_recs:
                for time in time_off_recs:
                    time_offs.append({
                        'employee_name': time.employee_id.name,
                        'type': time.holiday_status_id.name,
                        'description': time.name,
                        'request_date_from': time.request_date_from.strftime(
                            '%m/%d/%Y ') if time.request_date_from else '',
                        'request_date_to': time.request_date_to.strftime('%m/%d/%Y ') if time.request_date_to else '',
                        'duration': time.duration_display,
                        'id': time.id,
                        'state': time.state,
                        'request_date_from_raw': time.request_date_from,
                        'request_date_to_raw': time.request_date_to,
                    })

            # Sort the records only if sort_by is specified
            if sort_by == 'request_date_from':
                time_offs.sort(key=lambda x: x['request_date_from_raw'] or datetime.min.date(), reverse=True)
            elif sort_by == 'request_date_to':
                time_offs.sort(key=lambda x: x['request_date_to_raw'] or datetime.min.date(), reverse=True)
            elif sort_by == 'duration':
                def duration_to_days(dur):
                    if not dur:
                        return 0
                    if 'days' in dur:
                        return float(dur.split()[0])
                    elif 'hours' in dur:
                        parts = dur.split()[0].split(':')
                        if len(parts) == 2:
                            hours = float(parts[0])
                            minutes = float(parts[1]) / 60
                            total_hours = hours + minutes
                            return total_hours / 8  # Convert hours to days (8-hour workday)
                    return 0

                time_offs.sort(key=lambda x: duration_to_days(x['duration']), reverse=True)

            # Group the records
            if group_by != 'none':
                for time_off in time_offs:
                    key = time_off[group_by] if group_by in time_off else 'Unknown'
                    if key not in grouped_data:
                        grouped_data[key] = []
                    grouped_data[key].append(time_off)
            else:
                grouped_data = {'none': time_offs}

        elif not env_user:
            raise ValidationError(_('Please login to access this page'))

        return request.render('hrl_leave_request_portal.time_off_controller_portal_view_id', {
            'grouped_data': grouped_data,
            'group_by': group_by,
            'filter_by': filter_by,
            'sort_by': sort_by,
            'data': time_offs,
            'all_types': all_types,
        })

    @http.route('/time/off/update/<int:leave_id>', type='http', auth='user', website=True, methods=['GET', 'POST'],
                csrf=True)
    def Update_Time_Off_Data(self, leave_id, **kwargs):
        leave = request.env['hr.leave'].browse(leave_id).exists()
        if not leave or leave.employee_id.user_id.id != request.env.uid:
            raise ValidationError(_('You do not have permission to update this leave request.'))

        if request.httprequest.method == 'POST':
            description = kwargs.get('description')
            time_off_type = kwargs.get('time_off_type')
            start_date_raw = kwargs.get('start_date')
            end_date_raw = kwargs.get('end_date')

            start_date = datetime.strptime(start_date_raw, '%Y-%m-%dT%H:%M') if start_date_raw else None
            end_date = datetime.strptime(end_date_raw, '%Y-%m-%dT%H:%M') if end_date_raw else None

            if leave.state not in ['validate']:  # Allow updates if not approved
                leave.write({
                    'name': description,
                    'holiday_status_id': int(time_off_type),
                    'request_date_from': start_date,
                    'request_date_to': end_date,
                })
            return request.redirect('/all/time/off')

    @http.route('/time/off/cancel/<int:leave_id>', type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def Cancel_Time_Off_Data(self, leave_id, **kwargs):
        leave = request.env['hr.leave'].browse(leave_id).exists()
        if not leave or leave.employee_id.user_id.id != request.env.uid:
            raise ValidationError(_('You do not have permission to cancel this leave request.'))

        if leave.state not in ['validate']:  # Allow cancellation if not approved
            leave.write({
                'state': 'refuse',
            })
        return request.redirect('/all/time/off')

    @http.route('/create/time/off', type='http', auth='user', website=True, methods=['GET', 'POST'], csrf=True)
    def create_Time_Off_Data(self, **kwargs):
        all_types = []
        employee_id = request.env['hr.employee'].search([('user_id', '=', request.env.uid)], limit=1)
        allocated_recs = request.env['hr.leave.allocation'].search([('employee_id', '=', employee_id.id)])
        for x in allocated_recs:
            all_types.append({
                'name': x.holiday_status_id.name,
                'id': x.holiday_status_id.id,
                'type': x.holiday_status_id.leave_type,
            })
        unpaid_leave_id = request.env['hr.leave.type'].search([('name', 'ilike', 'Unpaid')], limit=1)
        if any(x['id'] == unpaid_leave_id.id for x in all_types):
            print('Already unpaid leave')
        else:
            all_types.append({'id': unpaid_leave_id.id, 'name': unpaid_leave_id.name})
        print(f'Leave: {all_types} ')

        if request.httprequest.method == 'POST':

            employee_id = request.env['hr.employee'].search([('user_id', '=', request.env.uid)], limit=1)
            if not employee_id:
                raise ValidationError(_('No employee record found for the current user.'))

            from_date = datetime.strptime(kwargs.get('from_date'), '%Y-%m-%dT%H:%M') if kwargs.get(
                'from_date') else None
            to_date = datetime.strptime(kwargs.get('to_date'), '%Y-%m-%dT%H:%M') if kwargs.get('to_date') else None
            if to_date < from_date:
                raise ValidationError(_('End Date Must Be After Start Date.'))

            if from_date < datetime.today():
                raise ValidationError(_('Start date cannot be in past.'))

            department = employee_id.department_id.id
            time_off_type = int(kwargs.get('time_off_type'))
            description = kwargs.get('description')

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

            request.env['hr.leave'].create({
                'employee_id': employee_id.id,
                'department_id': department,
                'name': description,
                'holiday_status_id': time_off_type,
                'request_date_from': from_date,
                'request_date_to': to_date,
                'medical_attachment_ids': create_attachments('attachment_file'),
            })
            return request.redirect('/all/time/off')

        return request.render('hrl_leave_request_portal.time_off_create_form_template', {'all_types': all_types})
