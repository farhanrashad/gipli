# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, AccessError

    

class FieldVariant(models.Model):
    _name = 'hr.service.field.variant'
    _description = 'Service Field Variant'
    _order = 'id'
    _rec_name = 'name'
    
    name = fields.Char(string='Name', required=True)
    field_variant_line_ids = fields.One2many('hr.service.field.variant.line', 'field_variant_id', string='Service Items')
    

    
class FieldVariantLine(models.Model):
    _name = 'hr.service.field.variant.line'
    _description = 'Service Field Variant Line'
    _order = 'id'
        
    field_variant_id = fields.Many2one(string='Field Variant',comodel_name='hr.service.field.variant')
    name = fields.Char(string='Name', required=True)
    description = fields.Char(string='Description')
    # display_column = fields.Char(string='Display Columns')
    
    display_column = fields.Selection(
        string='Display Columns', required=True,
        selection=[('col_6', '6 Col'), ('col_12', '12 Col')]
    )
    
    


  

   