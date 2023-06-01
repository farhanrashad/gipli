# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import email_split, float_is_zero


class HREOSContract(models.Model):
    _inherit = "hr.eos.contract"
    
    account_move_id = fields.Many2one('account.move', string='Journal Entry', ondelete='restrict', copy=False, readonly=True)
    journal_id = fields.Many2one('account.journal', string='Journal', check_company=True, domain="[('type', '=', 'purchase'), ('company_id', '=', company_id)]",)

    def action_sheet_move_create(self):
        if any(not line.comp_rule_id.product_id for line in self.eos_comp_line):
            raise UserError(_("Please assigned product for each rule."))
        if not self.employee_id.address_home_id:
            raise UserError(_("You need to have maintain the home address of the employee to generate accounting entries."))
        
        if not self.journal_id:
            raise UserError(_("Contract must have an journal specified to generate accounting entries."))
            
        self.account_move_id = self._create_invoice()
        self.write({'state':'done'})
            
    def _create_invoice(self):
        move_id = self.env['account.move']
        lines_data = []
        for line in self.eos_comp_line:
            lines_data.append([0,0,{
                'name': str(self.name) + ' ' + str(line.comp_rule_id.product_id.name),
                'price_unit': line.rate,
                'quantity': line.quantity,
                'product_id': line.comp_rule_id.product_id.id,
                'product_uom_id': line.comp_rule_id.product_id.uom_id.id,
                'tax_ids': [(6, 0, line.comp_rule_id.product_id.supplier_taxes_id.ids)],
                #'analytic_account_id': line.analytic_account_id.id,
                #'analytic_tag_ids': [(6, 0, line.analytic_tag_ids.ids)],
            }])
        move_id = self.env['account.move'].create({
            'move_type': 'in_refund',
            'invoice_date': fields.Datetime.now(),
            'partner_id': self.employee_id.address_id.id,
            'currency_id': self.currency_id.id,
            'journal_id': self.journal_id.id,
            'invoice_origin': self.name,
            'invoice_payment_term_id': self.employee_id.address_id.property_supplier_payment_term_id.id,
            'narration': self.name,
            'invoice_user_id': self.user_id.id,
            'invoice_line_ids':lines_data,
        })
        return move_id