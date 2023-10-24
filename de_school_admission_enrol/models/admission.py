# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.osv import expression


class Admission(models.Model):
    _inherit = 'oe.admission'

    sale_order_count = fields.Integer(compute='_compute_sale_data', string="Number of Enrol Orders")
    order_ids = fields.One2many('sale.order', 'admission_id', string='Orders')

    @api.depends('order_ids.state', 'order_ids.currency_id', 'order_ids.amount_untaxed', 'order_ids.date_order', 'order_ids.company_id')
    def _compute_sale_data(self):
        for lead in self:
            company_currency = lead.company_currency or self.env.company.currency_id
            sale_orders = lead.order_ids.filtered_domain(self._get_lead_sale_order_domain())
            lead.sale_amount_total = sum(
                order.currency_id._convert(
                    order.amount_untaxed, company_currency, order.company_id, order.date_order or fields.Date.today()
                )
                for order in sale_orders
            )
            lead.sale_order_count = len(sale_orders)

    def _get_lead_sale_order_domain(self):
        return [('state', 'not in', ('draft', 'sent', 'cancel'))]
