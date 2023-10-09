# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict

from odoo import models, fields, api, _
from odoo.tools.misc import frozendict


class AccountMove(models.Model):
    _inherit = "account.move"

    loan_id = fields.One2many('hr.loan', 'account_move_id')
    loan_line_id = fields.One2many('hr.loan.line', 'account_move_id')