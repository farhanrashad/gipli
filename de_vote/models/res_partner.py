# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
import logging

from psycopg2 import sql, DatabaseError

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import ValidationError, UserError
from odoo.addons.base.models.res_partner import WARNING_MESSAGE, WARNING_HELP

class ResPartner(models.Model):
    _inherit = 'res.partner'
 
    is_member = fields.Boolean('Is Member')
    is_pol_party = fields.Boolean('Is Political Party')
    
    vote_sign_id = fields.Many2one('vote.sign', string='Sign')
    vote_sign_image = fields.Binary('vote_sign_id.image_1920')
    
    # Demographic Info
    date_birth = fields.Date(string='Date of Birth')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], string='Gender')
    merital_status = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('widowed', 'Widowed'),
        ('separated', 'Separated'),
        ('divorced', 'Divorced'),
        ('other', 'Other'),
    ], string='Merital Status')
    country_birth = fields.Many2one('res.country','Country of Birth')
    country_nationality = fields.Many2one('res.country','Nationality')