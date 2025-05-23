from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError


class Employee_Grievance(models.Model):
    _name = 'emp.grievance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Employee Grievance'

    name = fields.Char(required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))

    complainant_id = fields.Many2one(
        'hr.employee',
        string='Complainant',
        tracking=True,
        store=True,
        readonly=True,
    )

    department_name = fields.Char(
        string='Department Name',
        related='complainant_id.department_id.name',
        tracking=True,
        store=True,
        translate=False,
        readonly=True,
    )

    complaint_type_id = fields.Many2one('emp.grievance.type', string='Complaint Type',readonly=True)

    description = fields.Char(
        string='Description',
        tracking=True
    )
    attachment_ids = fields.Many2many(
        'ir.attachment',
        relation='employee_grievance_attachment',
        string="Proof Document",
        store=True
    )

    status = fields.Selection([
        ('new', 'Submitted'),
        ('in_review', 'Investigating'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed')
    ], string='Status', default='new', tracking=True)

    hr_responsible_id = fields.Many2one(
        'res.users',
        string='HR Responsible'
    )

    submission_date = fields.Date(
        string='Submission Date',
        default=fields.Date.today,
        readonly=True,
    )

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('emp.grievance') or _('New')
        return super(Employee_Grievance, self).create(vals)

    def action_review(self):
        self.write({'status': 'in_review'})

    def action_resolve(self):
        self.write({'status': 'resolved'})

    def action_close(self):
        self.write({'status': 'closed'})

    def action_reset(self):
        self.write({'status': 'new'})


class Employee_Grievance_types(models.Model):
    _name = 'emp.grievance.type'

    name = fields.Char('Grievance Type', index=True)
