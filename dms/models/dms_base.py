from odoo import models, fields


class DMS_Base(models.Model):
    _name = 'dms.base'
    _description = 'DMS Base'
    _rec_name = 'dealer_name'

    dealer_name = fields.Char(string='Dealer Name')
    status = fields.Selection([
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('blacklisted', 'Blacklisted'),
    ], string='Status')
    priority = fields.Selection([('Low', 'Low'), ('Medium', 'Medium')], string='Priority')

    dealer_code = fields.Char(string='Dealer Code')
    dealer_type = fields.Many2one('dms.type', string='Dealer Type')
    dealer_region = fields.Many2one('dms.zone', string='Dealer Region')
    partner_id = fields.Many2one('res.partner', string='Partner')

    partner_email = fields.Char(related='partner_id.email', string='Partner Email', readonly=True)
    partner_phone = fields.Char(related='partner_id.phone', string='Partner Phone', readonly=True)
    partner_street = fields.Char(related='partner_id.street', string='Partner Street', readonly=True)
    partner_city = fields.Char(related='partner_id.city', string='Partner City', readonly=True)

    opening_date = fields.Datetime(string='Opening Date', default=fields.Date.today())
    authorized_brands = fields.Many2many('dms.brands', string='Authorized Brands')
