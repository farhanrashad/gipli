# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    roll = fields.Char(string='Roll')
    pcs = fields.Char(string='PCS')
