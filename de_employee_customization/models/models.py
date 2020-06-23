# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError


class de_employee_customization(models.Model):
    _inherit = 'hr.employee'
    
    date_of_joining = fields.Date(string='Date of Joining')
    eobi_number = fields.Integer(string="EOBI Number")
    ref_name = fields.Char(string="Name")
    ref_phone_number = fields.Integer(string="Phone Number")
    ref_relationship = fields.Char(string="Relationship")
    ref_address = fields.Char(string="Address")
    permanent_address = fields.Char(string="Permanent Address")
    temporary_address = fields.Char(string="Temproray Address")
    age = fields.Integer()
    cnic = fields.Integer()
    siblings = fields.Integer()
    religion = fields.Char()
    mother_name = fields.Char(string="Mother's Name")
    father_name = fields.Char(string="Father's Name")
    father_occupation = fields.Char(string="Father's Occupation")
    domicile = fields.Char()
    dependants = fields.One2many('children.data','employee_id')
    children = fields.Integer(string='Number of Children', groups="hr.group_hr_user", tracking=True,compute='get_number_children',inverse='manually_add_dependants',store=True)
    languages = fields.Char()
    computer_literacy = fields.Char()
    educations = fields.One2many('employee.education','employee_edu')
    is_child = fields.Boolean()
    major_responsibilities = fields.One2many('major.responsibilities','employee_major')
    minor_responsibilities = fields.One2many('minor.responsibilities','employee_minor')
    experiences = fields.One2many('employee.expereince','employee_exp',string="Experience")
    
    
    @api.onchange('educations')
    def get_level(self):
        le = []
        for rec in self.educations:
            if rec.level:
                if rec.level in le:
                    rec.level = False
                    raise ValidationError(_("You are not allowed to select same level"))
                le.append(rec.level)
    
    
    @api.depends('dependants')
    def get_number_children(self):
        for rec in self:
            if not rec.children:
                rec.children = False
                rec.children = len(rec.dependants)
    
    def manually_add_dependants(self):
        for rec in self:
            rec.is_child = True

class Children(models.Model):
    _name = 'children.data'
    
    name = fields.Char(required=True)
    age = fields.Integer()
    gender = fields.Selection([('male','Male'),('female','Female')],default='male')
    employee_id =  fields.Many2one('hr.employee')
    
class EmployeeEducation(models.Model):
    _name = 'employee.education'
    
    level = fields.Selection([('middle','Middle'),('matric','Matric'),('fa','FA/FSC/I.COM'),('ba','BA/BSC/B.COM'),('ma','MA/MSC/M.COM'),('other','Other')],required=True)
    major = fields.Char(required=True)
    passed_year = fields.Integer()
    grade = fields.Char(string="Grade/Div")
    employee_edu =  fields.Many2one('hr.employee')
    

class MajorResponsiblities(models.Model):
    _name = 'major.responsibilities'
    
    responsibility = fields.Char(required=True)
    employee_major =  fields.Many2one('hr.employee')
    
class MinorResponsiblities(models.Model):
    _name = 'minor.responsibilities'
    
    responsibility = fields.Char(required=True)
    employee_minor =  fields.Many2one('hr.employee')
    
class EmployeeExperience(models.Model):
    _name = 'employee.expereince'
    
    last_designation = fields.Char(string="Designation")
    last_company = fields.Char(string="Company")
    last_city = fields.Char()
    years_worked = fields.Integer(string="Years Worked")
    date_from = fields.Date(string="From")
    date_to = fields.Date(string="To")
    last_salary = fields.Integer(string="Last Salary")
    employee_exp =  fields.Many2one('hr.employee')