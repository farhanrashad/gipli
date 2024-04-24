from odoo import api, fields, models
import io
import json
try:
   from odoo.tools.misc import xlsxwriter
except ImportError:
   import xlsxwriter


class DynamicPurchaseReport(models.Model):
   """Model for getting dynamic purchase report """
   _name = "dynamic.purchase.report"
   _description = "Dynamic Purchase Report"
   purchase_report = fields.Char(string="Purchase Report",
                                 help='Name of the report')
   date_from = fields.Datetime(string="Date From", help='Start date of report')
   date_to = fields.Datetime(string="Date to", help='End date of report')
   report_type = fields.Selection([
       ('report_by_order', 'Report By Order'),
       ('report_by_order_detail', 'Report By Order Detail')], default='report_by_order',
       help='The order of the report')
   @api.model
   def purchase_report(self, option):
       """Function for getting datas for requests """
       report_values = self.env['dynamic.purchase.report'].search(
           [('id', '=', option[0])])
       data = {
           'report_type': report_values.report_type,
           'model': self,
       }
       if report_values.date_from:
           data.update({
               'date_from': report_values.date_from,
           })
       if report_values.date_to:
           data.update({
               'date_to': report_values.date_to,
           })
       filters = self.get_filter(option)
       lines = self._get_report_values(data).get('PURCHASE')
       return {
           'name': "Purchase Orders",
           'type': 'ir.actions.client',
           'tag': 's_r',
           'orders': data,
           'filters': filters,
           'report_lines': lines,
       }
   def get_filter(self, option):
       """Function for get data according to order_by filter """
       data = self.get_filter_data(option)
       filters = {}
       if data.get('report_type') == 'report_by_order':
           filters['report_type'] = 'Report By Order'
       else:
           filters['report_type'] = 'Report By Order Detail'
       return filters
   def get_filter_data(self, option):
       """ Function for get filter data in report """
       record = self.env['dynamic.purchase.report'].search([('id', '=', option[0])])
       default_filters = {}
       filter_dict = {
           'report_type': record.report_type,
       }
       filter_dict.update(default_filters)
       return filter_dict

    def _get_report_sub_lines(self, data):
       """ Function for get report value using sql query """
       report_sub_lines = []
       if data.get('report_type') == 'report_by_order':
           query = """ select l.name,l.date_order, l.partner_id,l.amount_total,
           l.notes,l.user_id,res_partner.name as partner,
           res_users.partner_id as user_partner,sum(purchase_order_line.product_qty),
           l.id as id,(SELECT res_partner.name as salesman FROM res_partner
           WHERE res_partner.id = res_users.partner_id) from purchase_order as l
           left join res_partner on l.partner_id = res_partner.id
           left join res_users on l.user_id = res_users.id
           left join purchase_order_line on l.id = purchase_order_line.order_id
           where 1=1 """
           if data.get('date_from'):
               query += """and l.date_order >= '%s' """ % data.get('date_from')
           if data.get('date_to'):
               query += """ and l.date_order <= '%s' """ % data.get('date_to')
           query += """group by l.user_id,res_users.partner_id,res_partner.name,
                     l.partner_id,l.date_order,l.name,l.amount_total,l.notes,l.id"""
           self._cr.execute(query)
           report_by_order = self._cr.dictfetchall()
           report_sub_lines.append(report_by_order)
       else :
           query = """ select l.name,l.date_order,l.partner_id,l.amount_total,
           l.notes, l.user_id,res_partner.name as partner,res_users.partner_id
           as user_partner,sum(purchase_order_line.product_qty),
           purchase_order_line.name as product, purchase_order_line.price_unit,
           purchase_order_line.price_subtotal,l.amount_total,
           purchase_order_line.product_id,product_product.default_code,
           (SELECT res_partner.name as salesman FROM res_partner WHERE
           res_partner.id = res_users.partner_id)from purchase_order as l
           left join res_partner on l.partner_id = res_partner.id
           left join res_users on l.user_id = res_users.id
           left join purchase_order_line on l.id = purchase_order_line.order_id
           left join product_product on purchase_order_line.product_id = product_product.id
           where 1=1 """
           if data.get('date_from'):
               query += """ and l.date_order >= '%s' """ % data.get('date_from')
           if data.get('date_to'):
               query += """ and l.date_order <= '%s' """ % data.get('date_to')
           query += """group by l.user_id,res_users.partner_id,res_partner.name,
           l.partner_id,l.date_order,l.name,l.amount_total,l.notes,
           purchase_order_line.name,purchase_order_line.price_unit,
           purchase_order_line.price_subtotal,l.amount_total,
           purchase_order_line.product_id,product_product.default_code"""
           self._cr.execute(query)
           report_by_order_details = self._cr.dictfetchall()
           report_sub_lines.append(report_by_order_details)
       return report_sub_lines
    def _get_report_values(self, data):
       """ Get report values based on the provided data. """
       docs = data['model']
       if data.get('report_type'):
           report_res = \
               self._get_report_sub_lines(data)[0]
       else:
           report_res = self._get_report_sub_lines(data)
       return {
           'doc_ids': self.ids,
           'docs': docs,
           'PURCHASE': report_res,
       }