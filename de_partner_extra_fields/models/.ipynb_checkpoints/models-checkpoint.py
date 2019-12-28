# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning


from odoo.addons import decimal_precision as dp

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    ntn = fields.Char(string='NTN', help="The National Tax Number.")
    nic = fields.Char(string='NIC', help="The National Identity Card Number.")