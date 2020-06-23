# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError


class de_employee_customization(models.Model):
    _inherit = 'hr.employee'
    
    date_of_joining = fields.Date(string='Date of Joining')
    last_company = fields.Char(string="Company")
    last_department = fields.Char(string="Department")
    source_name = fields.Char(string="Source Name")
    last_salary = fields.Integer(string="Last Salary")
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
    children = fields.Integer(string='Number of Children', groups="hr.group_hr_user", tracking=True,compute='get_number_children')
    languages = fields.Char()
    computer_literacy = fields.Char()
    educations = fields.One2many('employee.education','employee_edu')
    
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
            rec.children = len(rec.dependants)
    

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
    