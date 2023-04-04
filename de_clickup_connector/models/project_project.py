# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import requests
import json
from datetime import datetime,date
from odoo.http import request



class ProjectProject(models.Model):
    _inherit = 'project.project'
    
    
    def get_clickup_config(self):
        clickup_conf = self.env['clickup.config'].search([], order="id desc", limit=1)
        if not clickup_conf:
            raise UserError('Clickup is not configured!')
            
            
        team_id = clickup_conf.workspace_id.clickup_id
        if not team_id:
            raise UserError('Please select Workspace/Team!')
        
        return clickup_conf
    
    
    
    def export_project_to_clickup(self):
        project_ids = self.search([('clickup_id','=',False),('id','in',self.ids)])
        
        if project_ids:
            clickup_conf = self.get_clickup_config()
            
            for project_id in project_ids:
                url = "https://api.clickup.com/api/v2/team/"+str(team_id)+"/space"
                
                payload = json.dumps({
                  "name": project_id.name,
                  "multiple_assignees": True,
                  "features": {
                    "due_dates": {
                      "enabled": True,
                      "start_date": False,
                      "remap_due_dates": True,
                      "remap_closed_due_date": False
                    },
                    "time_tracking": {
                      "enabled": False
                    },
                    "tags": {
                      "enabled": True
                    },
                    "time_estimates": {
                      "enabled": True
                    },
                    "checklists": {
                      "enabled": True
                    },
                    "custom_fields": {
                      "enabled": True
                    },
                    "remap_dependencies": {
                      "enabled": True
                    },
                    "dependency_warning": {
                      "enabled": True
                    },
                    "portfolios": {
                      "enabled": True
                    }
                  }
                })
                headers = {
                  'Authorization': clickup_conf.token,
                  'Content-Type': 'application/json'
                }
                
                response = requests.request("POST", url, headers=headers, data=payload)
                response = response.json()
                print(response)
                
                project_id.update({
                    'clickup_id': response.get('id'),
                    'clickup_team_id': team_id,
                    }) 
                
                
    def unlink(self):
        if self.clickup_id:
            clickup_conf = self.env['clickup.config'].search([], order="id desc", limit=1)
            if not clickup_conf:
                raise UserError('Clickup is not configured!')
            
            url = "https://api.clickup.com/api/v2/space/"+str(self.clickup_id)
            
            payload={}
            headers = {
              'Authorization': clickup_conf.token
            }
            
            response = requests.request("DELETE", url, headers=headers, data=payload)
            print(response.text)

        rec = super(ProjectProject, self).unlink()
        return rec
    
    
    
    
    
    clickup_team_id = fields.Integer(string='Team ID')
    clickup_id = fields.Integer(string='Clickup ID')
    
    _sql_constraints = [
    ('clickup_id_uniq', 'unique (clickup_id)', "Clickup ID already exists!"),
    ]               
                   
