# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import email_split, float_is_zero


class HREOSContract(models.Model):
    _inherit = "hr.eos.contract"

    comp_category_id = fields.Many2one('hr.eos.comp.rule.category', string="Category", copy=False, required=1)
    eos_comp_line = fields.One2many('hr.eos.comp.line', 'eos_contract_id', string='Compensation Lines', copy=False, compute='_compute_compensation_lines', store=True, readonly=False)
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True, default=lambda self: self.env.company.currency_id)

    @api.depends('comp_category_id')
    def _compute_compensation_lines(self):
        rule_ids = self.env['hr.eos.comp.rule'].search([('eos_category_ids','in',self.comp_category_id.id)])
        line_values = []
        comp_line_obj = self.env['hr.eos.comp.line']
        for contract in self:
            if len(contract.eos_comp_line):
                contract.eos_comp_line.unlink()
            for rule in rule_ids:
                line_values.append({
                    'comp_rule_id': rule.id,
                    'quantity': 1,
                    'rate': 1,
                    'eos_contract_id': contract.id,
                })
            contract.eos_comp_line = comp_line_obj.create(line_values)
            
            

class HREOSCompLine(models.Model):
    _name = "hr.eos.comp.line"
    _description = "EOS Compensation Line"
    
    eos_contract_id = fields.Many2one('hr.eos.contract', string="EOS Contract", copy=False)
    employee_id = fields.Many2one('hr.employee', related='eos_contract_id.employee_id')
    sequence = fields.Integer(default=1)
    comp_rule_id = fields.Many2one('hr.eos.comp.rule', string='Compensation', ondelete='restrict', readonly=True, required=True)
    currency_id = fields.Many2one('res.currency', related='eos_contract_id.currency_id')
    quantity = fields.Float(required=True, digits='Product Unit of Measure', default=1)
    rate = fields.Float("Rate", required=True, copy=True,digits='Product Price', default=1)
    total_amount = fields.Monetary("Total", compute='_compute_amount', store=True, currency_field='currency_id', tracking=True)
    
    @api.depends('quantity', 'rate',)
    def _compute_amount(self):
        for comp in self:
            comp.total_amount = comp.rate * comp.quantity



