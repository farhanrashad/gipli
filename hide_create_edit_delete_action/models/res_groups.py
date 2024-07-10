# -*- coding: utf-8 -*-
from odoo import models, fields
from lxml import etree

class ResUsers(models.Model):
    
    _inherit = 'res.groups'
    
    hide_create_objects = fields.Many2many('ir.model',string="Objects",relation="model_creates")
    hide_edit_objects = fields.Many2many('ir.model',string="Objects",relation="model_edits")
    hide_delete_objects = fields.Many2many('ir.model',string="Objects",relation="model_delete")
