# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class Stage(models.Model):
    _inherit = "crm.stage"

    is_kyb = fields.Boolean(default=False)