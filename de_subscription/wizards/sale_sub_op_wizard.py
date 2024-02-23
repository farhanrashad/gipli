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
            renew_msg_body = self._get_order_digest(origin=self.op_type, lang=lang)
            action = self._prepare_new_subscription_order(renew_msg_body)

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
        

    def _get_order_digest(self, origin='', template='de_subscription.subscription_order_digest', lang=None):
        self.ensure_one()
        values = {'origin': origin,
                  'record_url': self.subscription_id._get_html_link(),
                  'date_start': self.subscription_id.date_start,
                  'date_next_invoice': self.subscription_id.date_next_invoice,
                  'amount_monthly_subscription': self.subscription_id.amount_monthly_subscription,
                  'untaxed_amount': self.subscription_id.amount_untaxed,
                  #'quotation_template': self.sale_order_template_id.name
                 } # see if we don't want plan instead
        return self.env['ir.qweb'].with_context(lang=lang)._render(template, values)
        
    def _prepare_new_subscription_order(self, message_body):
        order = self._create_new_subscription_order(message_body)
        action = self._get_associated_so_action(order)
        action['name'] = self.op_type
        action['views'] = [(self.env.ref('de_subscription.subscription_order_primary_form_view').id, 'form')]
        action['res_id'] = order.id
        return action

    def _create_new_subscription_order(self, message_body):
        self.ensure_one()
        subscription = self.subscription_id
        
        if subscription.date_start == subscription.date_next_invoice:
            raise ValidationError("You cannot perform an upsell or renewal on a subscription that has not yet been invoiced. "
                      "Please ensure that the subscription '%s' is invoiced before proceeding." % subscription.name)
    
        new_order_values = self._prepare_new_subscription_order_values()
        new_order = self.env['sale.order'].create(new_order_values)
        subscription.subscription_line_ids = [(4, new_order.id)]
        new_order.message_post(body=message_body)
    
        if self.op_type == 'upsell':
            parent_message_body = _("An upsell quotation %s has been created", new_order._get_html_link())
        elif self.op_type == 'revised':
            parent_message_body = _("An revised quotation %s has been created", new_order._get_html_link())
        elif self.op_type == 'renewal':
            parent_message_body = _("A renewal quotation %s has been created", new_order._get_html_link())
        else:
            parent_message_body = _("A subscription %s has been closed", new_order._get_html_link())
        
        subscription.message_post(body=parent_message_body)
        new_order.order_line._compute_tax_id()
        
        return new_order

    def _prepare_new_subscription_order_values(self):
        self.ensure_one()
        today = fields.Date.today()
        subscription = self.subscription_id
    
        if subscription.subscription_type == 'upsell' and subscription.date_next_invoice <= max(subscription.date_first_contract or today, today):
            raise UserError("You cannot create an upsell for this subscription because it:\n"
                            "- Has not started yet.\n"
                            "- Has no invoiced period in the future.")
    
        order_lines = subscription.order_line._get_renew_order_values(subscription, period_end=subscription.date_next_invoice)    
        if subscription.subscription_type == 'upsell':
            date_start = today
            date_next_invoice = subscription.date_next_invoice
        else:
            date_start = subscription.date_next_invoice
            date_next_invoice = subscription.date_next_invoice  # The next invoice date is the start_date for new contract
    
        return {
            'subscription_order': True,
            'parent_subscription_id': subscription.id,
            'pricelist_id': subscription.pricelist_id.id,
            'partner_id': subscription.partner_id.id,
            'partner_invoice_id': subscription.partner_invoice_id.id,
            'partner_shipping_id': subscription.partner_shipping_id.id,
            'order_line': order_lines,
            'analytic_account_id': subscription.analytic_account_id.id,
            'subscription_type': self.op_type,
            'origin': subscription.client_order_ref,
            'client_order_ref': subscription.client_order_ref,
            'note': subscription.note,
            'user_id': subscription.user_id.id,
            'payment_term_id': subscription.payment_term_id.id,
            'company_id': subscription.company_id.id,
            'date_start': date_start,
            'date_next_invoice': date_next_invoice,
            'subscription_plan_id': subscription.subscription_plan_id.id,
        }

    @api.model
    def _get_associated_so_action(self, order):
        return {
                'name': order.subscription_type,
                'view_mode': 'form',
                'res_model': 'sale.order',
                'res_id': order.id,
                'type': 'ir.actions.act_window',
            }