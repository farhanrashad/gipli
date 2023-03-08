# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import email_split, float_is_zero


class HrExpense(models.Model):
    
    _inherit = "hr.expense"
        
    payment_mode = fields.Selection(selection_add=[('prepayment', 'Prepayment (to reimburse)')], )
    expense_prepayment_line_id = fields.Many2one('hr.expense.prepayment.line', string="Expense Prepayment Line", copy=False, domain="[('state','=','done'),('employee_id','=',employee_id)]")
    amount_advanced = fields.Monetary(string='Amount Advanced', related='expense_prepayment_line_id.amount_residual')
    
    def _create_sheet_from_expenses(self):
        if any(expense.state != 'draft' or expense.sheet_id for expense in self):
            raise UserError(_("You cannot report twice the same line!"))
        if len(self.mapped('employee_id')) != 1:
            raise UserError(_("You cannot report expenses for different employees in the same report."))
        if any(not expense.product_id for expense in self):
            raise UserError(_("You can not create report without product."))

        todo = self.filtered(lambda x: x.payment_mode=='own_account') or self.filtered(lambda x: x.payment_mode=='company_account') or self.filtered(lambda x: x.payment_mode=='prepayment')
        sheet = self.env['hr.expense.sheet'].create({
            'company_id': self.company_id.id,
            'employee_id': self[0].employee_id.id,
            'name': todo[0].name if len(todo) == 1 else '',
            'expense_line_ids': [(6, 0, todo.ids)]
        })
        return sheet
    
    def _get_account_move_line_values(self):
        move_line_values_by_expense = {}
        for expense in self:
            move_line_name = expense.employee_id.name + ': ' + expense.name.split('\n')[0][:64] + ' - ' + str(expense.accounting_date)
            account_src = expense._get_expense_account_source()
            account_dst = expense._get_expense_account_destination()
            account_date = expense.sheet_id.accounting_date or expense.date or fields.Date.context_today(expense)

            company_currency = expense.company_id.currency_id
            
            account_adv = expense.expense_prepayment_line_id.account_id

            move_line_values = []
            taxes = expense.tax_ids.with_context(round=True).compute_all(expense.unit_amount, expense.currency_id, expense.quantity, expense.product_id)
            total_amount = 0.0
            total_amount_currency = 0.0
            partner_id = expense.employee_id.sudo().address_home_id.commercial_partner_id.id

            # source move line
            balance = expense.currency_id._convert(taxes['total_excluded'], company_currency, expense.company_id, account_date)
            amount_currency = taxes['total_excluded']
            move_line_src = {
                'name': move_line_name,
                'quantity': expense.quantity or 1,
                'debit': balance if balance > 0 else 0,
                'credit': -balance if balance < 0 else 0,
                'amount_currency': amount_currency,
                'account_id': account_src.id,
                'product_id': expense.product_id.id,
                'product_uom_id': expense.product_uom_id.id,
                'analytic_account_id': expense.analytic_account_id.id,
                'analytic_tag_ids': [(6, 0, expense.analytic_tag_ids.ids)],
                'expense_id': expense.id,
                'partner_id': partner_id,
                'tax_ids': [(6, 0, expense.tax_ids.ids)],
                'tax_tag_ids': [(6, 0, taxes['base_tags'])],
                'currency_id': expense.currency_id.id,
            }
            move_line_values.append(move_line_src)
            if expense.payment_mode == 'prepayment':
                move_line_src = {
                    'name': move_line_name,
                    'quantity': expense.quantity or 1,
                    'debit': balance if balance < 0 else 0,
                    'credit': -balance if balance > 0 else 0,
                    'amount_currency': amount_currency,
                    'account_id': account_adv.id,
                    'expense_id': expense.id,
                    'hr_expense_prepayment_line_id': expense.expense_prepayment_line_id.id,
                    'partner_id': partner_id,
                    'currency_id': expense.currency_id.id,
                }
                
            total_amount -= balance
            total_amount_currency -= move_line_src['amount_currency']

            # taxes move lines
            for tax in taxes['taxes']:
                balance = expense.currency_id._convert(tax['amount'], company_currency, expense.company_id, account_date)
                amount_currency = tax['amount']

                if tax['tax_repartition_line_id']:
                    rep_ln = self.env['account.tax.repartition.line'].browse(tax['tax_repartition_line_id'])
                    base_amount = self.env['account.move']._get_base_amount_to_display(tax['base'], rep_ln)
                    base_amount = expense.currency_id._convert(base_amount, company_currency, expense.company_id, account_date)
                else:
                    base_amount = None

                move_line_tax_values = {
                    'name': tax['name'],
                    'quantity': 1,
                    'debit': balance if balance > 0 else 0,
                    'credit': -balance if balance < 0 else 0,
                    'amount_currency': amount_currency,
                    'account_id': tax['account_id'] or move_line_src['account_id'],
                    'tax_repartition_line_id': tax['tax_repartition_line_id'],
                    'tax_tag_ids': tax['tag_ids'],
                    'tax_base_amount': base_amount,
                    'expense_id': expense.id,
                    'partner_id': partner_id,
                    'currency_id': expense.currency_id.id,
                    'analytic_account_id': expense.analytic_account_id.id if tax['analytic'] else False,
                    'analytic_tag_ids': [(6, 0, expense.analytic_tag_ids.ids)] if tax['analytic'] else False,
                }
                total_amount -= balance
                total_amount_currency -= move_line_tax_values['amount_currency']
                move_line_values.append(move_line_tax_values)

            # destination move line
            move_line_dst = {
                'name': move_line_name,
                'debit': total_amount > 0 and total_amount,
                'credit': total_amount < 0 and -total_amount,
                'account_id': account_dst,
                'date_maturity': account_date,
                'amount_currency': total_amount_currency,
                'currency_id': expense.currency_id.id,
                'expense_id': expense.id,
                'partner_id': partner_id,
            }
            move_line_values.append(move_line_dst)
            
            if expense.payment_mode == 'prepayment':
                move_line_dst = {
                    'name': move_line_name + ' / ' + expense.expense_prepayment_line_id.name + ' - ' + expense.expense_prepayment_line_id.expense_prepayment_id.ref,
                    'debit': total_amount > 0 and total_amount,
                    'credit': total_amount < 0 and -total_amount,
                    'account_id': account_adv.id,
                    'date_maturity': account_date,
                    'amount_currency': total_amount_currency,
                    'currency_id': expense.currency_id.id,
                    'expense_id': expense.id,
                    'hr_expense_prepayment_line_id': expense.expense_prepayment_line_id.id,
                    'partner_id': partner_id,
                }
                move_line_values.append(move_line_dst)
                
                move_line_dst = {
                    'name': move_line_name + ' / ' + expense.expense_prepayment_line_id.name + ' - ' + expense.expense_prepayment_line_id.expense_prepayment_id.ref,
                    'debit': total_amount < 0 and -total_amount,
                    'credit': total_amount > 0 and total_amount,
                    'account_id': account_dst,
                    'date_maturity': account_date,
                    'amount_currency': total_amount_currency,
                    'currency_id': expense.currency_id.id,
                    'expense_id': expense.id,
                    'hr_expense_prepayment_line_id': expense.expense_prepayment_line_id.id,
                    'partner_id': partner_id,
                }
                move_line_values.append(move_line_dst)
            move_line_values_by_expense[expense.id] = move_line_values
        return move_line_values_by_expense
    
    
class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'
    
    def action_sheet_move_create(self):
        samples = self.mapped('expense_line_ids.sample')
        if samples.count(True):
            if samples.count(False):
                raise UserError(_("You can't mix sample expenses and regular ones"))
            self.write({'state': 'post'})
            return

        if any(sheet.state != 'approve' for sheet in self):
            raise UserError(_("You can only generate accounting entry for approved expense(s)."))

        if any(not sheet.journal_id for sheet in self):
            raise UserError(_("Expenses must have an expense journal specified to generate accounting entries."))

        expense_line_ids = self.mapped('expense_line_ids')\
            .filtered(lambda r: not float_is_zero(r.total_amount, precision_rounding=(r.currency_id or self.env.company.currency_id).rounding))
        res = expense_line_ids.action_move_create()
        for sheet in self.filtered(lambda s: not s.accounting_date):
            sheet.accounting_date = sheet.account_move_id.date
        to_post = self.filtered(lambda sheet: sheet.payment_mode == 'own_account' and sheet.expense_line_ids)
        to_post.write({'state': 'post'})
        (self - to_post).write({'state': 'done'})
        self.activity_update()
        
        #payment reconciliation
        prepayment_move_lines = exp_move_lines = self.env['account.move.line']
        for expense in self.expense_line_ids.filtered(lambda x: x.expense_prepayment_line_id != False):
            prepayment_move_lines += self.env['account.move.line'].search([('hr_expense_prepayment_line_id','=',expense.expense_prepayment_line_id.id)])
        exp_move_lines = self.env['account.move.line'].search([('move_id','=',self.account_move_id.id)])

        if self.payment_mode == 'prepayment':
            for account in self.account_move_id.line_ids.account_id.filtered(lambda x: x.reconcile == True):
                (exp_move_lines + prepayment_move_lines)\
                    .filtered_domain([('account_id', '=', account.id), ('reconciled', '=', False)])\
                    .reconcile()
        return res
    
    
    def action_sheet_move_create1(self):
        res = super(HrExpenseSheet, self).action_sheet_move_create()
        if not self.account_move_id.state == 'posted':
                self.account_move_id.sudo()._post()
        prepayment_move_lines = exp_move_lines = self.env['account.move.line']
        for expense in self.expense_line_ids.filtered(lambda x: x.expense_prepayment_line_id != False):
            prepayment_move_lines += self.env['account.move.line'].search([('hr_expense_prepayment_line_id','=',expense.expense_prepayment_line_id.id)])
        exp_move_lines = self.env['account.move.line'].search([('move_id','=',self.account_move_id.id)])

        #if self.payment_mode == 'prepayment':
        #    for account in self.account_move_id.line_ids.account_id.filtered(lambda x: x.reconcile == True):
        #        (exp_move_lines + prepayment_move_lines)\
        #            .filtered_domain([('account_id', '=', account.id), ('reconciled', '=', False)])\
        #            .reconcile()
        return res
    