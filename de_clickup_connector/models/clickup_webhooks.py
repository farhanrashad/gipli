# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import requests
import json
from datetime import datetime,date
from odoo.http import request



class ClickupWebhook(models.Model):
    _name = 'clickup.webhook'
    _description = 'Clickup Webhooks'
    _rec_name = 'end_point'

    
    
    def unlink(self):
        for rec in self.browse(self.ids):
            if rec.clickup_id:
                clickup_conf = self.env['clickup.config'].search([], order="id desc", limit=1)
                
                if not clickup_conf:
                    raise UserError('Clickup is not configured!')
                
                
                url = "https://api.clickup.com/api/v2/webhook/"+str(rec.clickup_id)
                payload={}
                headers = {
                  'Authorization': clickup_conf.token
                }
                
                response = requests.request("DELETE", url, headers=headers, data=payload)
                print(response.json())

        rec = super(ClickupWebhook, self).unlink()
        return rec
    
    
    
    team_id = fields.Many2one('clickup.workspace', string="Workspace/Team")
    end_point = fields.Char(string="End Point")
    status = fields.Char(string="Health Status")
    clickup_id = fields.Char(string='Clickup ID')
    
    _sql_constraints = [
    ('clickup_id_uniq', 'unique (clickup_id)', "Clickup ID already exists!"),
    ]
    