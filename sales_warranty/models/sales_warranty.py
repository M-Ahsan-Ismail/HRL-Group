import base64
import logging

from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import formataddr
from odoo.tools.safe_eval import datetime
_logger = logging.getLogger(__name__)

class SalesWarranty(models.Model):
    _name = 'sales.warranty'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True,
                copy=False, readonly=True, index=True, default=lambda self: _('New'))
    sale_order_id = fields.Many2one('sale.order', 'Sales Order')
    active = fields.Boolean('Active', default=True)

    state = fields.Selection([('in_warranty', 'In Warranty'), ('expired', 'Expired')], string='State', readonly=True,
                             default='in_warranty')

    customer_id = fields.Many2one('res.partner', 'Customer')
    product_id = fields.Many2one('product.template', 'Order Product')
    date_of_purchase = fields.Date('Date of Purchase')
    warranty_end_date = fields.Date('Warrenty End Date')
    warranty_period = fields.Float('Warranty Period')
    notes = fields.Text('Notes', readonly=True)
    sale_order_count = fields.Integer('Sales Order Count', compute='_compute_sale_order_count')
    remaining_months = fields.Integer('Remaining Months', compute='_compute_remaining_months')

    terms_condition_id = fields.Many2one('warranty.terms', 'Terms & Conditions')
    warranty_include_id = fields.Many2one('warranty.includes', 'Warranty Includes')
    warranty_exclude_id = fields.Many2one('warranty.excludes', 'Warranty Excludes')

    @api.depends('warranty_end_date')
    def _compute_remaining_months(self):
        today = fields.Date.today()
        for record in self:
            if record.warranty_end_date and record.warranty_end_date > today:
                delta = relativedelta(record.warranty_end_date, today)
                record.remaining_months = (delta.years * 12) + delta.months
            else:
                record.remaining_months = 0

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('sales.warranty.sequence') or _('New')
        return super(SalesWarranty, self).create(vals)

    def force_expire(self):
        self.write({'state': 'expired', 'active': False})

    def action_view_related_sale_order(self):
        return {
            'name': 'Related Sale Orders',
            'res_model': 'sale.order',
            'view_mode': 'list,form',
            'domain': [('sale_warranty_id', '=', self.id)],
            'context': {'create': False, 'delete': False},
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    @api.depends('sale_order_id')
    def _compute_sale_order_count(self):
        for x in self:
            if x.sale_order_id:
                x.sale_order_count = len(x.sale_order_id)

    def cron_job_change_warranty(self):
        today_date = fields.Date.today()
        warranties_to_expire = self.env['sales.warranty'].search([
            ('state', '=', 'in_warranty'),
            ('warranty_end_date', '!=', False),
            ('warranty_end_date', '<=', today_date),
        ])
        print(f"Found {len(warranties_to_expire)} warranties to expire on {today_date}")
        for record in warranties_to_expire:
            print(f"Processing warranty {record.name}: End Date {record.warranty_end_date}")
            record.write({
                'state': 'expired',
                'active': False,
            })
            print(f"Updated warranty {record.name} to expired")

    def action_reset_warranty(self):
        self.write({'state': 'in_warranty', 'active': True})

    def send_warranty_email(self):
        """Open mail composition wizard with warranty card PDF attached."""
        self.ensure_one()  # Ensure we're working with a single record
        if not self.customer_id or not self.customer_id.email:
            raise UserError("Customer or customer email is missing.")
        if not self.customer_id.name:
            raise UserError("Customer name is missing.")

        # Fetch the report action by its report_name, avoiding env.ref
        report = self.env['ir.actions.report'].search(
            [('report_name', '=', 'sales_warranty.sales_warranty_report_id')],
            limit=1
        )
        if not report:
            raise UserError("Warranty card report not found.")

        # Explicitly pass report_ref to _render_qweb_pdf
        try:
            _logger.info("Rendering PDF for record %s with report ID %s", self.id, report.id)
            # Pass report_ref explicitly as the first argument
            pdf_content = report._render_qweb_pdf(report.report_name, res_ids=[self.id])[0]
            _logger.info("PDF rendering successful for record %s", self.id)
        except Exception as e:
            error_message = f"Failed to render warranty card PDF: {str(e)}"
            _logger.error(error_message)
            raise UserError(error_message)

        # Create an attachment for the PDF
        attachment = self.env['ir.attachment'].create({
            'name': f"Warranty_Card_{self.name or 'Warranty_' + str(self.id)}.pdf",
            'type': 'binary',
            'datas': base64.b64encode(pdf_content),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/pdf',
        })

        ctx = {
            'default_model': self._name,
            'default_res_ids': [self.id],
            'default_use_template': False,
            'default_template_id': False,
            'default_composition_mode': 'comment',
            'default_partner_ids': [self.customer_id.id],
            'default_subject': 'Sales Warranty Email',
            'default_body': f"""
                <div>
                    <p>Dear {self.customer_id.name},</p>
                    <p>Please find attached your warranty card for your recent purchase.</p>
                    <p>Thank you for choosing us!</p>
                </div>
            """,
            'default_attachment_ids': [(4, attachment.id)],
        }

        # Return an action to open the mail composer
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'target': 'new',
            'context': ctx,
        }



class WarrantyTerms(models.Model):
    _name = 'warranty.terms'
    _rec_name = 'terms_conditions'

    terms_conditions = fields.Text('Terms & Conditions', sanitize=True, tracking=True,
                                   default=lambda self: self._get_default_terms_conditions())

    @api.model
    def _get_default_terms_conditions(self):
        return """
                Add here warranty terms and conditions.
               """


class WarrantyIncludes(models.Model):
    _name = 'warranty.includes'
    _rec_name = 'warranty_includes'

    warranty_includes = fields.Text('Warranty Includes', sanitize=True, tracking=True,
                                    default=lambda self: self._get_default_warranty_includes())

    @api.model
    def _get_default_warranty_includes(self):
        return """
                     Add here warranty inclusions.
                   """


class WarrantyExcludes(models.Model):
    _name = 'warranty.excludes'
    _rec_name = 'warranty_excludes'

    warranty_excludes = fields.Text('Warranty Excludes', sanitize=True, tracking=True,
                                    default=lambda self: self._get_default_warranty_excludes())

    @api.model
    def _get_default_warranty_excludes(self):
        return """
                     Add here warranty exclusions.
                   """
