# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning

from odoo.addons import decimal_precision as dp


class AccountMove(models.Model):
    _inherit = 'account.move'
        
    sale_team_id = fields.Many2one('crm.team', string='Product Category', required=True) 
    

