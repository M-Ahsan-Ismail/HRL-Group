from odoo import  fields, models


class RejectionWizard(models.TransientModel):
    _name = 'rejection.wizard'
    _description = 'Rejection Wizard'

    name = fields.Char('Reason', required=True)

    def reject_claim(self):
        active_id = self.env.context.get('active_id')
        if not active_id:
            raise models.UserError("No active record found.")
        obj = self.env['warranty.claim'].browse(active_id)
        obj.decision_note = self.name
        obj.action_reject()

