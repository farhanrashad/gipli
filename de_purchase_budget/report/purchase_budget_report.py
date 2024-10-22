# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import tools
from odoo import api, fields, models


class PurchaseBudgetReport(models.Model):
    _name = "purchase.budget.report"
    _description = "Purchase Budget Report"
    _auto = False
    _rec_name = 'name'
    _order = 'name'
    
    name = fields.Char('Budget Line', readonly=True)
    budget = fields.Char('Budget Reference', readonly=True)
    nbr = fields.Integer('# of Lines', readonly=True)
    date_from = fields.Date('From Date', readonly=True)
    date_to = fields.Datetime('To Date', readonly=True)
    date_order = fields.Datetime(string='Order Date', readonly=True)

    planned_quantity = fields.Float('Planned Qty', readonly=True)
    planned_price_unit = fields.Float('Planned Price', readonly=True)    
    planned_amount = fields.Float('Planned Amount', readonly=True)
    
    actual_quantity = fields.Float('Actual Qty', readonly=True)
    average_price = fields.Float('Avg. Price', readonly=True)
    actual_amount = fields.Float('Actual Amount', readonly=True)
    
    remain_qty = fields.Float('Remaining Qty', readonly=True)
    remain_amount = fields.Float('Remaining Amount.', readonly=True)
    
    purchase_id = fields.Many2one('purchase.order', 'Purchase Order', readonly=True)
    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    partner_id = fields.Many2one('res.partner', 'Vendor', readonly=True)

    analytic_account_id = fields.Many2one('account.analytic', 'Analytic Account', readonly=True)
    #department_id = fields.Many2one('hr.department', 'Department', readonly=True)
    expense_category = fields.Selection([
        ('capex', 'CAPEX'),
        ('opex', 'OPEX'),
        ], 'Expense Type', default='capex', index=True, readonly=True, )
    purchase_budget_state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('confirm', 'Confirmed'),
        ('validate', 'Validated'),
        ('done', 'Done')
        ], 'Status', default='draft', readonly=True, )
    
    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        with_ = ("WITH %s" % with_clause) if with_clause else ""

        select_ = """
         count(*) as nbr, min(bl.id) as id, po.id as purchase_id, po.date_order, po.partner_id, b.name as budget, bl.expense_category, bl.name, bl.date_from, bl.date_to, bl.analytic_account_id, pl.product_id, sum(bl.planned_quantity) as planned_quantity, avg(bl.planned_price_unit) as planned_price_unit, sum(bl.planned_quantity * bl.planned_price_unit) as planned_amount, sum(pl.product_qty) as actual_quantity, avg(pl.price_unit) as average_price, sum(pl.product_qty * pl.price_unit) as actual_amount, bl.purchase_budget_state, sum(bl.planned_quantity) - sum(pl.product_qty) as remain_qty, 
sum(bl.planned_quantity * bl.planned_price_unit) - sum(pl.product_qty * pl.price_unit) as remain_amount
from purchase_budget_lines bl
join purchase_budget b on bl.purchase_budget_id = b.id
left join purchase_order_line pl on pl.purchase_budget_line_id = bl.id
join purchase_order po on pl.order_id = po.id
where b.state not in ('draft','cancel') and po.state in ('purchase','done')
group by po.id, po.partner_id, b.name, bl.expense_category, bl.name, pl.product_id, po.date_order, bl.date_from, bl.date_to, bl.analytic_account_id, bl.purchase_budget_state
"""

        for field in fields.values():
            select_ += field
        
        from_ = groupby_ = ''

        return '%s (SELECT %s %s %s)' % (with_, select_, from_, groupby_)

    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))