# -*- coding: utf-8 -*-

# from odoo import models, fields, api
#
# class AccountMoveInherit(models.Model):
#     _inherit = 'account.move'
#
#     account_id = fields.Many2one('account.account', string='Account Reference')

# class de_account_reference_column(models.Model):
#     _name = 'de_account_reference_column.de_account_reference_column'
#     _description = 'de_account_reference_column.de_account_reference_column'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
