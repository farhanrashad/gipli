from odoo import api, fields, models

class PolComm(models.Model):
    _name='policy.commision'
    name = fields.Char(
        string='Name',
        required=False)

class Polbonous(models.Model):
    _name='policy.bonous'
    name = fields.Char(
        string='Name',
        required=False)
class PolNts(models.Model):
    _name='policy.nts'
    name = fields.Char(
        string='Name',
        required=False)
