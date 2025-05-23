from odoo import fields, models


class InheritHREmployee(models.Model):
    _inherit = 'hr.employee'

    is_dealer = fields.Boolean('Is Dealer')
