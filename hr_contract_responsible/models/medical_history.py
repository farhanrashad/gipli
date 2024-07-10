from odoo import api, fields, models
from odoo.exceptions import ValidationError


class MedicalHistory(models.Model):
    _name='medical.history'

    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee")
    action = fields.Char(string="Action", required=False)
    date = fields.Date(string="Date", required=False)
    provider_id = fields.Many2one(comodel_name="res.partner", string="Provider", required=False, )
