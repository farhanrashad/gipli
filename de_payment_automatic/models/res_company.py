# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit = "res.company"

    pr_default_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string="Journal",
        check_company=True,
        domain="[('type', 'in', ('bank','cash'))]",
        help='The default accounting journal that will use automatic payment run.')
    