from datetime import timedelta
from odoo import models, fields, api, _


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'


    warranty_eligibility = fields.Boolean('Warranty Eligibility',
                                          help="Indicates whether the dealer is eligible to offer warranty services.")
    warranty_period_months = fields.Integer('Warranty Period (Months)', help="Duration of warranty coverage in months.")
