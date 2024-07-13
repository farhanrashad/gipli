from odoo import api, fields, models


class CustomerType(models.Model):
    _name='customer.types'
    name = fields.Char(string='Name', required=True)

class Account1(models.Model):
    _name='accounts.account1'
    name = fields.Char(string='Name', required=True)
class Account2(models.Model):
    _name='accounts.account2'
    name = fields.Char(string='Name', required=True)
class Account3(models.Model):
    _name='accounts.account3'
    name = fields.Char(string='Name', required=True)
class DimensionsParent(models.Model):
    _name='dimensions.parent'
    name = fields.Char(string='Name', required=True)
class DimensionsName(models.Model):
    _name='dimensions.name'
    name = fields.Char(string='Name', required=True)