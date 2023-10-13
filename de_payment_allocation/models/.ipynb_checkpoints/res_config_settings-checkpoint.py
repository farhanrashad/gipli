# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    recon_journal_id = fields.Many2one(
        'account.journal',
        'Reconciliation Journal',
        domain="[('type', '=', 'general')]",
        config_parameter='de_payment_allocation.payment_allocation_journal_id',
        help='journal used for payment allocation')