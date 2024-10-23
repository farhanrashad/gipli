# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProjectBudget(models.Model):
    _name = 'project.budget'
    _description = 'Project Budget'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'project_id'
    _order = "id desc"

    project_id = fields.Many2one(
        'project.project',  # Assuming this is the model for projects
        string='Project',
        required=True,
        ondelete='cascade'
    )

    user_id = fields.Many2one(
        'res.users',  # Standard model for users
        string='User',
        required=True,
        default=lambda self: self.env.user  # Default to the current user
    )

    start_date = fields.Date(
        string='Start Date',
        required=True
    )

    end_date = fields.Date(
        string='End Date',
        required=True
    )

    company_id = fields.Many2one(
        'res.company',  # Standard model for companies
        string='Company',
        required=True,
        default=lambda self: self.env.company  # Default to the current company
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft', required=True, tracking=True,copy=False
    )

    # One2many relation to the budget lines
    line_ids = fields.One2many(
        'project.budget.line',  # The model for budget lines
        'budget_id',  # Field in the line model that relates to this budget
        string='Budget Lines'
    )


    def action_budget_draft(self):
        self.write({
            'state': 'draft'
        })

    def action_budget_confirm(self):
        self.write({
            'state': 'confirmed'
        })

    def action_budget_done(self):
        self.write({
            'state': 'done'
        })

    def action_budget_cancel(self):
        self.write({
            'state': 'cancel'
        })
class ProjectBudgetLine(models.Model):
    _name = 'project.budget.line'
    _description = 'Project Budget Line'

    budget_id = fields.Many2one(
        'project.budget',  # Link back to the budget
        string='Budget',
        required=True,
        ondelete='cascade'
    )

    sequence = fields.Integer(
        string='Sequence',
        default=10 
    )
    product_id = fields.Many2one(
        'product.product',  # Assuming you have a product model
        string='Product',
        required=True
    )

    quantity = fields.Float(
        string='Quantity',
        required=True,
        default=1.0  # Default quantity
    )

    cost = fields.Float(
        string='Cost',
        required=True
    )

    total = fields.Monetary(
        string='Total',
        currency_field='currency_id',  # Reference to the currency field
        compute='_compute_total',
        store=True  # Store the computed value
    )

    amount_budget = fields.Monetary(
        string='Amount Budget',
        currency_field='currency_id',  # Reference to the currency field
    )
    qty_committed = fields.Float(
        string='Commiteed Qty',
        compute='_compute_committed_qty',
        help='Received Quantity + Confirmed Requisition'
    )
    qty_achieved = fields.Float(
        string='Achieved Qty',
        compute='_compute_achieved_qty',
        help='Received Quantity + Confirmed Requisition'
    )

    currency_id = fields.Many2one(
        'res.currency',  # Currency model
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id  # Default to the company currency
    )

    def _compute_committed_qty(self):
        for record in self:
            record.qty_committed = 0

    def _compute_achieved_qty(self):
        for record in self:
            record.qty_achieved = 0

    @api.depends('quantity', 'cost')
    def _compute_total(self):
        for line in self:
            line.total = line.quantity * line.cost

    def action_open_budget_entries(self):
        self.ensure_one()        
        action = self.env.ref('stock.stock_move_line_action').sudo().read()[0]
        action['context'] = {
            'search_default_done': 1, 
            'create': 0, 
            'edit': 0,
            'delete': 0,
        }
        action['domain'] = [
            ('picking_id.project_id', '=', self.budget_id.project_id.id),
            ('state','=','done')
        ]
        return action

    
