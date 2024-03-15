# -*- coding: utf-8 -*-

from odoo import fields, models, _, api, Command, SUPERUSER_ID, modules
from odoo.exceptions import UserError, ValidationError
from odoo.tools import html_escape
from odoo.tools import date_utils

class OperationWizard(models.TransientModel):
    _name = 'sale.sub.op.wizard'
    _description = 'Subscription Operations Wizard'

    op_type = fields.Selection([
        ('renewal', 'Renewal'),  
        ('upsell', 'Upsell'),  
        ('revised', 'Revision'),
        ('close', 'Close'),
    ], 
        string='Operation', required=True, default="renewal",
    )
    sub_close_reason_id = fields.Many2one('sale.sub.close.reason', string='Close Reason', ondelete='restrict', copy=False)

    subscription_id = fields.Many2one('sale.order', string='Subscription', copy=False, readonly=True)


    @api.model
    def default_get(self, fields):
        res = super(OperationWizard, self).default_get(fields)
        if 'subscription_id' in self._context:
            res['subscription_id'] = self._context.get('subscription_id')
        return res
        
    def run_process(self):
        self.ensure_one()
        active_id = self.env.context.get('active_id', [])
        subscription_id = self.env['sale.order'].browse(active_id)
        related_subscription_ids = self.env['sale.order'].search([
            ('parent_subscription_id','=',self.subscription_id.id),
            ('state','!=','cancel'),
        ])
            
        if self.op_type == 'renewal':            
            if related_subscription_ids or len(related_subscription_ids):
                raise UserError(_('You can not create multiple upsell or renew subscriptions. \n'
                              'Please process the existing contract first.'))
            
        if self.op_type != 'close':
            if subscription_id.date_start == subscription_id.date_next_invoice:
                raise UserError(_("You can not upsell or renew a subscription that has not been invoiced yet. "
                                    "Please, update directly the %s contract or invoice it first.", subscription_id.name))
                
            lang = subscription_id.partner_id.lang or self.env.user.lang
            renew_msg_body = self.subscription_id._get_order_subscription_digest(origin=self.op_type, lang=lang)
            raise UserError(renew_msg_body)
            action = self.subscription_id._prepare_new_subscription_order(self.op_type, renew_msg_body)

            if self.op_type in ('renewal','revised'):
                subscription_id.write({
                    'subscription_status': 'close',
                    'sub_close_reason_id': self.sub_close_reason_id.id,
                })
            return action
            
        else:
            subscription_id.write({
                    'subscription_status': 'close',
                    'sub_close_reason_id': self.sub_close_reason_id.id,
                })
        

    