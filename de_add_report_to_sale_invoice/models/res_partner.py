# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
    
    
class ResPartner(models.Model):
    _inherit = 'res.partner'

    strg = fields.Char(string="Sales Tax reg Number:")   