# -*- coding: utf-8 -*-
################################################################################
#
#    A part of OpenHRMS Project <https://www.openhrms.com>
#
#    Copyright (C) 2025-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Cybrosys Techno Solutions (odoo@cybrosys.com)
#
#    This program is under the terms of the Odoo Proprietary License v1.0
#    (OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the
#    Software or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#    OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
#    USE OR OTHER DEALINGS IN THE SOFTWARE.
#
################################################################################
from datetime import date
from odoo import models
from odoo.exceptions import UserError


class HrLoanLine(models.Model):
    """ Creates an invoice for loans. """
    _inherit = "hr.loan.line"

    def action_paid_amount(self, month):
        """
            This creates the account move line for payment of each installment.
        """
        for line in self:
            if line.loan_id.state != 'approve':
                raise UserError("Loan Request must be approved")
            debit_vals = {
                'name': line.employee_id.name,
                'account_id': line.loan_id.employee_account_id.id,
                'journal_id': line.loan_id.journal_id.id,
                'date': date.today(),
                'debit': line.amount > 0.0 and line.amount or 0.0,
                'credit': line.amount < 0.0 and -line.amount or 0.0,
            }
            credit_vals = {
                'name': line.employee_id.name,
                'account_id': line.loan_id.treasury_account_id.id,
                'journal_id': line.loan_id.journal_id.id,
                'date': date.today(),
                'debit': line.amount < 0.0 and -line.amount or 0.0,
                'credit': line.amount > 0.0 and line.amount or 0.0,
            }
            vals = {
                'name': 'LOAN/' + ' ' + line.employee_id.name + '/' + month,
                'narration': line.employee_id.name,
                'ref': line.loan_id.name,
                'journal_id': line.loan_id.journal_id.id,
                'date': date.today(),
                'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
            }
            move = self.env['account.move'].create(vals)
            move.action_post()
        return True
