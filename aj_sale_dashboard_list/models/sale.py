from odoo import models, fields, api, _
from datetime import datetime, time
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, format_amount, format_date, formatLang, get_lang, groupby


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def retrieve_dashboard(self):
        """ This function returns the values to populate the custom dashboard in
            the purchase order views.
        """
        self.check_access_rights('read')

        result = {
            'all_quotation': 0,
            'all_quotation_sent': 0,
            'all_sales_order': 0,
            'my_quotation': 0,
            'my_quotation_sent': 0,
            'my_sales_order': 0,
            'all_avg_order_value': 0,
            'all_avg_days_to_purchase': 0,
            'all_total_last_7_days': 0,
            'all_sent_rfqs': 0,
            'company_currency_symbol': self.env.company.currency_id.symbol
        }

        one_week_ago = fields.Datetime.to_string(fields.Datetime.now() - relativedelta(days=7))
        query = """SELECT COUNT(1)
                   FROM mail_message m
                   JOIN sale_order po ON (po.id = m.res_id)
                   WHERE m.create_date >= %s
                     AND m.model = 'sale.order'
                     AND m.message_type = 'comment'
                     AND m.subtype_id = %s
                     AND po.company_id = %s;
                """

        self.env.cr.execute(query, (one_week_ago, 1, self.env.company.id))
        res = self.env.cr.fetchone()
        result['all_sent_rfqs'] = res[0] or 0

        # easy counts
        so = self.env['sale.order']
        result['all_quotation'] = so.search_count([('state', '=', 'draft')])
        result['all_quotation_sent'] = so.search_count([('state', '=', 'sent')])
        result['all_sales_order'] = so.search_count([('state', '=', 'sale')])

        result['my_quotation'] = so.search_count([('state', '=', 'draft'), ('user_id', '=', self.env.uid)])
        result['my_quotation_sent'] = so.search_count([('state', '=', 'sent'), ('date_order', '>=', fields.Datetime.now()), ('user_id', '=', self.env.uid)])
        result['my_sales_order'] = so.search_count([('state', '=', 'sale'), ('date_order', '<', fields.Datetime.now()), ('user_id', '=', self.env.uid)])

        result['sold_total_last_7_days'] = so.search_count([('state', 'in', ('sale', 'done')), ('date_order', '>=', one_week_ago)])
        result['order_create_last_7_days'] = so.search_count([('date_order', '>=', one_week_ago)])

        query = """SELECT AVG(COALESCE(po.amount_total / NULLIF(po.currency_rate, 0), po.amount_total)),
                          AVG(extract(epoch from age(po.validity_date,po.create_date)/(24*60*60)::decimal(16,2))),
                          SUM(CASE WHEN po.date_order >= %s THEN COALESCE(po.amount_total / NULLIF(po.currency_rate, 0), po.amount_total) ELSE 0 END)
                   FROM sale_order po
                   WHERE po.state in ('sale', 'done')
                     AND po.company_id = %s
                """
        self._cr.execute(query, (one_week_ago, self.env.company.id))
        res = self.env.cr.fetchone()
        result['all_avg_days_to_purchase'] = round(res[1] or 0, 2)
        currency = self.env.company.currency_id
        result['all_avg_order_value'] = format_amount(self.env, res[0] or 0, currency)
        result['all_total_last_7_days'] = format_amount(self.env, res[2] or 0, currency)

        return result
