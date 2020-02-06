# -*- coding: utf-8 -*-

import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning


from odoo.addons import decimal_precision as dp

class AccountMove(models.Model):
    _inherit = 'account.move.line'
    
    invoiced_qty = fields.Float(string='Tgt.Bal.Qty',store=False, readonly=True,compute='_compute_invoiced_quantity')
    
    #@api.model
    def _compute_invoiced_quantity(self):
        target_id = 0
        target_qty = 0
        sale_target_obj = self.env['account.sale.target']
        for line in self:
            target_qty = 0
            invoice_date = line.move_id.invoice_date
            if line.product_id.id:
                sale_target_obj = self.env['account.sale.target'].search([('date_from', '>=', invoice_date), ('date_to', '<=', invoice_date), ],limit=1)
                sale_target_line = self.env['account.sale.target.line'].search([('product_id', '=', line.product_id.id),])
                for target in sale_target_line.filtered(lambda x: x.sale_target_id.state in ('done') and line.move_id.invoice_date >= x.sale_target_id.date_from and line.move_id.invoice_date <= x.sale_target_id.date_to):
                    target_qty = target.remaining_qty
            line.update({
                'invoiced_qty': target_qty
            })
    
    @api.model
    def _compute_invoiced_quantity1(self):
        target_id = 0
        for line in self:
            #acc_ids = line.general_budget_id.account_ids.ids
            #date_to = line.move_id.date_to
            #date_from = line.move_id.date_from
            invoice_date = line.move_id.invoice_date
            if line.product_id.id and line.move_id.id:
                sale_target_obj = self.env['account.sale.target'].search([('date_from', '>=', invoice_date), ('date_to', '<=', invoice_date), ('state', '=', 'done')])
                    
                account_line_obj = self.env['account.sale.target.line']
                domain = [('product_id', '=', line.product_id.id),
                          ]
                
                if sale_target_obj:
                    domain += [('sale_target_id', 'in', sale_target_obj.id)]
                    
                #line.invoiced_qty = target_id
                #if acc_ids:
                    #domain += [('general_account_id', 'in', acc_ids)]

                where_query = account_line_obj._where_calc(domain)
                account_line_obj._apply_ir_rules(where_query, 'read')
                from_clause, where_clause, where_clause_params = where_query.get_sql()
                select = "SELECT sum(target_qty) - sum(invoiced_qty) from " + from_clause + " where " + where_clause
                
                self.env.cr.execute(select, where_clause_params)
                line.invoiced_qty = self.env.cr.fetchone()[0] or 0.0