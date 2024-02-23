# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta, date
from odoo import api, fields, models, _
from odoo.tools import float_compare, format_datetime, format_time
from pytz import timezone, UTC
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta

SUBSCRIPTION_DRAFT_STATUS = ['draft']
SUBSCRIPTION_PROGRESS_STATUS = ['progress']
SUBSCRIPTION_CLOSED_STATUS = ['CLOSE']

SUBSCRIPTION_STATUSES = [
    ('draft', 'Quotation'),  # Quotation for a new subscription
    ('progress', 'In Progress'),  # Active Subscription or confirmed renewal for active subscription
    ('paused', 'Paused'),
    ('close', 'Close'),  # Closed or ended subscription
]


class SubscriptionOrder(models.Model):
    _inherit = 'sale.order'

    def _get_default_subscription_plan(self):
        plan_id = self.env['sale.recur.plan'].search([('active','=',True)],limit=1)
        return plan_id

    
    subscription_order = fields.Boolean("Subscription")
    subscription_status = fields.Selection(
        string='Subscription Status',
        selection=SUBSCRIPTION_STATUSES,
        compute='_compute_subscription_status', store=True, index='btree_not_null', tracking=True, group_expand='_group_expand_states',
    )
    subscription_type = fields.Selection([
        ('normal', 'Normal'),
        ('renewal', 'Renewal'),  
        ('upsell', 'Upsell'),  
        ('revised', 'Revision'),
        ('close', 'Close'),
    ], 
        string='Subscription Type', default="normal",
    )
    

    subscription_plan_id = fields.Many2one('sale.recur.plan', string='Recurring Plan',
                            default=lambda s: s._get_default_subscription_plan(),
                              ondelete='restrict', readonly=False, store=True, index='btree_not_null')

    
    date_last_invoice = fields.Date(string='Last invoice date', compute='_compute_last_invoice_date')
    date_next_invoice = fields.Date(
        string='Date of Next Invoice',
        compute='_compute_next_invoice_date',
        store=True, copy=False,
        readonly=False,
        tracking=True,
        help="The next invoice will be created on this date then the period will be extended.")
    date_start = fields.Date(string='Start Date',
                             compute='_compute_date_start',
                             readonly=False,
                             store=True,
                             tracking=True,
                             help="The start date indicate when the subscription periods begin.")
    
    date_end = fields.Date(string='End Date', tracking=True,
                           compute='_compute_date_end',
                           readonly=False,
                           store=True,
                           help="If set in advance, the subscription will be set to renew 1 month before the date and will be closed on the date set in this field.")
    date_first_contract = fields.Date(
        compute='_compute_contact_start_date',
        store=True,
        help="The first contract date is the start date of the first contract of the sequence. It is common across a subscription and its renewals.")

    parent_subscription_id = fields.Many2one('sale.order', string='Parent Contract', ondelete='restrict', copy=False)
    subscription_line_ids = fields.One2many('sale.order', 'parent_subscription_id')

    sub_close_reason_id = fields.Many2one("sale.sub.close.reason", string="Close Reason", copy=False, tracking=True)
    
    # Count Fields
    count_past_subscriptions = fields.Integer(compute='_compute_past_subscriptions')
    count_upselling_subscriptions = fields.Integer(compute='_compute_upselling_count')
    count_renewal_subscriptions = fields.Integer(compute="_compute_renewal_count")
    count_revised_subscriptions = fields.Integer(compute="_compute_revised_count")

    amount_total_subscription = fields.Monetary(compute='_compute_subscription_total', string="Total Subscription", store=True)
    amount_monthly_subscription = fields.Monetary(compute='_compute_monthly_subsccription', string="Monthly Subscription",
                                        store=True, tracking=True)
    non_recurring_total = fields.Monetary(compute='_compute_non_recurring_total', string="Total Non Recurring Revenue")
    
    # =======================================================================
    # ========================== Computed Mehtods ===========================
    # =======================================================================

    @api.depends('subscription_status', 'state', 'subscription_order', 'amount_untaxed')
    def _compute_subscription_total(self):
        for order in self:
            if order.subscription_order:
                order.amount_total_subscription = sum(order.order_line.filtered(lambda l: l.product_id.is_recurring).mapped('price_subtotal'))
                continue
            order.amount_total_subscription = 0

    @api.depends('subscription_status', 'state', 'subscription_order', 'amount_untaxed')
    def _compute_monthly_subsccription(self):
        """ Compute the amount monthly recurring revenue. When a subscription has a parent still ongoing.
        Depending on invoice_ids force the recurring monthly to be recomputed regularly, even for the first invoice
        where confirmation is set the next_invoice_date and first invoice do not update it (in automatic mode).
        """
        for order in self:
            if order.subscription_order:
                order.amount_monthly_subscription = sum(order.order_line.mapped('amount_monthly_subscription'))
                continue
            order.amount_monthly_subscription = 0
            
    def _compute_past_subscriptions(self):
        for order in self:
            subscription_ids = self.env['sale.order'].search([('parent_subscription_id', '=', order.id)])
            order.count_past_subscriptions = len(subscription_ids)

    def _compute_upselling_count(self):
        for order in self:
            subscription_ids = self.env['sale.order'].search([('parent_subscription_id', '=', order.id),('subscription_type','=','upsell')])
            order.count_upselling_subscriptions = len(subscription_ids)

    def _compute_renewal_count(self):
        for order in self:
            subscription_ids = self.env['sale.order'].search([('parent_subscription_id', '=', order.id),('subscription_type','=','renewal')])
            order.count_renewal_subscriptions = len(subscription_ids)

    def _compute_revised_count(self):
        for order in self:
            subscription_ids = self.env['sale.order'].search([('parent_subscription_id', '=', order.id),('subscription_type','=','revised')])
            order.count_revised_subscriptions = len(subscription_ids)
        
    @api.depends('subscription_order')
    def _compute_subscription_status(self):
        
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            #elif order.subscription_status in ['2_renewal', '7_upsell']:
            #    continue
            elif order.subscription_order or order.state == 'draft' and order.subscription_status == 'draft':
                # We keep the subscription state 1_draft to keep the subscription quotation in the subscription app
                # quotation view.
                #    order.subscription_status = '2_renewal' if order.subscription_id else '1_draft'
                order.subscription_status = 'draft'
            else:
                order.subscription_status = False
                
    def _group_expand_states(self, states, domain, order):
        return ['progress', 'close']


    @api.depends('date_start', 'state', 'date_next_invoice')
    def _compute_last_invoice_date(self):
        for order in self:
            last_date = order.date_next_invoice and order.subscription_plan_id.billing_period and order.date_next_invoice - order.subscription_plan_id.billing_period
            date_start = order.date_start or fields.Date.today()
            if order.state == 'sale' and last_date and last_date >= date_start:
                # we use get_timedelta and not the effective invoice date because
                # we don't want gaps. Invoicing date could be shifted because of technical issues.
                order.date_last_invoice = last_date
            else:
                order.date_last_invoice = False

    @api.depends(
        'subscription_order', 
        'state', 
        'date_start', 
        'subscription_status',
        'order_line',
        'order_line.invoice_lines',
        'order_line.invoice_lines.parent_state',
        'order_line.invoice_lines.move_id.state',
    )
    def _compute_next_invoice_date(self):
         for so in self:
            invoices = so.order_line.invoice_lines.mapped('move_id')
            if not so.subscription_order and so.subscription_type != 'upsell':
                so.date_next_invoice = False
            elif not so.date_next_invoice and so.state == 'sale':
                so.date_next_invoice = so.date_start or fields.Date.today()
            else:
                if invoices or len(invoices):
                    kwargs = {so.subscription_plan_id.recurring_interval_type+"s": len(invoices)}
                    so.date_next_invoice = so.date_start + relativedelta(**kwargs)

                

    @api.depends('subscription_order', 'state', 'subscription_status','subscription_plan_id')
    def _compute_date_start(self):
        for so in self:
            if not so.subscription_order:
                so.date_start = False
            elif not so.date_start:
                    so.date_start = fields.Date.today()

    @api.depends('date_start','subscription_plan_id')
    def _compute_date_end(self):
        for so in self:
            if not so.subscription_order:
                so.date_end = False
            elif not so.date_end:
                    kwargs = {so.subscription_plan_id.recurring_interval_type+"s": so.subscription_plan_id.intervals_total}
                    date_end = so.date_start + relativedelta(**kwargs)
                    so.date_end = date_end
                
    @api.depends('date_start')
    def _compute_contact_start_date(self):
        for so in self:
            so.date_first_contract = so.date_start
                
    # =========================================================================
    # ============================ Action Button ==============================
    # =========================================================================
    def action_confirm(self):
        """Update and/or create subscriptions on order confirmation."""
        recurring_order = self.env['sale.order']
        for order in self:
            res_sub = super(SubscriptionOrder, self).action_confirm()
            order.write({
                'subscription_status': 'progress',
            })

        return res_sub

    def button_operations(self):
        self.ensure_one()
        return {
            'name': 'Operations',
            'view_mode': 'form',
            'res_model': 'sale.sub.op.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'subscription_id': self.id,
            },
        }

    def open_subscription_renewal(self):
        return {
            'name': 'Renewed Subscriptions',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'domain': [('parent_subscription_id','=',self.id),('subscription_type','=','renewal')],
            'action_id': self.env.ref('de_subscription.action_subscription_order').id,
        }

    def open_subscription_upsell(self):
        return {
            'name': 'Upselling Subscriptions',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'domain': [('parent_subscription_id','=',self.id),('subscription_type','=','upsell')],
            'action_id': self.env.ref('de_subscription.action_subscription_order').id,
        }

    def open_past_subscriptions(self):
        return {
            'name': 'Upselling Subscriptions',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'domain': [('parent_subscription_id','=',self.id)],
            'action_id': self.env.ref('de_subscription.action_subscription_order').id,
        }

    def open_revised_subscriptions(self):
        return {
            'name': 'Upselling Subscriptions',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'domain': [('parent_subscription_id','=',self.id),('subscription_type','=','revised')],
            'action_id': self.env.ref('de_subscription.action_subscription_order').id,
        }

    def _action_cancel(self):
        for order in self:
            if order.subscription_type == 'upsell':
                cancel_message_body = _("The upsell %s has been canceled.", order._get_html_link())
                order.parent_subscription_id.message_post(body=cancel_message_body)
            elif order.subscription_type == 'renewal':
                cancel_message_body = _("The renewal %s has been canceled.", order._get_html_link())
                order.parent_subscription_id.message_post(body=cancel_message_body)
            elif (order.subscription_status in SUBSCRIPTION_PROGRESS_STATUS + SUBSCRIPTION_DRAFT_STATUS
                  and not any(state in ['draft', 'posted'] for state in order.order_line.invoice_lines.move_id.mapped('state'))):
                order.subscription_status = False
            elif order.subscription_status in SUBSCRIPTION_PROGRESS_STATUS:
                raise ValidationError(_('You cannot cancel a subscription that has been invoiced.'))
        return super()._action_cancel()

    def action_subscription_pause(self):
        self.filtered(lambda so: so.subscription_status == 'progress').write({'subscription_status': 'paused'})

    def resume_subscription(self):
        self.filtered(lambda so: so.subscription_status == 'paused').write({'subscription_status': 'progress'})

    def _create_invoices(self, grouped=False, final=False, date=None):
        """ Override to increment periods when needed """
        order_already_invoiced = self.env['sale.order']
        for order in self:
            if not order.subscription_order:
                continue
            if order.order_line.invoice_lines.move_id.filtered(lambda r: r.move_type in ('out_invoice', 'out_refund') and r.state == 'draft'):
                order_already_invoiced |= order

        
        if order_already_invoiced:
            order_error = ", ".join(order_already_invoiced.mapped('name'))
            raise ValidationError(_("The following recurring orders have draft invoices. Please Confirm them or cancel them "
                                    "before creating new invoices. %s.", order_error))
        invoices = super()._create_invoices(grouped=grouped, final=final, date=date)
        #invoices = self._create_invoices2(grouped=grouped, final=final, date=date)
        return invoices

    # ========================================================================
    def _get_invoiceable_lines(self, final=False):
        date_from = fields.Date.today()
        res = super()._get_invoiceable_lines(final=final)
        res = res.filtered(lambda l: not l.is_recurring or l.order_id.subscription_type == 'upsell')
        automatic_invoice = self.env.context.get('recurring_automatic')

        invoiceable_line_ids = []
        downpayment_line_ids = []
        pending_section = None
        for line in self.order_line:
            if line.display_type == 'line_section':
                # Only add section if one of its lines is invoiceable
                pending_section = line
                continue

            if line.state != 'sale':
                continue

            if automatic_invoice:
                # We don't invoice line before their SO's next_invoice_date
                line_condition = line.order_id.date_next_invoice and line.order_id.date_next_invoice <= date_from and line.order_id.date_start and line.order_id.date_start <= date_from
            else:
                # We don't invoice line past their SO's date_end
                line_condition = not line.order_id.date_end or (line.order_id.date_next_invoice and line.order_id.date_next_invoice < line.order_id.date_end)

            line_to_invoice = False
            if line in res:
                # Line was already marked as to be invoiced
                line_to_invoice = True
            elif line.order_id.subscription_type == 'upsell':
                # Super() already select everything that is needed for upsells
                line_to_invoice = False
            elif line.display_type or not line.is_recurring:
                # Avoid invoicing section/notes or lines starting in the future or not starting at all
                line_to_invoice = False
            elif line_condition:
                if(
                    line.product_id.invoice_policy == 'order'
                    and line.order_id.subscription_type != 'renewed'
                ):
                    # Invoice due lines
                    line_to_invoice = True
                elif (
                    line.product_id.invoice_policy == 'delivery'
                    and not float_is_zero(
                        line.qty_delivered,
                        precision_rounding=line.product_id.uom_id.rounding,
                    )
                ):
                    line_to_invoice = True

            if line_to_invoice:
                if line.is_downpayment:
                    # downpayment line must be kept at the end in its dedicated section
                    downpayment_line_ids.append(line.id)
                    continue
                if pending_section:
                    invoiceable_line_ids.append(pending_section.id)
                    pending_section = False
                invoiceable_line_ids.append(line.id)

        return self.env["sale.order.line"].browse(invoiceable_line_ids + downpayment_line_ids)

    @api.model
    def _process_invoices_to_send(self, account_moves):
        for invoice in account_moves:
            if not invoice.is_move_sent and invoice._is_ready_to_be_sent() and invoice.state == 'posted':
                subscription = invoice.line_ids.subscription_id
                subscription.validate_and_send_invoice(invoice)
                invoice.message_subscribe(subscription.user_id.partner_id.ids)
            elif invoice.line_ids.subscription_id:
                invoice.message_subscribe(invoice.line_ids.subscription_id.user_id.partner_id.ids)

    # =========================================================
    # Crone Jobs =========================
    # =========================================================
    def _cron_expire_subscription_orders(self):
        # Flush models according to following SQL requests
        self.env['sale.order'].flush_model(
            fnames=['order_line', 'subscription_plan_id', 'state', 'subscription_status', 'date_next_invoice'])
        self.env['account.move'].flush_model(fnames=['payment_state', 'line_ids'])
        self.env['account.move.line'].flush_model(fnames=['move_id', 'sale_line_ids'])
        self.env['sale.subscription.plan'].flush_model(fnames=['auto_close_limit'])
        today = fields.Date.today()
        # set to close if date is passed or if renewed sale order passed
        domain_close = [
            ('subscription_order', '=', True),
            ('date_end', '<', today),
            ('state', '=', 'sale'),
            ('subscription_status', 'in', SUBSCRIPTION_PROGRESS_STATUS)]
        subscriptions_close = self.search(domain_close)
        unpaid_results = self._handle_unpaid_subscriptions()
        unpaid_ids = unpaid_results.keys()
        expired_result = self._get_expired_subscriptions()
        expired_ids = [r['so_id'] for r in expired_result]
        subscriptions_close |= self.env['sale.order'].browse(unpaid_ids) | self.env['sale.order'].browse(expired_ids)
        auto_commit = not bool(config['test_enable'] or config['test_file'])
        #expired_close_reason = self.env.ref('de_subscription.close_reason_auto_close_limit_reached')
        unpaid_close_reason = self.env.ref('de_subscription.close_reason_unpaid_subscription')
        for batched_to_close in split_every(30, subscriptions_close.ids, self.env['sale.order'].browse):
            unpaid_so = self.env['sale.order']
            expired_so = self.env['sale.order']
            for so in batched_to_close:
                if so.id in unpaid_ids:
                    unpaid_so |= so
                    account_move = self.env['account.move'].browse(unpaid_results[so.id])
                    so.message_post(
                        body=_("The last invoice (%s) of this subscription is unpaid after the due date.",
                               account_move._get_html_link()),
                        partner_ids=so.team_user_id.partner_id.ids,
                    )
                elif so.id in expired_ids:
                    expired_so |= so

            unpaid_so.set_close(close_reason_id=unpaid_close_reason.id)
            expired_so.set_close(close_reason_id=expired_close_reason.id)
            (batched_to_close - unpaid_so - expired_so).set_close()
            if auto_commit:
                self.env.cr.commit()
        return dict(closed=subscriptions_close.ids)

    def _cron_create_subscription_invoice(self):
        deferred_account = self.env.company.deferred_revenue_account_id
        deferred_journal = self.env.company.deferred_journal_id
        if not deferred_account or not deferred_journal:
            raise ValidationError(_("The deferred settings are not properly set. Please complete them to generate subscription deferred revenues"))
        return self._create_recurring_invoice()

    def _create_recurring_invoice(self, batch_size=30):
        today = fields.Date.today()
        auto_commit = not bool(config['test_enable'] or config['test_file'])
        grouped_invoice = self.env['ir.config_parameter'].get_param('sale_subscription.invoice_consolidation', False)
        all_subscriptions, need_cron_trigger = self._recurring_invoice_get_subscriptions(grouped=grouped_invoice, batch_size=batch_size)
        if not all_subscriptions:
            return self.env['account.move']

        # We mark current batch as having been seen by the cron
        all_invoiceable_lines = self.env['sale.order.line']
        for subscription in all_subscriptions:
            subscription.is_invoice_cron = True
            # Don't spam sale with assigned emails.
            subscription = subscription.with_context(mail_auto_subscribe_no_notify=True)
            # Close ending subscriptions
            auto_close_subscription = subscription.filtered_domain([('end_date', '!=', False)])
            closed_contract = auto_close_subscription._subscription_auto_close()
            subscription -= closed_contract
            all_invoiceable_lines += subscription.with_context(recurring_automatic=True)._get_invoiceable_lines()

        lines_to_reset_qty = self.env['sale.order.line']
        account_moves = self.env['account.move']
        move_to_send_ids = []
        # Set quantity to invoice before the invoice creation. If something goes wrong, the line will appear as "to invoice"
        # It prevents the use of _compute method and compare the today date and the next_invoice_date in the compute which would be bad for perfs
        all_invoiceable_lines._reset_subscription_qty_to_invoice()
        self._subscription_commit_cursor(auto_commit)
        for subscription in all_subscriptions:
            if len(subscription) == 1:
                subscription = subscription[0]  # Trick to not prefetch other subscriptions is all_subscription is recordset, as the cache is currently invalidated at each iteration

            # We check that the subscription should not be processed or that it has not already been set to "in exception" by previous cron failure
            # We only invoice contract in sale state. Locked contracts are invoiced in advance. They are frozen.
            subscription = subscription.filtered(lambda sub: sub.subscription_state == '3_progress' and not sub.payment_exception)
            if not subscription:
                continue
            try:
                self._subscription_commit_cursor(auto_commit)  # To avoid a rollback in case something is wrong, we create the invoices one by one
                draft_invoices = subscription.invoice_ids.filtered(lambda am: am.state == 'draft')
                if subscription.payment_token_id and draft_invoices:
                    draft_invoices.button_cancel()
                elif draft_invoices:
                    # Skip subscription if no payment_token, and it has a draft invoice
                    continue
                invoiceable_lines = all_invoiceable_lines.filtered(lambda l: l.order_id.id in subscription.ids)
                invoice_is_free, is_exception = subscription._invoice_is_considered_free(invoiceable_lines)
                if not invoiceable_lines or invoice_is_free:
                    if is_exception:
                        for sub in subscription:
                            # Mix between recurring and non-recurring lines. We let the contract in exception, it should be
                            # handled manually
                            msg_body = _(
                                "Mix of negative recurring lines and non-recurring line. The contract should be fixed manually",
                                inv=sub.next_invoice_date
                            )
                            sub.message_post(body=msg_body)
                        subscription.payment_exception = True
                    # We still update the next_invoice_date if it is due
                    elif subscription.next_invoice_date and subscription.next_invoice_date <= today:
                        subscription._update_next_invoice_date()
                        if invoice_is_free:
                            for line in invoiceable_lines:
                                line.qty_invoiced = line.product_uom_qty
                            subscription._subscription_post_success_free_renewal()
                    continue

                try:
                    invoice = subscription.with_context(recurring_automatic=True)._create_invoices(final=True)
                    lines_to_reset_qty |= invoiceable_lines
                except Exception as e:
                    # We only raise the error in test, if the transaction is broken we should raise the exception
                    if not auto_commit and isinstance(e, TransactionRollbackError):
                        raise
                    # we suppose that the payment is run only once a day
                    self._subscription_rollback_cursor(auto_commit)
                    for sub in subscription:
                        email_context = sub._get_subscription_mail_payment_context()
                        error_message = _("Error during renewal of contract %s (Payment not recorded)", sub.name)
                        _logger.exception(error_message)
                        body = self._get_traceback_body(e, error_message)
                        mail = self.env['mail.mail'].sudo().create(
                            {'body_html': body, 'subject': error_message,
                             'email_to': email_context['responsible_email'], 'auto_delete': True})
                        mail.send()
                    continue
                self._subscription_commit_cursor(auto_commit)
                # Handle automatic payment or invoice posting

                existing_invoices = subscription.with_context(recurring_automatic=True)._handle_automatic_invoices(invoice, auto_commit) or self.env['account.move']
                account_moves |= existing_invoices
                subscription.with_context(mail_notrack=True).payment_exception = False
                if not subscription.mapped('payment_token_id'): # _get_auto_invoice_grouping_keys groups by token too
                    move_to_send_ids += existing_invoices.ids
            except Exception:
                name_list = [f"{sub.name} {sub.client_order_ref}" for sub in subscription]
                _logger.exception("Error during renewal of contract %s", "; ".join(name_list))
                self._subscription_rollback_cursor(auto_commit)
        self._subscription_commit_cursor(auto_commit)
        self._process_invoices_to_send(self.env['account.move'].browse(move_to_send_ids))
        # There is still some subscriptions to process. Then, make sure the CRON will be triggered again asap.
        if need_cron_trigger:
            self._subscription_launch_cron_parallel(batch_size)
        else:
            self.env['sale.order']._post_invoice_hook()
            failing_subscriptions = self.search([('is_batch', '=', True)])
            failing_subscriptions.write({'is_batch': False})

        return account_moves