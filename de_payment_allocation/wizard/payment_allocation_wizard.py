# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class PaymentAllocation(models.TransientModel):
    _name = 'payment.allocation.wizard'
    _description = 'Payment Allocation Wizard'
    
    
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    company_id = fields.Many2one('res.company', string='Company')
    currency_id = fields.Many2one('res.currency', string='Currency')
    is_payment = fields.Boolean(string='Is Payment')
    is_invoice = fields.Boolean(string='Is Invoice')
    account_id = fields.Many2one('account.account', string='Account')
    amount = fields.Monetary(string='Amount')
    journal_entries_ids = fields.One2many('invoice.allocation.wizard.line.entry', 'allocation_id', string='Journal Entries')
    payment_line_ids = fields.One2many('payment.allocation.wizard.line', 'allocation_id', string='Payment Lines')
    invoice_move_ids = fields.One2many('invoice.allocation.wizard.line', 'allocation_id', string='Invoice Lines')
    invoice_refund_ids = fields.One2many('invoice.allocation.wizard.line.credit', 'allocation_id', string='Invoice Refund Lines')
    payment_id = fields.Many2one('account.payment', string='Payment')
    move_id = fields.Many2one('account.move', string='Move')
    
    payment_amount = fields.Monetary(string='Payment Amount', compute='_amount_all')
    allocated_amount = fields.Monetary(string='Allocated Amount', compute='_amount_all')
    diff_amount = fields.Monetary(string='Difference', compute='_amount_all')
    is_refund_reconciled = fields.Boolean(string='Invoice/Refund Reconcile')   
    journal_id = fields.Many2one(related='payment_id.journal_id')
    payment_type = fields.Selection(related='payment_id.payment_type')
    partner_type = fields.Selection(related='payment_id.partner_type')
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Method', readonly=False, store=True, compute='_compute_payment_method_id', )
    
    
    @api.depends('invoice_move_ids.allocate_amount', 'payment_line_ids.allocate_amount', 'invoice_refund_ids.allocate_amount', 'journal_entries_ids.allocate_amount')
    def _amount_all(self):
        for order in self:
            amount_untaxed = 0.0
            payment_total = 0.0
            if self.payment_id:
                for line in order.invoice_move_ids:
                    if line.allocate == True:
                        amount_untaxed += line.allocate_amount
                for refund_line in order.invoice_refund_ids:
                    if refund_line.allocate == True:
                        amount_untaxed -= refund_line.allocate_amount 
                for entry_line in order.journal_entries_ids:
                    if entry_line.allocate == True:
                        amount_untaxed += entry_line.allocate_amount
                for payment in order.payment_line_ids:
                    if payment.allocate == True:
                        payment_total += payment.allocate_amount
            else:
                for payment_line in order.payment_line_ids:
                    if payment_line.allocate == True:
                        amount_untaxed += payment_line.allocate_amount
            order.update({
                'payment_amount': payment_total,
                'allocated_amount': amount_untaxed,
                'diff_amount': (payment_total - amount_untaxed),
            })

            
    
    @api.depends('journal_id')
    def _compute_payment_method_id(self):
        for wizard in self:
            payment_type = wizard.payment_type

            if payment_type == 'inbound':
                available_payment_methods = wizard.journal_id.inbound_payment_method_ids
            else:
                available_payment_methods = wizard.journal_id.outbound_payment_method_ids

            # Select the first available one by default.
            if available_payment_methods:
                wizard.payment_method_id = available_payment_methods[0]._origin
            else:
                wizard.payment_method_id = False
                
                
    def action_allocate_invoice_payment(self):
        tot_payment_amount = 0.0
        tot_invoice_amount = 0.0  
        for invoice in self.invoice_move_ids:
            if invoice.allocate == True:
                tot_invoice_amount = tot_invoice_amount + invoice.allocate_amount  
                
        for payment_line in self.payment_line_ids: 
            if payment_line.allocate == True:
                if payment_line.payment_id.currency_id.id == self.move_id.currency_id.id:
                    tot_payment_amount = tot_payment_amount + payment_line.allocate_amount
                else:
                    tot_payment_amount = tot_payment_amount + payment_line.payment_id.currency_id._convert(payment_line.allocate_amount, self.move_id.currency_id, self.move_id.company_id, self.move_id.date)
                    
        for refund_line in self.invoice_refund_ids: 
            if refund_line.allocate == True:
                if refund_line.currency_id.id == self.move_id.currency_id.id:
                    tot_payment_amount = tot_payment_amount + refund_line.allocate_amount
                else:
                    tot_payment_amount = tot_payment_amount + refund_line.currency_id._convert(refund_line.allocate_amount, self.move_id.currency_id, self.move_id.company_id, self.move_id.date)            

        for payment in self.payment_line_ids:
            if payment.allocate == True:
                debit_line = 0
                credit_line = 0
                payment_debit_line = 0
                for line in self.move_id.line_ids:
                    if line.credit != 0.0:
                        credit_line = line.id 
                    if line.credit == 0.0:
                        debit_line = line.id  
                        
                for payment_line in payment.payment_id.move_id.line_ids:                    
                    payment_debit_line = payment_line.id
                recocile_vals = {
                    'exchange_move_id': self.move_id.id,
                }
                reconcile_id = self.env['account.full.reconcile'].create(recocile_vals)
                amount_reconcile = 0.0
                if payment.payment_id.currency_id.id == self.move_id.currency_id.id:
                    amount_reconcile = payment.allocate_amount
                else:
                    amount_reconcile = payment.allocate_amount
                    
                vals = {
                    'full_reconcile_id': reconcile_id.id,
                    'amount':  payment.allocate_amount,
                    'credit_move_id':  credit_line,
                    'debit_move_id': payment_debit_line,
                    'credit_amount_currency': amount_reconcile,
                    'debit_amount_currency': amount_reconcile,
                }
                partial_payment = self.env['account.partial.reconcile'].create(vals)    
        for refund in self.invoice_refund_ids:
            if refund.allocate == True:
                refund_debit_line = 0
                refund_credit_line = 0
                pmove_debit_line = 0
                for line in refund.move_id.line_ids:
                    if line.credit == 0.0:
                        refund_credit_line = line.id        
                for inv_line in self.payment_id.move_id.line_ids:
                    if inv_line.debit == 0.0:
                        pmove_debit_line = inv_line.id    
                refund_recocile_vals = {
                    'exchange_move_id': refund.move_id.id,
                } 
                refund_reconcile_id = self.env['account.full.reconcile'].create(refund_recocile_vals)
                refund_amount_reconcile = 0.0
                if refund.move_id.currency_id.id == self.payment_id.currency_id.id:
                    refund_amount_reconcile = refund.allocate_amount
                else:
                    refund_amount_reconcile = refund.allocate_amount
                vals = {
                    'full_reconcile_id': refund_reconcile_id.id,
                    'amount':  refund.allocate_amount,
                    'credit_move_id':  pmove_debit_line ,
                    'debit_move_id': refund_credit_line,
                    'credit_amount_currency': refund_amount_reconcile,
                    'debit_amount_currency': refund_amount_reconcile,
                }
                partial_payment = self.env['account.partial.reconcile'].create(vals)
                
                
    def  action_invoice_refund_reconciled(self):
        invoice_count = debit_line = refund_entry = invoice_entry = refund_credit_line = 0
        total_invoice_amount = total_refund_amount = amount_entry = 0
        remulti_debit_line = 0
        for invoice in self.invoice_move_ids:
            if invoice.allocate == True:
                invoice_entry = invoice
                invoice_count += 1
        if invoice_count > 1:
            for multi_invoice in self.invoice_move_ids:
                if multi_invoice.allocate == True:
                    multi_invoice_entry = multi_invoice
                    for multi_inv_line in multi_invoice.move_id.line_ids:
                        if multi_invoice.move_id.move_type == 'in_invoice':
                            if multi_inv_line.credit > 0:
                                multi_debit_line =  multi_inv_line.id
                        if multi_invoice.move_id.move_type == 'out_invoice':
                            if multi_inv_line.debit > 0:
                                multi_debit_line =  multi_inv_line.id 
                    for multi_refund in self.invoice_refund_ids:
                        if multi_refund.allocate == True:
                            for multi_refund_line in multi_refund.move_id.line_ids:
                                if multi_refund.move_id.move_type == 'in_refund':
                                    if multi_refund_line.debit > 0:
                                        multi_refund_credit_line =  multi_refund_line.id
                                        remulti_debit_line = multi_refund_line.id
                                if multi_refund.move_id.move_type == 'out_refund':
                                    if multi_refund_line.credit > 0:
                                        multi_refund_credit_line =  multi_refund_line.id
                                        remulti_debit_line = multi_refund_line.id

                            if multi_refund.move_id.amount_residual > 0.0 and multi_invoice.move_id.amount_residual> 0.0: 
                                multi_recocile_vals = {
                                    'exchange_move_id': multi_invoice.move_id.id,
                                }
                                multi_reconcile_id = self.env['account.full.reconcile'].create(multi_recocile_vals)
                                multi_amount_reconcile = 0.0
                                if multi_invoice.move_id.currency_id.id == multi_refund.move_id.currency_id.id:
                                    if multi_invoice.allocate_amount > multi_refund.allocate_amount:
                                        multi_amount_reconcile = multi_refund.allocate_amount
                                    else:
                                        multi_amount_reconcile = multi_invoice.allocate_amount
                                else:
                                    if multi_invoice_entry.allocate_amount > multi_refund.allocate_amount:
                                        multi_amount_reconcile = multi_refund.move_id.currency_id._convert(multi_invoice.allocate_amount, multi_invoice.move_id.currency_id, multi_invoice.move_id.company_id, multi_invoice.move_id.date) 
                                    else:
                                        multi_amount_reconcile = multi_invoice.move_id.currency_id._convert(multi_refund.allocate_amount, multi_refund.move_id.currency_id, multi_refund.move_id.company_id, multi_refund.move_id.date)
                                if  multi_invoice_entry.move_id.move_type == 'out_invoice':       
                                    multi_vals = {
                                        'full_reconcile_id': multi_reconcile_id.id,
                                        'amount':  multi_invoice_entry.allocate_amount,
                                        'credit_move_id':  multi_refund_credit_line,
                                        'debit_move_id': multi_debit_line,
                                        'credit_amount_currency': multi_amount_reconcile,
                                        'debit_amount_currency': multi_amount_reconcile,
                                    }
                                    reconcile_line = self.env['account.partial.reconcile'].create(multi_vals)
                                else:       
                                    multi_vals = {
                                        'full_reconcile_id': multi_reconcile_id.id,
                                        'amount':  multi_invoice_entry.allocate_amount,
                                        'credit_move_id':  multi_debit_line,
                                        'debit_move_id': multi_refund_credit_line,
                                        'credit_amount_currency': multi_amount_reconcile,
                                        'debit_amount_currency': multi_amount_reconcile,
                                    }
                                    reconcile_line = self.env['account.partial.reconcile'].create(multi_vals)    
                                paymulti_recocile_vals = {
                                    'exchange_move_id': multi_invoice.move_id.id,
                                }
                                paymulti_reconcile_id = self.env['account.full.reconcile'].create(paymulti_recocile_vals)
                                rep_refund_payment_debit_line = 0
                                for rep_refund_payment_line in self.payment_id.move_id.line_ids:
                                    if rep_refund_payment_line.debit == 0.0:
                                        rep_refund_payment_debit_line = rep_refund_payment_line.id
                                paymulti_vals = {
                                    'full_reconcile_id': paymulti_reconcile_id.id,
                                    'amount':  0,
                                    'credit_move_id':  multi_debit_line,
                                    'debit_move_id': rep_refund_payment_debit_line,
                                    'credit_amount_currency': 0,
                                    'debit_amount_currency': 0,
                                }
                                payreconcile_line = self.env['account.partial.reconcile'].create(paymulti_vals)
                                re_paymulti_recocile_vals = {
                                    'exchange_move_id': multi_refund.move_id.id,
                                }
                                re_paymulti_reconcile_id = self.env['account.full.reconcile'].create(paymulti_recocile_vals)
                                re_p_refund_payment_debit_line = 0
                                for re_p_refund_payment_line in self.payment_id.move_id.line_ids:
                                    if re_p_refund_payment_line.debit == 0.0:
                                        re_p_refund_payment_debit_line = re_p_refund_payment_line.id
                                re_paymulti_vals = {
                                    'full_reconcile_id': re_paymulti_reconcile_id.id,
                                    'amount':  0,
                                    'credit_move_id':  remulti_debit_line,
                                    'debit_move_id': re_p_refund_payment_debit_line,
                                    'credit_amount_currency': 0,
                                    'debit_amount_currency': 0,
                                }
                                re_payreconcile_line = self.env['account.partial.reconcile'].create(re_paymulti_vals)
      
        else:
            for invoice in self.invoice_move_ids:
                if invoice.allocate == True:
                    invoice_entry = invoice
                    for inv_line in invoice.move_id.line_ids:
                        if invoice.move_id.move_type == 'in_invoice':
                            if inv_line.credit > 0:
                                debit_line =  inv_line.id
                        if invoice.move_id.move_type == 'out_invoice':
                            if inv_line.debit > 0:
                                debit_line =  inv_line.id 
                                
            for refund in self.invoice_refund_ids:
                if refund.allocate == True:
                    refund_entry = refund
                    for refund_line in refund.move_id.line_ids:
                        if refund.move_id.move_type == 'in_refund':
                            if refund_line.debit > 0:
                                refund_credit_line =  refund_line.id 
                        if refund.move_id.move_type == 'out_refund':
                            if refund_line.credit > 0:
                                refund_credit_line =  refund_line.id        
            reconcile_amount = 0.0
            if invoice_entry.move_id.currency_id.id != refund_entry.move_id.currency_id.id:
                reconcile_amount = invoice_entry.move_id.currency_id._convert(refund_entry.allocate_amount, refund_entry.move_id.currency_id, refund_entry.move_id.company_id, refund_entry.move_id.date)    
            recocile_vals = {
                'exchange_move_id': invoice_entry.move_id.id,
            }
            reconcile_id = self.env['account.full.reconcile'].create(recocile_vals)
            amount_reconcile = 0.0
            if invoice_entry.move_id.currency_id.id == refund_entry.move_id.currency_id.id:
                if invoice_entry.allocate_amount > refund_entry.allocate_amount:
                    amount_reconcile = refund_entry.allocate_amount
                else:
                    amount_reconcile = invoice_entry.allocate_amount
            else:
                if invoice_entry.allocate_amount > refund_entry.allocate_amount:
                    amount_reconcile = refund_entry.move_id.currency_id._convert(invoice_entry.allocate_amount, invoice_entry.move_id.currency_id, invoice_entry.move_id.company_id, invoice_entry.move_id.date) 
                else:
                    amount_reconcile = invoice_entry.move_id.currency_id._convert(refund_entry.allocate_amount, refund_entry.move_id.currency_id, refund_entry.move_id.company_id, refund_entry.move_id.date)
            if invoice_entry.move_id.move_type == 'out_invoice':        
                vals = {
                    'full_reconcile_id': reconcile_id.id,
                    'amount':  invoice_entry.allocate_amount,
                    'credit_move_id':  refund_credit_line,
                    'debit_move_id': debit_line,
                    'credit_amount_currency': amount_reconcile,
                    'debit_amount_currency': amount_reconcile,
                }
                payment = self.env['account.partial.reconcile'].create(vals) 
            else:
                vals = {
                    'full_reconcile_id': reconcile_id.id,
                    'amount':  invoice_entry.allocate_amount,
                    'credit_move_id':  debit_line,
                    'debit_move_id': refund_credit_line,
                    'credit_amount_currency': amount_reconcile,
                    'debit_amount_currency': amount_reconcile,
                }
                payment = self.env['account.partial.reconcile'].create(vals)
            for pay_invoice in self.invoice_move_ids:
                if pay_invoice.allocate == True:
                    pay_debit_line = 0
                    pay_credit_line = 0
                    pay_payment_debit_line = 0
                    for pay_line in pay_invoice.move_id.line_ids:
                        if pay_line.credit != 0.0:
                            pay_credit_line = pay_line.id 
                        if pay_line.credit == 0.0:
                            pay_debit_line = pay_line.id    
                    pay_invoice.move_id.id
                    for pay_payment_line in self.payment_id.move_id.line_ids:                    
                        pay_payment_debit_line = pay_payment_line.id    
                    recocile_vals = {
                        'exchange_move_id': pay_invoice.move_id.id,
                    }
                    pay_reconcile_id = self.env['account.full.reconcile'].create(recocile_vals)
                    
                    vals = {
                        'full_reconcile_id': pay_reconcile_id.id,
                        'amount':  0,
                        'credit_move_id':  pay_credit_line,
                        'debit_move_id': pay_payment_debit_line,
                        'credit_amount_currency': 0,
                        'debit_amount_currency': 0,
                    }
                    pay_payment = self.env['account.partial.reconcile'].create(vals) 
            for re_refund in self.invoice_refund_ids:
                if re_refund.allocate == True:
                    re_refund_debit_line = 0
                    re_refund_credit_line = 0
                    re_refund_payment_debit_line = 0
                    for re_line in re_refund.move_id.line_ids:
                        if re_line.credit == 0.0:
                            re_refund_credit_line = re_line.id 

                    for re_refund_payment_line in self.payment_id.move_id.line_ids:
                        re_refund_payment_debit_line = re_refund_payment_line.id
  
                    refund_recocile_vals = {
                        'exchange_move_id': refund.move_id.id,
                    }
                    re_refund_reconcile_id = self.env['account.full.reconcile'].create(refund_recocile_vals)
 
                    vals = {
                        'full_reconcile_id': re_refund_reconcile_id.id,
                        'amount':  0,
                        'credit_move_id':  re_refund_payment_debit_line,
                        'debit_move_id': re_refund_credit_line ,
                        'credit_amount_currency': 0,
                        'debit_amount_currency': 0,
                    }
                    re_refund_payment = self.env['account.partial.reconcile'].create(vals)        
    
    
    def action_allocate_payment(self):
        if self.is_refund_reconciled==True:
            self.action_invoice_refund_reconciled()
        else:    
            if self.diff_amount != 0:
                raise UserError(_('The allocation amount difference found.'))
            invoice_line = []
            line_ids = [] 
            tot_invoice_amount = 0.0  
            tot_payment_amount = 0.0    
            for invoice in self.invoice_move_ids:
                if invoice.allocate == True:
                    tot_invoice_amount = tot_invoice_amount + invoice.allocate_amount 
            for refund_mv in self.invoice_refund_ids:
                if refund_mv.allocate == True:
                    tot_invoice_amount = tot_invoice_amount + refund_mv.allocate_amount 
            for jv_mv in self.journal_entries_ids:
                if jv_mv.allocate == True:
                    tot_invoice_amount = tot_invoice_amount + jv_mv.allocate_amount         

            for payment_line in self.payment_line_ids:                    
                tot_payment_amount = tot_payment_amount + payment_line.allocate_amount
                 
            for invoice in self.invoice_move_ids:
                if invoice.allocate == True:
                    debit_line = 0
                    credit_line = 0
                    payment_debit_line = 0
                    for line in invoice.move_id.line_ids:
                        if line.credit != 0.0:
                            credit_line = line.id 
                        if line.credit == 0.0:
                            debit_line = line.id    
                    invoice.move_id.id
                    for payment_line in self.payment_id.move_id.line_ids:                    
                        payment_debit_line = payment_line.id
                    reconcile_amount = 0.0
                    if invoice.move_id.currency_id.id != self.payment_id.currency_id.id:
                        reconcile_amount = invoice.currency_id._convert(invoice.allocate_amount, self.payment_id.currency_id, self.payment_id.company_id, self.payment_id.date)    
                    recocile_vals = {
                        'exchange_move_id': invoice.move_id.id,
                    }
                    reconcile_id = self.env['account.full.reconcile'].create(recocile_vals)
                    amount_reconcile = 0.0
                    if invoice.move_id.currency_id.id == self.payment_id.currency_id.id:
                        amount_reconcile = invoice.allocate_amount
                    else:
                        amount_reconcile = self.payment_id.currency_id._convert(invoice.allocate_amount, invoice.move_id.currency_id, invoice.move_id.company_id, invoice.move_id.date) 
                    vals = {
                        'full_reconcile_id': reconcile_id.id,
                        'amount':  invoice.allocate_amount,
                        'credit_move_id':  credit_line,
                        'debit_move_id': payment_debit_line,
                        'credit_amount_currency': amount_reconcile,
                        'debit_amount_currency': amount_reconcile,
                    }
                    payment = self.env['account.partial.reconcile'].create(vals)
                    if reconcile_amount == invoice.allocate_amount:
                        exchange_amount = invoice.move_id.amount_residual 
                        exchange_moves = self.action_exchange_rate(invoice.currency_id.id, exchange_amount)
                        ext_payment_debit_line = 0
                        for ext_line in exchange_moves.line_ids:
                            ext_payment_debit_line = ext_line.id
                            break
                        for ext_line in exchange_moves.line_ids:
                            if ext_line.account_id.id == self.payment_id.destination_account_id.id:
                                ext_payment_debit_line = ext_line.id
                        ext_recocile_vals = {
                            'exchange_move_id': invoice.move_id.id,
                            }
                        reconcile_id = self.env['account.full.reconcile'].create(ext_recocile_vals)                       
                        ext_vals = {
                            'full_reconcile_id': reconcile_id.id,
                            'amount':  invoice.allocate_amount,
                            'credit_move_id':  credit_line,
                            'debit_move_id': ext_payment_debit_line,
                            'credit_amount_currency': exchange_amount,
                            'debit_amount_currency': exchange_amount,
                            }
                        inv_payment = self.env['account.partial.reconcile'].create(ext_vals)

            for journal_move in self.journal_entries_ids:
                if journal_move.allocate == True:
                    jv_debit_line = 0
                    jv_credit_line = 0
                    jv_payment_debit_line = 0
                    for jv_line in journal_move.move_id.line_ids:
                        if jv_line.credit != 0.0:
                            jv_credit_line = jv_line.id 
                        if jv_line.credit == 0.0:
                            jv_debit_line = jv_line.id    
                    for jv_payment_line in self.payment_id.move_id.line_ids:                    
                        jv_payment_debit_line = jv_payment_line.id

                    jv_reconcile_amount = 0.0
                    if journal_move.move_id.currency_id.id != self.payment_id.currency_id.id:
                        jv_reconcile_amount = journal_move.currency_id._convert(journal_move.allocate_amount, self.payment_id.currency_id, self.payment_id.company_id, self.payment_id.date)    
                    jv_recocile_vals = {
                        'exchange_move_id': journal_move.move_id.id,
                    }
                    jv_reconcile_id = self.env['account.full.reconcile'].create(jv_recocile_vals)


                    jv_amount_reconcile = 0.0
                    if journal_move.move_id.currency_id.id == self.payment_id.currency_id.id:
                        jv_amount_reconcile = journal_move.allocate_amount
                    else:
                        jv_amount_reconcile = self.payment_id.currency_id._convert(journal_move.allocate_amount, journal_move.move_id.currency_id, journal_move.move_id.company_id, journal_move.move_id.date) 
                    jv_vals = {
                        'full_reconcile_id': jv_reconcile_id.id,
                        'amount':  journal_move.allocate_amount,
                        'credit_move_id':  jv_credit_line,
                        'debit_move_id': jv_payment_debit_line,
                        'credit_amount_currency': jv_amount_reconcile,
                        'debit_amount_currency': jv_amount_reconcile,
                    }
                    jv_payment = self.env['account.partial.reconcile'].create(jv_vals)

                    if jv_reconcile_amount == journal_move.allocate_amount:

                        jv_exchange_amount = journal_move.move_id.amount_residual 

                        jv_exchange_moves = self.action_exchange_rate(journal_move.currency_id.id, jv_exchange_amount)
                        jv_ext_payment_debit_line = 0
                        for jv_ext_line in jv_exchange_moves.line_ids:
                            jv_ext_payment_debit_line = jv_ext_line.id
                            break
                        for jv_ext_line in jv_exchange_moves.line_ids:
                            if jv_ext_line.account_id.id == self.payment_id.destination_account_id.id:
                                jv_ext_payment_debit_line = jv_ext_line.id
                        jv_ext_recocile_vals = {
                            'exchange_move_id': journal_move.move_id.id,
                            }

                        jv_ex_reconcile_id = self.env['account.full.reconcile'].create(jv_ext_recocile_vals)                       
                        jv_ext_vals = {
                            'full_reconcile_id': jv_ex_reconcile_id.id,
                            'amount':  journal_move.allocate_amount,
                            'credit_move_id':  jv_credit_line,
                            'debit_move_id': jv_ext_payment_debit_line,
                            'credit_amount_currency': jv_exchange_amount,
                            'debit_amount_currency': jv_exchange_amount,
                            }
                        jv_inv_payment = self.env['account.partial.reconcile'].create(jv_ext_vals)


            for refund in self.invoice_refund_ids:
                if refund.allocate == True:
                    refund_debit_line = 0
                    refund_credit_line = 0
                    refund_payment_debit_line = 0
                    for line in refund.move_id.line_ids:
                        if line.credit == 0.0:
                            refund_credit_line = line.id 

                    for refund_payment_line in self.payment_id.move_id.line_ids:
                        if line.debit == 0.0:
                            refund_payment_debit_line = refund_payment_line.id

                    refund_reconcile_amount = 0.0
                    if refund.move_id.currency_id.id != self.payment_id.currency_id.id:
                        refund_reconcile_amount = refund.currency_id._convert(refund.allocate_amount, self.payment_id.currency_id, self.payment_id.company_id, self.payment_id.date)    
                    refund_recocile_vals = {
                        'exchange_move_id': refund.move_id.id,
                    }
                    refund_reconcile_id = self.env['account.full.reconcile'].create(refund_recocile_vals)


                    refund_amount_reconcile = 0.0
                    if refund.move_id.currency_id.id == self.payment_id.currency_id.id:
                        refund_amount_reconcile = refund.allocate_amount
                    else:
                        refund_amount_reconcile = self.payment_id.currency_id._convert(refund.allocate_amount, refund.move_id.currency_id, refund.move_id.company_id, refund.move_id.date) 
                    vals = {
                        'full_reconcile_id': refund_reconcile_id.id,
                        'amount':  refund.allocate_amount,
                        'credit_move_id':  refund_payment_debit_line,
                        'debit_move_id': refund_credit_line ,
                        'credit_amount_currency': refund_amount_reconcile,
                        'debit_amount_currency': refund_amount_reconcile,
                    }
                    refund_payment = self.env['account.partial.reconcile'].create(vals)

                    if refund_reconcile_amount == refund.allocate_amount:
                        refund_exchange_amount = refund.move_id.amount_residual 
                        refund_exchange_moves = self.action_exchange_rate(refund.currency_id.id, refund_exchange_amount)
                        refund_ext_payment_debit_line = 0
                        for refund_ext_line in refund_exchange_moves.line_ids:
                            refund_ext_payment_debit_line = ext_line.id
                            break
                        for refund_ext_line in refund_exchange_moves.line_ids:
                            if refund_ext_line.account_id.id == self.payment_id.destination_account_id.id:
                                refund_ext_payment_debit_line = refund_ext_line.id
                        refund_ext_recocile_vals = {
                            'exchange_move_id': refund.move_id.id,
                            }

                        refund_ext_reconcile_id = self.env['account.full.reconcile'].create(refund_ext_recocile_vals)                       
                        refund_ext_vals = {
                            'full_reconcile_id': refund_ext_reconcile_id.id,
                            'amount':  - refund.allocate_amount,
                            'credit_move_id':  refund_credit_line,
                            'debit_move_id': refund_ext_payment_debit_line,
                            'credit_amount_currency': refund_exchange_amount,
                            'debit_amount_currency': refund_exchange_amount,
                            }
                        refund_inv_payment = self.env['account.partial.reconcile'].create(refund_ext_vals)            

                    
    def action_exchange_rate(self, currency, exchange_amount):
        line_src_ids = []
        exchange_journal = self.env['account.journal'].search([('name','=','Exchange Difference')], limit=1)
        if not exchange_journal :
            journal_vals = {
                            'name': 'Exchange Difference',
                            'code': 'EXCH',
                            'company_id': self.env.company,
                        }
            exchange_journal = self.env['account.journal'].create(journal_vals)
        procuretags = self.env['account.analytic.tag'].search([('name','=','Procurement & Vendor Management')], limit=1)
        if not procuretags:
            procure_tag = {
                    'name': 'Procurement & Vendor Management',
                }
            procuretags = self.env['account.analytic.tag'].create(procure_tag) 

            line_src_ids.append((0,0, {
                    'account_id':  self.payment_id.destination_account_id.id,
                    'partner_id':  self.payment_id.partner_id.id,
                    'name': 'Currency exchange rate difference',
                    'amount_currency': exchange_amount,
                     'currency_id':  currency,
                    'analytic_tag_ids': [(6, 0, procuretags.ids)],
                    }))
                        
        ext_account = self.env['account.account'].search([('name' ,'=', 'Foreign Exchange Gain')], limit=1)
        if not ext_account:
            account_vals = {
                        'name': 'Foreign Exchange Gain',
                        'code': 441000,
                        'user_type_id': 13 ,
            }
            ext_account = self.env['account.account'].create(account_vals)
        line_src_ids.append ((0,0, {
                    'account_id':  ext_account.id,
                    'partner_id':  self.payment_id.partner_id.id,
                    'name': 'Currency exchange rate difference',
                    'amount_currency': exchange_amount,
                    'currency_id':  currency,
                    'analytic_tag_ids': [(6, 0, procuretags.ids)],
        }))
 
        move_values = {
                    'date': fields.date.today(),
                    'move_type': 'entry',
                    'invoice_date': fields.date.today(),
                    'journal_id': exchange_journal.id,
                    'currency_id': self.payment_id.currency_id.id, 
                    'line_ids': line_src_ids,
            }
        exchange_moves = self.env['account.move'].create(move_values) 
        return exchange_moves
        
    
class PaymentAllocationLine(models.TransientModel):
    _name = 'payment.allocation.wizard.line'
    _description = 'Payment Allocation Wizard Line'
    
    payment_id = fields.Many2one('account.payment', string='Payment', store=True)
    allocation_id = fields.Many2one('payment.allocation.wizard', string='Allocation', store=True )
    payment_amount = fields.Monetary(string='Payment Amount', store=True, currency_field='currency_id' )
    payment_date = fields.Date(string='Payment Date' , store=True)
    unallocate_amount = fields.Monetary(string='Unallocated Amount', store=True, currency_field='currency_id' )
    allocate = fields.Boolean(string='Allocate', store=True)
    allocate_amount = fields.Monetary(string='Allocate Amount', store=True, currency_field='currency_id' )
    allocate_currency_amount = fields.Monetary(string='Allocate Amount', store=True, readonly="1", currency_field='company_currency_id', compute="_compute_all_currency_amount" )
    currency_id = fields.Many2one('res.currency', store=True, readonly=True, tracking=True, required=False,
        string='Currency')
    company_currency_id = fields.Many2one('res.currency', store=True, readonly=True, tracking=True, required=False,
        string='Payment Currency')
    
    @api.depends('allocate_amount')
    def _compute_all_currency_amount(self):
        total_allocation = 0
        if not (self.currency_id.id == self.company_currency_id.id):
            total_allocation = self.currency_id._get_conversion_rate(self.currency_id, self.company_currency_id,self.payment_id.company_id, fields.date.today()) * self.allocate_amount
        else:
            total_allocation = self.allocate_amount    
        self.allocate_currency_amount = total_allocation
    
    @api.onchange('allocate_amount')
    def onchange_allocate_amount(self):
        if self.allocate_amount > self.unallocate_amount:
            raise UserError(_('Allocate Amount cannot be greater than '+str(self.unallocate_amount)))
        self.update({
            'allocate' : True,
        })
        
    @api.onchange('allocate')
    def onchange_allocate(self):
        invoice_amount = 0.0
        payment_amount = 0.0
        amount = 0.0
        invoice_amount = self.allocation_id.move_id.amount_residual     
        for inv in self:
            if inv.allocate == True:
                if inv.payment_id.currency_id.id == self.allocation_id.move_id.id:                              
                    payment_amount = payment_amount + inv.allocate_amount   
                else:
                    payment_amount = payment_amount +  inv.payment_id.currency_id._convert(inv.allocate_amount, inv.allocation_id.move_id.currency_id, inv.allocation_id.move_id.company_id, inv.allocation_id.move_id.date)

        if  invoice_amount <  payment_amount:
            amount = payment_amount - invoice_amount
            raise UserError(_('Allocate Amount cannot be greater than '+str(payment_amount)))

    
    
class InvoiceAllocationLine(models.TransientModel):
    _name = 'invoice.allocation.wizard.line'
    _description = 'Invoice Allocation Wizard Line'
    
    
    move_id = fields.Many2one('account.move', string='Invoice', store=True)
    allocation_id = fields.Many2one('payment.allocation.wizard', string='Allocation', store=True)
    payment_date = fields.Date(string='Invoice Date', store=True)
    due_date = fields.Date(string='Due Date', store=True)
    invoice_amount = fields.Monetary(string='Invoice Amount', store=True, currency_field='currency_id')
    unallocate_amount = fields.Monetary(string='Unallocated Amount', store=True, currency_field='allocation_currency_id')
    allocate = fields.Boolean(string='Allocate', store=True)
    allocate_amount = fields.Monetary(string='Allocate Amount', store=True, currency_field='allocation_currency_id')
    allocate_currency_amount = fields.Monetary(string='Allocate Amount', store=True, readonly="1", currency_field='company_currency_id', compute="_compute_all_currency_amount" )
    currency_id = fields.Many2one('res.currency', store=True, readonly=True, tracking=True, required=False,
        string='Currency')
    allocation_currency_id = fields.Many2one('res.currency', related='allocation_id.currency_id')
    company_currency_id = fields.Many2one('res.currency', store=True, readonly=True, tracking=True, required=False,
        string='Invoice Currency')
    
    @api.depends('allocate_amount')
    def _compute_all_currency_amount(self):
        total_allocation = 0.0
        for record in self:
            total_allocation = record.allocation_currency_id._get_conversion_rate(record.allocation_currency_id, record.company_currency_id,record.allocation_id.company_id, fields.date.today()) * float(record.allocate_amount)
            record.allocate_currency_amount = float(total_allocation)
        
    @api.onchange('allocate')
    def onchange_allocate(self):
        payment_amount = 0.0
        inv_amount = 0.0
        amount = 0.0
        for payment in self.allocation_id.payment_line_ids:
            payment_amount = payment.allocate_amount     
        for inv in self:
            if inv.allocate == True:
                if inv.move_id.currency_id.id == inv.allocation_id.payment_id.currency_id.id:                
                    inv_amount = inv_amount + inv.allocate_amount
                else:
                    inv_amount = inv_amount + inv.move_id.currency_id._convert(inv.allocate_amount, inv.allocation_id.payment_id.currency_id, inv.allocation_id.payment_id.company_id, inv.allocation_id.payment_id.date)


        #if  payment_amount <  inv_amount:
        #    amount = inv_amount - payment_amount
        #    raise UserError(_('Allocate Amount cannot be greater than '+str(payment_amount)))

            
            
class InvoiceAllocationLineCreditmemo(models.TransientModel):
    _name = 'invoice.allocation.wizard.line.credit'
    _description = 'Invoice Allocation Wizard Line Credit Memo'
    
    
    move_id = fields.Many2one('account.move', string='Invoice', store=True)
    allocation_id = fields.Many2one('payment.allocation.wizard', string='Allocation', store=True)
    payment_date = fields.Date(string='Invoice Date', store=True)
    due_date = fields.Date(string='Due Date', store=True)
    invoice_amount = fields.Monetary(string='Invoice Amount', store=True)
    unallocate_amount = fields.Monetary(string='Unallocated Amount', store=True)
    allocate = fields.Boolean(string='Allocate', store=True)
    allocate_amount = fields.Monetary(string='Allocate Amount', store=True)
    allocate_currency_amount = fields.Monetary(string='Allocate Amount', store=True, readonly="1", currency_field='company_currency_id', compute="_compute_all_currency_amount" )
    currency_id = fields.Many2one('res.currency', store=True, readonly=True, tracking=True, required=False,
        string='Currency')
    allocation_currency_id = fields.Many2one('res.currency', related='allocation_id.currency_id')
    company_currency_id = fields.Many2one('res.currency', store=True, readonly=True, tracking=True, required=False,
        string='Invoice Currency')
    
    @api.depends('allocate_amount')
    def _compute_all_currency_amount(self):
        total_allocation = 0
        for record in self:
            total_allocation = record.allocation_currency_id._get_conversion_rate(record.allocation_currency_id, record.company_currency_id,record.allocation_id.company_id, fields.date.today()) * record.allocate_amount
            record.allocate_currency_amount = total_allocation
    
class InvoiceAllocationLineEntry(models.TransientModel):
    _name = 'invoice.allocation.wizard.line.entry'
    _description = 'Invoice Allocation Wizard Line Entry'
    
    
    move_id = fields.Many2one('account.move', string='Invoice', store=True)
    allocation_id = fields.Many2one('payment.allocation.wizard', string='Allocation', store=True)
    payment_date = fields.Date(string='Invoice Date', store=True)
    due_date = fields.Date(string='Due Date', store=True)
    invoice_amount = fields.Monetary(string='Invoice Amount', store=True)
    unallocate_amount = fields.Monetary(string='Unallocated Amount', store=True)
    allocate = fields.Boolean(string='Allocate', store=True)
    allocate_amount = fields.Monetary(string='allocate Amount', store=True)
    allocate_currency_amount = fields.Monetary(string='Allocate Amount', store=True, readonly="1", currency_field='company_currency_id', compute="_compute_all_currency_amount" )
    currency_id = fields.Many2one('res.currency', store=True, readonly=True, tracking=True, required=False,
        string='Currency')
    allocation_currency_id = fields.Many2one('res.currency', related='allocation_id.currency_id')
    company_currency_id = fields.Many2one('res.currency', store=True, readonly=True, tracking=True, required=False,
        string='Invoice Currency')    
    
    @api.depends('allocate_amount')
    def _compute_all_currency_amount(self):
        total_allocation = 0
        for record in self:
            total_allocation = record.allocation_currency_id._get_conversion_rate(record.allocation_currency_id, record.company_currency_id,record.allocation_id.company_id, fields.date.today()) * record.allocate_amount
            record.allocate_currency_amount = total_allocation
    

                        