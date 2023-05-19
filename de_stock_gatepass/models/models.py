# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class de_stock_gatepass(models.Model):
#     _name = 'de_stock_gatepass.de_stock_gatepass'
#     _description = 'de_stock_gatepass.de_stock_gatepass'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
