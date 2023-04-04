# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import requests
import json
from datetime import datetime,date
from odoo.http import request



class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    
    def get_clickup_config(self):
        clickup_conf = self.env['clickup.config'].search([], order="id desc", limit=1)
        if not clickup_conf:
            raise UserError('Clickup is not configured!')
            
            
        team_id = clickup_conf.workspace_id.clickup_id
        if not team_id:
            raise UserError('Please select Workspace/Team!')
        
        return clickup_conf
    
    
    def export_task_attachment_to_clickup(self):
        clickup_conf = self.get_clickup_config()
        ProjectTask = self.env['project.task']
        attachment_ids = self.search([('clickup_id','=',False),('id','in',self.ids),('res_model','=','project.task')])
        
        for attachment_id in attachment_ids:
            task_id = ProjectTask.browse(attachment_id.res_id)
            
            if task_id.clickup_id:
                url = "https://api.clickup.com/api/v2/task/"+str(task_id.clickup_id)+"/attachment"
                print('111111111')
                payload={}
                
#                 decode_data = attachment_id.datas.decode('image/png')
                decode_data = attachment_id.datas.decode('utf-8')
                decode_file = f"data:{attachment_id.mimetype};base64," + decode_data
#                 values = """
#                     attachment: raw_image_file (file)
#                     filename: example.png (string)"""
                file = '/clickup.png'
                files=[
#                     ('attachment',(open(file, 'rb'),'abc'))
                ('attachment',(str(attachment_id.name),open(file,'rb'),'image/png'))
                ]
                headers = {
                  'Authorization': clickup_conf.token,
                  'Content-Type': 'multipart/form-data'
                }
                response = requests.request("POST", url, headers=headers, data=payload, files=files)
                print('444444444444')
                print(response.json())

            
        
        
    clickup_attachment_url = fields.Char(string='Attachment URL', copy=False)
    clickup_id = fields.Char(string='Clickup ID', copy=False)
    
    _sql_constraints = [
    ('clickup_id_uniq', 'unique (clickup_id)', "Clickup ID already exists!"),
    ]        