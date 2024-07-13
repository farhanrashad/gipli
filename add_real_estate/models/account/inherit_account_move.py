from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from .num2words import num2words
from odoo.tools import float_is_zero, float_compare, safe_eval, date_utils, email_split, email_escape_char, email_re
import json
from odoo.exceptions import  UserError


class DisType(models.Model):
    _name='inv.dis.type'
    name = fields.Char(
        string='Name',
        required=False)
class AccountMove(models.Model):
    _inherit = "account.move"

    is_contract = fields.Boolean(string="Is Contract", readonly=True )
    reservation_id = fields.Many2one(comodel_name="res.reservation", string="Reservation", required=False, )
    property_id = fields.Many2one(related="reservation_id.property_id", comodel_name="product.product", string="Unit",
                                  required=False, store=True, readonly=False)
    broker_id = fields.Many2one(related="reservation_id.broker_id",comodel_name="res.partner", string="Broker", required=False, )
    source_doc = fields.Char(string='New Source Document')
    source_doc_readonly = fields.Boolean()

    invoice_details = fields.One2many(comodel_name='invoice.details',inverse_name='invoice_id')
    draft_no = fields.Char(string='Draft No',copy=False)
    custom_invoice_date= fields.Date(
        string='Invoice Date',
        required=False)
    tax_add = fields.Float(string='ق.ض',compute='_calc_tax_add',store=True)
    tax_sub = fields.Float(string='ض.خ',compute='_calc_tax_add',store=True)
    tax_code = fields.Char(string='كود الضريبة',compute='_calc_deal',store=True)
    deal = fields.Selection(string='طبيعة التعامل',compute='_calc_deal',store=True,
                            selection=[('s', 'خدمات'), ('i', 'توريد'), ('c', 'استشارات وسمسرة')])
    tax_discount_percentage= fields.Float(string='نسبه الخصم',compute='_calc_deal',store=True)
    discount_code= fields.Char(string='كود ')

    new_discount_type = fields.Many2one(comodel_name='inv.dis.type',string='')
    document_type_id = fields.Many2one(comodel_name="move.doc.type", string="نوع المستند", required=False)
    external_document_number = fields.Char(string="رقم المستند الخارجي", required=False)
    external_document_type = fields.Char(string="نوع المستند الخارجي", required=False)
    payment_papers = fields.Char(string="اوراق دفع", required=False)
    statement_ref = fields.Char(string="Statement Ref", required=False)
    muayada = fields.Selection(string="مؤيد/غ مؤيد", selection=[('t1', 'مؤيد'), ('t2', 'غ/مؤيد'), ], required=False)
    installment_type = fields.Char(
        string='Installment Type',
        required=False)

    state_payment = fields.Selection([('cash', 'Cash'),
                                      ('visa', 'Visa'),
                                      ('cheque', 'Cheque'),
                              ('bank', 'Bank'),
                              ],default="cheque")
    cheque = fields.Char(_("Cheque Number"))
    deposite = fields.Boolean(string='Deposit')
    is_maintainance = fields.Boolean(string=" maintainance & Insurance ",  )
    amount_total_words = fields.Char("Total (In Words)", compute="_compute_amount_total_words")
    vat_tax_amount = fields.Float(string='Vat', compute="_calc_vat_tax_amount", store=False)
    withholding_tax_amount = fields.Float(string='Withholding', compute="_calc_vat_tax_amount", store=False)
    check_payment_state = fields.Selection(selection=[('holding','Posted'),('depoisted','Under collection'),
                                         ('approved','Withdrawal'),
                                        ('rejected','Rejected'),
                                        ('send_to_lagel', 'Send To Legal'),
                                        ('deliver', 'Deliver'),
                                        ('refund_deliver', 'Refund Deliver'),
                                        ('refund', 'Refund'),
                                        ('refund_send_to_lagel','Refund Send To Legal')
                                         , ('returned', 'Refund Under collection'), ('handed', 'Handed'),
                                        ('debited', 'Withdrawal Payable'),
                                        ('canceled', 'Canceled'),
                                        ('cs_return','Refund Notes Receivable'),
                                        ('payment_cancel','Payment Canceled'),
                                        ('payment_draft','Payment Draft'),
                                        ('delivery_to_customer', 'Delivery To Customer'),

                                        ]
                            ,track_visibility='onchange',string='Last Payment Status',compute='_compute_payments_widget_to_reconcile_info',store=True)

    is_required_elect_no = fields.Boolean('الرقم الالكتروني للفاتوره الضريبية',related='journal_id.required_elect_no',store=True)
    required_elect_no = fields.Char('الرقم الالكتروني للفاتوره الضريبية')

    @api.constrains("is_required_elect_no", "required_elect_no")
    def _check_required_elect_no_required(self):
        for rec in self:
            if rec.is_required_elect_no and rec.required_elect_no:
                if len(self.search([("required_elect_no", "=", rec.required_elect_no)])) > 1:
                    raise ValidationError("الرقم الالكتروني للفاتوره الضريبية مكرر")


    @api.depends('tax_totals')
    def _calc_vat_tax_amount(self):
        for rec in self:
            vat = withholding = 0
            if rec.tax_totals:
                groups_by_subtotal = rec.tax_totals.get('groups_by_subtotal')
                if groups_by_subtotal:
                    values = groups_by_subtotal.get(_('Untaxed Amount'))
                    if values:
                        for value in values:
                            tax_id = self.env['account.tax'].sudo().search(
                                [('tax_group_id', '=', int(value.get('tax_group_id')))], limit=1)
                            if tax_id.amount > 0:
                                vat += abs(value.get('tax_group_amount'))
                            else:
                                withholding += abs(value.get('tax_group_amount'))
            rec.vat_tax_amount = vat
            rec.withholding_tax_amount = withholding

    @api.depends('amount_total')
    def _compute_amount_total_words(self):
        for invoice in self:
            invoice.amount_total_words = invoice.currency_id.amount_to_text(invoice.amount_total)

    @api.constrains('line_ids', 'journal_id', 'auto_reverse', 'reverse_date')
    def _validate_move_modification(self):
        pass

    def unlink(self):
        for move in self:
            move.line_ids.unlink()
        return models.Model.unlink(self)


    @api.depends('invoice_line_ids')
    def _calc_deal(self):
        deal=False
        tax_code=False
        tax_discount_percentage=0
        for rec in self:
            for line in rec.invoice_line_ids:
                if line.tax_ids:
                    for tax in line.tax_ids:
                        if tax.amount<0:
                            deal=tax.deal
                            tax_code=tax.tax_code
                            tax_code=tax.tax_code
                            tax_discount_percentage=tax.amount
            rec.deal=deal
            rec.tax_code=tax_code
            rec.tax_discount_percentage=tax_discount_percentage



    # @api.depends('amount_by_group')
    def _calc_tax_add(self):
        tax_add=tax_sub=0
        for rec in self:
            for  amount_by_group in rec.amount_by_group:
                print('D>D>D>',amount_by_group)
                if float(amount_by_group[1]) > 0:
                    tax_add += float(amount_by_group[1])
                else:
                    tax_sub += float(amount_by_group[1])
        rec.tax_add=round(abs(tax_add),2)
        rec.tax_sub=round(abs(tax_sub),2)


    

    def ar_amount_to_text(self):
        convert_amount_in_words = num2words(self.amount_total, lang='en_US')
        return convert_amount_in_words

    def action_post(self):
        res = super(AccountMove, self).action_post()
        if self.reservation_id:
                total_ins = 0

                for line in self.reservation_id.payment_strg_ids:
                    print("line.reserve_id.id,", line.reserve_id.id)
                    print("line.reserve_id.id,", line.cheque)
                    print("line.reserve_id.id,", line.id)
                    # if line.cheque:
                    #     strg = self.env['payment.strg'].search([('id', '=', self.payment_strg_ids.ids),('cheque','=',line.cheque),('id','!=',line.id)])
                    #     if strg:
                    #         raise ValidationError(_('Error !,Number Cheque Duplicate.'))

                    if line.is_maintainance == False:
                        total_ins += line.amount

                print("self.env.user.has_group('add_real_estate.group_custom_payment') :> ",
                      self.env.user.has_group('add_real_estate.group_custom_payment'))
                if self.env.user.has_group('add_real_estate.group_custom_payment') == False:
                    # if  self.user_has_groups('add_real_estate.group_custom_payment'):

                    print("total_ins  :> ", total_ins)
                    print("total_ins  :> ", round(total_ins))
                    # print("self.net_price  :> ", self.net_price)
                    # print("self.net_price  :> ", round(self.net_price))
                    if self.reservation_id.pay_strategy_id:
                        if round(total_ins) != round(self.reservation_id.net_price):
                            raise ValidationError(_('Error !,The Total installment is not equal The net Price.'))

                # self.reservation_id.state = 'contracted'
                # self.reservation_id.property_id.state = 'contracted'


        return res

    def button_draft(self):
        res = super(AccountMove, self).button_draft()
        self.reservation_id.state = 'initial_contracted'
        self.reservation_id.property_id.state = 'initial_contracted'
        return res

    @api.model
    def create(self, values):
        # Add code here
        res = super(AccountMove, self).create(values)
        if res.move_type=="out_invoice":
            res.draft_no = self.env['ir.sequence'].next_by_code('invoice.seq.draft') or _('New')
        return res

    @api.constrains('draft_no')
    def check_draft_no(self):
        if self.draft_no:
            if len(self.search([("draft_no", "=", self.draft_no)])) > 1:
                raise ValidationError("Draft No already exists")

    def _compute_payments_widget_to_reconcile_info(self):
        for move in self:
            move.invoice_outstanding_credits_debits_widget = False
            move.invoice_has_outstanding = False

            if move.state != 'posted' \
                    or move.payment_state not in ('not_paid', 'partial') \
                    or not move.is_invoice(include_receipts=True):
                continue

            pay_term_lines = move.line_ids\
                .filtered(lambda line: line.account_id.account_type in ('asset_receivable', 'liability_payable'))

            domain = [
                ('account_id', 'in', pay_term_lines.account_id.ids),
                ('parent_state', '=', 'posted'),
                ('partner_id', '=', move.commercial_partner_id.id),
                ('reconciled', '=', False),
                '|', ('amount_residual', '!=', 0.0), ('amount_residual_currency', '!=', 0.0),
            ]

            payments_widget_vals = {'outstanding': True, 'content': [], 'move_id': move.id}

            if move.is_inbound():
                domain.append(('balance', '<', 0.0))
                payments_widget_vals['title'] = _('Outstanding credits')
            else:
                domain.append(('balance', '>', 0.0))
                payments_widget_vals['title'] = _('Outstanding debits')

            for line in self.env['account.move.line'].search(domain):

                if line.currency_id == move.currency_id:
                    # Same foreign currency.
                    amount = abs(line.amount_residual_currency)
                else:
                    # Different foreign currencies.
                    amount = line.company_currency_id._convert(
                        abs(line.amount_residual),
                        move.currency_id,
                        move.company_id,
                        line.date,
                    )

                if move.currency_id.is_zero(amount):
                    continue


                show_add=True

                ref = line.move_id.ref or ""
                if line.move_id.check_id.check_number:
                    move.check_payment_state=line.move_id.check_id.state
                    print("D>D>D3333333>D",line.move_id,line.move_id.check_id,line.move_id.check_id.state)
                    if line.move_id.check_id.state in ['cs_return','delivery_to_customer']:
                        show_add=False
                    print("D>D>D>D>",show_add)
                    ref += ',' + str(line.move_id.check_id.check_number)
                    if line.move_id.check_id.check_date:
                        ref += ',' + str(line.move_id.check_id.check_date)



                payments_widget_vals['content'].append({
                    'journal_name': line.ref or line.check_payment_id.name if line.check_payment_id else "" +"-"+ref,
                    'amount': amount,
                    'currency_id': move.currency_id.id,
                    'id': line.id,
                    'move_id': line.move_id.id,
                    'date': fields.Date.to_string(line.date),
                    'account_payment_id': line.payment_id.id,
                    'show_add': show_add,
                })

            if not payments_widget_vals['content']:
                continue

            move.invoice_outstanding_credits_debits_widget = payments_widget_vals
            move.invoice_has_outstanding = True





class AccountMovedd(models.Model):
    _inherit = "account.move.line"
    serial_no = fields.Char(string="S.N")
    name = fields.Char()

    cheque_number_line = fields.Char(string="Cheque number", compute='_clac_cheque_number_line', store=True,
                                     readonly=False)


    reservation_id = fields.Many2one(comodel_name="res.reservation", string="Reservation", related="move_id.reservation_id",store=True,readonly=False)
    property_id = fields.Many2one(related="reservation_id.property_id", comodel_name="product.product", string="Unit",
                                  required=False, store=True, readonly=False)
    policy_commission_id= fields.Many2one(comodel_name='policy.commision',string='Commission',related='payment_id.policy_commission_id',store=True)
    policy_bonous_id= fields.Many2one(comodel_name='policy.bonous',string='Bonus',related='payment_id.policy_bonous_id',store=True)
    policy_nts_id= fields.Many2one(comodel_name='policy.nts',string='Nts',related='payment_id.policy_nts_id',store=True)
    paid_or_no = fields.Selection(string='Paid/Unpaid',
        selection=[('paid', 'Paid'),
                   ('unpaid', 'Unpaid'), ],related='account_id.paid_or_no',store=True,
        required=False, )
    external_document_number = fields.Char(string="رقم المستند الخارجي", related='move_id.external_document_number',store=True)
    vat_tax_amount = fields.Float(string='Vat', compute="_calc_vat_tax_amount", store=False)
    withholding_tax_amount = fields.Float(string='Withholding', compute="_calc_vat_tax_amount", store=False)

    @api.depends('move_id.tax_totals')
    def _calc_vat_tax_amount(self):
        for rec in self:
            vat = withholding = 0
            if rec.move_id.tax_totals:
                groups_by_subtotal = rec.move_id.tax_totals.get('groups_by_subtotal')
                if groups_by_subtotal:
                    values = groups_by_subtotal.get(_('Untaxed Amount'))
                    if values:
                        for value in values:
                            tax_id = self.env['account.tax'].sudo().search(
                                [('tax_group_id', '=', int(value.get('tax_group_id')))], limit=1)
                            if tax_id.amount > 0:
                                vat += abs(value.get('tax_group_amount'))
                            else:
                                withholding += abs(value.get('tax_group_amount'))
            rec.vat_tax_amount = vat
            rec.withholding_tax_amount = withholding



    @api.constrains('serial_no')
    def check_serial_no(self):
        for rec in self:
            if rec.serial_no:
                if len(self.env['account.move.line'].search([("serial_no", "=", rec.serial_no)])) > 1:
                    raise ValidationError("Serial Number  already exists")

    @api.constrains("partner_id", "account_id", "debit", "credit")
    def _check_partner_id_required(self):
        for rec in self:
            if rec.account_id.partner_required_in_journal_entry:
                if not rec.partner_id:
                    raise ValidationError("Partner Required For This Account-"+str(rec.account_id.name))



    #
    # @api.onchange('product_id')
    # def _onchange_product_id(self):
    #     print("eid")
    #     for line in self:
    #         if not line.product_id or line.display_type in ('line_section', 'line_note'):
    #             continue
    #
    #         line.name = line._compute_name()
    #         line.account_id = line._compute_account_id()
    #         line.tax_ids = line._get_computed_taxes()
    #         line.product_uom_id = line._get_computed_uom()
    #         line.price_unit = line._get_computed_price_unit()
    #
    #         # Manage the fiscal position after that and adapt the price_unit.
    #         # E.g. mapping a price-included-tax to a price-excluded-tax must
    #         # remove the tax amount from the price_unit.
    #         # However, mapping a price-included tax to another price-included tax must preserve the balance but
    #         # adapt the price_unit to the new tax.
    #         # E.g. mapping a 10% price-included tax to a 20% price-included tax for a price_unit of 110 should preserve
    #         # 100 as balance but set 120 as price_unit.
    #         if line.tax_ids and line.move_id.fiscal_position_id:
    #             line.price_unit = line._get_price_total_and_subtotal()['price_subtotal']
    #             line.tax_ids = line.move_id.fiscal_position_id.map_tax(line.tax_ids._origin, partner=line.move_id.partner_id)
    #             accounting_vals = line._get_fields_onchange_subtotal(price_subtotal=line.price_unit, currency=line.move_id.company_currency_id)
    #             balance = accounting_vals['debit'] - accounting_vals['credit']
    #             line.price_unit = line._get_fields_onchange_balance(balance=balance).get('price_unit', line.price_unit)
    #
    #         # Convert the unit price to the invoice's currency.
    #         company = line.move_id.company_id
    #         line.price_unit = company.currency_id._convert(line.price_unit, line.move_id.currency_id, company, line.move_id.date)
    #
    #     if len(self) == 1:
    #         return {'domain': {'product_uom_id': [('category_id', '=', self.product_uom_id.category_id.id)]}}

    @api.depends('payment_id.cheque_number', 'payment_id.check_number','move_id.cheque')
    def _clac_cheque_number_line(self):
        for rec in self:
            chck = ""
            if rec.payment_id.cheque_number:
                chck = rec.payment_id.cheque_number
            if rec.payment_id.check_number:
                chck = rec.payment_id.check_number
            if rec.move_id.cheque:
                chck = rec.move_id.cheque
            rec.cheque_number_line = chck

    @api.model
    def compute_amount_fields(self, amount, src_currency, company_currency, invoice_currency=False):
        """ Helper function to compute value for fields debit/credit/amount_currency based on an amount and the currencies given in parameter"""
        amount_currency = False
        currency_id = False
        if src_currency and src_currency != company_currency:
            amount_currency = amount
            amount = src_currency.with_context(self._context).compute(amount, company_currency)
            currency_id = src_currency.id
        debit = amount > 0 and amount or 0.0
        credit = amount < 0 and -amount or 0.0
        if invoice_currency and invoice_currency != company_currency and not amount_currency:
            amount_currency = src_currency.with_context(self._context).compute(amount, invoice_currency)
            currency_id = invoice_currency.id
        return debit, credit, amount_currency, currency_id

    # @api.multi
    # def reconcile(self, writeoff_acc_id=False, writeoff_journal_id=False):
    #     # Empty self can happen if the user tries to reconcile entries which are already reconciled.
    #     # The calling method might have filtered out reconciled lines.
    #     if not self:
    #         return True
    #
    #     ctx_discount_batch = self._context.get('discount_check')
    #     ctx_del = self._context.get('delivery_aml')
    #     ctx_bank = self._context.get('bank_aml')
    #     ctx_del_batch = self._context.get('delivery_aml_batch')
    #     ctx_bank_batch = self._context.get('bank_aml_batch')
    #     ctx_loan_batch = self._context.get('loan_check')
    #     collect_disc_batch = self._context.get('collect_disc_batch')
    #     loan_check = self._context.get('loan_check')
    #     discount_all = self._context.get('discount_all')
    #     refund_discount = self._context.get('refund_discount')
    #     if collect_disc_batch or loan_check or discount_all or refund_discount or ctx_del_batch or ctx_del or ctx_bank_batch or ctx_bank or ctx_loan_batch or ctx_discount_batch:
    #         return True
    #     # Perform all checks on lines
    #     company_ids = set()
    #     all_accounts = []
    #     partners = set()
    #     for line in self:
    #
    #         company_ids.add(line.company_id.id)
    #         all_accounts.append(line.account_id)
    #         if (line.account_id.account_type in ('asset_receivable', 'liability_payable')):
    #             partners.add(line.partner_id.id)
    #         if line.reconciled:
    #             raise UserError(_('You are trying to reconcile some entries that are already reconciled!'))
    #
    #     if len(company_ids) > 1:
    #         raise UserError(_('To reconcile the entries company should be the same for all entries!'))
    #
    #     if len(set(all_accounts)) > 1:
    #         raise UserError(_('Entries are not of the same account!'))
    #
    #     if not (all_accounts[0].reconcile or all_accounts[0].account_type == 'liquidity'):
    #         raise UserError(_('The account %s (%s) is not marked as reconciliable !') % (
    #             all_accounts[0].name, all_accounts[0].code))
    #     if len(partners) > 1:
    #         raise UserError(_('The partner has to be the same on all lines for receivable and payable accounts!'))
    #
    #     not_paid_invoices = self.mapped('move_id').filtered(
    #         lambda m: m.is_invoice(include_receipts=True) and m.invoice_payment_state not in ('paid', 'in_payment')
    #     )
    #
    #     reconciled_lines = self.filtered(lambda aml: float_is_zero(aml.balance,
    #                                                                precision_rounding=aml.move_id.company_id.currency_id.rounding) and aml.reconciled)
    #     (self - reconciled_lines)._check_reconcile_validity()
    #     # reconcile everything that can be
    #     remaining_moves = self.auto_reconcile_lines()
    #
    #     writeoff_to_reconcile = self.env['account.move.line']
    #     # if writeoff_acc_id specified, then create write-off move with value the remaining amount from move in self
    #     if writeoff_acc_id and writeoff_journal_id and remaining_moves:
    #         all_aml_share_same_currency = all([x.currency_id == self[0].currency_id for x in self])
    #         writeoff_vals = {
    #             'account_id': writeoff_acc_id.id,
    #             'journal_id': writeoff_journal_id.id
    #         }
    #         if not all_aml_share_same_currency:
    #             writeoff_vals['amount_currency'] = False
    #         writeoff_to_reconcile = remaining_moves._create_writeoff([writeoff_vals])
    #         # add writeoff line to reconcile algorithm and finish the reconciliation
    #         remaining_moves = (remaining_moves + writeoff_to_reconcile).auto_reconcile_lines()
    #     # Check if reconciliation is total or needs an exchange rate entry to be created
    #     (self + writeoff_to_reconcile).check_full_reconcile()
    #
    #     # Trigger action for paid invoices
    #     not_paid_invoices.filtered(
    #         lambda m: m.invoice_payment_state in ('paid', 'in_payment')
    #     ).action_invoice_paid()
    #
    #     return True
        


class InvoiceDetails(models.Model):
    _name='invoice.details'
    header_1= fields.Char(string='Header 1')
    header_2= fields.Char(string='Header 2')
    invoice_id = fields.Many2one( comodel_name='account.move')

class DocumentType(models.Model):
    _name='move.doc.type'
    name = fields.Char(string="Name", required=True)
