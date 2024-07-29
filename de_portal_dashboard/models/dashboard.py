# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class BaseDashboardItem(models.Model):
    _name = 'base.dashboard.item'
    _description = 'Dashboard Item'
    _order = 'id'

    name = fields.Char(string='Name', required=True, translate=True)
    model_id = fields.Many2one('ir.model', ondelete='cascade', string='Model', required=True)
    field_ids = fields.Many2many(
        'ir.model.fields', 
        string='Fields',
        domain="[('model_id', '=', model_id), ('ttype', 'in', ['integer', 'float', 'monetary'])]"
    )
    view_type = fields.Selection([
        ('list', 'List'),
        ('graph', 'Graph')
    ], string='View Type', required=True, default='list')
    graph_label_field_id = fields.Many2one(
        'ir.model.fields', 
        string='Label Field',
        domain="[('model_id', '=', model_id), ('ttype', 'in', ['char', 'selection'])]"
    )
    graph_data_field_id = fields.Many2one(
        'ir.model.fields', 
        string='Data Field',
        domain="[('model_id', '=', model_id), ('ttype', 'in', ['integer', 'float', 'monetary'])]"
    )
