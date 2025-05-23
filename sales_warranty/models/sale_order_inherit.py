from datetime import timedelta
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    sale_warranty_id = fields.Many2one('sales.warranty', string='Sales Warranty')
    sale_warranty_count = fields.Integer('Sales Order Count', compute='_compute_sale_warranty_count')
    warranty_end_date = fields.Date('Warrenty End Date', readonly=True, store=True,
                                    compute='_compute_warranty_end_date')
    warranty_period = fields.Integer('Warranty Period (Months)', digits=(6, 2), store=True, readonly=True,
                                     related='order_line.product_template_id.warranty_period_months')

                                                


    @api.depends('date_order', 'warranty_period')
    def _compute_warranty_end_date(self):
        for record in self:
            if not record.date_order or not record.warranty_period:
                record.warranty_end_date = False
            else:
                record.warranty_end_date = record.date_order + relativedelta(months=record.warranty_period)

    def action_view_related_sale_warranty(self):
        return {
            'name': 'Related Warranty',
            'res_model': 'sales.warranty',
            'view_mode': 'list,form',
            'domain': [('sale_order_id', '=', self.id)],
            'context': {'create': False, 'delete': False},
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    @api.depends('sale_warranty_id')
    def _compute_sale_warranty_count(self):
        for x in self:
            x.sale_warranty_count = self.env['sales.warranty'].search_count([('sale_order_id', '=', x.id)])


class Sale_order_line_inherit(models.Model):
    _inherit = 'sale.order.line'

    def add_warranty_period(self):
        for line in self:
            if line.product_template_id:
                context = {
                    'default_order_id': line.order_id.id,
                    'default_customer_id': line.order_id.partner_id.id,
                    'default_product_id': line.product_template_id.id,
                    'default_sale_order_id': line.order_id.id,
                    'default_date_of_purchase': line.order_id.date_order,
                    'default_warranty_period': line.order_id.warranty_period,
                    'default_warranty_end_date': line.order_id.warranty_end_date,
                }
                return {
                    'name': 'Add Warranty Period',
                    'type': 'ir.actions.act_window',
                    'res_model': 'sales.warranty.wizard',
                    'view_mode': 'form',
                    'view_id': self.env.ref('sales_warranty.sales_warranty_wizard_view_form').id,
                    'target': 'new',
                    'context': context,
                }
