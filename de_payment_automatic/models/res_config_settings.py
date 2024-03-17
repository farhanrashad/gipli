# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models

from odoo.addons.account.models.company import PEPPOL_LIST


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pr_default_journal_id = fields.Many2one('account.journal', related="company_id.pr_default_journal_id", required=True, readonly=False,
        string='Journal')
    
    
    