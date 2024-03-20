# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = "res.partner"

    pr_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Journal',
        domain="[('type', 'in', ('bank','cash')),('company_id','=',company_id)]",
        help='Default Journal use for payment run',
        check_company=True,
    )
    pr_payment_method_id = fields.Many2one(
        string='Payment Method',
        comodel_name='account.payment.method',
        ondelete='cascade'
    )
    