# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ApprovalCategory(models.Model):
    _inherit = 'approval.category'
    
    model_id = fields.Many2one('ir.model', string='Model')
    
    