# -*- coding: utf-8 -*-

from odoo import _, api, fields, models, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.tools import format_date, frozendict


class PurchaseAdvancePaymentInv(models.TransientModel):
    _name = "purchase.advance.payment.inv"
    _description = "Purchase Advance Payment Invoice"

    @api.model
    def _count(self):
        return len(self._context.get('active_ids', []))

    @api.model
    def _default_product_id(self):
        product_id = self.env['ir.config_parameter'].sudo().get_param('de_purchase_bill.purchase_deposit_product_id')
        return self.env['product.product'].browse(int(product_id)).exists()
    
    @api.model
    def _default_journal_id(self):
        journal_id = self.env['ir.config_parameter'].sudo().get_param('de_purchase_bill.default_deposit_journal_id')
        if not journal_id:
            return self.env['account.journal'].search([('type','=','purchase'),('active','=',True)],limit=1)
        return self.env['account.journal'].browse(int(journal_id)).exists()

    @api.model
    def _default_deposit_account_id(self):
        return self._default_product_id()._get_product_accounts()['expense']

    @api.model
    def _default_deposit_taxes_id(self):
        return self._default_product_id().taxes_id

    @api.model
    def _default_has_down_payment(self):
        if self._context.get('active_model') == 'purchase.order' and self._context.get('active_id', False):
            purchase_order = self.env['purchase.order'].browse(self._context.get('active_id'))
            return purchase_order.order_line.filtered(
                lambda purchase_order_line: purchase_order_line.is_downpayment
            )

        return False

    @api.model
    def _default_currency_id(self):
        if self._context.get('active_model') == 'purchase.order' and self._context.get('active_id', False):
            purchase_order = self.env['purchase.order'].browse(self._context.get('active_id'))
            return purchase_order.currency_id

    advance_payment_method = fields.Selection([
        ('delivered', 'Regular invoice'),
        ('percentage', 'Down payment (percentage)'),
        ('fixed', 'Down payment (fixed amount)')
        ], string='Create Invoice', default='delivered', required=True,
        help="A standard invoice is issued with all the order lines ready for invoicing, \
        according to their invoicing policy (based on ordered or delivered quantity).")
    deduct_down_payments = fields.Boolean('Deduct down payments', default=True)
    has_down_payments = fields.Boolean('Has down payments', default=_default_has_down_payment, readonly=True)
    
    journal_id = fields.Many2one('account.journal', string='Down Payment Journal', domain=[('type', '=', 'purchase')],
        default=_default_journal_id)
    company_id = fields.Many2one(
        comodel_name='res.company',
        compute='_compute_company_id',
        store=True)
    count = fields.Integer(default=_count, string='Order Count')
    purchase_order_ids = fields.Many2many(
        'purchase.order', default=lambda self: self.env.context.get('active_ids'))

    # New Down Payment
    product_id = fields.Many2one(
        comodel_name='product.product',
        string="Down Payment Product",
        domain=[('type', '=', 'service')],
        compute='_compute_product_id',
        readonly=False,
        store=True
    )
    consolidated_billing = fields.Boolean(
        string="Consolidated Billing", default=True,
        help="Create one invoice for all orders related to same customer and same invoicing address"
    )
    amount = fields.Float('Down Payment Amount', digits='Account', help="The percentage of amount to be invoiced in advance, taxes excluded.")
    currency_id = fields.Many2one('res.currency', string='Currency', default=_default_currency_id)
    fixed_amount = fields.Monetary('Down Payment Amount (Fixed)', help="The fixed amount to be invoiced in advance, taxes excluded.")
    deposit_account_id = fields.Many2one("account.account", string="Income Account", domain=[('deprecated', '=', False)],
        help="Account used for deposits", default=_default_deposit_account_id)
    deposit_taxes_id = fields.Many2many("account.tax", string="Customer Taxes", help="Taxes used for deposits", default=_default_deposit_taxes_id)

    # Computed Methods
    @api.depends('purchase_order_ids')
    def _compute_company_id(self):
        self.company_id = False
        for wizard in self:
            if wizard.count == 1:
                wizard.company_id = wizard.purchase_order_ids.company_id
                
    @api.onchange('advance_payment_method')
    def onchange_advance_payment_method(self):
        if self.advance_payment_method == 'percentage':
            amount = self.default_get(['amount']).get('amount')
            return {'value': {'amount': amount}}
        return {}

    @api.depends('company_id')
    def _compute_product_id(self):
        self.product_id = False
        for wizard in self:
            if wizard.count == 1:
                wizard.product_id = wizard.company_id.purchase_down_payment_product_id

    # Actions
    def _check_amount_is_positive(self):
        for wizard in self:
            if wizard.advance_payment_method == 'percentage' and wizard.amount <= 0.00:
                raise UserError(_('The value of the down payment amount must be positive.'))
            elif wizard.advance_payment_method == 'fixed' and wizard.fixed_amount <= 0.00:
                raise UserError(_('The value of the down payment amount must be positive.'))
                
    def create_bills(self):
        self._check_amount_is_positive()
        bills = self._create_bills(self.purchase_order_ids)
        return self.purchase_order_ids.action_view_bill(bills=bills)
        
    

    #=== BUSINESS METHODS ===#
    #   below all are new

    def _create_bills(self, purchase_orders):
        self.ensure_one()
        if self.advance_payment_method == 'delivered':
            return purchase_orders._create_bills(final=self.deduct_down_payments, grouped=not self.consolidated_billing)
        else:
            self.purchase_order_ids.ensure_one()
            self = self.with_company(self.company_id)
            order = self.purchase_order_ids

            # Create deposit product if necessary
            if not self.product_id:
                self.company_id.purchase_down_payment_product_id = self.env['product.product'].create(
                    self._prepare_down_payment_product_values()
                )
                self._compute_product_id()

            # Create down payment section if necessary
            PurchaseOrderline = self.env['purchase.order.line'].with_context(purchase_no_log_for_new_lines=True)
            if not any(line.display_type and line.is_downpayment for line in order.order_line):
                PurchaseOrderline.create(
                    self._prepare_down_payment_section_values(order)
                )

            down_payment_lines = PurchaseOrderline.create(
                self._prepare_down_payment_lines_values(order)
            )

            invoice = self.env['account.move'].sudo().create(
                self._prepare_bill_values(order, down_payment_lines)
            )

            # Ensure the invoice total is exactly the expected fixed amount.
            if self.advance_payment_method == 'fixed':
                delta_amount = (invoice.amount_total - self.fixed_amount) * (1 if invoice.is_inbound() else -1)
                if not order.currency_id.is_zero(delta_amount):
                    receivable_line = invoice.line_ids\
                        .filtered(lambda aml: aml.account_id.account_type == 'asset_receivable')[:1]
                    product_lines = invoice.line_ids\
                        .filtered(lambda aml: aml.display_type == 'product')
                    tax_lines = invoice.line_ids\
                        .filtered(lambda aml: aml.tax_line_id.amount_type not in (False, 'fixed'))

                    if product_lines and tax_lines and receivable_line:
                        line_commands = [Command.update(receivable_line.id, {
                            'amount_currency': receivable_line.amount_currency + delta_amount,
                        })]
                        delta_sign = 1 if delta_amount > 0 else -1
                        for lines, attr, sign in (
                            (product_lines, 'price_total', -1),
                            (tax_lines, 'amount_currency', 1),
                        ):
                            remaining = delta_amount
                            lines_len = len(lines)
                            for line in lines:
                                if order.currency_id.compare_amounts(remaining, 0) != delta_sign:
                                    break
                                amt = delta_sign * max(
                                    order.currency_id.rounding,
                                    abs(order.currency_id.round(remaining / lines_len)),
                                )
                                remaining -= amt
                                line_commands.append(Command.update(line.id, {attr: line[attr] + amt * sign}))
                        invoice.line_ids = line_commands

            # Unsudo the invoice after creation if not already sudoed
            invoice = invoice.sudo(self.env.su)

            poster = self.env.user._is_internal() and self.env.user.id or SUPERUSER_ID
            invoice.with_user(poster).message_post_with_source(
                'mail.message_origin_link',
                render_values={'self': invoice, 'origin': order},
                subtype_xmlid='mail.mt_note',
            )

            title = _("Down payment invoice")
            order.with_user(poster).message_post(
                body=_("%s has been created", invoice._get_html_link(title=title)),
            )

            return invoice

    def _prepare_down_payment_lines_values(self, order):
        """ Create one down payment line per tax or unique taxes combination.
            Apply the tax(es) to their respective lines.

            :param order: Order for which the down payment lines are created.
            :return:      An array of dicts with the down payment lines values.
        """
        self.ensure_one()

        if self.advance_payment_method == 'percentage':
            percentage = self.amount / 100
        else:
            percentage = self.fixed_amount / order.amount_total if order.amount_total else 1

        order_lines = order.order_line.filtered(lambda l: not l.display_type)
        base_downpayment_lines_values = self._prepare_base_downpayment_line_values(order)

        tax_base_line_dicts = [
            line._convert_to_tax_base_line_dict(
                #analytic_distribution=line.analytic_distribution,
                #handle_price_include=False
            )
            for line in order_lines
        ]
        computed_taxes = self.env['account.tax']._compute_taxes(
            tax_base_line_dicts)
        down_payment_values = []
        for line, tax_repartition in computed_taxes['base_lines_to_update']:
            taxes = line['taxes'].flatten_taxes_hierarchy()
            fixed_taxes = taxes.filtered(lambda tax: tax.amount_type == 'fixed')
            down_payment_values.append([
                taxes - fixed_taxes,
                line['analytic_distribution'],
                tax_repartition['price_subtotal']
            ])
            for fixed_tax in fixed_taxes:
                # Fixed taxes cannot be set as taxes on down payments as they always amounts to 100%
                # of the tax amount. Therefore fixed taxes are removed and are replace by a new line
                # with appropriate amount, and non fixed taxes if the fixed tax affected the base of
                # any other non fixed tax.
                if fixed_tax.include_base_amount:
                    pct_tax = taxes[list(taxes).index(fixed_tax) + 1:]\
                        .filtered(lambda t: t.is_base_affected and t.amount_type != 'fixed')
                else:
                    pct_tax = self.env['account.tax']
                down_payment_values.append([
                    pct_tax,
                    line['analytic_distribution'],
                    line['quantity'] * fixed_tax.amount
                ])

        downpayment_line_map = {}
        for tax_id, analytic_distribution, price_subtotal in down_payment_values:
            grouping_key = frozendict({
                'taxes_id': tuple(sorted(tax_id.ids)),
                'analytic_distribution': analytic_distribution,
            })
            downpayment_line_map.setdefault(grouping_key, {
                **base_downpayment_lines_values,
                **grouping_key,
                'product_uom_qty': 0.0,
                'price_unit': 0.0,
            })
            downpayment_line_map[grouping_key]['price_unit'] += \
                order.currency_id.round(price_subtotal * percentage)

        return list(downpayment_line_map.values())

    def _prepare_base_downpayment_line_values(self, order):
        self.ensure_one()
        context = {'lang': order.partner_id.lang}
        so_values = {
            'name': _(
                'Down Payment: %(date)s (Draft)', date=format_date(self.env, fields.Date.today())
            ),
            'product_uom_qty': 0.0,
            'product_qty': 0.0,
            'order_id': order.id,
            'discount': 0.0,
            'product_id': self.product_id.id,
            'is_downpayment': True,
            'sequence': order.order_line and order.order_line[-1].sequence + 1 or 10,
        }
        del context
        return so_values

    def _prepare_down_payment_product_values(self):
        self.ensure_one()
        return {
            'name': _('Down payment'),
            'type': 'service',
            'purchase_method': 'purchase',
            'company_id': self.company_id.id,
            'property_account_expense_id': self.deposit_account_id.id,
            'taxes_id': [Command.set(self.deposit_taxes_id.ids)],
        }
    def _prepare_down_payment_section_values(self, order):
        context = {'lang': order.partner_id.lang}
        so_values = {
            'name': _('Down Payments'),
            'product_uom_qty': 0.0,
            'product_qty': 0.0,
            'order_id': order.id,
            'display_type': 'line_section',
            'is_downpayment': True,
            'sequence': order.order_line and order.order_line[-1].sequence + 1 or 10,
        }

        del context
        return so_values

    def _prepare_bill_values(self, order, po_lines):
        self.ensure_one()
        return {
            **order._prepare_invoice(),
            'invoice_line_ids': [Command.create(
                line._prepare_invoice_line(
                    name=self._get_down_payment_description(order),
                    quantity=1.0,
                )
            ) for line in po_lines],
        }
        
    def _get_down_payment_description(self, order):
        self.ensure_one()
        context = {'lang': order.partner_id.lang}
        if self.advance_payment_method == 'percentage':
            name = _("Down payment of %s%%", self.amount)
        else:
            name = _('Down Payment')
        del context
        return name