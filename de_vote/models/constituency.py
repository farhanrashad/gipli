# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
from random import randint


class ConstituencyType(models.Model):
    _name = 'vote.const.type'
    _description = 'Constituency Type'
    name = fields.Char(string='Type', required=True, index=True, translate=True)
    code = fields.Char(string='Code', required=True)

    
class Constituency(models.Model):
    _name = 'vote.const'
    _description = 'constituency'
    _order = 'name'
    _rec_names_search = ['name', 'code']
    
    def _default_color(self):
        return randint(1, 11)
    
    name = fields.Char(string='Constituency', required=True, index=True, translate=True) 
    code = fields.Char(string='Code', required=True, size=10)
    complete_name = fields.Char('Complete Name', compute='_compute_complete_name', recursive=True, store=True)
    parent_id = fields.Many2one('vote.const', string='Parent Constituency', index=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    active = fields.Boolean('Active', default=True)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)

    color = fields.Integer(default=_default_color)    

    const_type_id = fields.Many2one('vote.const.type', string='Constituency Type', required=True)
    
    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for const in self:
            if const.parent_id:
                const.complete_name = '%s / %s' % (const.parent_id.complete_name, const.name)
            else:
                const.complete_name = const.name
    