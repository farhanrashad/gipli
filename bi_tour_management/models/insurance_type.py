from odoo import models, fields, api


class InsuranceType(models.Model):
    _name = 'insurance.type'
    _description = 'Insurance Type'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    adult_cost = fields.Float(string='Adult Cost', required=True)
    child_cost = fields.Float(string='Child Cost', required=True)
