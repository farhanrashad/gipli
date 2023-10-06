# -*- coding: utf-8 -*-

from odoo import models, fields

class CRMLead(models.Model):
    _inherit = 'crm.lead'

    ap_id = fields.Char(
        string='Apollo ID',
        help="The Apollo ID is used for tracking purposes."
    )
