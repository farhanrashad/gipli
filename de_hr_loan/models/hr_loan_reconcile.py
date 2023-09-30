# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict

from odoo import models, fields, api, _
from odoo.tools.misc import frozendict


class LoanReconcile(models.Model):
    _name = "hr.loan.reconcile"
    _description = "Loan Reconcile"

    loan_id = fields.Many2one('hr.loan.line', string='Loan')
    loan_line_id = fields.Many2one('hr.loan.line', string='Loan Line')
    account_move_id = fields.Many2one('account.move', string='Journal Entry')
