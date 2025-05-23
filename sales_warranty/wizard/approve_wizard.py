from odoo import fields, models


class ApproveWizard(models.TransientModel):
    _name = 'approve.wizard'
    _description = 'Approve Wizard'

    name = fields.Text('Visit Location', required=True)

    def visit_location(self):
        self.ensure_one()
        active_id = self.env.context.get('active_id')
        res = self.env['warranty.claim'].browse(active_id)
        if res:
            res.visit_required = True
            res.service_center = self.name
            res.action_approve()
