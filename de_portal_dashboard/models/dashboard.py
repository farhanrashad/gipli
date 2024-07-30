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

    view_type = fields.Selection([
        ('list', 'List'),
        ('graph', 'Graph')
    ], string='View Type', required=True, default='list')

    field_ids = fields.Many2many(
        'ir.model.fields', 
        'base_dashboard_item_field_rel', 
        'item_id', 
        'field_id', 
        string='Fields',
        domain="[('model_id', '=', model_id)]"
    )
    
    detail_field_ids = fields.Many2many(
        'ir.model.fields', 
        'base_dashboard_item_detail_field_rel', 
        'item_id', 
        'field_id', 
        string='Detail Page Fields',
        domain="[('model_id', '=', model_id)]"
    )
    
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

    dash_item_line = fields.One2many('base.dashboard.item.line', 'dash_item_id', string='Item Lines', copy=True, auto_join=True)


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

class ItemLine(models.Model):
    _name = 'base.dashboard.item.line'
    _description = 'Dashboard Item Line'
    _order = 'id'
    
    dash_item_id = fields.Many2one('base.dashboard.item', string='Dashboard Item', readonly=True,)
    header_model_id = fields.Many2one('ir.model', related='dash_item_id.model_id')

    relational_field_id = fields.Many2one('ir.model.fields', string='Relational Field', ondelete="cascade", required=True)

    line_model_id = fields.Many2one('ir.model', ondelete='cascade', string='Model', store=True, compute='_compute_model_from_relational_field')
    
    field_ids = fields.Many2many(
        'ir.model.fields', 
        string='Fields',
        domain="[('model_id', '=', line_model_id)]"
    )

    dash_item_line = fields.One2many('base.dashboard.item.line', 'dash_item_id', string='Item Lines', copy=True, auto_join=True)


    @api.depends('relational_field_id')
    def _compute_model_from_relational_field(self):
        model_id = self.env['ir.model']
        field_id = self.env['ir.model.fields']
        for line in self:
            model_id = self.env['ir.model'].search([('model','=',line.relational_field_id.relation)],limit=1)
            field_id = self.env['ir.model.fields'].sudo().search([('model_id','=',model_id.id),('relation','=',line.header_model_id.model)],limit=1)
            line.line_model_id = model_id.id
            #line.parent_relational_field_id = field_id.id


class ItemLine(models.Model):
    _name = 'base.dashboard.item.line'
    _description = 'Dashboard Item Line'
    _order = 'id'
    
    dash_item_id = fields.Many2one('base.dashboard.item', string='Dashboard Item', readonly=True,)
    header_model_id = fields.Many2one('ir.model', related='dash_item_id.model_id')

    relational_field_id = fields.Many2one('ir.model.fields', string='Relational Field', ondelete="cascade", required=True)

    line_model_id = fields.Many2one('ir.model', ondelete='cascade', string='Model', store=True, compute='_compute_model_from_relational_field')
    parent_relational_field_id = fields.Many2one('ir.model.fields', string='Parent Relational', ondelete="cascade", store=True, compute='_compute_model_from_relational_field')
    
    field_ids = fields.Many2many(
        'ir.model.fields', 
        string='Fields',
        domain="[('model_id', '=', line_model_id)]"
    )

    @api.depends('relational_field_id')
    def _compute_model_from_relational_field(self):
        model_id = self.env['ir.model']
        field_id = self.env['ir.model.fields']
        for line in self:
            model_id = self.env['ir.model'].search([('model','=',line.relational_field_id.relation)],limit=1)
            field_id = self.env['ir.model.fields'].sudo().search([('model_id','=',model_id.id),('relation','=',line.header_model_id.model)],limit=1)
            line.line_model_id = model_id.id
            line.parent_relational_field_id = field_id.id
