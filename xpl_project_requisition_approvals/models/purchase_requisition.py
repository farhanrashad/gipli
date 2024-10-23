
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

    def action_confirm(self):
        self.ensure_one()

        # Custom approval logic: Check if all approval records are approved
        if self.approval_ids:
            # Check if any approval is not 'approved'
            if any(approval.approval_status != 'approved' for approval in self.approval_ids):
                raise UserError(_("You cannot confirm the requisition '%s' because all approvals must be completed.") % self.name)

        # Call the original `action_confirm` logic (existing functionality)
        super(PurchaseRequisition, self).action_confirm()


class ReqisitionApprovalGroup(models.Model):
    _name = "purchase.requisition.approvals"
    _description = "Purchase Requisition Approvals"
    _order = "requisition_id, sequence"
    _rec_name = "user_id"

    requisition_id = fields.Many2one('purchase.requisition', string='Purchase Requisition', required=True, ondelete='cascade')
    sequence = fields.Integer(string='Sequence', default=10, help="Defines the order of approval roles within the approval group.")
    approval_group_id = fields.Many2one('res.groups', string='Approval Group', required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', string='Approver')
    approval_status = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', default='pending')
    
    date_approved = fields.Datetime(string='Approval Date')
    note = fields.Text(string='Note')

    is_user_approved = fields.Boolean(compute='_compute_is_user_approval', store=True)


    # Logic to automatically approve if all conditions are met
    def action_button_approve(self):
        # Check if the current user has the rights for the approval group
        if not (self.approval_group_id & self.env.user.groups_id):
            raise ValidationError(_("You do not have the required rights to approve this request."))
            
        self._check_previous_approvals()
        
        self.write({
            'approval_status': 'approved',
            'date_approved': fields.Datetime.now(),
            'user_id': self.env.user.id,
        })

        # Log a message in the requisition's chatter
        self.approval_message(
            _("Approval from %s has been completed.") % (self.env.user.name)
        )
    
        # Check if all approvals are now approved, and confirm the requisition if true
        if self._check_all_approvals_approved():
            self.requisition_id.sudo().action_confirm()
        

    def action_button_reject(self):
        # Check if the current user has the rights for the approval group
        if not (self.approval_group_id & self.env.user.groups_id):
            raise ValidationError(_("You do not have the required rights to reject this request."))
            
        self.write({
            'approval_status': 'rejected',
            'date_approved': fields.Datetime.now(),
            'user_id': self.env.user.id,
        })
        # Log a message in the requisition's chatter
        self.approval_message(
            _("Approval from %s has been rejected.") % (self.env.user.name)
        )
        self.requisition_id.sudo().action_cancel()

    def _check_previous_approvals(self):
        previous_approvals = self.search([
            ('requisition_id', '=', self.requisition_id.id),
            ('sequence', '<', self.sequence),
            ('approval_status', '!=', 'approved')
        ])
        if previous_approvals:
            raise ValidationError(_("You cannot approve this record until all prior approvals have been approved."))

    def _check_all_approvals_approved(self):
        """
        Helper method to check if all approvals for the requisition are in the 'approved' state.
        The requisition can only be confirmed if all approval statuses are 'approved'.
        """
        approvals = self.search([
            ('requisition_id', '=', self.requisition_id.id),
        ])
        
        # Check if there are any pending or rejected approvals
        non_approved = approvals.filtered(lambda a: a.approval_status != 'approved')
        
        # If there are any non-approved approvals (pending/rejected), return False
        if non_approved:
            return False
        
        # If all approvals are approved, return True
        return True

    def approval_message(self, message):
        self.requisition_id.message_post(
            body=message,
            message_type='notification',
            subtype_xmlid='mail.mt_note'
        )

    @api.depends('approval_group_id')
    def _compute_is_user_approval(self):
        for record in self:
            record.is_user_approved = record.approval_group_id.id in self.env.user.groups_id.ids



    


    