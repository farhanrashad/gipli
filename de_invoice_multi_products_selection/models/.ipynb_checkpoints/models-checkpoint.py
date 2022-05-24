# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class de_invoice_multi_products_selection(models.Model):
#     _name = 'de_invoice_multi_products_selection.de_invoice_multi_products_selection'
#     _description = 'de_invoice_multi_products_selection.de_invoice_multi_products_selection'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
