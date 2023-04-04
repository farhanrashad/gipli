# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import requests
import json
from datetime import datetime,date
from odoo.http import request



class ClickupWorkspaces(models.Model):
    _name = 'clickup.workspace'
    _description = 'Clickup Workspace'
    
    
    name = fields.Char(string='Name')
    clickup_id = fields.Integer(string='Clickup ID')
    
    _sql_constraints = [
    ('clickup_id_uniq', 'unique (clickup_id)', "Clickup ID already exists!"),
    ]
    
                    

class ClickupFolder(models.Model):
    _name = 'clickup.folder'
    _description = 'Clickup Folder'
    
    
    name = fields.Char(string='Name')
    clickup_id = fields.Integer(string='Clickup ID')
    clickup_team_id = fields.Integer(string='Clickup Team ID')
    project_id = fields.Many2one('project.project', string='Project')
    
    _sql_constraints = [
    ('clickup_id_uniq', 'unique (clickup_id)', "Clickup ID already exists!"),
    ]                
 
               
    
class ClickupList(models.Model):
    _name = 'clickup.list'
    _description = 'Clickup List'
    
    
    def get_clickup_config(self):
        clickup_conf = self.env['clickup.config'].search([], order="id desc", limit=1)
        if not clickup_conf:
            raise UserError('Clickup is not configured!')
            
            
        team_id = clickup_conf.workspace_id.clickup_id
        if not team_id:
            raise UserError('Please select Workspace/Team!')
        
        return clickup_conf
    
    
#     def export_list_to_clickup(self):
    def push_list_to_clickup(self):
        """folderless list"""
        ClickupFolder = self.env['clickup.folder']
        space_id = self.project_id.clickup_id
        list_name = self.name
        
        url = "https://api.clickup.com/api/v2/space/"+str(space_id)+"/list"
        
        payload = json.dumps({
          "name": list_name
        })
        headers = {
          'Authorization': self.get_clickup_config().token,
          'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        print(response)
        
        if 'id' in response:
            project_folder_id = ClickupFolder.search([('clickup_id','=',response.get('folder').get('id'))], order="id desc", limit=1) 
            
            self.update({
                'clickup_id': int(response.get('id')),
                'clickup_folder_id': response.get('space').get('id'),
                'project_folder_id': project_folder_id.id,
                })

    
    
    name = fields.Char(string='Name')
    clickup_id = fields.Integer(string='Clickup ID')
    clickup_folder_id = fields.Integer(string='Clickup Folder ID')
    project_folder_id = fields.Many2one('clickup.folder', string='Project Folder ID')
    project_id = fields.Many2one('project.project', string='Project')
    
    _sql_constraints = [
    ('clickup_id_uniq', 'unique (clickup_id)', "Clickup ID already exists!"),
    ]