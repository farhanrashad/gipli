# -*- coding: utf-8 -*-

import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning


from odoo.addons import decimal_precision as dp

class SaleTarget(models.Model):
    _name = 'account.sale.target'
    _description = 'Account Sale Target'
    
    name = fields.Char(string='Name',  copy=False,  index=True, required=True)
    journal_id = fields.Many2one('account.journal', string='Journal', required=True,)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    date_from = fields.Date(string='Date From',required=False, readonly=True, states={'draft': [('readonly', False)]},)
    date_to = fields.Date(string='Date To',required=False, readonly=True, states={'draft': [('readonly', False)]},)
    state = fields.Selection([('draft','New'),
                              ('done','Validate'),
                              ('cancel','Cancel')],string = "Status", default='draft',track_visibility='onchange')
    
    sale_target_line_ids = fields.One2many('account.sale.target.line', 'sale_target_id', string='Sale Target Lines', readonly=True, states={'draft': [('readonly', False)]}, copy=True, auto_join=True)
    
    def action_validate(self):
        self.state = 'done'
        
    def action_cancel(self):
        self.state = 'cancel'
    
class SaleTargetLine(models.Model):
    _name = 'account.sale.target.line'
    _description = 'Account Sale Target Line'
    
    sale_target_id = fields.Many2one('account.sale.target', string='Sale Target', index=True, required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', index=True, required=True, ondelete='cascade')
    product_uom_id = fields.Many2one('uom.uom', required=True, string='Unit of Measure', domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', readonly=True)
    
    target_qty = fields.Float(string='Target Qty',required=True,default='1.0')
    
    invoiced_qty = fields.Float(string='Invoiced Qty',store=True, readonly=True,compute='_compute_invoiced_quantity')
    remaining_qty = fields.Float(string='Remaining Qty',readonly=True,compute='_compute_all_quantity')
    
    def _compute_invoiced_quantity(self):
        for line in self:
            #acc_ids = line.general_budget_id.account_ids.ids
            date_to = line.sale_target_id.date_to
            date_from = line.sale_target_id.date_from
            if line.product_id.id:
                account_line_obj = self.env['account.move.line']
                domain = [('product_id', '=', line.product_id.id),
                          ('date', '>=', date_from),
                          ('date', '<=', date_to),
                          ('move_id.state', '=', 'posted')
                          ]
                #if acc_ids:
                    #domain += [('general_account_id', 'in', acc_ids)]

                where_query = account_line_obj._where_calc(domain)
                account_line_obj._apply_ir_rules(where_query, 'read')
                from_clause, where_clause, where_clause_params = where_query.get_sql()
                select = "SELECT SUM(quantity) from " + from_clause + " where " + where_clause

            #else:
                #aml_obj = self.env['account.move.line']
                #domain = [('account_id', 'in',
                           #line.general_budget_id.account_ids.ids),
                          #('date', '>=', date_from),
                          #('date', '<=', date_to),
                          #('move_id.state', '=', 'posted')
                          #]
                #where_query = aml_obj._where_calc(domain)
                #aml_obj._apply_ir_rules(where_query, 'read')
                #from_clause, where_clause, where_clause_params = where_query.get_sql()
                #select = "SELECT sum(credit)-sum(debit) from " + from_clause + " where " + where_clause

            self.env.cr.execute(select, where_clause_params)
            line.invoiced_qty = self.env.cr.fetchone()[0] or 0.0
            
    
    def _compute_all_quantity(self):
        for rs in self:
            move_lines = self.env['account.move.line'].search([('product_id', '=', rs.product_id.id),('date', '>=', rs.sale_target_id.date_from),('date', '<=', rs.sale_target_id.date_to)])
            for line in move_lines.filtered(lambda x: x.move_id.state not in ('draft', 'cancel') and x.move_id.journal_id.id == rs.sale_target_id.journal_id.id):
                rs.invoiced_qty += line.quantity
            rs.remaining_qty = rs.target_qty - rs.invoiced_qty
        
    @api.onchange('product_id')
    def _onchange_product_id(self):
        move_lines = self.env['account.move.line'].search([('product_id', '=', self.product_id.id),('date', '>=', self.sale_target_id.date_from),('date', '<=', self.sale_target_id.date_to)])
        #for line in move_lines.filtered(lambda x: x.state not in ('draft', 'cancel')):
        #self.invoiced_qty
        