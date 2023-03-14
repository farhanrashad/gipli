from odoo import models, fields


class ExtraCharges(models.Model):
    _name = 'extra.charges'
    _description = 'Extra Charges'

    name = fields.Char(string='Extra Charges', required=True)
    amount = fields.Float(string='Amount', required=True)
    contract_id = fields.Many2one('hr.contract')
