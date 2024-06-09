# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import fields, models
from odoo.addons.de_subscription.models.sale_order import SUBSCRIPTION_STATUSES

class SaleSubscriptionReport(models.Model):
    _inherit = "sale.report"
    _name = "sale.subs.report"
    _description = "Sale Subscription Analysis"
    _auto = False

    client_order_ref = fields.Char(string="Customer Reference", readonly=False)
    date_first_contract = fields.Date(string='First contract date', readonly=True)
    date_end = fields.Date('End Date', readonly=True)
    recurring_monthly = fields.Monetary('Monthly Recurring', readonly=True)
    recurring_yearly = fields.Monetary('Yearly Recurring', readonly=True)
    recurring_total = fields.Monetary('Recurring Revenue', readonly=True)
    subscription_order = fields.Boolean(readonly=True)
    template_id = fields.Many2one('sale.order.template', 'Subscription Template', readonly=True)
    country_id = fields.Many2one('res.country', 'Country', readonly=True)
    commercial_partner_id = fields.Many2one('res.partner', 'Customer Company', readonly=True)
    industry_id = fields.Many2one('res.partner.industry', 'Industry', readonly=True)
    close_reason_id = fields.Many2one('sale.sub.close.reason', 'Close Reason', readonly=True)
    margin = fields.Float() # not used but we want to avoid creating a bridge module for nothing
    subscription_status = fields.Selection(SUBSCRIPTION_STATUSES, readonly=True)
    date_next_invoice = fields.Date('Next Invoice Date', readonly=True)
    subscription_plan_id = fields.Many2one('sale.recur.plan', 'Recurring Plan', readonly=True)

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res['subscription_order'] = "s.subscription_order"
        res['subscription_status'] = "s.subscription_status"
        res['date_end'] = "s.date_end"
        res['date_first_contract'] = "s.date_first_contract"
        res['template_id'] = "s.sale_order_template_id"
        res['close_reason_id'] = "s.close_reason_id"
        res['date_next_invoice'] = "s.date_next_invoice"
        res['subscription_plan_id'] = "s.subscription_plan_id"
        res['client_order_ref'] = "s.client_order_ref"
        res['margin'] = 0
        res['recurring_monthly'] = f"""sum(l.price_subtotal)
            / CASE
                WHEN ssp.recurring_interval_type = 'week' THEN 7.0 / 30.437
                WHEN ssp.recurring_interval_type = 'month' THEN 1
                WHEN ssp.recurring_interval_type = 'year' THEN 12
                ELSE 1
             END
            / ssp.recurring_interval
            / {self._case_value_or_one('s.currency_rate') }
            * {self._case_value_or_one('currency_table.rate') } 
        """
        res['recurring_yearly'] = f"""sum(l.price_subtotal)
            / CASE
                WHEN ssp.recurring_interval_type = 'week' THEN 7.0 / 30.437
                WHEN ssp.recurring_interval_type = 'month' THEN 1
                WHEN ssp.recurring_interval_type = 'year' THEN 12
                ELSE 1
             END
            / ssp.recurring_interval
            * 12
            / {self._case_value_or_one('s.currency_rate') }
            * {self._case_value_or_one('currency_table.rate') }
        """
        res['recurring_total'] = f"""
                s.amount_total_subscription
                / {self._case_value_or_one('s.currency_rate') }
                * {self._case_value_or_one('currency_table.rate') }  
        """
        return res

    def _from_sale(self):
        frm = super()._from_sale()
        return f"""
            {frm}
            LEFT JOIN sale_recur_plan ssp ON ssp.id = s.subscription_plan_id
        """

    def _where_sale(self):
        where = super()._where_sale()
        return f"""
            {where}
            AND s.subscription_status IS NOT NULL
        """

    def _group_by_sale(self):
        group_by_str = super()._group_by_sale()
        group_by_str = f"""{group_by_str},
                    s.subscription_status,
                    s.date_end,
                    s.subscription_status,
                    s.sale_order_template_id,
                    partner.industry_id,
                    s.close_reason_id,
                    s.state,
                    s.date_next_invoice,
                    s.subscription_plan_id,
                    s.date_first_contract,
                    s.client_order_ref,
                    ssp.recurring_interval_type,
                    ssp.recurring_interval
        """
        return group_by_str

    def action_open_subscription_order(self):
        self.ensure_one()
        if self.order_reference._name == 'sale.order':
            action = self.order_reference._get_associated_so_action()
            action['views'] = [(self.env.ref('de_subscription.subscription_order_primary_form_view').id, 'form')]
            action['res_id'] = self.order_reference.id
            return action
        return {
            'res_model': self._name,
            'type': 'ir.actions.act_window',
            'views': [[False, "form"]],
            'res_id': self.id,
        }
