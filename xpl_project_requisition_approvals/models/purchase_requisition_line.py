# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    cost_account_id = fields.Many2one('account.analytic.account', string='Cost Code')

    @api.onchange('cost_account_id','product_id','requisition_id.project_id')
    def _onchange_cost_account_id(self):
        """Updates the analytic distribution JSON field based on the selected cost account and project."""
        distribution = {}

        if self.cost_account_id:
            # Add the cost account with 100% (1.0)
            distribution[self.cost_account_id.id] = 100

        if self.requisition_id.project_id:
            # Add the project analytic account (if exists) with 100% (1.0)
            distribution[self.requisition_id.project_id.account_id.id] = 100

        # Update the analytic_distribution field with the computed distribution
        self.analytic_distribution = distribution if distribution else {}