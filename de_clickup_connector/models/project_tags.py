# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import requests
import json
from datetime import datetime,date
from odoo.http import request



class ProjectTags(models.Model):
    _inherit = 'project.tags'

    
    @api.onchange('name')
    def onchange_actual_name(self):
        if self.name:
            self.clickup_tag_name =  str(self.name).lower()
        
        
    clickup_tag_name = fields.Char(string='Clickup Tag Name', help='this field is used by clickup api')
                   
