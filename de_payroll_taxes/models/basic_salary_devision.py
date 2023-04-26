# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

CATEGORY_SELECTION = [
    ('basic', 'Basic'),
    ('utility', 'Utility'),
    ('rent', 'House rent')]


class BasicSalaryDevision(models.Model):
    _name = 'basic.salary.devision'
    _description='Basic Salary Devision'
    
    name=fields.Char(string='Name')
    percentage = fields.Float(string='Percentage', digits=(12, 4))
    has_category = fields.Selection(CATEGORY_SELECTION, string="Category", default="basic", required=True)

    
    
    
    
    

