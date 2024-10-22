# -*- coding: utf-8 -*-

from datetime import datetime, time
from dateutil.relativedelta import relativedelta
from itertools import groupby
from pytz import timezone, UTC
from werkzeug.urls import url_encode

from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_is_zero
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang


class PurchaseBudget(models.Model):
    _name = "purchase.budget"
    _description = "Purchase Budget"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Budget Name', required=True, states={'done': [('readonly', True)]})
    user_id = fields.Many2one('res.users', 'Responsible', default=lambda self: self.env.user)
    department_ids = fields.Many2many('hr.department', string='Departments')
    date_from = fields.Date('Start Date', required=True, states={'done': [('readonly', True)]})
    date_to = fields.Date('End Date', required=True, states={'done': [('readonly', True)]})
    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('confirm', 'Confirmed'),
        ('validate', 'Validated'),
        ('done', 'Done')
        ], 'Status', default='draft', index=True, required=True, readonly=True, copy=False, tracking=True)
    purchase_budget_line = fields.One2many('purchase.budget.lines', 'purchase_budget_id', 'Budget Lines',
        states={'done': [('readonly', True)]}, copy=True)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
        default=lambda self: self.env.company.currency_id.id)
    
    budget_apply = fields.Selection([
        ('purchase', 'Manually update on Purchase Order'),
        ('automated', 'Automated'),
        ], 'Apply On', default='automated', index=True, required=True, )

    company_id = fields.Many2one('res.company', 'Company', required=True,
        default=lambda self: self.env.company)
    purchase_count = fields.Integer(compute='_compute_purchase_count', string='Purchases')


    def _compute_purchase_count(self):
        Purchase = self.env['purchase.order.line']
        can_read = Purchase.check_access_rights('read', raise_exception=False)
        for budget in self:
            budget.purchase_count = can_read and Purchase.search_count([('purchase_budget_line_id.purchase_budget_id', '=', budget.id),('state', '!=', 'cancel')]) or 0

    def action_view_purchases(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'binding_type': 'action',
            'name': 'Purchase Lines',
            'res_model': 'purchase.order.line',
            'domain': [('purchase_budget_line_id', 'in', self.purchase_budget_line.ids)],
            'target': 'current',
            'view_mode': 'tree,form',
        }
    
    def action_view_purchases1(self):
        action = self.env["ir.actions.actions"]._for_xml_id("action_purchase_order_line_budget_view")
        purchases = self.env['purchase.order.line'].search([('purchase_budget_line_id.purchase_budget_id', '=', self.id),('state', '!=', 'cancel')])
        if len(purchases) > 1:
            action['domain'] = [('purchase_budget_line_id.purchase_budget_id', '=', self.id),('state', '!=', 'cancel')]
        elif purchases:
            form_view = [(self.env.ref('purchase_order_form_inherit_budget').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = purchases.id
        return action
    
            
    def action_budget_confirm(self):
        self.write({'state': 'confirm'})

    def action_budget_draft(self):
        self.write({'state': 'draft'})

    def action_budget_validate(self):
        self.write({'state': 'validate'})

    def action_budget_cancel(self):
        self.write({'state': 'cancel'})

    def action_budget_done(self):
        self.write({'state': 'done'})

class PurchaseBudgetExpenseCategory(models.Model):
    _name = "purchase.budget.expense.category"
    _description = "Purchase Budget Expense Category"
    _rec_name = 'complete_name'
    
    name = fields.Char(string='Category Name', required=True)
    complete_name = fields.Char(string='Full Category Name', compute='_compute_complete_name')
    active = fields.Boolean(string='Active', default=True,)
    
    exp_category_id = fields.Many2one('purchase.budget.expense.category', 'Parent Category', index=True, ondelete='cascade' )
    
    @api.depends('name', 'exp_category_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.exp_category_id:
                category.complete_name = '%s/%s' % (category.exp_category_id.complete_name, category.name)
            else:
                category.complete_name = category.name
    
class PurchaseBudgetLines(models.Model):
    _name = "purchase.budget.lines"
    _description = "Purchase Budget Line"

    name = fields.Char(compute='_compute_line_name', store=True, readonly=False)
    purchase_budget_id = fields.Many2one('purchase.budget', 'Budget', ondelete='cascade', index=True, required=True)
    date_from = fields.Date('Start Date', required=True)
    date_to = fields.Date('End Date', required=True)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    analytic_group_id = fields.Many2one('account.analytic.group', 'Analytic Group', related='analytic_account_id.group_id', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)], change_default=True)
    categ_id = fields.Many2one('product.category', 'Category',
        change_default=True, group_expand='_read_group_categ_id',
        help="Select category for the current product")
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', string="Uom Category")
    planned_quantity = fields.Float('Planned Qty', required=True,
        help="Quantity you plan to purchase/sale. Record a positive amount if it is a revenue and a negative amount if it is a cost.")
    practical_quantity = fields.Float(
        compute='_compute_all_practical', string='Act. Qty', help="Quantity really earned/spent.")
    planned_price_unit = fields.Float(string='Planned UP', required=True, digits='Product Price')
    planned_amount = fields.Monetary(
        compute='_compute_planned_amount', string='Planned Amt',
        help="Amount you are supposed to have purchase at this date.")
    practical_amount = fields.Monetary(
        compute='_compute_all_practical', string='Act. Amt', help="Amount really spent.")
    currency_id = fields.Many2one('res.currency', related='purchase_budget_id.currency_id', readonly=True)
    percentage = fields.Float(
        compute='_compute_percentage', string='Achievement',
        help="Comparison between practical and theoretical amount. This measure tells you if you are below or over budget.")
    
    company_id = fields.Many2one(related='purchase_budget_id.company_id', comodel_name='res.company',
        string='Company', store=True, readonly=True)
    purchase_budget_state = fields.Selection(related='purchase_budget_id.state', string='Budget State', store=True, readonly=True)
    
    expense_category = fields.Selection([
        ('capex', 'CAPEX'),
        ('opex', 'OPEX'),
        ], 'Expense Type', default='capex', index=True, required=True, )
    
    exp_category_id = fields.Many2one('purchase.budget.expense.category', string='Expense Category', index=True, ondelete='cascade' )

    
    @api.constrains('product_id', 'categ_id')
    def _must_have_product_or_category_or_both(self):
        for record in self:
            if not record.product_id and not record.categ_id and not record.name and not record.analytic_account_id:
                raise ValidationError(
                    _("You have to enter at least a name, analytic, product or product category on a budget line."))
    
    @api.constrains('date_from', 'date_to')
    def _line_dates_between_budget_dates(self):
        for line in self:
            budget_date_from = line.purchase_budget_id.date_from
            budget_date_to = line.purchase_budget_id.date_to
            if line.date_from:
                date_from = line.date_from
                if date_from < budget_date_from or date_from > budget_date_to:
                    raise ValidationError(_('"Start Date" of the budget line should be included in the Period of the budget'))
            if line.date_to:
                date_to = line.date_to
                if date_to < budget_date_from or date_to > budget_date_to:
                    raise ValidationError(_('"End Date" of the budget line should be included in the Period of the budget'))
    
    def _compute_all_practical(self):
        purchase_order_lines = self.env['purchase.order.line']
        domain = ''
        subtotal = total = qty = 0
        for line in self:
            subtotal = total = qty = 0
            domain = [('purchase_budget_line_id', '=', line.id),
                      ('order_id.date_order', '>=', line.date_from),
                      ('order_id.date_order', '<=', line.date_to),
                      ('order_id.state', 'in', ['purchase','done'])
                     ]
            purchase_order_lines = self.env['purchase.order.line'].search(domain)
            for pline in purchase_order_lines:
                if not (pline.currency_id.id == line.purchase_budget_id.currency_id.id):
                    #subtotal += pline.currency_id._get_conversion_rate(pline.currency_id, line.purchase_budget_id.currency_id,line.purchase_budget_id.company_id, fields.date.today()) * pline.price_subtotal
                    subtotal += pline.currency_id._convert(pline.price_subtotal, line.purchase_budget_id.currency_id, line.purchase_budget_id.company_id, fields.date.today()) 

                else:
                    subtotal += pline.price_subtotal
                qty += pline.product_qty
            line.practical_quantity = qty or 0.0
            line.practical_amount = subtotal or 0.0
            
    def _compute_all_practical1(self):
        for line in self:
            product_ids = self.env['product.product'].search([('categ_id','=',line.categ_id.id)])
            date_to = line.date_to
            date_from = line.date_from
            
            if line.purchase_budget_id.budget_apply:
                purchase_line_obj = self.env['purchase.order.line']
                domain = [('purchase_budget_line_id', '=', line.id),
                          ('order_id.date_order', '>=', date_from),
                          ('order_id.date_order', '<=', date_to),
                          ('order_id.state', 'in', ['purchase','done'])
                         ]
                where_query = purchase_line_obj._where_calc(domain)
                purchase_line_obj._apply_ir_rules(where_query, 'read')
                from_clause, where_clause, where_clause_params = where_query.get_sql()
                select = "SELECT SUM(product_qty) from " + from_clause + " where " + where_clause
                select_amount = "SELECT SUM(price_total) from " + from_clause + " where " + where_clause
            self.env.cr.execute(select, where_clause_params)
            line.practical_quantity = self.env.cr.fetchone()[0] or 0.0
            self.env.cr.execute(select_amount, where_clause_params)
            line.practical_amount = self.env.cr.fetchone()[0] or 0.0
    
    def _compute_planned_amount(self):
        for line in self:
            line.planned_amount = line.planned_quantity * line.planned_price_unit
            
    def _compute_practical_amount1(self):
        for line in self:
            product_ids = self.env['product.product'].search([('categ_id','=',line.categ_id.id)])
            date_to = line.date_to
            date_from = line.date_from
            if not (line.purchase_budget_id.budget_apply) and line.analytic_account_id.id:
                analytic_line_obj = self.env['account.analytic.line']
                if line.product_id:
                    domain = [('account_id', '=', line.analytic_account_id.id),
                              ('product_id', '=', line.product_id.id),
                              ('date', '>=', date_from),
                              ('date', '<=', date_to),
                              ]
                elif line.categ_id:
                    domain = [('account_id', '=', line.analytic_account_id.id),
                              ('product_id', 'in', product_ids),
                              ('date', '>=', date_from),
                              ('date', '<=', date_to),
                              ]

                where_query = analytic_line_obj._where_calc(domain)
                analytic_line_obj._apply_ir_rules(where_query, 'read')
                from_clause, where_clause, where_clause_params = where_query.get_sql()
                select = "SELECT SUM(amount) from " + from_clause + " where " + where_clause
            self.env.cr.execute(select, where_clause_params)
            line.practical_amount = self.env.cr.fetchone()[0] or 0.0
            
    def _compute_percentage(self):
        for line in self:
            if line.planned_quantity != 0.00:
                line.percentage = float((line.practical_quantity or 0.0) / line.planned_quantity)
            else:
                line.percentage = 0.00
    
    @api.depends("purchase_budget_id", "product_id", "categ_id")
    def _compute_line_name(self):
        #just in case someone opens the budget line in form view
        computed_name = ''
        for record in self:
            if record.purchase_budget_id.budget_apply != 'purchase':
                computed_name = record.purchase_budget_id.name
                if record.product_id:
                    computed_name += ' - ' + record.product_id.name
                if record.categ_id:
                    computed_name += ' - ' + record.categ_id.name
            record.name = computed_name
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        for line in self:
            if line.product_id:
                line.product_uom = line.product_id.uom_po_id
            
    def action_open_budget_entries(self):
        product_ids = self.env['product.product'].search([('categ_id','=',self.categ_id.id)])
        if self.analytic_account_id:
            # if there is an analytic account, then the analytic items are loaded
            action = self.env['ir.actions.act_window']._for_xml_id('analytic.account_analytic_line_action_entries')
            if self.product_id:
                    action['domain'] = [('account_id', '=', self.analytic_account_id.id),
                              ('product_id', '=', self.product_id.id),
                              ('date', '>=', self.date_from),
                              ('date', '<=', self.date_to),
                              ]
            elif self.categ_id:
                    action['domain'] = [('account_id', '=', self.analytic_account_id.id),
                              ('product_id', 'in', product_ids),
                              ('date', '>=', self.date_from),
                              ('date', '<=', self.date_to),
                              ]
        return action
    
    def action_open_budget_purchase_lines(self):
        action = self.env["ir.actions.actions"]._for_xml_id("action_purchase_order_line_budget_view")

        #po_lines = self.mapped('picking_ids')
        po_lines = seld.env['purchase.order.line'].search([('purchase_budget_line_id','=',self.id)])
        if len(po_lines) > 1:
            action['domain'] = [('id', 'in', po_lines.ids)]
        elif po_lines:
            form_view = [(self.env.ref('purchase_order_line_budget_form_view').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = po_lines.id
        
        return action
    
    
        
    
    
        #action = self.env['ir.actions.act_window']._for_xml_id('action_purchase_order_line_budget_view')
        #action['domain'] = [('purchase_budget_line_id', '=', self.id),
                              #('date', '>=', self.date_from),
                              #('date', '<=', self.date_to),
                              #]
        #return action
    
