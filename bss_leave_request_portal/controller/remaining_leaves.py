# from odoo import http, fields, _
# from odoo.http import request
# from odoo.addons.bss_leave_request_portal.controller.time_off_controller import TimeOffController

#
# class RemainingLeaves(TimeOffController):
#     @http.route('/all/time/off', type='http', auth='user', website=True, methods=['GET', 'POST'], csrf=True)
#     def GetRemainingLeaves(self, **kwargs):
#
#         leave_types = []
#
#         user_id = request.env.user.employee_id.id
#         leave_recs = request.env['hr.leave.allocation'].sudo().search([('state', '=', 'validate')])
#         # Build leave_types with duplicates
#         temp_leave_types = []
#         for leave_rec in leave_recs:
#             temp_leave_types.append({
#                 'leave_name': leave_rec.holiday_status_id.leave_type,
#                 'time_off_in': leave_rec.holiday_status_id.request_unit
#             })
#
#         # Deduplicate leave_types based on leave_name and time_off_in
#         unique_leave_types = {}
#         for leave in temp_leave_types:
#             leave_name = leave['leave_name']
#             if leave_name not in unique_leave_types:
#                 unique_leave_types[leave_name] = leave
#         leave_types = list(unique_leave_types.values())
#         print(f'Leave Name: {leave_types}')
#
#         taken_leaves = {}
#
#         # Initialize taken_leaves dictionary to aggregate totals
#         for leave in leave_types:
#             leave_name = leave['leave_name']
#             taken_leaves[leave_name] = {
#                 'time_off_in': leave['time_off_in'],
#                 'total_taken': 0,
#                 'unit': 'days' if leave['time_off_in'] in ['day', 'half_day'] else 'hours'
#             }
#
#         # Fetch and aggregate leaves taken for each leave type
#         for leave in leave_types:
#             leave_name = leave['leave_name']
#             used_leaves_recs = request.env['hr.leave'].search([
#                 ('employee_id', '=', user_id),
#                 ('holiday_status_id.leave_type', '=', leave_name),
#                 ('state', 'in', ['validate', 'validate1'])
#             ])
#             print(f"Found {len(used_leaves_recs)} records for leave type {leave_name}")  # Debug
#
#             for rec in used_leaves_recs:
#                 duration = rec.duration_display  # e.g., "32:00 hours" or "2 days"
#                 print(f"Duration for {leave_name}: {duration}")  # Debug
#                 if duration:
#                     try:
#                         value_str, unit = duration.split()  # Split into "32:00" and "hours" or "2" and "days"
#                         if unit.lower() == 'hours':
#                             if ':' in value_str:  # Handle "HH:MM" format
#                                 hours, minutes = map(int, value_str.split(':'))
#                                 value = hours + minutes / 60.0  # Convert to decimal hours
#                             else:  # Handle simple "X hours" format
#                                 value = float(value_str)
#                         elif unit.lower() == 'days':
#                             value = float(value_str)
#                         else:
#                             raise ValueError(f"Unknown unit: {unit}")
#
#                         # Aggregate the total based on the leave type's unit
#                         if leave['time_off_in'] in ['day', 'half_day'] and unit.lower() == 'days':
#                             taken_leaves[leave_name]['total_taken'] += value
#                         elif leave['time_off_in'] == 'hour' and unit.lower() == 'hours':
#                             taken_leaves[leave_name]['total_taken'] += value
#
#                     except (ValueError, IndexError) as e:
#                         print(f"Invalid duration format for leave {leave_name}: {duration}")
#
#         # Convert hours to days for display (if applicable) and format output
#         taken_leaves_list = []
#         for leave_name, data in taken_leaves.items():
#             total = data['total_taken']
#             unit = data['unit']
#             display_value = total
#             display_unit = unit
#
#             # Convert hours to days for sick leave (assuming 8 hours = 1 day)
#             if leave_name == 'sick' and data['time_off_in'] == 'hour':
#                 display_value = total / 8  # Convert hours to days
#                 display_unit = 'days'
#
#             taken_leaves_list.append({
#                 'Leave': leave_name,
#                 'Taken': f"{display_value:.1f} {display_unit}"
#             })
#
#         print(f'Taken Leaves: {taken_leaves_list}')
#
#         return super(RemainingLeaves, self).Retrieve_Time_Off_Data(**kwargs)
