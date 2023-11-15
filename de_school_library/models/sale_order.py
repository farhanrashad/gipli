# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta, date
from odoo import api, fields, models, _
from odoo.tools import float_compare, format_datetime, format_time
from pytz import timezone, UTC


class CirculationAgreement(models.Model):
    _inherit = 'sale.order'

    is_borrow_order = fields.Boolean("Circulation Agreement")
    borrow_status = fields.Selection([
        ('draft', 'Draft'),
        ('confirm','Confirm'), 
        ('reserve','Reserve'), # Reserve book will hold the book and will not avaible for issuance.
        ('issue','Issued'), # book issue to petron.
        ('return', 'Returned'), # book return by petron.
        ('done', 'Done'), # agreement closed 
        ('cancel', 'Cancelled'), 
    ], string="Borrow Status", default='draft', store=True, tracking=True, index=True,)

    borrow_next_action_date = fields.Datetime(
        string="Next Action", compute='_compute_next_action_date', store=True)

    #has_pickable_lines = fields.Boolean(compute="_compute_rental_status", store=True)
    #has_late_lines = fields.Boolean(compute="_compute_has_late_lines")

    # compute Method
    #@api.depends('state', 'order_line', 'order_line.product_uom_qty', 'order_line.qty_delivered', 'order_line.qty_returned')
    def _compute_next_action_date(self):
        for order in self:
            if order.state in ['sale', 'done'] and order.is_borrow_order:
                rental_order_lines = order.order_line.filtered(lambda l: l.is_rental and l.start_date and l.return_date)
                pickeable_lines = rental_order_lines.filtered(lambda sol: sol.qty_delivered < sol.product_uom_qty)
                returnable_lines = rental_order_lines.filtered(lambda sol: sol.qty_returned < sol.qty_delivered)
                min_pickup_date = min(pickeable_lines.mapped('start_date')) if pickeable_lines else 0
                min_return_date = min(returnable_lines.mapped('return_date')) if returnable_lines else 0
                if min_pickup_date and pickeable_lines and (not returnable_lines or min_pickup_date <= min_return_date):
                    order.borrow_status = 'pickup'
                    order.borrow_next_action_date = min_pickup_date
                elif returnable_lines:
                    order.borrow_status = 'return'
                    order.borrow_next_action_date = min_return_date
                else:
                    order.borrow_status = 'return'
                    order.next_action_date = False
                #order.has_pickable_lines = bool(pickeable_lines)
                #order.has_returnable_lines = bool(returnable_lines)
            else:
                #order.has_pickable_lines = False
                #order.has_returnable_lines = False
                #order.rental_status = order.state if order.is_borrow_order else False
                order.borrow_next_action_date = False
    
    @api.depends('is_borrow_order', 'borrow_next_action_date', 'rental_status')
    def _compute_has_late_lines(self):
        for order in self:
            order.has_late_lines = (
                order.is_borrow_order
                and order.rental_status in ['pickup', 'return']  # has_pickable_lines or has_returnable_lines
                and order.borrow_next_action_date and order.borrow_next_action_date < fields.Datetime.now())


    def action_confirm(self):
        if self.is_borrow_order:
            self._action_borrow_order()
        else:
            super(CirculationAgreement, self).action_confirm()

    def _action_borrow_order(self):
        self.write({
            'state': 'sale',
            'borrow_status': 'confirm',
        })


    def open_issue_form(self):
        pass
    def open_return_form(self):
        pass
    

    