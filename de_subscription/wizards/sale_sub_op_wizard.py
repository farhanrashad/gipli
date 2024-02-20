# -*- coding: utf-8 -*-

from odoo import fields, models, _, api, Command, SUPERUSER_ID, modules
from odoo.exceptions import UserError, ValidationError

class OperationWizard(models.TransientModel):
    _name = 'sale.sub.op.wizard'
    _description = 'Subscription Operations Wizard'

    op_type = fields.Selection([
        ('renewal', 'Renewal'),  
        ('upsell', 'Upsell'),  
        ('revise', 'Revision'),
        ('close', 'Close'),
    ], 
        string='Operation', required=True, default="renewal",
    )
    subscription_close = fields.Boolean('Close', default=True)
    sub_close_reason_id = fields.Many2one('sale.sub.close.reason', string='Close Reason', ondelete='restrict', copy=False)

    def run_process(self):
        self.ensure_one()
        active_id = self.env.context.get('active_id', [])
        subscription_id = self.env['sale.order'].browse(active_id)
        if self.op_type == 'renewal':
            lang = subscription_id.partner_id.lang or self.env.user.lang
            renew_msg_body = self._get_order_digest(subscription_id, origin='renewal', lang=lang)
            action = self._prepare_new_subscription_order(subscription_id, self.op_type, renew_msg_body)
        
        #raise UserError(active_id)

    def _get_order_digest(self, subscription_id, origin='', template='de_subscription.subscription_order_digest', lang=None):
        self.ensure_one()
        values = {'origin': origin,
                  'record_url': subscription_id._get_html_link(),
                  'date_start': subscription_id.date_start,
                  'date_next_invoice': subscription_id.date_next_invoice,
                  #'recurring_monthly': self.recurring_monthly,
                  'untaxed_amount': subscription_id.amount_untaxed,
                  #'quotation_template': self.sale_order_template_id.name
                 } # see if we don't want plan instead
        return self.env['ir.qweb'].with_context(lang=lang)._render(template, values)
        
    def _prepare_new_subscription_order(self, subscription, subscription_state, message_body):
        order = self._create_new_subscription_order(subscription, subscription_state, message_body)
        action = self._get_associated_so_action()
        action['name'] = _('Upsell') if subscription_state == '7_upsell' else _('Renew')
        action['views'] = [(self.env.ref('de_subscription.subscription_order_primary_form_view').id, 'form')]
        action['res_id'] = order.id
        return action

    def _create_new_subscription_order(self, subscription, subscription_state, message_body):
        self.ensure_one()
        if subscription.date_start == subscription.date_next_invoice:
            raise ValidationError(_("You can not upsell or renew a subscription that has not been invoiced yet. "
                                    "Please, update directly the %s contract or invoice it first.", subscription.name))
        values = self._prepare_new_subscription_order_values(subscription, subscription_state)
        order = self.env['sale.order'].create(values)
        subscription.subscription_line_ids = [Command.link(order.id)]
        order.message_post(body=message_body)
        if subscription_state == '7_upsell':
            parent_message_body = _("An upsell quotation %s has been created", order._get_html_link())
        else:
            parent_message_body = _("A renewal quotation %s has been created", order._get_html_link())
        subscription.message_post(body=parent_message_body)
        order.order_line._compute_tax_id()
        return order

    def _prepare_new_subscription_order_values(self, subscription_id, subscription_state):
        """
        Create a new draft order with the same lines as the parent subscription. All recurring lines are linked to their parent lines
        :return: dict of new sale order values
        """
        self.ensure_one()
        today = fields.Date.today()
        if subscription_state == '7_upsell' and subscription_id.date_next_invoice <= max(self.first_contract_date or today, today):
            raise UserError(_('You cannot create an upsell for this subscription because it :\n'
                              ' - Has not started yet.\n'
                              ' - Has no invoiced period in the future.'))
        subscription = subscription_id #self.with_company(subscription.company_id)
        order_lines = subscription.order_line._get_renew_order_values(subscription_state, period_end=subscription_id.date_next_invoice)
        is_subscription = subscription_state == '2_renewal'
        option_lines_data = [Command.link(option.copy().id) for option in subscription.sale_order_option_ids]
        if subscription_state == '7_upsell':
            date_start = fields.Date.today()
            date_next_invoice = subscription_id.date_next_invoice
        else:
            # renewal
            date_start = subscription.date_next_invoice
            date_next_invoice = subscription.date_next_invoice # the next invoice date is the start_date for new contract
        return {
            'subscription_order': is_subscription,
            'new_subscription_id': subscription.id,
            'pricelist_id': subscription.pricelist_id.id,
            'partner_id': subscription.partner_id.id,
            'partner_invoice_id': subscription.partner_invoice_id.id,
            'partner_shipping_id': subscription.partner_shipping_id.id,
            'order_line': order_lines,
            'analytic_account_id': subscription.analytic_account_id.id,
            #'subscription_status': subscription_state,
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
    def _get_associated_so_action(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "views": [[self.env.ref('de_subscription.subscription_order_tree_view').id, "tree"],
                      [self.env.ref('de_subscription.subscription_order_primary_form_view').id, "form"],
                      [False, "kanban"], [False, "calendar"], [False, "pivot"], [False, "graph"]],
        }