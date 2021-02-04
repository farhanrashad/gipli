# -*- coding: utf-8 -*-
#################################################################################
# Author      : Dynexcel (<https://dynexcel.com/>)
# Copyright(c): 2015-Present dynexcel.com
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
#################################################################################


from odoo.exceptions import Warning
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class PaymentState(models.Model):
    _name = 'account.vendor_bill_state'
    _description = 'Vendor Bill State'

    name = fields.Char(string='Bill Status',help='maintain the states of the payment document')
    authority = fields.Many2one('res.groups')

class account_payment(models.Model):
    _inherit = 'account.move'
    
    state = fields.Selection([('draft', 'Draft'),
                              ('waiting', 'Waiting For Approval'),
                              ('approved', 'Approved'),
                              ('posted', 'Posted'),
                              ('cancel','Cancelled') ],
                             readonly=True, default='draft', copy=False, string="Status", track_visibility='onchange')


    def send_approval(self):
        self.write({'state': 'waiting'})
        self.message_post(body=_('Dear %s, bill is sent for approval.') % (self.env.user.name,),
                          partner_ids=[self.env.user.partner_id.id])

    def action_reset_draft(self):
        user = self.env.user.id
        record = self.env['bill.approval'].search([('approver_id', '=', user)])
        if record:
            for rec in record:
                if rec.submitted_id.id == self.invoice_user_id.id:
                    self.write({'state': 'draft'})
                    self.message_post(body=_('Dear %s, bill is Rejected from Approval.') % (self.env.user.name,),
                                      partner_ids=[self.env.user.partner_id.id])
        else:
            raise UserError(_('You have No Access Rights To Dis Approve The Bill'))

    def approve_bill(self):
        user = self.env.user.id
        record = self.env['bill.approval'].search([('approver_id', '=', user)])
        if record:
            for rec in record:
                if rec.submitted_id.id == self.invoice_user_id.id:
                    self.write({'state': 'approved'})
                    self.message_post(body=_('Dear %s, bill has approved.') % (self.env.user.name,),
                                      partner_ids=[self.env.user.partner_id.id])
        else:
            raise UserError(_('You have No Access Rights To Approve The Bill'))

    def action_post(self):
        self.message_post(body=_('Dear %s, bill has posted') % (self.env.user.name,),
                              partner_ids=[self.env.user.partner_id.id])
        res = super(account_payment, self).action_post()
      
        return res




class BillApproval(models.Model):
    _name = 'bill.approval'
    _description = 'vendor bill approval'

    submitted_id = fields.Many2one('res.users', string='Bill Submission By', required=True)
    approver_id = fields.Many2many('res.users', string='Bill approval By', required=True)

