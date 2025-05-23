from odoo import models, fields
from odoo.exceptions import ValidationError


class SalesWarrantyWizard(models.TransientModel):
    _name = 'sales.warranty.wizard'

    sale_order_id = fields.Many2one('sale.order', 'Sales Order')
    customer_id = fields.Many2one('res.partner', 'Customer')
    product_id = fields.Many2one('product.template', 'Order Product')
    date_of_purchase = fields.Date('Date of Purchase')
    warranty_end_date = fields.Date('Warrenty End Date', readonly=True)
    warranty_period = fields.Integer('Warranty Period (Months)', digits=(6, 2), readonly=True)
    notes = fields.Text('Notes')

    def create_warranty_period(self):
        for record in self:
            # Check if any warranty exists for this product in the sale order
            existing_warranties = self.env['sales.warranty'].search([
                ('sale_order_id', '=', record.sale_order_id.id),
                ('product_id', '=', record.product_id.id),
                ('state', '=', 'in_warranty'),
            ])
            if existing_warranties:
                raise ValidationError(
                    f'Product: {record.product_id.name} is already under warranty for Sale Order: {record.sale_order_id.name}')

            if record.date_of_purchase and record.product_id and record.warranty_period:
                warranty_id = self.env['sales.warranty'].create({
                    'sale_order_id': record.sale_order_id.id,
                    'customer_id': record.customer_id.id,
                    'product_id': record.product_id.id,
                    'date_of_purchase': record.date_of_purchase,
                    'warranty_end_date': record.warranty_end_date,
                    'warranty_period': record.warranty_period,
                    'notes': record.notes,
                })
                print(f'Warranty: {warranty_id} Created')
                record.sale_order_id.write({'sale_warranty_id': warranty_id.id})
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Success',
                        'message': f'ID Warranty {warranty_id.id} created successfully',
                        'type': 'success',
                        'sticky': False,
                    }
                }
            return {'type': 'ir.actions.act_window_close'}  # Close wizard if validation fails or fields are missing
