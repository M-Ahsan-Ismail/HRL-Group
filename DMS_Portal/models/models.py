from odoo import fields, models, api, _
from datetime import datetime

from odoo.exceptions import ValidationError


class DMS_Portal(models.Model):
    _name = 'dms.portal'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Applicant Name', compute='_compute_applicant_name')
    active = fields.Boolean(string='Active', default=True)

    reference_no = fields.Char('Application No', readonly=True,  default=lambda self: _('New'))

    state = fields.Selection(
        [('draft', 'New'), ('under_review', 'Under Review'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        string='Status', default='draft')
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'High'),
    ], string="Priority", default='0')

    request_month = fields.Date('Request Month', default=datetime.today())
    approved_month = fields.Date('Approved Month')

    assigne_id = fields.Many2one('res.users', string='Assigned To')

    first_name = fields.Char('First Name')
    last_name = fields.Char('Last Name')
    email_id = fields.Char('Email ID')
    date_of_birth = fields.Date('Date of Birth')

    phone_no = fields.Char(string="Phone No")
    mobile_no = fields.Char(string="Mobile No")

    location = fields.Char(string="Location")
    location2 = fields.Char(string="Location 2")
    city = fields.Char(string="City", )
    pincode = fields.Char(string="PinCode")
    country_id = fields.Many2one('res.country', string="Country")
    province = fields.Char(string="State")

    qualification = fields.Char(string="Personal Detail")
    current_occupation = fields.Selection(
        string="Current Occupation",
        selection=[('self_employed', 'Self Employed'), ('salaried', 'Salaried'), ('other', 'Other')])

    # Fill Your Adverisment Details as per Industry Standards.
    dealer_vacancy_known_through = fields.Selection([
        ('advertisement', 'Advertisement'), ('area_sale_manager', 'Area Sale Manager'),
        ('regional_manager', 'Regional Manager'), ('other', 'Other')
    ], string="Dealer Vacancy Knowledge Through")
    code = fields.Char(string="Code")

    # Fill Your Application Form Details.
    image_1920 = fields.Binary(string="Image 1920", store=True)
    company_name = fields.Char(string="Company Name")
    business_type = fields.Char(string="Business Type")
    contact_person_name = fields.Char(string="Contact Person Name")
    business_email = fields.Char(string="Email")
    business_phone = fields.Char(string="Phone")
    business_address = fields.Char(string="Address")
    existing_dealership = fields.Boolean(string="Existing Dealership")
    infrastructure_detail = fields.Text(string="Infrastructure Detail")
    business_staff_count = fields.Float(string="Business Staff Count")

    licence_upload = fields.Many2many(
        'ir.attachment',
        relation='dms_portal_licence_upload_rel',
        string="License",
        store=True
    )
    registration_upload = fields.Many2many(
        'ir.attachment',
        relation='dms_portal_registration_upload_rel',
        string="Registration",
        store=True
    )
    ownership_proof = fields.Many2many(
        'ir.attachment',
        relation='dms_portal_ownership_proof_rel',
        string="Ownership Proof",
        store=True
    )
    tax_legal_registration = fields.Boolean(string="Tax Legal Registration")
    tax_ntn_number = fields.Char(string="Tax NTN Number")
    tax_cnic = fields.Char(string="Tax CNIC")
    secp_certificate_number = fields.Many2many(
        'ir.attachment',
        relation='dms_portal_secp_certificate_rel',
        string="SECP Certificate",
        store=True
    )

    # Site Location Details
    not_available_site_location = fields.Selection(
        [('to_be_purchased', 'To Be Purchased'), ('to_be_rented', 'To Be Rented'), ('to_be_leased', 'To Be Leased')],
        string="Site Location")
    available_site_location = fields.Selection(
        [('owned', 'Owned'), ('rented', 'Rented'), ('leased', 'Leased'), ('other', 'Other')],
        string="Site Location")
    total_area = fields.Float('Total Area')
    query = fields.Char('Query')

    # Investment Details
    investment_from = fields.Float('Investment From')
    investment_to = fields.Float('Investment To')

    def action_submit(self):
        self.write({'state': 'under_review'})

    def action_reject(self):
        self.write({'state': 'rejected', 'active': False})

    def action_approve(self):
        self.write({'state': 'approved', 'approved_month': fields.Date.today()})

    def action_reset(self):
        self.write({'state': 'draft', 'active': True})

    def create_partner(self):
        for rec in self:
            if rec.state == 'approved':
                # Validate company_name
                if not rec.company_name:
                    raise ValidationError(_("Company name is required to create an employee."))

                # Search for the company
                company = self.env['res.company'].search([('name', '=', rec.company_name)], limit=1)
                if not company:
                    # Fallback to user's current company
                    company = self.env.company
                    print(
                        f"No company found for '{rec.company_name}'. Using default company: {company.name} (ID: {company.id})")

                # Create res.partner record
                res_partner_id = self.env['res.partner'].create({
                    'name': f'{rec.first_name} {rec.last_name}',
                    'is_company': False,
                    'is_dealer': True,
                    'city': rec.city,
                    'zip': rec.pincode,
                    'country_id': rec.country_id.id,
                    'state_id': self.env['res.country.state'].search([('name', '=', rec.province)], limit=1).id,
                    'function': rec.qualification,
                    'phone': rec.phone_no,
                    'mobile': rec.mobile_no,
                    'email': rec.email_id,
                    'image_1920': rec.image_1920,
                })
                print(f'Partner Id: {res_partner_id.id}')

                # Create hr.employee record
                hr_employee_id = self.env['hr.employee'].create({
                    'name': f'{rec.first_name} {rec.last_name}',
                    'job_title': rec.qualification,
                    'work_email': rec.email_id,
                    'work_phone': rec.phone_no,
                    'mobile_phone': rec.mobile_no,
                    'company_id': company.id,  # Use validated company ID
                    'parent_id': rec.assigne_id.id,
                    'coach_id': rec.assigne_id.id,
                    'is_dealer': True,
                })
                print(f'Employee Id: {hr_employee_id.id}')

                # Return client-side notification
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Success',
                        'message': f'Partner (ID: {res_partner_id.id}) and Employee (ID: {hr_employee_id.id}) created successfully for {rec.first_name} {rec.last_name}.',
                        'type': 'success',
                        'sticky': False,
                    }
                }

    @api.depends('first_name', 'last_name')
    def _compute_applicant_name(self):
        for rec in self:
            if rec.first_name and rec.last_name:
                rec.name = f'{rec.first_name} {rec.last_name}'
            else:
                rec.name = f''

    @api.model
    def create(self, vals):
        if vals.get('reference_no', _('New')) == _('New'):
            vals['reference_no'] = self.env['ir.sequence'].next_by_code('dms.portal.sequence') or _('New')
        return super(DMS_Portal, self).create(vals)
