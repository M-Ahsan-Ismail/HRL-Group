from odoo import api, fields, models, _


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    is_vehicle = fields.Boolean('Is Vehicle', default=False)
    is_spare_part = fields.Boolean('Is Spare Part', default=False)

    # Vehicle Details
    model_name = fields.Many2one('brand.models', 'Model Name')
    fuel_type = fields.Selection([('petrol', 'Petrol'), ('diesel', 'Diesel'), ('hybrid', 'Hybrid')],
                                 string='Fuel Type')
    code = fields.Char('Model Code', related='model_name.code')
    launch_year = fields.Date('Launch Year')
    body_type = fields.Selection(
        [('sedan', 'Sedan'), ('suv', 'Suv'), ('crossover', 'Crossover'), ('hatchback', 'Hatchback')], 'Body Type')
    seating_capacity = fields.Integer('Seating Capacity')

    # Engine Details
    model_variant_id = fields.Many2one('model.variant', 'Variant')
    engine_size = fields.Char('Engine Size', related='model_variant_id.engine_size')
    color = fields.Integer('Variant Color', related='model_variant_id.color')
    color_code = fields.Integer('Variant Color', related='model_variant_id.color')
    transmission_type = fields.Selection(
        selection=[
            ('manual', 'Manual'),
            ('automatic', 'Automatic'),
            ('cvt', 'CVT'),
            ('semi_automatic', 'Semi-Automatic'),
            ('dual_clutch', 'Dual-Clutch')
        ],
        string="Transmission Type",
        related='model_variant_id.transmission_type'
    )
    feature_ids = fields.Many2many('variant.features', string='Features', related='model_variant_id.feature_ids')

    spare_part_name = fields.Char(string='Part Name', required=True)
    part_number = fields.Char(string='Part Number', help="Unique identifier for the part")

    spare_part_type = fields.Selection([
        ('genuine', 'Genuine'),
        ('aftermarket', 'Aftermarket'),
        ('accessory', 'Accessory'),
    ], string='Spare Part Type', required=True)

    compatible_model_ids = fields.Many2many(
        'brand.models',
        string='Compatible Models',
        help='Vehicle models this part is compatible with'
    )
