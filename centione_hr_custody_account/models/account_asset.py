# # -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class AccountAssetAsset(models.Model):
    _inherit = 'account.asset'

    is_custody = fields.Boolean(string="Is Used In Custody",default=False )