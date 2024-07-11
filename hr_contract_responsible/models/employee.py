from odoo import api, fields, models


class JobFamily(models.Model):
    _name='job.family'

    name = fields.Char(string="Name", required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    salary_range = fields.Char(string="Salary Range", required=False)
    from_ = fields.Float(string="From", required=False)
    to_ = fields.Float(string="To", required=False)
    social_insurance_id = fields.Many2one(comodel_name="social.insurance", string="Social Insurance", required=False)
    employee_percentage = fields.Float(string="Employee Percentage", related='social_insurance_id.employee_percentage',
                                       store=True)
    alert = fields.Integer(string="Alert", required=False)
    other_employees = fields.Many2many(comodel_name="hr.employee", relation="alert_emps", string="Other Employees")



class Job(models.Model):
    _inherit='hr.job'
    job_family_id= fields.Many2one(comodel_name="job.family", string="Job Family", required=False)
    employee_percentage = fields.Float(string="Employee Percentage",related='job_family_id.employee_percentage',store=True)
    job_level_id = fields.Many2one(comodel_name="medical.job.level", string="Job level", required=False)
    medical_insurance_id= fields.Many2one(comodel_name="medical.insurance", string="Medical Insurance Contract", required=False)
    provider_id = fields.Many2one(comodel_name="res.partner", string="Provider", related='medical_insurance_id.provider_id', store=True )




class Employee(models.Model):
    _inherit='hr.employee'
    medical_insurance_id= fields.Many2one(comodel_name="medical.insurance", string="Medical Insurance Contract",related='job_id.medical_insurance_id',store=True)
    job_level_id = fields.Many2one(comodel_name="medical.job.level", string="Job level", related='job_id.job_level_id',store=True)
    package_name_id = fields.Many2one(comodel_name="medical.package.name", string="Package Name",compute='_calc_package_name_id',store=True,readonly=False)
    package_name_ids = fields.Many2many(comodel_name="medical.package.name", relation="emp_packs", compute='_calc_package_name_id',store=False)
    medical_package = fields.Float(compute='_calc_package_name_id',store=True)

    @api.onchange('medical_insurance_id')
    @api.depends('medical_insurance_id')
    def onchange_medical_insurance_id(self):
        if self.medical_insurance_id.insurance_ids:
            domain = [('id', 'in', self.medical_insurance_id.insurance_ids.mapped('package_name_id.id'))]
            return {
                'domain': {'package_name_id': domain}
            }


    @api.depends('job_level_id','medical_insurance_id')
    def _calc_package_name_id(self):
       for rec in self:
           res=rec.medical_insurance_id.insurance_ids.filtered(lambda line:line.job_level_id.id==rec.job_level_id.id)
           rec.package_name_ids=[(4, id) for id in self.medical_insurance_id.insurance_ids.mapped('package_name_id.id')]
           if res:
               rec.package_name_id=res[0].package_name_id.id
               rec.medical_package=res[0].amount
           else:
               rec.package_name_id=False
               rec.medical_package=0

