from odoo import models, fields


class DeductionDescription(models.Model):
    _name = 'deduction.description'
    _description = 'Deduction Description'

    deduction_description = fields.Char(string='Deduction Description')
    amount = fields.Float(string='Amount')
    contract_id = fields.Many2one('hr.contract', string='Contract')
