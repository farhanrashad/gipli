# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class BaseDashboardItem(models.Model):
    _name = 'base.dashboard.item'
    _description = 'Dashboard Item'

    name = fields.Char(string='Name', required=True, translate=True)
    model_id = fields.Many2one('ir.model', ondelete='cascade', string='Model', required=True)
    field_ids = fields.Many2many(
        'ir.model.fields', 
        string='Fields',
        domain="[('model_id', '=', model_id)]"
    )
