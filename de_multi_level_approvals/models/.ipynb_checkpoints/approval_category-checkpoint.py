# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ApprovalCategory(models.Model):
    _inherit = 'approval.category'
    
    approval_type = fields.Selection([
        ("R", "Default Approval"),
        ("D", "Multi-Level Dynamic"),
        ("S", "Multi-Level Static"),
    ], default='R', required=True, help="Technical field for UX purpose.")
    
    approval_category_line = fields.One2many('approval.category.line', 'approval_category_id')
    
    is_multi_approval = fields.Boolean(
        string="Multi Level Approvals",
        help="Automatically add multi manager(s) as approver in the request as per approval levels")
    
    approval_level = fields.Integer(string="Approval's Level", default="1", required=True)
    
class ApproverCategoryLine(models.Model):
    _name = 'approval.category.line'
    _description = 'Approval Category Line'
    
    approval_category_id = fields.Many2one('approval.category', string='Approval Category', required=True, ondelete='cascade', index=True, copy=False)
    sequence = fields.Integer(string='Sequence', default=10)
    user_id = fields.Many2one('res.users', string='Approver', index=True, tracking=2, required=True)
    department_id = fields.Many2one(related='user_id.department_id')
    job_title = fields.Char(related='user_id.job_title')
    

