# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccounTax(models.Model):
    _inherit = 'account.tax'

    withholding = fields.Boolean(string='Withholding')