# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class PurchaseOrder(models.Model):
    _inherit= "purchase.order"
    
class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    
    budget_exception = fields.Char(compute="_budget_exception", string="Budget Exception")
    def _budget_exception(self):
        message = ''
        for line in self.order_line:
            if line.purchase_budget_line_id:
                for budget in line.purchase_budget_line_id:
                    if (budget.planned_quantity - (budget.practical_quantity+line.product_qty)) < 0:
                        message = 'Budget is exceeding for one of the product'
                        break
        self.budget_exception = message
    
class PurchaseOrderLine(models.Model):
    _inherit= "purchase.order.line"

    purchase_budget_line_id = fields.Many2one('purchase.budget.lines', string="Budget Line", domain="[('purchase_budget_id.state','=','validate')]")
    budget_avaiable_qty = fields.Float(string="Avl.budget", compute="_budget_available_quantity")
    
    def _budget_available_quantity(self):
        amt = 0
        if self.purchase_budget_line_id:
            for line in self.purchase_budget_line_id:
                amt = line.planned_quantity - line.practical_quantity
        self.budget_avaiable_qty = amt