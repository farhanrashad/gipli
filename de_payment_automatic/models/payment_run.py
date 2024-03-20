# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.tools import safe_eval
from odoo.exceptions import UserError, ValidationError
from collections import defaultdict

STATES = [
    ('draft', 'Draft'), 
    ('proposal', 'Proposal'),
    ('scheduled', 'Scheduled'),
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

    run_method = fields.Selection([
        ('now', 'Now'),
        ('scheduled', 'Schedule Later'),
    ], string='When', default='now', required=True,
    )
    
    date = fields.Date(
        string='Run Date',
        index=True,
        store=True, required=True, readonly=False,
        default=lambda self: fields.Date.context_today(self),
        copy=False,
        tracking=True,
    )

    date_next_run = fields.Date(
        string='Next Run Date',
        index=True,
        store=True, required=True, readonly=False,
        default=lambda self: (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d'),
        copy=False,
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
    
    payment_type = fields.Selection([
        ('outbound', 'Send'),
        ('inbound', 'Receive'),
    ], string='Payment Type', default='inbound', required=True, tracking=True)
    partner_type = fields.Selection([
        ('customer', 'Customer'),
        ('supplier', 'Vendor'),
    ], default='customer', tracking=True, required=True)
    
    
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

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
    count_proposal = fields.Integer('Proposals',
                                    compute='_compute_proposal_count',
                                   )
    count_payments = fields.Integer('Payments',
                                    compute='_compute_payment_count',
                                   )
    
    # Computed Methods
    def _compute_proposal_count(self):
        for proposal in self:
            proposal.count_proposal = len(proposal.line_ids)

    def _compute_payment_count(self):
        for proposal in self:
            proposal.count_payments = len(proposal.line_ids.mapped('payment_id'))


    # Actions
    def button_proposal(self):
        move_ids = self.env['account.move'].search(self._prepare_domain())
        self.line_ids.unlink()
        for move in move_ids:
            self.env['account.payment.run.line'].create(self._prepare_payment_run_line(move))
            self.write({
                'state': 'proposal',
            })

    def button_draft(self):
        self.line_ids.unlink()
        self.write({
            'state': 'draft',
        })

    def button_schedule(self):
        self.write({
            'state': 'scheduled',
        })
         
    def button_execute (self):
        if self.group_payment:
            self._create_payment(self.group_payment)
        else:
            self._create_multiple_payments()

        if self.run_method == 'scheduled':
            if self.date == fields.Date.today():
                raise UserError('Run date must be in future')
            self.write({
                'state': 'scheduled',
            })
        else:
            self.write({
                'state': 'posted',
            })

    def _create_payment(self, group_payment=False):
        if group_payment:
            partner_lines = defaultdict(list)
            for move in self.line_ids:
                partner_lines[move.move_id.partner_id.id].append(move)
            for partner_id, lines in partner_lines.items():
                total_amount = sum(line.amount_to_pay for line in lines)
                payment_vals = self._prepare_payment(lines[0])
                payment_vals.update({
                    'amount': abs(total_amount),
                    'payment_run_id': self.id,
                })
                payment_id = self.env['account.payment'].create(payment_vals)
                payment_id.action_post()
                for line in lines:
                    line.write({'payment_id': payment_id.id})
                    line._reconcile_payment(line.move_id, payment_id.move_id)

    def _create_multiple_payments(self):
        for move in self.line_ids:
            payment_vals = self._prepare_payment(move)
            payment_vals.update({
                'amount': abs(move.amount_total),
                'payment_run_id': self.id,
            })
            payment_id = self.env['account.payment'].create(payment_vals)
            payment_id.action_post()
            move.write({'payment_id': payment_id.id})
            move._reconcile_payment(move.move_id, payment_id.move_id)
            
    def _prepare_payment(self,line):
        vals = {
            'partner_type': self.partner_type,
            'partner_id': line.partner_id.id,
            'date': self.date,
            'ref': line.move_id.name,
            'journal_id': self.company_id.pr_default_journal_id.id,
            #'amount': abs(line.amount_to_pay),
            #'payment_run_id': self.id,
        }
        if line.move_id.move_type == 'in_refund' or line.move_id.move_type == 'out_invoice':
            vals['payment_type'] = 'inbound'
        else:
            vals['payment_type'] = 'outbound'
            
        return vals

    

    def _prepare_payment_run_line(self,move):
        return {
            'payment_run_id': self.id,
            'move_id': move.id,
            'payment_journal_id': move.partner_id.pr_journal_id.id or self.company_id.pr_default_journal_id.id
        }
    
    def _prepare_domain(self):
        search_domain = [
            ('payment_state','in', ['not_paid','partial']),
            ('state','=','posted'),
                        ]
        if self.filter_domain:
            search_domain += safe_eval.safe_eval(self.filter_domain)
        if self.date_due_by:
            search_domain += [('invoice_date_due', '<=', self.date_due_by)]
        if self.date_due_by:
            search_domain += [('invoice_date', '<=', self.date_invoice)]
        if self.exclude_partner_ids:
            search_domain += [('partner_id', 'not in', self.exclude_partner_ids.ids)]
        if self.partner_type == 'supplier':
            search_domain += [('move_type','in',('in_invoice','in_refund'))]
        else:
            search_domain += [('move_type','in',('out_invoice','out_refund'))]
        
        return search_domain
        
        
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

    def open_payments(self):
        if self.partner_type == 'supplier':
            action = self.env.ref('account.action_account_payments_payable').read()[0]
        else:
            action = self.env.ref('account.action_account_payments').read()[0]
            
        action.update({
            'name': 'Payment',
            'view_mode': 'tree',
            'res_model': 'account.payment',
            'type': 'ir.actions.act_window',
            'domain': [('payment_run_id','=',self.id),('state','!=','cancel')],
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
    payment_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string="Journal",
        check_company=True,
        domain="[('type', 'in', ('bank','cash'))]",
    )
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
    exclude_for_payment = fields.Boolean('Exclude')
    parent_state = fields.Char('payment_run_id.state')

    payment_id = fields.Many2one(
        comodel_name='account.payment',
        string="Payment",
        readonly=True,
        compute='_compute_payment',
        domain="[('state','!=','cancel')]",
        store=True
    )

    @api.depends('payment_id.state')
    def _compute_payment(self):
        for record in self:
            if record.payment_id.state == 'cancel':
                record.payment_id = False
        
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
        
    def _reconcile_payment(self,move_id, payment_move_id):
        move_lines = move_id.line_ids.filtered(lambda line: line.account_id in (self._find_accounts(line)))
        payment_lines = payment_move_id.line_ids.filtered(lambda line: line.account_id in (self._find_accounts(line)))
        (move_lines + payment_lines).reconcile()
        
    def _find_accounts(self,line):
        return [
            line.partner_id.property_account_payable_id,
            line.partner_id.property_account_receivable_id,
        ]
    