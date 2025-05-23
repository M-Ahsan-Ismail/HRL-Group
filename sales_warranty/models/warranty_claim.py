import base64
import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class WarrantyClaim(models.Model):
    _name = 'warranty.claim'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True,
                       copy=False, readonly=True, index=True, default=lambda self: _('New'))
    active = fields.Boolean('Active', default=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('under_review', 'Under Review'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        string='Claim Status', readonly=True,
    )

    warranty_number_id = fields.Many2one('sales.warranty', 'Warranty Number', readonly=True)
    customer_id = fields.Many2one('res.partner', string='Customer', readonly=True)
    product_id = fields.Many2one('product.template', string='Product', readonly=True)

    claim_date = fields.Date(string='Claim Date', readonly=True)
    warranty_end_date = fields.Date(string='Warranty End Date', readonly=True)
    description = fields.Char(string='Issue Description')

    attachment_ids = fields.Many2many(
        'ir.attachment',
        relation='warranty_claim_proof_rel',
        string="Proof Document",
        store=True
    )
    image_1920 = fields.Binary(string="Proof Image", store=True)
    visit_required = fields.Boolean('Visit Service Center')
    service_center = fields.Char(string='Service Center Location')

    decision_note = fields.Text(string='Rejection Reason')

    @api.model
    def create(self, vals):
        # Generate sequence if name is 'New'
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('warranty.claim.sequence') or _('New')
        return super(WarrantyClaim, self).create(vals)

    def action_reset_to_draft(self):
        self.write({'state': 'draft', 'active': True})

    def action_submit(self):
        self.write({'state': 'under_review'})

    def action_reject(self):
        self.write({'state': 'rejected','active': False})

    def action_approve(self):
        self.write({'state': 'approved'})
