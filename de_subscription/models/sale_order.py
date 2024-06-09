# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta, date
from odoo import api, fields, models, _
from odoo.tools import float_compare, format_datetime, format_time
from pytz import timezone, UTC
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


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
        compute='_compute_subscription_status', store=True, index='btree_not_null', tracking=True, group_expand='_group_expand_subscription_status',
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

    
    date_last_invoice = fields.Date(string='Last invoice date', compute='_compute_date_last_invoice')
    date_next_invoice = fields.Date(
        string='Date of Next Invoice',
        compute='_compute_date_next_invoice',
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
        readonly=True,
        help="The first contract date is the start date of the first contract of the sequence. It is common across a subscription and its renewals.")

    parent_subscription_id = fields.Many2one('sale.order', string='Parent Contract', copy=False)
    subscription_line_ids = fields.One2many('sale.order', 'parent_subscription_id')

    sub_close_reason_id = fields.Many2one("sale.sub.close.reason", string="Close Reason", copy=False, tracking=True)
    
    # Count Fields
    count_past_subscriptions = fields.Integer(compute='_compute_past_subscriptions')
    count_upselling_subscriptions = fields.Integer(compute='_compute_upselling_count')
    count_renewal_subscriptions = fields.Integer(compute="_compute_renewal_subscription_count")
    count_revised_subscriptions = fields.Integer(compute="_compute_revised_count")

    amount_total_subscription = fields.Monetary(compute='_compute_subscription_total', string="Total Subscription", store=True)
    amount_monthly_subscription = fields.Monetary(compute='_compute_monthly_subsccription', string="Monthly Subscription",
                                        store=True, tracking=True)
    non_recurring_total = fields.Monetary(compute='_compute_non_recurring_total', string="Total Non Recurring Revenue")

    #boolean flag to manage order operations on portal
    portal_renew = fields.Boolean(string='Allow Renew', compute='_compute_portal_renewal')
    portal_change_quantity = fields.Boolean(string='Allow Change Quantity', compute='_compute_portal_change_quantity')
    portal_change_plan = fields.Boolean(string='Allow Change Plan', compute='_compute_portal_change_plan')
    portal_close = fields.Boolean(string='Allow Close Order', compute='_compute_portal_close')
    portal_upsell = fields.Boolean(string='Allow Upselling', compute='_compute_portal_upsell')
    
    # =======================================================================
    # ========================== Computed Mehtods ===========================
    # =======================================================================
    def _compute_portal_renewal(self):
        for order in self:
            if order.subscription_status == 'progress' and order.invoice_count > 0 and order.subscription_plan_id.allow_portal_renewal:
                order.portal_renew = True
            else:
                order.portal_renew = False

    def _compute_portal_change_quantity(self):
        for order in self:
            if order.subscription_status == 'draft':
                order.portal_change_quantity = True
            else:
                order.portal_change_quantity = False

    def _compute_portal_change_plan(self):
        for order in self:
            if order.subscription_status == 'progress' and order.subscription_plan_id.allow_portal_renewal:
                order.portal_change_plan = True
            else:
                order.portal_change_plan = False

    def _compute_portal_close(self):
        for order in self:
            if order.subscription_plan_id.allow_portal_closing and order.subscription_status != 'close':
                order.portal_close = True
            else:
                order.portal_close = False

    def _compute_portal_upsell(self):
        for order in self:
            if order.subscription_plan_id.allow_portal_upsell and order.subscription_status == 'progress':
                order.portal_upsell = True
            else:
                order.portal_upsell = False
                
    def _compute_type_name(self):
        other_orders = self.env['sale.order']
        for order in self:
            if order.subscription_order and order.state == 'sale':
                order.type_name = _('Subscription')
            #elif order.subscription_state == '7_upsell':
            #    order.type_name = _('Upsell')
            #elif order.subscription_state == '2_renewal':
            #    order.type_name = _('Renewal Quotation')
            else:
                other_orders |= order

        super(SubscriptionOrder, other_orders)._compute_type_name()

    
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

    def _compute_renewal_subscription_count(self):
        for order in self:
            order.count_renewal_subscriptions = len(order.subscription_line_ids.filtered(lambda x: x.subscription_type == 'renewal'))
            #subscription_ids = self.env['sale.order'].search([
            #    ('parent_subscription_id', '=', order.id),
            #    ('subscription_type','=','renewal'),
            #])
            #if len(subscription_ids):
            #    order.count_renewal_subscriptions = len(subscription_ids)
            #else:
            #    order.count_renewal_subscriptions = 0

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
                
    def _group_expand_subscription_status(self, states, domain, order):
        return ['progress', 'close']


    @api.depends(
        'date_start', 
        'state', 
        'date_next_invoice', 
        'subscription_plan_id', 
    )
    def _compute_date_last_invoice(self):
        for order in self:
            try:
                last_date = False
                if order.date_next_invoice and order.subscription_plan_id:
                    last_date = order.date_next_invoice - order.subscription_plan_id.billing_period
                date_start = order.date_start or fields.Date.today()
                if order.state == 'sale' and last_date and last_date >= date_start:
                    order.date_last_invoice = last_date
                else:
                    order.date_last_invoice = False
            except:
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
    def _compute_date_next_invoice(self):
         for so in self:
            invoices = so.order_line.invoice_lines.mapped('move_id').filtered(lambda x:x.state != 'cancel')
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
            #res_sub = super(SubscriptionOrder, self).action_confirm()
            res = super(SubscriptionOrder, self).action_confirm()
            order.write({
                'subscription_status': 'progress',
            })
            return res

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
        action = self.env.ref('de_subscription.action_subscription_all').read()[0]
        action.update({
            'name': 'Renewed Subscriptions',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'domain': [('parent_subscription_id','=',self.id),('subscription_type','=','renewal')],
            'context': {
                'create': False,
                'edit': False,
            },
            
        })
        return action

    def open_subscription_upsell(self):
        action = self.env.ref('de_subscription.action_subscription_all').read()[0]
        action.update({
            'name': 'Upselling Subscriptions',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'domain': [('parent_subscription_id','=',self.id),('subscription_type','=','upsell')],
            'context': {
                'create': False,
                'edit': False,
            },
            
        })
        return action

    def open_past_subscriptions(self):
        action = self.env.ref('de_subscription.action_subscription_all').read()[0]
        action.update({
            'name': 'Subscription History',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'domain': [('parent_subscription_id','=',self.id)],
            'context': {
                'create': False,
                'edit': False,
            },
            
        })
        return action

    def open_revised_subscriptions(self):
        action = self.env.ref('de_subscription.action_subscription_all').read()[0]
        action.update({
            'name': 'Revised Subscriptions',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'domain': [('parent_subscription_id','=',self.id),('subscription_type','=','revised')],
            'context': {
                'create': False,
                'edit': False,
            },
            
        })
        return action

    def _action_cancel(self):
        for order in self:
            if order.subscription_type == 'upsell':
                cancel_message_body = _("The upsell %s has been canceled.", order._get_html_link())
                order.parent_subscription_id.message_post(body=cancel_message_body)
            elif order.subscription_type == 'renewal':
                cancel_message_body = _("The renewal %s has been canceled.", order._get_html_link())
                order.parent_subscription_id.message_post(body=cancel_message_body)
            elif order.subscription_type == 'revised':
                cancel_message_body = _("The revised %s has been canceled.", order._get_html_link())
                order.parent_subscription_id.message_post(body=cancel_message_body)
            elif (order.subscription_status in SUBSCRIPTION_PROGRESS_STATUS + SUBSCRIPTION_DRAFT_STATUS
                  and not any(state in ['draft', 'posted'] for state in order.order_line.invoice_lines.move_id.mapped('state'))):
                order.subscription_status = False
            elif order.subscription_status in SUBSCRIPTION_PROGRESS_STATUS:
                raise ValidationError(_('You cannot cancel a subscription that has been invoiced.'))
        return super()._action_cancel()

    def action_close_subscription(self,close_reason_id=False, subscription_type=False):
        today = fields.Date.context_today(self)
        values = {
            'end_date': today,
        }
        if subscription_type != 'upsell':
            values['subscription_status'] = 'close'
            
        if close_reason_id:
            values['sub_close_reason_id'] = close_reason_id.id
            self.update(values)
    
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
    # Review
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

    # review
    @api.model
    def _process_invoices_to_send(self, account_moves):
        for invoice in account_moves:
            if not invoice.is_move_sent and invoice._is_ready_to_be_sent() and invoice.state == 'posted':
                subscription = invoice.line_ids.subscription_id
                subscription.validate_and_send_invoice(invoice)
                invoice.message_subscribe(subscription.user_id.partner_id.ids)
            elif invoice.line_ids.subscription_id:
                invoice.message_subscribe(invoice.line_ids.subscription_id.user_id.partner_id.ids)

    # ==========================================================
    # =================== Create Orders ========================
    # ==========================================================

    # review
    def _get_order_subscription_digest(self, origin='', template='de_subscription.subscription_order_digest', lang=None):
        self.ensure_one()
        values = {'origin': origin,
                  'record_url': self._get_html_link(),
                  'date_start': self.date_start,
                  'date_next_invoice': self.date_next_invoice,
                  'amount_monthly_subscription': self.amount_monthly_subscription,
                  'untaxed_amount': self.amount_untaxed,
                 }
        return self.env['ir.qweb'].with_context(lang=lang)._render(template, values)
        
    def _prepare_new_subscription_order(self, subscription_type, message_body):
        order = self._create_new_subscription_order(subscription_type, message_body)
        action = self._action_open_subscription(order)
        action['name'] = subscription_type
        action['views'] = [(self.env.ref('de_subscription.subscription_order_primary_form_view').id, 'form')]
        action['res_id'] = order.id
        return action

    def _create_new_subscription_order(self, subscription_type, message_body):
        self.ensure_one()
        subscription = self
        
        if subscription.date_start == subscription.date_next_invoice:
            raise ValidationError("You cannot perform an upsell or renewal on a subscription that has not yet been invoiced. "
                      "Please ensure that the subscription '%s' is invoiced before proceeding." % subscription.name)
    
        new_order_values = self._prepare_new_subscription_order_values(subscription_type)
        new_order = self.env['sale.order'].create(new_order_values)
        subscription.subscription_line_ids = [(4, new_order.id)]
        new_order.message_post(body=message_body)
    
        if subscription_type == 'upsell':
            parent_message_body = _("An upsell quotation %s has been created", new_order._get_html_link())
        elif subscription_type == 'revised':
            parent_message_body = _("An revised quotation %s has been created", new_order._get_html_link())
        elif subscription_type == 'renewal':
            parent_message_body = _("A renewal quotation %s has been created", new_order._get_html_link())
        else:
            parent_message_body = _("A subscription %s has been closed", new_order._get_html_link())
        
        subscription.message_post(body=parent_message_body)
        new_order.order_line._compute_tax_id()
        
        return new_order

    def _prepare_new_subscription_order_values(self, subscription_type):
        self.ensure_one()
        today = fields.Date.today()
        subscription = self
    
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
            'subscription_type': subscription_type,
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
    def _action_open_subscription(self, order):
        return {
                'name': order.subscription_type,
                'view_mode': 'form',
                'res_model': 'sale.order',
                'res_id': order.id,
                'type': 'ir.actions.act_window',
            }
    # =========================================================
    # ==================== Crone Jobs =========================
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
        #auto_commit = not bool(config['test_enable'] or config['test_file'])
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
            #if auto_commit:
            #    self.env.cr.commit()
        return dict(closed=subscriptions_close.ids)

    def _cron_create_subscription_invoice(self):
        return self._create_subscription_recurring_invoice()

    def _create_subscription_recurring_invoice(self, batch_size=30):
        today = fields.Date.today()
        domain = [
            ('subscription_order', '=', True),
            ('date_next_invoice', '<=', today),
            ('state', '=', 'sale'),
            ('subscription_status', 'in', SUBSCRIPTION_PROGRESS_STATUS)]
        subscriptions = self.env['sale.order'].search(domain)
        
        for order in subscriptions:
            try:
                order._create_invoices()
            except Exception as e:
                # Log the exception
                _logger.exception("Error occurred while creating invoices for order %s: %s", order.name, str(e))
                order.message_post(body=f"Error occurred while creating invoices: {str(e)}")

    # actions for portal operations
    def _create_new_upsell_subscription(self, kw, message_body):
        self.ensure_one()
        subscription = self
        
        if subscription.date_start == subscription.date_next_invoice:
            raise ValidationError("You cannot perform an upsell or renewal on a subscription that has not yet been invoiced. "
                      "Please ensure that the subscription '%s' is invoiced before proceeding." % subscription.name)
    
        new_order_values = self._prepare_upsell_subscription_values(kw)
        new_order = self.env['sale.order'].create(new_order_values)
        subscription.subscription_line_ids = [(4, new_order.id)]
        new_order.message_post(body=message_body)
    
        parent_message_body = _("An upsell quotation %s has been created", new_order._get_html_link())
        
        subscription.message_post(body=parent_message_body)
        new_order.order_line._compute_tax_id()
        
        return new_order
        
    def _prepare_upsell_subscription_values(self, kw):
        self.ensure_one()
        today = fields.Date.today()
        subscription = self
    
        order_lines = subscription.order_line._get_upsell_order_lines(kw)    
            
        date_start = today
        date_next_invoice = subscription.date_next_invoice
    
        return {
            'subscription_order': True,
            'parent_subscription_id': subscription.id,
            'pricelist_id': subscription.pricelist_id.id,
            'partner_id': subscription.partner_id.id,
            'partner_invoice_id': subscription.partner_invoice_id.id,
            'partner_shipping_id': subscription.partner_shipping_id.id,
            'order_line': order_lines,
            'analytic_account_id': subscription.analytic_account_id.id,
            'subscription_type': 'upsell',
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