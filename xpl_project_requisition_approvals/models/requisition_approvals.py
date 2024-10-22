
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ReqisitionApprovalGroup(models.Model):
    _name = "purchase.requisition.approvals.group"
    _description = "Requisition Approvals Group"
    _order = "id desc"

    name = fields.Char(string='Group Name', required=True)
    project_id = fields.Many2one('project.project')
    role_ids = fields.One2many('purchase.requisition.approvals.group.role', 'approval_group_id', string='Approval Roles')    
    description = fields.Text(string='Description')

    _sql_constraints = [
        ('unique_project', 'unique(project_id)', 'Each project can have only one approval group.')
    ]

class RequisitionApprovalsGroupsRole(models.Model):
    _name = "purchase.requisition.approvals.group.role"
    _description = "Requisition Approvals Group Roles"
    _order = "id desc"

    approval_group_id = fields.Many2one('purchase.requisition.approvals.group', string='Approval Group', required=True, ondelete='cascade')
    group_id = fields.Many2one('res.groups', string='Approval Group', required=True)
    sequence = fields.Integer(string='Sequence', default=10, help="Defines the order of approval roles within the approval group.")