# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import requests
import json
from datetime import datetime,date
from odoo.http import request



class MailMessage(models.Model):
    _inherit = 'mail.message'
    
    
    
    clickup_id = fields.Integer(string='Clickup ID')
    
    _sql_constraints = [
    ('clickup_id_uniq', 'unique (clickup_id)', "Clickup ID already exists!"),
    ]               