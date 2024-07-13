# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _
import datetime
from datetime import datetime, date,timedelta
from datetime import datetime
class EditAnalyticAccount(models.TransientModel):
    _name = 'edit.analytic.after'
    line_id = fields.Many2one(
        comodel_name='account.move.line',
        string='Journal Item',
        required=False)
    analytic_precision = fields.Integer(
        store=False,
        default=lambda self: self.env['decimal.precision'].precision_get("Percentage Analytic"),
    )
    analytic_distribution = fields.Json('Analytic')


    

    # @api.multi
    def action_apply(self):
       if self.line_id:
           self.line_id.write({'analytic_distribution':self.analytic_distribution})
           self.line_id._prepare_analytic_lines()