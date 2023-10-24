# -*- coding: utf-8 -*-

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    admission_id = fields.Many2one(
        'oe.admission', string='Opportunity', check_company=True,
        domain="[('type', '=', 'opportunity'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    def action_confirm(self):
        return super(SaleOrder, self.with_context({k:v for k,v in self._context.items() if k != 'default_tag_ids'})).action_confirm()
