# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
from random import randint
    
class VoteSign(models.Model):
    _name = 'vote.sign'
    _description = 'Sign'
    _inherit = ['format.address.mixin', 'avatar.mixin']
    _order = 'name'
    
    def _default_color(self):
        return randint(1, 11)
    
    name = fields.Char(string='Location', required=True, index=True, translate=True) 
    code = fields.Char(string='Code', required=True, size=10)
    active = fields.Boolean('Active', default=True)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)

    color = fields.Integer(default=_default_color)
    