# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError

class HunterResults(models.Model):
    _name = 'hunter.results'
    _description = 'Hunter Search Results'

    name = fields.Char(string='Name')
    email = fields.Char(string='email')
    position = fields.Char(string='Position', readonly=True)
    department = fields.Char(string='Department', readonly=True)
    phone = fields.Char(string='Phone', readonly=True)

    lead_id = fields.Many2one('crm.lead', string="Lead")
    partner_id = fields.Many2one('res.partner', string="Partner")