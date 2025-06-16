import base64
from odoo import http, fields, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.http import request


class FetcherUserWise_Attendance_Records(http.Controller):
    @http.route(['/fetch/attendance', '/fetch/attendance/page/<int:page>'], type='http', auth='user', website=True,
                methods=['GET'], csrf=False)
    def fetch_attendance(self, page=1, **kwargs):
        user_id = request.env.user.employee_id.id
        attendance_data = []
        check_in = False
        check_out = False
        filter_by = False
        leave_count_list = 0
        worked_hours = 0
        today = datetime.now().date()

        # Base domain for attendance queries
        domain = [('employee_id', '=', user_id)]

        # Handle check_in and check_out parameters
        check_in_param = kwargs.get('check_in', '')
        check_out_param = kwargs.get('check_out', '')

        # Convert 'False' string to False, and ensure valid date string
        if check_in_param and check_in_param != 'False':
            check_in = check_in_param
        if check_out_param and check_out_param != 'False':
            check_out = check_out_param

        # Check if filter_by is provided
        if kwargs.get('filter_by', ''):
            filter_by = kwargs.get('filter_by', '')

        # If no filters are applied, return empty dataset
        if not (check_in and check_out) and not filter_by:
            return request.render('bss_attendance_portal_v16.attendance_history_fetcher_id',
                                  {
                                      'attendance_data': [],
                                      'leave_count': 0,
                                      'search_done': False,
                                      'pager': {},
                                      'total_records': 0,
                                      'worked_hours': 0,
                                  })

        # Apply date filters for both attendance and leave
        if filter_by:
            if filter_by == 'last_week':
                last_week_start = today - timedelta(days=today.weekday() + 7)
                last_week_end = last_week_start + timedelta(days=6)
                domain.extend([('check_in', '>=', last_week_start), ('check_out', '<=', last_week_end)])

            elif filter_by == 'last_month':
                last_month = today.replace(day=1) - timedelta(days=1)
                last_month_start = last_month.replace(day=1)
                domain.extend([('check_in', '>=', last_month_start), ('check_out', '<', today.replace(day=1))])

            elif filter_by == 'last_year':
                last_year_start = today.replace(year=today.year - 1, month=1, day=1)
                last_year_end = today.replace(year=today.year - 1, month=12, day=31)
                domain.extend([('check_in', '>=', last_year_start), ('check_out', '<=', last_year_end)])

        if check_in and check_out:
            if not check_in or not check_out:
                raise ValidationError('Both Check In and Check Out are required.')
            if check_in > check_out:
                raise ValidationError('Check Out Must Be Greater Than Check In')
            if datetime.strptime(check_in, '%Y-%m-%d').date() > today:
                raise ValidationError(_('Selected Date cannot be in future.'))

            domain.extend([('check_in', '>=', check_in), ('check_out', '<=', check_out)])

        # Get total count for pagination + Worked hours
        attendance_count = request.env['hr.attendance'].search_count(domain)
        attendance_recs = request.env['hr.attendance'].search(domain)
        worked_hours = sum(x.worked_hours for x in attendance_recs)

        # Setup pager with proper handling of False values
        pager = request.website.pager(
            url="/fetch/attendance",
            url_args={
                'check_in': check_in if check_in else None,
                'check_out': check_out if check_out else None,
                'filter_by': filter_by if filter_by else None,
            },
            total=attendance_count,
            page=page,
            step=10  # Records per page
        )

        # Get paginated records
        attendance_recs = request.env['hr.attendance'].search(
            domain,
            limit=10,
            offset=pager['offset'],
            order='check_in desc'
        )

        for rec in attendance_recs:
            attendance_data.append({
                'check_in': rec.check_in + timedelta(hours=5) if rec.check_in else None,
                'check_out': rec.check_out + timedelta(hours=5) if rec.check_out else None,
                'worked_hours': rec.worked_hours,
            })

        return request.render('bss_attendance_portal_v16.attendance_history_fetcher_id',
                              {
                                  'attendance_data': attendance_data,
                                  'search_done': bool(check_in or check_out or filter_by),
                                  'pager': pager,
                                  'total_records': attendance_count,
                                  'worked_hours': worked_hours,
                              })
