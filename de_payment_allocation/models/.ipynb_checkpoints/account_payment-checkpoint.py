# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero, date_utils, email_split, email_re, html_escape, is_html_empty


class AccountPayment(models.Model):
    _inherit = 'account.payment'
    
    @api.model
    def _recon_journal_id(self):
        journal_id = self.env['ir.config_parameter'].sudo().get_param('de_payment_allocation.payment_allocation_journal_id')
        journal_id = self.env['account.journal'].search([('is_clearing','=',True),('company_id','=',self.env.company.id)],limit=1)
        #return self.env['account.journal'].browse(int(journal_id)).exists()
        return journal_id
    
        
    payment_reconcile_line = fields.One2many('account.payment.reconcile.line', 'payment_id', string='Payment Reconcile Lines', copy=False)
    payment_reconcile_debit_line = fields.One2many('account.payment.reconcile.line', 'payment_id', string='Debit Reconcile lines', copy=False, readonly=False, domain=[('is_debit_line', '=', True)],)
    payment_reconcile_credit_line = fields.One2many('account.payment.reconcile.line', 'payment_id', string='Debit Reconcile lines', copy=False, readonly=False, domain=[('is_debit_line', '=', False)],)


    writeoff_account_id = fields.Many2one('account.account', string='Writeoff Account')
    writeoff_label = fields.Char(string='Label', default='Write-Off')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
        
    amount_debit_currency = fields.Monetary(string='Debit', store=True, readonly=True,compute='_amount_all', )
    amount_credit_currency = fields.Monetary(string='Credit', store=True, readonly=True,compute='_amount_all',)
    amount_diff_currency = fields.Monetary(string='Difference', store=True, readonly=True,compute='_amount_all')
    
    amount_debit_recon = fields.Monetary(string='Debit', store=True, readonly=True,compute='_amount_all', )
    amount_credit_recon = fields.Monetary(string='Credit', store=True, readonly=True,compute='_amount_all',)
    amount_diff_recon = fields.Monetary(string='Difference', store=True, readonly=True,compute='_amount_all')
    
    
    debit_total_currency = fields.Monetary(string='Debit Total', compute='_total_all_currency', currency_field='currency_id')
    credit_total_currency = fields.Monetary(string='Credit Total', compute='_total_all_currency', currency_field='currency_id')
    diff_amount_currency = fields.Monetary(string='Difference', compute='_total_all_currency')
    
    
    exchange_rate = fields.Char(string='Exchange Rate', compute='_compute_all_exchange')
    last_exchange_rate = fields.Char(string='Last Exchange Rate', readonly="1", compute='_compute_all_exchange')
    
    payment_reconciled = fields.Boolean(string='Payment Reconciled',copy=False)
    
    matching_move_id = fields.Many2one('account.move', string='Matching Entry', copy=False)
    move_line_ids = fields.Many2many('account.move.line', string='Journal Items', domain="[('move_id','=',move_id)]", compute='_compute_move_lines', readonly=True)
    
    matching_reconcile_move_ids = fields.Many2many('account.move', string='Reconciled Moves', compute='_matching_reconcile_moves')
    
    @api.depends('move_line_ids')
    def _matching_reconcile_moves(self):
        for payment in self:
            payment.matching_reconcile_move_ids = payment.move_line_ids.full_reconcile_id.reconciled_line_ids.mapped('move_id').filtered(lambda x: x.id not in (payment.move_id.id, payment.matching_move_id.id))


    def action_view_matchings(self):
        invoices = self.mapped('matching_reconcile_move_ids')
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
       
        return action
    
    @api.depends('payment_reconcile_debit_line.amount_assigned','payment_reconcile_credit_line.amount_assigned','amount')
    def _amount_all(self):
        for payment in self:
            amount_debit_currency = amount_credit_currency = amount_debit_recon = amount_credit_recon = 0.0
            amount = amount_currency = 0
                        
            for line in payment.payment_reconcile_debit_line.filtered(lambda x: x.assigned):
                amount_debit_currency += line.amount_assigned_currency
                amount_debit_recon += line.amount_assigned_recon
            for line in payment.payment_reconcile_credit_line.filtered(lambda x: x.assigned):
                amount_credit_currency += line.amount_assigned_currency
                amount_credit_recon += line.amount_assigned_recon
            
            amount_currency = payment.currency_id._convert(abs(payment.amount), payment.company_currency_id, payment.company_id, fields.date.today())
            amount = payment.amount
            
            if payment.payment_type == 'inbound':
                amount_credit_currency = amount_credit_currency + amount_currency
                amount_credit_recon = amount_credit_recon + amount
            elif payment.payment_type == 'outbound':
                amount_debit_currency = amount_debit_currency + amount_currency
                amount_debit_recon = amount_debit_recon + amount
            
            payment.update({                
                'amount_debit_currency': amount_debit_currency,
                'amount_credit_currency': amount_credit_currency,
                'amount_diff_currency': (amount_debit_currency - amount_credit_currency),
                
                'amount_debit_recon': amount_debit_recon,
                'amount_credit_recon': amount_credit_recon,
                'amount_diff_recon': (amount_debit_recon - amount_credit_recon),
            })
    
    #@api.onchange('currency_id')
    #def _onchange_currency_id(self):
    #    self.payment_reconcile_line.unlink()
        
    #@api.onchange('partner_id')
    #def _onchange_partner_id(self):
    #    self.payment_reconcile_line.unlink()
        
    def _compute_move_lines(self):
        self.move_line_ids = self.move_id.mapped('line_ids') | self.matching_move_id.mapped('line_ids').filtered(lambda x: x.parent_state not in ('cancel'))
            
    def _compute_move_lines1(self):
        if self.matching_move_id:
            for move in self.matching_move_id:
                self.matching_move_line_ids = move.line_ids + self.move_id.line_ids
        else:
            self.matching_move_line_ids = False
    
    def action_unreconcile(self):
        self.move_id.line_ids.remove_move_reconcile()
        self.matching_move_id.line_ids.remove_move_reconcile()
        self.move_id.button_cancel()
        self.matching_move_id.button_cancel()
        self.update({
            'payment_reconciled': False,
            'matching_move_id': False
        })
        
    def action_cancel(self):
        ''' draft -> cancelled '''
        self.action_unreconcile()
        
    def action_draft(self):
        ''' posted -> draft '''
        self.action_unreconcile()
        self.move_id.button_draft()
        
    def action_generate_journal_entry(self):
        for payment in self:
            if not payment.writeoff_account_id:
                if not payment.amount_diff_currency == 0:
                    raise UserError(_("Cannot create unbalanced journal entry. \nDifferences debit - credit: %s") % (str(payment.amount_diff_currency)))
                
            debit_sum = credit_sum = 0.0
            amount = 0
            total_debit_diff = total_credit_diff = 0
            line_ids = update_line_ids = []
            exchange_diff_currency = 0
            temp = ''
            #if payment.move_id:
            #    if payment.move_id == 'draft':
            #        payment.move_id.line_ids.filtered(lambda line: line.account_id.id == self.destination_account_id.id).unlink()
                    #payment.payment_move_id.unlink()
            if payment.matching_move_id:
                if payment.matching_move_id.state == 'posted':
                    payment.matching_move_id.button_draft()
                    payment.matching_move_id.button_cancel()
                else:
                    payment.matching_move_id.unlink()
                    
            if not (payment.currency_id.id == payment.company_id.currency_id.id):
                #amount = payment.currency_id._get_conversion_rate(payment.currency_id, payment.company_id.currency_id,payment.company_id, fields.date.today()) * payment.amount
                amount = payment.currency_id._convert(abs(payment.amount), payment.company_id.currency_id, payment.company_id, fields.date.today())                    

            else:
                amount = payment.amount
                
            # journal_id = self.env['account.journal'].search([('type','=','general')],limit=1)
            journal_id = self._recon_journal_id()
            move_dict = {
                'journal_id': journal_id.id, #self.journal_id.id,
                'date': self.date,
                'state': 'draft',
                'currency_id': self.currency_id.id,
                'move_type': 'entry',
                'payment_id': payment.id,
            }
            payment_display_name = {
                'outbound-customer': _("Customer Reimbursement"),
                'inbound-customer': _("Customer Payment"),
                'outbound-supplier': _("Vendor Payment"),
                'inbound-supplier': _("Vendor Reimbursement"),
            }
            default_line_name = self.env['account.move.line']._get_default_line_name(_("Internal Transfer") if self.is_internal_transfer else payment_display_name['%s-%s' % (self.payment_type, self.partner_type)], self.amount, self.currency_id, self.date, partner=self.partner_id,)
            
            debit_line_name = ' - '.join(recon.move_id.name + ' ' + str(self.currency_id.symbol) + ' ' + "{:,.2f}".format(recon.amount_assigned_recon) for recon in self.payment_reconcile_debit_line.filtered(lambda x: x.assigned))
            credit_line_name = ' - '.join(recon.move_id.name + ' ' + str(self.currency_id.symbol) + ' ' + "{:,.2f}".format(recon.amount_assigned_recon) for recon in self.payment_reconcile_credit_line.filtered(lambda x: x.assigned))
            
            # --------------------------------------------
            # Greate move lines for incoming payment
            # --------------------------------------------
            if payment.payment_type == 'inbound':
                #generate cash/bank line for outgoing payment - credit line
                line_ids.append([0,0,{
                    'name': debit_line_name + credit_line_name,
                    'ref': payment.name,
                    #'move_line_id': payment_entry.id, 
                    'debit': round(payment.amount_total_signed,2),
                    'credit': 0.0,
                    #'account_id': payment.journal_id.payment_debit_account_id.id,
                    'account_id': payment.destination_account_id.id,
                    'payment_id': payment.id,
                    'currency_id': payment.currency_id.id,
                    'amount_currency':  payment.amount,
                    'partner_id': payment.partner_id.id,
                    'payment_matching': True,
                    'payment_id': payment.id,
                }])
                #temp += 'payment==' + str(round(payment.amount_total_signed,2)) + ' credit=' + str(0) + ' amount currency=' + str(round(payment.amount,2)) + '\n'

            # --------------------------------------------
            # Greate move lines for outgoing payment
            # --------------------------------------------
            if payment.payment_type == 'outbound':
                #generate cash/bank line for outgoing payment - credit line
                line_ids.append([0,0,{
                    'name': debit_line_name + credit_line_name,
                    'ref': payment.name,
                    #'move_line_id': payment_entry.id, 
                    'debit': 0.0,
                    'credit': round(payment.amount_total_signed,2),
                    #'account_id': payment.journal_id.payment_credit_account_id.id,
                    'account_id': payment.destination_account_id.id,
                    'payment_id': payment.id,
                    'currency_id': payment.currency_id.id,
                    'amount_currency':  payment.amount * -1,
                    'partner_id': payment.partner_id.id,
                    'payment_matching': True,
                    'payment_id': payment.id,
                }])
            # --------------------------------------------
            # generate contra credit lines for selected debit allocation lines
            # --------------------------------------------
            for line in payment.payment_reconcile_debit_line:
                if line.assigned:
                    line_ids.append([0,0,{
                        'name': payment.move_id.name + ' - ' + line.move_id.name,
                        #'display_name': payment.move_id.name + ' - ' + line.move_id.name,
                        #'move_line_id': payment_entry.id,
                        'ref': line.move_id.name,
                        'debit': 0.0,
                        'credit': round(abs(line.amount_assigned_currency),2),
                        'account_id': line.account_id.id,
                        'payment_id': payment.id,
                        'currency_id': payment.currency_id.id,
                        'amount_currency':  line.amount_assigned_recon * -1,
                        'payment_id': payment.id,
                        'allocation_move_line_id': line.move_line_id.id,
                        'partner_id': payment.partner_id.id,
                    }])
                    #temp += 'Allocation=' + str(0) + ' credit=' + str(round(abs(line.allocated_amount),2)) + ' amount currency=' + str(round(line.allocated_amount_currency * -1,2)) + '\n'
            # --------------------------------------------
            # generate contra debit lines for selected credit allocation lines
            # --------------------------------------------
            for line in payment.payment_reconcile_credit_line:
                if line.assigned:
                    line_ids.append([0,0,{
                        'name': payment.move_id.name + ' - ' + line.move_id.name,
                        #'display_name': payment.move_id.name + ' - ' + line.move_id.name,
                        'ref': line.move_id.name,
                        #'move_line_id': payment_entry.id,
                        'debit': round(abs(line.amount_assigned_currency),2),
                        'credit': 0.0,
                        'account_id': line.account_id.id,
                        'payment_id': payment.id,
                        'currency_id': payment.currency_id.id,
                        'amount_currency':  abs(line.amount_assigned_recon),
                        'payment_id': payment.id,
                        'allocation_move_line_id': line.move_line_id.id,
                        'partner_id': payment.partner_id.id,
                    }])    
            # --------------------------------------------
            # Post Difference Entry
            # --------------------------------------------
            if payment.amount_diff_currency > 0:
                total_debit_diff = payment.amount_diff_currency
                total_credit_diff = 0
            elif payment.amount_diff_currency < 0:
                total_debit_diff = 0
                total_credit_diff = payment.amount_diff_currency
                
            if payment.writeoff_account_id:
                line_ids.append([0,0,{
                    'name': payment.writeoff_label + '-' + payment.name,
                    'display_name': payment.writeoff_label + '-' + payment.name,
                    'ref': payment.name,
                    #'move_line_id': payment_entry.id,
                    'debit': round(abs(total_debit_diff),2),
                    'credit': round(abs(total_credit_diff),2),
                    'account_id': payment.writeoff_account_id.id,
                    'payment_id': payment.id,
                    'currency_id': payment.currency_id.id,
                    #'amount_currency': round(payment.diff_amount_currency,2),
                    'payment_id': payment.id,
                    'partner_id': payment.partner_id.id,
                }])
                #temp += 'writeoff/debit=' + str(round(abs(total_debit_diff),2)) + ' credit=' + str(round(abs(total_credit_diff),2)) + ' amount currency=' + str(round(payment.diff_amount_currency,2)) + '\n'
            #raise ValidationError(_(temp))
            move_dict['line_ids'] = line_ids
            move = self.env['account.move'].create(move_dict)
            payment.matching_move_id = move.id
            #payment.matching_move_id._post(soft=False)
            #payment.move_id.update({
            #    'line_ids': line_ids,
            #})
            #move_lines = self.move_id.line_ids.filtered(lambda line: line.account_id == self.destination_account_id)
            #move_lines.unlink()
            #payment.move_id.write(move_dict)
            #raise UserError(move_dict)
            #payment.payment_move_id=move.id
            #payment.move_id = move.id
    
    def action_post(self):
        ''' draft -> posted '''
        for payment in self:
            if not payment.move_id.state == 'posted':
                payment.move_id._post(soft=False)
                
            #if len(payment.payment_reconcile_debit_line.mapped('payment_id')) >= 1 or len(payment.payment_reconcile_credit_line.mapped('payment_id')) >= 1:
            if len(payment.payment_reconcile_debit_line.filtered(lambda x: x.assigned)) or len(payment.payment_reconcile_credit_line.filtered(lambda x: x.assigned)):
                payment.action_generate_journal_entry()
            
            if not payment.matching_move_id.state == 'posted':
                payment.matching_move_id._post(soft=False)
            
            try:
                payment.action_reconcile()
            except:
                pass
                #action_server = self.env['ir.actions.server'].search([('name','=','Payment Reconcile')],limit=1)
                #if action_server:
                #    ctx = {
                #        'active_model': self._name,
                #        'active_id': payment.id,
                #    }
                #    action_server.sudo().with_context(**ctx).sudo().run()
            #else:
            #    payment.move_id._post(soft=False)
        
        
    
    def action_reconcile(self):
        for payment in self:
            payment_line = payment_debit_line = payment_credit_line = self.env['account.move.line']
            
            debit_lines = credit_lines = payment_line = self.env['account.move.line']
            debit_line = credit_line = self.env['account.move.line']
            if len(payment.payment_reconcile_debit_line.filtered(lambda x: x.assigned)) or len(payment.payment_reconcile_credit_line.filtered(lambda x: x.assigned)):
                #domain = [('account_internal_type', 'in', ('receivable', 'payable')), ('reconciled', '=', False)]
                
                # --------------------------------------------
                # Reconcile Payment Line
                # --------------------------------------------
                if payment.payment_type == 'outbound':
                    payment_line = payment.move_id.line_ids.filtered(lambda line: line.account_id.id == self.destination_account_id.id)
                    payment_debit_line = payment_line
                    payment_credit_line = payment.matching_move_id.line_ids.filtered(lambda line: line.account_id.id == self.destination_account_id.id and line.payment_matching)
                elif payment.payment_type == 'inbound':
                    payment_line = payment.move_id.line_ids.filtered(lambda line: line.account_id.id == self.destination_account_id.id)
                    payment_credit_line = payment_line
                    payment_debit_line = payment.matching_move_id.line_ids.filtered(lambda line: line.account_id.id == self.destination_account_id.id and line.payment_matching)
                if payment.amount > 0 :
                    for account in payment.move_id.line_ids.account_id.filtered(lambda x: x.internal_type in ['receivable','payable']):
                            (payment_debit_line + payment_credit_line)\
                                .filtered_domain([('account_id', '=', account.id), ('reconciled', '=', False)])\
                                .reconcile()
                        
                
                
                #====================================================13-march-2022========
                # --------------------------------------------
                # Reconcile entries for outoing payment
                # --------------------------------------------
                if self.payment_type == 'outbound' or self.payment_type == 'inbound':
                    #sorted_lines = self.sorted(key=lambda line: (line.date_maturity or line.date, line.currency_id))
                    for line in self.payment_reconcile_debit_line.filtered(lambda line: line.assigned == True):
                        debit_line = line.move_line_id
                        credit_line = self.env['account.move.line'].search([('allocation_move_line_id','=',line.move_line_id.id),('parent_state','=','posted'),('payment_id','=',payment.id)])
                        if credit_line:
                            (credit_line + debit_line)\
                            .filtered_domain([('account_id', '=', line.account_id.id), ('reconciled', '=', False)])\
                            .reconcile()
                    for line in self.payment_reconcile_credit_line.filtered(lambda line: line.assigned == True):
                        credit_line = line.move_line_id
                        debit_line = self.env['account.move.line'].search([('allocation_move_line_id','=',line.move_line_id.id),('parent_state','=','posted'),('payment_id','=',payment.id)])
                        if debit_line:
                            (credit_line + debit_line)\
                            .filtered_domain([('account_id', '=', line.account_id.id), ('reconciled', '=', False)])\
                            .reconcile()
                    #if payment.amount > 0 :
                    #    for account in payment.move_id.line_ids.account_id.filtered(lambda x: x.internal_type in ['receivable','payable']):
                    #        (debit_lines + credit_lines)\
                    #            .filtered_domain([('account_id', '=', account.id), ('reconciled', '=', False)])\
                    #            .reconcile()
                        
                    #for line in self.debit_allocation_ids:
                    #    if line.is_allocate == True:
                    #        payment_line += self.env['account.move.line'].search([('id','=',line.move_line_id.id)])
                    #for line in self.credit_allocation_ids:
                    #    if line.is_allocate == True:
                    #        sorted_lines += self.env['account.move.line'].search([('id','=',line.move_line_id.id)])
                    #    involved_lines = sorted_lines + payment_line
                    #    payment_lines = self.move_id.line_ids.filtered_domain(domain)
                    #    payment_lines += payment.debit_allocation_ids.move_line_id.filtered_domain(domain)
                    #    #for account in payment_lines.account_id:
                    #    for account in payment.destination_account_id:    
                    #        (payment_lines + sorted_lines)\
                    #            .filtered_domain([('account_id', '=', account.id), ('reconciled', '=', False)])\
                    #            .reconcile()
            payment.update({
                'payment_reconciled': True,
                #'reconciled': True
            })
                    
    
    
    def _compute_reconcile_amount(self):
        for payment in self:
            reconcile_amount = 0.0
            for move_line in payment.move_id.line_ids:
                for credit_line in move_line.matched_credit_ids:
                    reconcile_amount = reconcile_amount + credit_line.amount
                for debit_line in move_line.matched_debit_ids:
                    reconcile_amount = reconcile_amount + debit_line.amount        
            payment.update({
                'reconcile_amount' : reconcile_amount
            })
        #    if payment.reconciled_invoices_count > 0:
        #        if payment.reconcile_amount == payment.amount:
        #            payment.update({
        #                'is_reconciled' : True
        #            })
        #    else:
        #        payment.update({
        #            'is_reconciled': False
        #        })
                   

    def action_process_openitems(self):
        
        # --------------------------------------------
        # create debit move lines for reconcile
        # --------------------------------------------
        # ('account_id.internal_type','in',('receivable','payable'))
        lines = []
        move_lines = self.env['account.move.line']
        self.payment_reconcile_line.unlink()
        move_lines = self.env['account.move.line'].search([('partner_id','=',self.partner_id.id),('move_id.state','=','posted'),('account_id.reconcile','=',True),('account_id.allow_payment_reconcile','=',True),('journal_id.allow_payment_reconcile','=',True),('amount_residual','!=',0),('move_id','!=',self.move_id.id),('full_reconcile_id','=',False), ('company_id','=',self.company_id.id)])
        for line in move_lines:
            if not line.debit ==0:
                is_debit_line = True
            else:
                is_debit_line = False
                
            lines.append((0,0,{
                'move_id': line.move_id.id,
                'account_id': line.account_id.id,  
                'move_line_id': line.id,
                'date': line.date,
                'due_date': line.move_id.invoice_date_due,
                'payment_id': self.id,
                'is_debit_line': is_debit_line,
            }))
        self.payment_reconcile_line  =  lines
        
        # --------------------------------------------
        debit_line = credit_line = self.env['account.move.line']
        debit_lines = []
        credit_lines = []
        residual_amount = residual_amount_currency = 0
        
        
        
        
    
    
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

    def _compute_all_exchange(self):
        exchange_rate = 0
        if not self.currency_id.id == self.company_currency_id.id:
            #exchange_rate = self.currency_id._get_conversion_rate(self.currency_id, self.company_currency_id,self.company_id, fields.date.today()) * 1
            exchange_rate = self.currency_id._convert(1, self.company_id.currency_id, self.company_id, fields.date.today())                    

            self.exchange_rate = '1 ' + str(self.company_currency_id.name) + ' = ' + str(round(exchange_rate,2)) + ' ' + str(self.currency_id.name)
            self.last_exchange_rate = 'At the operation date, the exchange rate was 1 ' + str(self.company_currency_id.name) + ' = ' + str(round(exchange_rate,2)) + ' ' + str(self.currency_id.name)
        else:
            self.exchange_rate = '1 ' + str(self.company_currency_id.name) + ' = ' + '1' + ' ' + str(self.currency_id.name)
            self.last_exchange_rate = '1 ' + str(self.company_currency_id.name) + ' = ' + '1' + ' ' + str(self.currency_id.name)

class AccountPaymentReconcileLines(models.Model):
    _name = 'account.payment.reconcile.line'
    _description = 'Account Payment Reconcile Lines'
    _order = 'assigned desc, date desc'

    move_id = fields.Many2one('account.move', string='Move', store=True)
    payment_id = fields.Many2one('account.payment', 'Payment', help="Change to a better name", index=True)
    move_line_id = fields.Many2one('account.move.line', string='Move Line')
    account_id = fields.Many2one('account.account', string='Account', store=True)
    date = fields.Date(string='Date', store=True)
    invoice_date = fields.Date(string='Invoice Date', related='move_id.invoice_date')
    due_date = fields.Date(string='Due Date', store=True)
    assigned = fields.Boolean(string='Assigned')
    
    is_debit_line = fields.Boolean(string='Debit Line')
    
    company_currency_id = fields.Many2one(string='Company Currency', readonly=True, related='move_line_id.company_currency_id')
    currency_id = fields.Many2one(string='Document Currency', readonly=True, related='move_line_id.currency_id')
    recon_currency_id = fields.Many2one(string='Reoncile Currency', readonly=True, related='payment_id.currency_id')
    
    amount_total = fields.Float(string='Total Amount', compute='_compute_from_move_line', store=True, help='Amount in Company Currency')
    amount_total_signed = fields.Float(string='Amount Signed', compute='_compute_from_move_line', store=True,help='Amount in Document Currency')
    amount_total_recon = fields.Float(string='Amount Signed', compute='_compute_from_move_line', store=True,help='Amount in Document Currency')

    
    
    amount_residual = fields.Float(string='Residual Amount', compute='_compute_from_move_line', store=True, help='Amount in company currency')
    amount_residual_currency = fields.Float(string='Residual Signed', compute='_compute_from_move_line', store=True, help='Amount in Document Currency')
    amount_residual_recon = fields.Float(string='Residual Recon', compute='_compute_from_move_line', store=True, help='Amount in clearing currecny selected in document')
    
    amount_assigned_recon = fields.Float(string='Assigned', help='Amount assigned in clearing currency')
    amount_assigned = fields.Float(string='Assign Amount', store=True, help='Amount assign in company currency',  compute='_compute_from_amount_assigned_recon',)
    amount_assigned_currency = fields.Float(string='Assign Currency', store=True, help='Amount assigned in document currency', compute='_compute_from_amount_assigned_recon')
    
            
    @api.depends('move_line_id')
    def _compute_from_move_line(self):
        for move in self.filtered('move_line_id'):
            #move.company_id = move.move_line_id.company_id.id
            
            try:
                move.amount_total = abs(move.move_line_id.debit - move.move_line_id.credit)
                move.amount_total_signed = abs(move.move_line_id.amount_currency)
            
                move.amount_residual = abs(move.move_line_id.amount_residual)
                move.amount_residual_currency = abs(move.move_line_id.amount_residual_currency)
            
                if move.recon_currency_id.id == move.company_currency_id.id:
                    move.amount_residual_recon = abs(move.move_line_id.amount_residual)
                    move.amount_total_recon = abs(move.move_line_id.debit - move.move_line_id.credit)
                elif move.recon_currency_id.id == move.currency_id.id:
                    move.amount_residual_recon = abs(move.move_line_id.amount_residual_currency)
                    move.amount_total_recon = abs(move.move_line_id.amount_currency)
                else:
                    if move.move_line_id.amount_residual != 0:
                        move.amount_residual_recon = abs(move.currency_id._convert(abs(move.move_line_id.amount_residual), move.recon_currency_id, move.move_line_id.company_id, fields.date.today()))
                    else:
                        move.amount_residual_recon = 0

                    move.amount_total_recon = abs(move.currency_id._convert(abs(move.move_line_id.debit - move.move_line_id.credit), move.recon_currency_id, move.move_line_id.company_id, fields.date.today()))
            except:
                move.amount_total = 0
                move.amount_total_signed = 0
                move.amount_total_recon = 0
                
                move.amount_residual = 0
                move.amount_residual_currency = 0
                move.amount_residual_recon = 0

                #fields.date.today()
    
    
    @api.depends('amount_assigned_recon')
    def _compute_from_amount_assigned_recon(self):
        for move in self:
            amount_assigned = amount_assigned_currency = 0.0
            amount_assigned = move.recon_currency_id._convert(abs(move.amount_assigned_recon), move.currency_id, move.payment_id.company_id, move.payment_id.date)
            amount_assigned_currency = move.recon_currency_id._convert(abs(move.amount_assigned_recon), move.company_currency_id, move.payment_id.company_id, move.payment_id.date)

            move.amount_assigned = abs(amount_assigned)
            move.amount_assigned_currency = abs(amount_assigned_currency)
            
    #@api.constrains('amount_assigned_recon', 'amount_residual_recon')
    #def _check_assigned_balance(self):
    #    for line in self:
    #        if line.amount_assigned_recon > abs(line.amount_residual_recon):
    #            raise UserError(_('You cannot assigned greater amount than avaialable amount'))
                
    @api.onchange('assigned')
    def _onchange_assigned(self):
        for move in self:
            if move.assigned == True:
                if move.amount_residual_recon != 0:
                    move.amount_assigned_recon = move.amount_residual_recon
                else:
                    move.amount_assigned_recon = move.amount_total_recon
            else:
                move.amount_assigned_recon = 0
                
                
    
