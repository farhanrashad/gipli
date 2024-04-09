# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models

from odoo.addons.account.models.company import PEPPOL_LIST


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    # Facebook
    module_fb = fields.Boolean('Facebook Developer Account')

    # Instagram

    # Youtube

    # Twitter