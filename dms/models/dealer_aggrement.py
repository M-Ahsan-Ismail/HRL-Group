from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class DealerAgreement(models.Model):
    _name = 'dealer.agreement'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Dealer Agreement'
    _rec_name = 'agreement_reference'

    priority = fields.Selection([('low', 'Low'), ('high', 'High')], default='low',tracking=True)

    agreement_reference = fields.Char(required=True,copy=False, readonly=True, index=True, default=lambda self: _('New'))

    dealer_name = fields.Char('Dealer Name')
    dealer_company_name = fields.Char('Dealer Company Name')
    dealer_code = fields.Char('Dealer Code', default=lambda self: self._generate_dealer_code(),tracking=True)
    agreement_date = fields.Date('Agreement Date', default=fields.Date.today,tracking=True)
    agreement_start_date = fields.Date('Agreement Start Date', tracking=True)
    agreement_end_date = fields.Date('Agreement End Date', tracking=True)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('terminated', 'Terminated')
    ], string='Status', default='draft', )

    # Dealer Details
    contact_person_name = fields.Char('Contact Person Name', tracking=True)
    phone_number = fields.Char('Phone Number',tracking=True )
    email_address = fields.Char('Email Address', tracking=True)
    business_address = fields.Text('Business Address',tracking=True )
    gst_tax_id = fields.Char('GST / Tax ID')

    # Dealership Scope
    vehicle_brand_ids = fields.Many2many('dms.brands', string='Vehicle Brands Covered')
    vehicle_type_id = fields.Many2one('model.type', string='Vehicle Type', )
    region_territory = fields.Char('Region / Territory Assigned')
    sales_target_monthly = fields.Integer('Monthly Sales Target',tracking=True)
    annual_sales_quota = fields.Integer('Annual Sales Quota',tracking=True)

    # Terms & Conditions
    is_exclusive = fields.Boolean('Exclusivity', default=False)
    agreement_type = fields.Selection([
        ('exclusive', 'Exclusive'),
        ('non_exclusive', 'Non-Exclusive'),
        ('temporary', 'Temporary')
    ], string='Agreement Type', default='non_exclusive', required=True)
    auto_renewal = fields.Boolean('Auto Renewal', default=False)
    renewal_terms = fields.Text('Renewal Terms', sanitize=True, default=lambda self: self._get_default_renewal_terms(),tracking=True)
    termination_clause = fields.Text('Termination Clause', sanitize=True,tracking=True,
                                     default=lambda self: self._get_default_termination_clause())
    penalty_clause = fields.Text('Penalty Clause', sanitize=True,tracking=True,
                                 default=lambda self: self._get_default_penalty_clause())
    support_service_ids = fields.Text('Support Services', sanitize=True,tracking=True,
                                      default=lambda self: self._get_default_support_services())

    # Financial Terms
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    initial_deposit = fields.Monetary('Initial Deposit / Investment', currency_field='currency_id')
    commission_rate = fields.Float('Commission Rate (%)', digits=(5, 2))
    incentive_structure = fields.Text('Incentive Structure')
    credit_limit = fields.Monetary('Credit Limit', currency_field='currency_id', default=0.0)


    # 📄 Attachments
    signed_agreement_document = fields.Many2many(
        'ir.attachment',
        relation='signed_agreement_proof_relation',
        string="Signed Agreement Document",
        store=True
    )
    dealer_license_copy = fields.Many2many(
        'ir.attachment',
        relation='dealer_license_copy_relation',
        string="Dealer License Copy",
        store=True
    )
    company_registration_certificate = fields.Many2many(
        'ir.attachment',
        relation='company_registration_certificate_relation',
        string="Company Registration Certificate",
        store=True
    )

    @api.model
    def create(self, vals):
        if vals.get('agreement_reference', _('New')) == _('New'):
            vals['agreement_reference'] = self.env['ir.sequence'].next_by_code('dealer.agreement') or _('New')
        return super(DealerAgreement, self).create(vals)

    def _generate_dealer_code(self):
        return self.env['ir.sequence'].next_by_code('dealer.code')

    @api.constrains('commission_rate')
    def _check_commission_rate(self):
        for record in self:
            if record.commission_rate < 0 or record.commission_rate > 100:
                raise ValidationError("Commission Rate must be between 0 and 100%.")

    @api.constrains('initial_deposit', 'credit_limit')
    def _check_monetary_fields(self):
        for record in self:
            if record.initial_deposit < 0:
                raise ValidationError("Initial Deposit cannot be negative.")
            if record.credit_limit < 0:
                raise ValidationError("Credit Limit cannot be negative.")

    @api.model
    def _get_default_renewal_terms(self):
        return """
                Renewal Terms:
                The agreement may be renewed under the following conditions:
                
                    --> Both parties agree in writing.
                    --> Renewal is subject to price adjustments based on market conditions.
                
            """

    @api.model
    def _get_default_termination_clause(self):
        return """
                Termination Clause:
                Either party may terminate this agreement under the following conditions:
            
                    --> Failure to meet the terms and conditions.
                    --> Non-payment for a period of 30 days.
               
            """

    @api.model
    def _get_default_penalty_clause(self):
        return """
              Penalty Clause:
                If the agreement is terminated before the agreed-upon period, the following penalties will apply:
               
                   --> A 10% penalty on the remaining contract value.
                   --> Additional administrative fees may apply.
               
            """

    @api.model
    def _get_default_support_services(self):
        return """
            Support Services:
            The following support services are included with this agreement:
            
                --> 24/7 customer service hotline
                --> On-site support for critical issues.
            
        """
