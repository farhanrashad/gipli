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
    target_qty = fields.Float(string='Target Qty',required=True,default='1.0')
    invoiced_qty = fields.Float(string='Invoiced Qty',readonly=True,compute='_compute_all_quantity')
    remaining_qty = fields.Float(string='Remaining Qty',readonly=True,compute='_compute_all_quantity')
    
    def _compute_all_quantity(self):
        move_lines = self.env['account.move.line'].search([('product_id', '=', self.product_id.id),('date', '>=', self.sale_target_id.date_from),('date', '<=', self.sale_target_id.date_to)])
        for line in move_lines.filtered(lambda x: x.move_id.state not in ('draft', 'cancel') and x.move_id.journal_id.id == self.sale_target_id.journal_id.id):
            self.invoiced_qty += line.quantity
        self.remaining_qty = self.target_qty - self.invoiced_qty
        
    @api.onchange('product_id')
    def _onchange_product_id(self):
        move_lines = self.env['account.move.line'].search([('product_id', '=', self.product_id.id),('date', '>=', self.sale_target_id.date_from),('date', '<=', self.sale_target_id.date_to)])
        #for line in move_lines.filtered(lambda x: x.state not in ('draft', 'cancel')):
        #self.invoiced_qty
        