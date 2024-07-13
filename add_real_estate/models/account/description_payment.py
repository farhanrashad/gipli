from odoo import api, fields, models
from odoo.exceptions import ValidationError

class DescriptionPayment(models.Model):
    _name='description.payment'
    name = fields.Char(string="Name", required=True)
    description = fields.Text(string="Description", required=True)
