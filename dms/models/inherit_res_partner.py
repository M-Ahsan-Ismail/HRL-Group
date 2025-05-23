from odoo import fields, models, api, _


class InheritResPartnerForDealer(models.Model):
    _inherit = 'res.partner'

    is_dealer = fields.Boolean('Is Dealer', default=False)
    res_user_id = fields.Many2one('res.users', 'DealerShip')

