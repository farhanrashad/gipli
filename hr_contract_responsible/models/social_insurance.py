from odoo import api, fields, models
from odoo.exceptions import ValidationError

class SocialInsurance(models.Model):
    _name='social.insurance'
    _rec_name='social_insurance_package'

    social_insurance_package = fields.Float(string="Social Insurance Package", required=False)
    employee_percentage = fields.Float(string="Employee Percentage", compute='_calc_employee_percentage', store=True)

    @api.depends('social_insurance_package')
    def _calc_employee_percentage(self):
        for rec in self:
            rec.employee_percentage = rec.social_insurance_package * .11