# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class Member(models.Model):
    _inherit = "res.partner"


    is_xpendless = fields.Boolean('Xpendless Contact')