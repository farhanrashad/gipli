# -*- coding: utf-8 -*-

from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    ap_id = fields.Char(
        string='Apollo ID',
        help="The Apollo ID is used for tracking purposes."
    )
