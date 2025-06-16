import base64

from odoo import http, fields, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.http import request


class FetchTimeOffController(http.Controller):
    @http.route('/all/time/off', type='http', auth='user', website=True, methods=['GET', 'POST'], csrf=True)
    def Retrieve_Time_Off_Data(self, **kwargs):
        all_types = []
        employee_id = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.uid)], limit=1)
        allocated_recs = request.env['hr.leave.allocation'].sudo().search(
            [('employee_id', '=', employee_id.id), ('state', 'in', ['validate'])])
        for x in allocated_recs:
            all_types.append({
                'name': x.holiday_status_id.name,
                'id': x.holiday_status_id.id,
                'no_of_days': x.number_of_days_display,
                'leave_type': x.holiday_status_id.leave_type,

            })
        unpaid_leave_id = request.env['hr.leave.type'].sudo().search([('name', 'ilike', 'Unpaid')], limit=1)
        if any(x['id'] == unpaid_leave_id.id for x in all_types):
            print('Already unpaid leave')
        else:
            all_types.append(
                {'id': unpaid_leave_id.id, 'name': unpaid_leave_id.name, 'leave_type': unpaid_leave_id.leave_type, })
        print(f'Leave: {all_types} ')

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

        # allocated and remaining and taken working here:------------------------------:
        leave_summary = {}
        allocated_records = request.env['hr.leave.allocation'].sudo().search(
            [('employee_id', '=', employee_id.id), ('state', 'in', ['validate'])])

        for rec in allocated_records:
            leave_type = rec.holiday_status_id.leave_type
            allocated_days = float(rec.number_of_days_display)
            if leave_type not in leave_summary:
                leave_summary[leave_type] = {'allocated': 0, 'taken': 0}
            leave_summary[leave_type]['allocated'] += allocated_days

        taken_leave_recs = request.env['hr.leave'].sudo().search(
            [('employee_id', '=', employee_id.id), ('state', 'in', ['validate', 'validate1'])]
        )
        for rec in taken_leave_recs:
            leave_type = rec.holiday_status_id.leave_type
            duration_str = str(rec.number_of_days_display)
            # Extract numeric value based on whether it's hours or days
            if 'hours' in duration_str.lower():
                taken_value = float(duration_str.split(' ')[0]) / 8  # Convert hours to days
            else:
                taken_value = float(duration_str.split(' ')[0])  # Direct days
            if leave_type not in leave_summary:
                leave_summary[leave_type] = {'allocated': 0, 'taken': 0}
            leave_summary[leave_type]['taken'] += taken_value

        leaves_info = [
            {
                'Leave_type': leave_type,
                'allocated': data['allocated'],
                'taken': data['taken'],
                'remaining': data['allocated'] - data['taken'],
            }
            for leave_type, data in leave_summary.items()
        ]
        print('Information: ', leaves_info)

        # Ended Here ------------------------------------------------------------------- :

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
            time_off_recs = request.env['hr.leave'].sudo().search(domain)
            # Inside Retrive_Time_Off_Data method, update the time_offs.append block
            if time_off_recs:
                for time in time_off_recs:
                    # Fetch existing attachments
                    attachments = time.medical_attachment_ids
                    attachment_data = []
                    for attachment in attachments:
                        attachment_data.append({
                            'id': attachment.id,
                            'name': attachment.name,
                            'url': f'/web/content/{attachment.id}?download=true',
                        })

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
                        'request_unit_half': time.request_unit_half,
                        'request_date_from_period': time.request_date_from_period,
                        'holiday_status_id': time.holiday_status_id.id,
                        'request_unit_hours': time.request_unit_hours,
                        'request_hour_from': time.request_hour_from,
                        'request_hour_to': time.request_hour_to,
                        'medical_attachments': attachment_data,  # Add attachment data
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

        return request.render('bss_leave_request_portal_v17.time_off_controller_portal_view_id', {
            'grouped_data': grouped_data,
            'group_by': group_by,
            'filter_by': filter_by,
            'sort_by': sort_by,
            'data': time_offs,
            'all_types': all_types,
            'leaves_info': leaves_info,
            'hour_options': hour_options,
        })
