# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class SaleSubCloseReason(models.Model):
    _name = "sale.sub.close.reason"
    _order = "id"
    _description = "Subscription Close Reason"

    name = fields.Char('Reason', required=True, translate=True)
