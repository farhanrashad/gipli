# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
   
    
class ApprovalRequest(models.Model):
    _inherit = 'approval.request'
    
    def action_confirm(self):
        #request = super().action_confirm()
        #approvers = self.mapped('approver_ids').filtered(lambda approver: approver.status == 'new')
        approvers = self.env['approval.approver'].search([('status','=','new'),('request_id','=',self.id)],limit=1)
        for approver in approvers:
            approver.write({'status': 'pending'})
            #break
        self.write({
            'request_status':'pending'
        })
            
    def action_approve(self, approver=None):
        request = super().action_approve()
        approver_count = 0
        for approverid in self.approver_ids:
            if approverid.status == 'new':                
                approver_count = approver_count + 1
        if approver_count == 0:
            pass
        else:
            self.action_confirm()
        
    def action_refuse(self, approver=None):
        request = super().action_refuse()
        
        self.write({
            'request_status':'refused'
        })
        approver_count = 0
        for approverid in self.approver_ids:
            if approverid.status == 'new':
                approver_count = approver_count + 1
        if approver_count == 0:
            pass
        
    def recursive_manager(self, user_id):
        employee_id = self.env['hr.employee'].search([('user_id','=',user_id.id)], limit=1)   
        #manager_id = self.env['hr.employee'].search([('id','=',employee_id.parent_id.id)])
        return employee_id.parent_id.user_id #manager_id.user_id
    
    @api.constrains('category_id','request_owner_id')
    def _check_category(self):
        for record in self:
            if record.category_id:
                if record.category_id.approval_type == 'S':
                    approver_data = []
                    #category = self.env['approval.category'].search([('id','=', self.category_id.id)])
                    for approver in self.category_id.approval_category_line:
                        approver_data.append((0,0, {
                            'user_id': approver.user_id.id,
                        }))    
                    record.approver_ids = approver_data
                elif record.category_id.approval_type == 'D':
                    approver_data = []
                    approvers = []
                    approval_level = record.category_id.approval_level
                    approver = record.request_owner_id
                    if record.approver_ids:
                        record.approver_ids.sudo().unlink()
                    for level in range(approval_level, 0, -1):
                        approver = self.recursive_manager(approver)
                        if approver:
                            self.env['approval.approver'].create({
                                'request_id': record.id,
                                'user_id': approver.id,
                                'status' : 'new',  
                            })
       
                    
        
class ApprovalApproverInherit(models.Model):
    _inherit = 'approval.approver'
    
    department_id = fields.Many2one(related='user_id.department_id')
    job_title = fields.Char(related='user_id.job_title')
    sequence = fields.Integer(string='Sequence', default=10)



    

