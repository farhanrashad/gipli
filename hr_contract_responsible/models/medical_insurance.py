from odoo import api, fields, models
from datetime import datetime
class MedicalInsurance(models.Model):
    _name = 'medical.insurance'
    _description = 'MedicalInsurance'
    _rec_name='provider_id'


    provider_id = fields.Many2one(comodel_name="res.partner", string="Provider", required=False, )
    start_date = fields.Date(string="Start Date", required=False, )
    end_date = fields.Date(string="End Date", required=False, )
    insurance_ids = fields.One2many(comodel_name="medical.insurance.line", inverse_name="medical_id", string="", required=False, )
    total_contract_value = fields.Char(string="Total Contract Value", required=False, )
    details = fields.Text(string="Details", required=False, )



class MedicalInsuranceLine(models.Model):
    _name = 'medical.insurance.line'
    _description = 'MedicalInsuranceLine'
    _rec_name='job_level_id'

    job_level_id = fields.Many2one(comodel_name="medical.job.level", string="Job level", required=False)
    package_name_id = fields.Many2one(comodel_name="medical.package.name", string="Package Name", required=False)

    cover_age_price = fields.Float(string="Coverage Price", required=False, )
    employee_percentage = fields.Float(string="Employee Percentage", required=False, )
    amount = fields.Float(string="Amount", store=True, compute="calc_amount")
    description = fields.Text(string="description", required=False, )
    medical_id = fields.Many2one(comodel_name="medical.insurance", string="", required=False, )
    provider_id = fields.Many2one(comodel_name="res.partner", string="Provider", related='medical_id.provider_id', store=True )

    @api.depends('cover_age_price', 'employee_percentage')
    def calc_amount(self):
        for rec in self:
            rec.amount = rec.cover_age_price * (rec.employee_percentage/100)
class JobLevel(models.Model):
    _name = 'medical.job.level'
    name = fields.Char(string="Name", required=False)

class PackageName(models.Model):
    _name = 'medical.package.name'
    name = fields.Char(string="Name", required=False)
