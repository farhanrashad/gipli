from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class CashCollection(models.Model):
    _name = "account.customer.collection"
    _description = 'Customer Cash Collection'
    _order = "date desc, id desc"

    name = fields.Char(string='Reference')
    date = fields.Date(required=True, copy=False, default=fields.Date.context_today, readonly=True, string='Cash Date')
    bank_date = fields.Date(required=True, copy=False, default=fields.Date.context_today, readonly=True, string='Bank Date')
    state = fields.Selection([
        ('draft', 'New'),
        ('payment', 'Payment'),
        ('deposit', 'Deposit'),
    ], store=True, default='draft')
    city = fields.Char(string='City')
    journal_id = fields.Many2one('account.journal', string='Cash Collection', domain=[('type', '=', 'cash')], required=True)
    bank = fields.Many2one('account.journal', string='Bank Account', domain=[('type', '=', 'bank')])
    payment_lines_ids = fields.One2many('account.customer.collection.line', 'batch_payment_lines_id')
    amount = fields.Monetary(store=True, readonly=True)
    currency_id = fields.Many2one('res.currency', store=True, readonly=True)
    batch_type = fields.Selection(selection=[('inbound', 'Inbound'), ('outbound', 'Outbound')], required=True, default='inbound', string='Type')
    payment_line = fields.Many2many('res.partner', compute='_compute_payment_line')
    payment_method_id = fields.Many2one(
        comodel_name='account.payment.method',
        string='Payment Method', store=True, readonly=False,
        compute='_compute_payment_method_id',
        domain="[('id', 'in', available_payment_method_ids)]",
        help="The payment method used by the payments in this batch.")
    available_payment_method_ids = fields.Many2many('account.payment.method',
                                                    compute='_compute_available_payment_method_ids')
    payment_method_code = fields.Char(related='payment_method_id.code', readonly=False)
    payments = fields.Many2many('account.payment', string="Payments",)
    
    
    @api.model
    def create(self, vals):
        vals['name'] = self._get_batch_name(vals.get('batch_type'), vals.get('date', fields.Date.context_today(self)), vals)
        rec = super(CashCollection, self).create(vals)
        return rec

    def write(self, vals):
        if 'batch_type' in vals:
            vals['name'] = self.with_context(default_journal_id=self.journal_id.id)._get_batch_name(vals['batch_type'], self.date, vals)
        rslt = super(CashCollection, self).write(vals)
        return rslt
    
    
    @api.onchange('payment_lines_ids')
    def _compute_payment_line(self):
        data = []
        for approver in self:
            for line in approver.payment_lines_ids:
                data.append(line.partner_id.id)
            approver.payment_line = data
            
            
    @api.model
    def _get_batch_name(self, batch_type, sequence_date, vals):
        if not vals.get('name'):
            sequence_code = 'account.inbound.cash.payment'
            if batch_type == 'outbound':
                sequence_code = 'account.outbound.cash.payment'
            return self.env['ir.sequence'].with_context(sequence_date=sequence_date).next_by_code(sequence_code)
        return vals['name']

    @api.depends('batch_type', 'journal_id')
    def _compute_payment_method_id(self):
        for batch in self:
            if batch.batch_type == 'inbound':
                available_payment_methods = batch.journal_id.inbound_payment_method_ids
            else:
                available_payment_methods = batch.journal_id.outbound_payment_method_ids

            # Select the first available one by default.
            if available_payment_methods:
                batch.payment_method_id = available_payment_methods[0]._origin
            else:
                batch.payment_method_id = False

    @api.depends('batch_type',
                 'journal_id.inbound_payment_method_ids',
                 'journal_id.outbound_payment_method_ids')
    def _compute_available_payment_method_ids(self):
        for batch in self:
            if batch.batch_type == 'inbound':
                batch.available_payment_method_ids = batch.journal_id.inbound_payment_method_ids
            else:
                batch.available_payment_method_ids = batch.journal_id.outbound_payment_method_ids
      
    def post_payment_button(self):
        data = []
        flag = 0
        if not self.payment_lines_ids:
            raise UserError(_("Cannot validate an empty collection. Please add some payments to it first."))
        
        for i in self.payment_lines_ids:
            batch = self.env['account.payment'].create({
            'journal_id': self.journal_id.id,
            'partner_id': i.partner_id.id,
            'amount': i.amount,
            'payment_date': self.date,
            'payment_type': self.batch_type,
            'partner_type': 'customer',
            'destination_account_id': i.partner_id.property_account_receivable_id.id,
            'payment_method_id': self.payment_method_id.id,
              })
            i.name = batch.id
            batch.post()
        self.write({'state':'payment'})

    
    def cash_deposit_button(self):
        if not (self.bank and self.journal_id):
            raise UserError(_('You must define a Bank Account for this customer.'))
        amount_total = 0
        for i in self.payment_lines_ids:
            amount_total = amount_total + i.amount
        
        record = self.env['account.move'].create({
            'date': fields.Date.today(),
            'date': self.bank_date,
            'journal_id': self.bank.id,
            'line_ids': [(0, 0, {'account_id': self.bank.default_debit_account_id.id,
                                        'name': self.name,
                                        'debit': amount_total, }),
                         (0, 0, {'account_id': self.journal_id.default_debit_account_id.id,
                                        'name': self.name,
                                        'credit': amount_total, })], 
              })
        record.action_post()
        
        self.write({'state':'deposit'})
        
    def action_add_payments(self):
        return self.payments
    
    @api.onchange('city')
    def _compute_line_cities(self):
        for partner in self:
            if partner.payment_lines_ids:
                for i in partner.payment_lines_ids:
                    i.city = partner.city
            else:
                pass

class CustomerCollectionLine(models.Model):
    _name = "account.customer.collection.line"
    _description = 'Customer Cash Collection Line'
    
    
    def get_partners(self):
        for rec in self:
            if rec.city:
                return [('city', '=', rec.city)]
            else:
                pass
    
    
    batch_payment_lines_id = fields.Many2one('account.customer.collection', ondelete='set null', copy=False, string='Cash Payment')
    name = fields.Many2one('account.payment', string="Reference")
    city = fields.Char(compute='_compute_city_to_search_partner')
    partner_id = fields.Many2one('res.partner', domain="[('city', '=', city),('id', 'not in', payment_ids)]" ,required=True)
    payment_ids = fields.Many2many('res.partner', compute='_compute_payment_ids')
    amount = fields.Integer(string='Amount')
     
    @api.onchange('partner_id', 'batch_payment_lines_id.city')
    def _compute_city_to_search_partner(self):
        for partner in self:
            partner.city = partner.batch_payment_lines_id.city
            
    
    @api.onchange('partner_id')
    def _compute_payment_ids(self):
        for approver in self:
            approver.payment_ids = approver.batch_payment_lines_id.payment_line
            
            
    @api.constrains('amount')
    def check_commission_amount(self):
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError('Amount should be greater than 0.')


class AccountJournalInherit(models.Model):
    _inherit = "account.journal"
    
    @api.model
    def _create_cash_payment_outbound_sequence(self):
        IrSequence = self.env['ir.sequence']
        if IrSequence.search([('code', '=', 'account.outbound.cash.payment')]):
            return
        return IrSequence.sudo().create({
            'name': _("Outbound Batch Payments Sequence"),
            'padding': 4,
            'code': 'account.outbound.cash.payment',
            'number_next': 1,
            'number_increment': 1,
            'use_date_range': True,
            'prefix': 'CASH/OUT/%(year)s/',
            #by default, share the sequence for all companies
            'company_id': False,
        })

    @api.model
    def _create_cash_payment_inbound_sequence(self):
        IrSequence = self.env['ir.sequence']
        if IrSequence.search([('code', '=', 'account.inbound.cash.payment')]):
            return
        return IrSequence.sudo().create({
            'name': _("Inbound Batch Payments Sequence"),
            'padding': 4,
            'code': 'account.inbound.cash.payment',
            'number_next': 1,
            'number_increment': 1,
            'use_date_range': True,
            'prefix': 'CASH/IN/%(year)s/',
            #by default, share the sequence for all companies
            'company_id': False,
        })