from odoo import fields, http
from odoo.http import request


class MrpOrdersDashboardController(http.Controller):
    @http.route('/mrp/orders/dashboard', type='http', auth="user", website=True, methods=['GET'], csrf=False)
    def mrp_orders_dashboard_portal(self, **kwargs):
        res_users = request.env['res.users'].sudo().search_read([], ['id', 'name'])

        # Build domain for filtering
        domain = []

        # Filter by responsible user
        if kwargs.get('responsible_user'):
            domain.append(('user_id', '=', int(kwargs.get('responsible_user'))))

        # Filter by state
        if kwargs.get('state'):
            domain.append(('state', '=', kwargs.get('state')))

        # Search with domain
        mrp_production_records = request.env['mrp.production'].search(domain)

        mrp_list = []
        for rec in mrp_production_records:
            image_data = None
            if rec.product_id and rec.product_id.image_1920:
                try:
                    if isinstance(rec.product_id.image_1920, bytes):
                        image_data = rec.product_id.image_1920.decode('utf-8')
                    else:
                        image_data = str(rec.product_id.image_1920)
                except:
                    image_data = None

            mrp_list.append({
                'image': image_data,
                'id': rec.id,
                'name': rec.name,
                'product': rec.product_id.name,
                'ordered_qty': rec.product_qty,
                'produced_qty': rec.qty_producing,
                'bill_of_material': rec.bom_id.product_tmpl_id.name if rec.bom_id else '',
                'date_start': rec.date_start,
                'date_end': rec.date_finished,
                'components_availability': rec.components_availability,
                'user_id': rec.user_id.name if rec.user_id else '',
                'state': rec.state,
            })

        return request.render('mrp_portal_dashboard.mrp_orders_admin_dashboard_id', {
            'mrp_list': mrp_list,
            'res_users': res_users,
            'kwargs': kwargs,
        })

    @http.route('/mrp/orders/details/<int:record_id>', type='http', auth="user", website=True, methods=['GET'],
                csrf=False)
    def mrp_order_details(self, record_id, **kwargs):
        # Fetch the specific manufacturing order by ID
        mrp_production = request.env['mrp.production'].sudo().search([('id', '=', record_id)], limit=1)

        if not mrp_production:
            # Return empty data if record not found
            return request.render('mrp_portal_dashboard.mrp_order_details', {
                'mrp_order': None,
            })

        # Loop over components (move_raw_ids)
        components = []
        for move in mrp_production.move_raw_ids:
            components.append({
                'component_product_name': move.product_id.name or '',
                'component_to_consume': move.product_uom_qty or 0.0,
                'component_quantity': move.quantity or 0.0,
                'component_consumed': move.picked or False,
            })

        # Loop over work centers (workorder_ids)
        work_centers = []
        for workorder in mrp_production.workorder_ids:
            work_centers.append({
                'wc_operation_name': workorder.name or '',
                'work_center': workorder.workcenter_id.name or '',
                'wc_product_name': workorder.product_id.name or '',
                'wc_quantity_remaining': workorder.qty_remaining or 0.0,
                'wc_expected_duration': workorder.duration_expected or 0.0,
                'wc_real_duration': workorder.duration or 0.0,
                'wc_state': workorder.state or '',
            })

        mrp_order = {
            'id': mrp_production.id,
            'ordered_qty': mrp_production.product_qty,
            'produced_qty': mrp_production.qty_producing,
            'bill_of_material': mrp_production.bom_id.product_tmpl_id.name if mrp_production.bom_id else '',
            'date_start': mrp_production.date_start,
            'date_end': mrp_production.date_finished,
            'components_availability': mrp_production.components_availability,
            'user_id': mrp_production.user_id.name if mrp_production.user_id else '',
            # Miscellaneous
            'operation_type': mrp_production.picking_type_id.name,
            'source': mrp_production.origin,
            'project_name': mrp_production.project_id.name,
            # Components data from loop
            'components': components,
            # Work centers data from loop
            'work_centers': work_centers,
        }

        return request.render('mrp_portal_dashboard.mrp_order_details', {
            'mrp_order': mrp_order,
        })


