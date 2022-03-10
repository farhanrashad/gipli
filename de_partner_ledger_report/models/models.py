# -*- coding: utf-8 -*-

from odoo import models, api, _, _lt, fields
from odoo.tools.misc import format_date
from datetime import timedelta

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    
    parnter_city = fields.Char(string="City")
    parnter_ntn = fields.Char(string="NTN")
    parnter_cnic = fields.Char(string="CNIC")
    partner_detail = fields.Char(string="Partner details",  compute='_compute_partner_detail')
    
    
    @api.depends('parnter_city', 'parnter_ntn','parnter_cnic', 'partner_detail')
    def _compute_partner_detail(self):
        for line in self:
            line.parnter_city = line.move_id.partner_id.city
            line.parnter_ntn = line.move_id.partner_id.ntn
            line.parnter_cnic = line.move_id.partner_id.nic
            line.partner_detail = line.move_id.partner_id.name