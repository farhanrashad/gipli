# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    hr_expense_prepayment_line_id = fields.Many2one('hr.expense.prepayment.line', string='Expense Prepayment Request', copy=False, help="Prepayment request where the move line come from")