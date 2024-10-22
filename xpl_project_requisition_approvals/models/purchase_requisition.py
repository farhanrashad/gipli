
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from collections import defaultdict


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    project_id = fields.Many2one('project.project')
    approval_ids = fields.One2many('purchase.requisition.approvals', 'requisition_id', string='Approvals')

    @api.model
    def create(self, vals):
        """Override the create method to automatically generate approval records."""
        requisition = super(PurchaseRequisition, self).create(vals)
        
        if requisition.project_id:
            # Get the approval group for the project
            approval_group = self.env['purchase.requisition.approvals.group'].search([('project_id', '=', requisition.project_id.id)], limit=1)
            
            if approval_group:
                # Get the roles for the approval group
                roles = self.env['purchase.requisition.approvals.group.role'].search([('approval_group_id', '=', approval_group.id)])
                
                # Create approval records for each role
                for role in roles:
                    self.env['purchase.requisition.approvals'].create({
                        'requisition_id': requisition.id,
                        'approval_group_id': role.group_id.id,
                        'approval_status': 'pending',
                        'sequence': role.sequence
                    })
        
        return requisition

class ReqisitionApprovalGroup(models.Model):
    _name = "purchase.requisition.approvals"
    _description = "Purchase Requisition Approvals"
    _order = "sequence"

    requisition_id = fields.Many2one('purchase.requisition', string='Purchase Requisition', required=True, ondelete='cascade')
    sequence = fields.Integer(string='Sequence', default=10, help="Defines the order of approval roles within the approval group.")
    approval_group_id = fields.Many2one('res.groups', string='Approval Group', required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', string='Approver')
    approval_status = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Approval Status', default='pending')
    
    date_approved = fields.Datetime(string='Approval Date')
    note = fields.Text(string='Note')
    
    # Logic to automatically approve if all conditions are met
    def approve(self):
        """Approve the requisition."""
        self.write({
            'approval_status': 'approved',
            'approval_date': fields.Datetime.now(),
        })

    def reject(self):
        """Reject the requisition."""
        self.write({
            'approval_status': 'rejected',
            'approval_date': fields.Datetime.now(),
        })

    