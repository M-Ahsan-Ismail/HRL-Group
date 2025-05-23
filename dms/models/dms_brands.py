from odoo import api, fields, models, _


class DmsBrands(models.Model):
    _name = 'dms.brands'
    name = fields.Char('Brands Name', required=True)
    code = fields.Char('Brands Code', required=True)
    color = fields.Integer('Brand Color', required=True, default=9)
    logo = fields.Binary('Brand Logo')
    description = fields.Text('Brand Description')


class BrandModels(models.Model):
    _name = 'brand.models'

    name = fields.Char('Model Name', required=True)
    brand_id = fields.Many2one('dms.brands', string='Brand', required=True)
    model_type = fields.Many2one('model.type', string='Model Type', required=True)
    code = fields.Char('Model Code')
    description = fields.Text('Model Description')
    active = fields.Boolean('Active', default=True)


class ModelVariants(models.Model):
    _name = 'model.variant'

    name = fields.Char('Variant Name', required=True)
    model_id = fields.Many2one('brand.models', string='Model', required=True)
    engine_type = fields.Selection([('petrol', 'Petrol'), ('diesel', 'Diesel'), ('hybrid', 'Hybrid')],
                                   string='Engine Type', required=True)
    color = fields.Integer('Variant Color')
    feature_ids = fields.Many2many('variant.features', string='Features')


class VariantFeatures(models.Model):
    _name = 'variant.features'

    name = fields.Char('Feature', required=True)
    color = fields.Integer('Feature Color', default=5)


class ModelType(models.Model):
    _name = 'model.type'

    name = fields.Char(
        string="Vehicle Type",
        help="Enter the type of vehicle (e.g., SUV, Sedan, Hatchback, Coupe, Convertible, Pickup Truck, Van, Minivan, Wagon, Crossover, Electric, Hybrid, Luxury, Sports Car, Off-Road)."
    )
