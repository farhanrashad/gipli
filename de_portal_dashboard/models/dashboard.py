# -*- coding: utf-8 -*-

import base64
import ast
import json
import re


from odoo import models, fields, api, _
from lxml import etree

from odoo.osv import expression

class BaseDashboardItem(models.Model):
    _name = 'base.dashboard.item'
    _description = 'Dashboard Item'
    _order = 'id'

    name = fields.Char(string='Name', required=True, translate=True)
    model_id = fields.Many2one('ir.model', ondelete='cascade', string='Model', required=True)
    model_name = fields.Char(related='model_id.model', string='Model Name')
    filter_domain = fields.Char(string='Domain', help="If present, this domain would apply to filter records.")
    filter_field_id = fields.Many2one('ir.model.fields', string='Filter By ',ondelete="cascade")


    field_ids = fields.Many2many(
        'ir.model.fields', 
        string='Fields',
        domain="[('model_id', '=', model_id)]"
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

    

    def _get_records_filter_by_domain(self,partner_id):
        domain = []
        domain += expression.AND([self._get_user_domain(partner_id), self._get_filter_domain()])
        records = self.env[self.model_id.model].search(domain).ids
        return records

    def _get_user_domain(self,partner_id):
        user_domain = []
        if self.filter_field_id:
            user_domain =  [(self.filter_field_id.name, 'in', [partner_id]),(self.filter_field_id.name, '=', partner_id)]
        return user_domain

    def _get_filter_domain(self):
        filter_domain = []
        if self.filter_domain:
            filter_domain = safe_eval.safe_eval(self.filter_domain)
        return filter_domain
