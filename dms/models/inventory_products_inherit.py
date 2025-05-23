from odoo import api, fields, models, _


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    is_vehicle = fields.Boolean('Is Vehicle', default=False)
    is_spare_part = fields.Boolean('Is Spare Part', default=False)

    model_name = fields.Char('Model Name', required=True)
    fuel_type = fields.Selection([('petrol', 'Petrol'), ('diesel', 'Diesel'), ('hybrid', 'Hybrid')],
                                 string='Fuel Type', required=True)
    code = fields.Char('Model Code', required=True)
    launch_year = fields.Date('Launch Year', required=True)
    body_type = fields.Selection(
        [('sedan', 'Sedan'), ('suv', 'Suv'), ('crossover', 'Crossover'), ('hatchback', 'Hatchback')], 'Body Type')
    seating_capacity = fields.Integer('Seating Capacity')

    model_variant_id = fields.Many2one('model.variant', 'Variant')
    engine_size = fields.Char('Engine Size')
    color = fields.Integer('Color')
    color_code = fields.Integer('Color Code')
    transmission_type = fields.Selection(
        selection=[
            ('manual', 'Manual'),
            ('automatic', 'Automatic'),
            ('cvt', 'CVT'),
            ('semi_automatic', 'Semi-Automatic'),
            ('dual_clutch', 'Dual-Clutch')
        ],
        string="Transmission Type",
        required=True
    )
    feature_ids = fields.Many2many('variant.features', 'Features')

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
