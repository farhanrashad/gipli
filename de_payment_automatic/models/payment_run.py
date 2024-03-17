# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

STATES = [
    ('draft', 'Draft'), 
    ('propose', 'Propose'),
    ('progress', 'In Progress'),
    ('posted', 'Posted'),
    ('Canceled', 'cancel'),  
]

class PaymentRun(models.Model):
    _name = 'account.payment.run'
    _description = "Payment Run"
    _order = "date desc, name desc"
    _inherit = ['mail.thread.main.attachment', 'mail.activity.mixin']
    _check_company_auto = True
    _sequence_index = "journal_id"

    name = fields.Char(
        string='Reference',
        copy=False,
        tracking=True,
        index='trigram',
    )

    date = fields.Date(
        string='Date',
        index=True,
        store=True, required=True, readonly=False,
        default=lambda self: fields.Date.context_today(self),
        copy=False,
        tracking=True,
    )
    
    state = fields.Selection(
        selection=STATES,
        string='Status',
        required=True,
        readonly=True,
        copy=False,
        tracking=True,
        default='draft',
    )
    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Journal',
        domain="[('type', 'in', ('bank','cash'))]",
        check_company=True,
        required=True,
    )
    
    payment_type = fields.Selection([
        ('outbound', 'Send'),
        ('inbound', 'Receive'),
    ], string='Payment Type', default='inbound', required=True, tracking=True)
    partner_type = fields.Selection([
        ('customer', 'Customer'),
        ('supplier', 'Vendor'),
    ], default='customer', tracking=True, required=True)
    amount = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        compute='_compute_currency_id', store=True, readonly=False, precompute=True,
        help="The payment's currency.")
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        compute='_compute_company_id', 
        store=True, readonly=False, precompute=True,
        index=True,
    )

    exclude_partner_ids = fields.Many2many(
        'res.partner',
        'partner_payment_run_rel',
        'partner_id',
        'payment_run_id',
        string='Excluded Partners'
    )
    group_payment = fields.Boolean(string='Group Payment',
                                    help='combine partner multiple payments in one payment.',
                                  )

    # Parameter fields
    date_invoice = fields.Date(
        string='Invoice Date Up To',
        copy=False,
    )
    date_accounting = fields.Date(
        string='Accounting Date',
        default=lambda self: fields.Date.context_today(self),
        copy=False,
    )
    date_due_by = fields.Date(
        string='Items Due By',
        copy=False,
    )
    # Extra Selection
    filter_domain = fields.Char(string='Apply On', help="If present, this domain would apply to filter accounting documents.")

    # to pay accounting documents
    line_ids = fields.One2many(
        'account.payment.run.line',
        'payment_run_id',
        string='Propose Accounting Documents',
        copy=True,
    )
    count_proposal = fields.Integer('Proposal Count',
                                    compute='_compute_proposal_count',
                                   )
    
    # Computed Methods
    def _compute_proposal_count(self):
        for proposal in self:
            proposal.count_proposal = len(proposal.line_ids)
        
    @api.depends('journal_id')
    def _compute_currency_id(self):
        for pay in self:
            pay.currency_id = pay.journal_id.currency_id or pay.journal_id.company_id.currency_id
            
    @api.depends('journal_id')
    def _compute_company_id(self):
        for move in self:
            if move.journal_id.company_id not in move.company_id.parent_ids:
                move.company_id = (move.journal_id.company_id or self.env.company)._accessible_branches()[:1]

    # Actions
    def button_proposal(self):
        move_ids = self.env['account.move'].search([
            ('move_type','in',('in_invoice','in_refund'))
        ])
        self.line_ids.unlink()
        for move in move_ids:
            self.env['account.payment.run.line'].create({
                'payment_run_id': self.id,
                'move_id': move.id,
            })
            
        
    def open_payment_proposal(self):
        action = self.env.ref('de_payment_automatic.action_payment_run_line').read()[0]
        action.update({
            'name': 'Accounting Documents',
            'view_mode': 'tree',
            'res_model': 'account.payment.run.line',
            'type': 'ir.actions.act_window',
            'domain': [('payment_run_id','=',self.id)],
            'context': {
                'create': False,
                'edit': True,
            },
            
        })
        return action


class PaymentRunLine(models.Model):
    _name = "account.payment.run.line"
    _description = "Payment Run Items"

    payment_run_id = fields.Many2one(
        comodel_name='account.payment.run',
        string='Payment Run',
        required=True,
        readonly=True,
        index=True,
        auto_join=True,
        ondelete="cascade",
        check_company=True,
    )
    company_id = fields.Many2one(
        related='payment_run_id.company_id', store=True, readonly=True, precompute=True,
        index=True,
    )
    #currency_id = fields.Many2one(
    #    related='payment_run_id.currency_id', store=True, readonly=True, precompute=True,
    #    index=True,
    #)
    move_id = fields.Many2one(
        comodel_name='account.move',
        string='Journal Entry',
        required=True,
        readonly=True,
        index=True,
        auto_join=True,
        ondelete="cascade",
        check_company=True,
    )
    partner_id = fields.Many2one(related='move_id.partner_id')
    journal_id = fields.Many2one(related='move_id.journal_id')
    invoice_date = fields.Date(related='move_id.invoice_date')
    invoice_date_due = fields.Date(related='move_id.invoice_date_due')
    
    amount_total_signed = fields.Monetary(related='move_id.amount_total_signed')
    amount_residual_signed = fields.Monetary(related='move_id.amount_residual_signed')
    amount_total = fields.Monetary(related='move_id.amount_total')
    amount_residual = fields.Monetary(related='move_id.amount_residual')
    currency_id = fields.Many2one(related='move_id.currency_id' )
    
    amount_to_pay = fields.Monetary(
        string='Amount to Pay',
        store=True,
        readonly=False,
        compute='_compute_to_pay_amount',
    )
    @api.depends('move_id')
    def _compute_to_pay_amount(self):
        for record in self:
            record.amount_to_pay = record.move_id.amount_residual_signed

    def open_Journal_entry(self):
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        action.update({
            'name': 'Accounting Documents',
            'view_mode': 'form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'domain': [('id','=',self.move_id.id)],
            'context': {
                'create': False,
                'edit': False,
                'active_id': self.move_id.id,  
                'active_model': 'account.move',
            },
            
        })
        return action
    
    