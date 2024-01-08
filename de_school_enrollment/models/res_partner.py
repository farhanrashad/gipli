# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date
from odoo import api, fields, models
from odoo.osv import expression


class ResPartner(models.Model):
    _inherit = "res.partner"
    
    enrol_order_ids = fields.One2many('sale.order', 'partner_id', string='Enrolment Orders')