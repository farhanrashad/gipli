# -*- coding: utf-8 -*-

from odoo import fields, models, _, api, Command, SUPERUSER_ID, modules
from odoo.exceptions import UserError, ValidationError

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
    subscription_close = fields.Boolean('Close', default=True)
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
        if related_subscription_ids or len(related_subscription_ids):
            raise UserError(_('You can not create multiple upsell or renew subscriptions. \n'
                              'Please process the existing contract first.'))
            
        if self.op_type == 'renewal':
            if subscription_id.date_start == subscription_id.date_next_invoice:
                raise ValidationError(_("You can not upsell or renew a subscription that has not been invoiced yet. "
                                    "Please, update directly the %s contract or invoice it first.", subscription_id.name))
            
            lang = subscription_id.partner_id.lang or self.env.user.lang
            renew_msg_body = self._get_order_digest(origin='renewal', lang=lang)
            action = self._prepare_new_subscription_order(renew_msg_body)
            subscription_id.write({
                'subscription_status': 'close',
                'sub_close_reason_id': self.sub_close_reason_id.id,
            })
            return action

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
        action['name'] = _('Upsell') if self.subscription_id.subscription_type == 'upsell' else _('Renew')
        action['views'] = [(self.env.ref('de_subscription.subscription_order_primary_form_view').id, 'form')]
        action['res_id'] = order.id
        return action

    def _create_new_subscription_order(self, message_body):
        self.ensure_one()
        if self.subscription_id.date_start == self.subscription_id.date_next_invoice:
            raise ValidationError(_("You can not upsell or renew a subscription that has not been invoiced yet. "
                                    "Please, update directly the %s contract or invoice it first.", self.subscription_id.name))
        values = self._prepare_new_subscription_order_values()
        order = self.env['sale.order'].create(values)
        self.subscription_id.subscription_line_ids = [Command.link(order.id)]
        order.message_post(body=message_body)
        if self.subscription_id.subscription_type == 'upsell':
            parent_message_body = _("An upsell quotation %s has been created", order._get_html_link())
        else:
            parent_message_body = _("A renewal quotation %s has been created", order._get_html_link())
        self.subscription_id.message_post(body=parent_message_body)
        order.order_line._compute_tax_id()
        return order

    def _prepare_new_subscription_order_values(self):
        """
        Create a new draft order with the same lines as the parent subscription. All recurring lines are linked to their parent lines
        :return: dict of new sale order values
        """
        self.ensure_one()
        today = fields.Date.today()
            
        if self.subscription_id.subscription_type == 'upsell' and self.subscription_id.date_next_invoice <= max(self.subscription_id.date_first_contract or today, today):
            raise UserError(_('You cannot create an upsell for this subscription because it :\n'
                              ' - Has not started yet.\n'
                              ' - Has no invoiced period in the future.'))
        subscription = self.subscription_id
        order_lines = subscription.order_line._get_renew_order_values(self.subscription_id, period_end=self.subscription_id.date_next_invoice)
        is_subscription = self.subscription_id.subscription_type == 'renewal'
        option_lines_data = [Command.link(option.copy().id) for option in subscription.sale_order_option_ids]
        if self.subscription_id.subscription_type == 'upsell':
            date_start = fields.Date.today()
            date_next_invoice = subscription_id.date_next_invoice
        else:
            # renewal
            date_start = subscription.date_next_invoice
            date_next_invoice = subscription.date_next_invoice # the next invoice date is the start_date for new contract
        return {
            'subscription_order': True,
            'parent_subscription_id': subscription.id,
            'pricelist_id': subscription.pricelist_id.id,
            'partner_id': subscription.partner_id.id,
            'partner_invoice_id': subscription.partner_invoice_id.id,
            'partner_shipping_id': subscription.partner_shipping_id.id,
            'order_line': order_lines,
            'analytic_account_id': subscription.analytic_account_id.id,
            #'subscription_status': 'draft',
            'subscription_type': self.op_type,
            'origin': subscription.client_order_ref,
            'client_order_ref': subscription.client_order_ref,
            #'origin_order_id': subscription.origin_order_id.id,
            'note': subscription.note,
            'user_id': subscription.user_id.id,
            'payment_term_id': subscription.payment_term_id.id,
            'company_id': subscription.company_id.id,
            #'sale_order_template_id': self.sale_order_template_id.id,
            'sale_order_option_ids': option_lines_data,
            #'payment_token_id': False,
            'date_start': date_start,
            'date_next_invoice': date_next_invoice,
            'subscription_plan_id': subscription.subscription_plan_id.id,
        }
        
    @api.model
    def _get_associated_so_action(self, order):
        return {
                'name': 'Renewal',
                'view_mode': 'form',
                'res_model': 'sale.order',
                'res_id': order.id,
                'type': 'ir.actions.act_window',
            }