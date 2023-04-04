# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import requests
import json
from datetime import datetime,date,time
from odoo.http import request
import pytz
import base64



class ClickupConfig(models.Model):
    _name = 'clickup.config'
    _description = 'Clickup Configuration'
    
    
#     def _get_default_image(self):
#         image_path = modules.get_module_resource('de_clickup_connector', 'static/src/img', 'clickup.png')
#         return tools.image_resize_image_big(base64.b64encode(open(image_path, 'rb').read()))
    def _get_default_id(self):
        id = None
        
        clickup_workspace = self.env['clickup.workspace'].search([], order='id asc', limit=1)
        if clickup_workspace:
            id = clickup_workspace.id
            
        return id
    
    
    name = fields.Char(string='Name', required=True)
    image_1920 = fields.Binary('Image')
    state = fields.Selection([('draft','Draft'),('confirm','Confirm')], default='draft')
    client_id = fields.Char(string='Client ID')
    client_secret = fields.Char(string="Client Secret")
    code = fields.Char(string="Code")
    token = fields.Char(string="Token")
    redirect_url = fields.Char(string="Redirect URL")
    workspace_id = fields.Many2one('clickup.workspace', string="Workspace/Team", default=_get_default_id)
    active = fields.Boolean('Active', default=True)
    
    webhook_end_point = fields.Char(string="End Point")
    webhook_status = fields.Char(string="Health Status")
    webhook_clickup_id = fields.Char(string='Webhook ID')
    
    
    def action_validate(self):
        self.state = 'confirm'
    
    
    @api.model
    def create(self, vals):
        exists = self.search([])
        
        if exists:
            raise UserError(('Clickup Configuration Already Exists!'))
        else:
            pass
           
        rec = super(ClickupConfig, self).create(vals)
        return rec
    
    
    def refresh_clickup_code_token(self):
        print('--login code--')
        print('request.httprequest.url',request.httprequest.url)
        print('request.httprequest.base_url',request.httprequest.base_url)
        print('request.httprequest.host_url',request.httprequest.host_url)

        redirect_url = 'https://app.clickup.com/api?client_id='+str(self.client_id)+'&redirect_uri='+str(self.redirect_url)
        return{
            'type':'ir.actions.act_url',
            'target':'new',
            'url':redirect_url,
            }
        
        
    def generate_token(self):
        if not self.code:
            raise UserError('Code not found! \nRefresh Clickup Code!')
        
        url = "https://api.clickup.com/api/v2/oauth/token?client_id="+str(self.client_id)+"&client_secret="+str(self.client_secret)+"&code="+str(self.code)
        payload={}
        headers = {}
        
        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        print(response)

        if response.get('access_token'):
            self.update({'token': response.get('access_token')})
        
        if response.get('ECODE') and response.get('ECODE') == 'OAUTH_014':
            raise UserError('Code already used! \nRefresh Clickup Code!')
                

    def get_clickup_workspaces(self):
        """clickup workspace = to api teams"""
        url = "https://api.clickup.com/api/v2/team"
        
        payload={}
        headers = {
          'Authorization': self.token
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        response = response.json()
        print(response)
        
        ClickupWorkspace = self.env['clickup.workspace']
        if 'teams' in response:
            for team in response.get('teams'):
                if 'id' and 'name' in team:
                    record_exsits = ClickupWorkspace.search([('clickup_id','=',int(team.get('id')))])
                    
                    if not record_exsits:
                        ClickupWorkspace.create({
                            'clickup_id': int(team.get('id')),
                            'name': team.get('name')
                            })
                    else:
                        record_exsits.update({
                            'name': team.get('name')
                            })
    
    
    
    def get_clickup_space_ids(self):
        clickup_project_ids = []
        project_ids = self.env['project.project'].search([('clickup_id','!=', False)])
        
        for project_id in project_ids:
            clickup_project_ids.append(project_id.clickup_id)
        return clickup_project_ids
    
    
    def get_clickup_folders(self):
        """clickup folders api"""
        clickup_project_ids = self.get_clickup_space_ids()
        ProjectProject = self.env['project.project']
        ClickupFolder = self.env['clickup.folder']
        
        print(clickup_project_ids)
        
        if clickup_project_ids != []:
            for clickup_project_id in clickup_project_ids:
                url = "https://api.clickup.com/api/v2/space/"+str(clickup_project_id)+"/folder"
                
                payload={}
                headers = {
                  'Authorization': self.token
                }
                
                response = requests.request("GET", url, headers=headers, data=payload)
                response = response.json()
                
                if response.get('folders') != []:
                    for folder in response.get('folders'):
                        print(folder)
                        record_exsits = ClickupFolder.search([('clickup_id','=',int(folder.get('id')))], order='id desc', limit=1)
                        project_id = ProjectProject.search([('clickup_id','=',folder.get('space').get('id'))], order="id desc", limit=1) 

                        
                        if not record_exsits:
                            ClickupFolder.create({
                                'clickup_id': int(folder.get('id')),
                                'name': folder.get('name'),
                                'clickup_team_id': folder.get('space').get('id'),
                                'project_id': project_id.id
                                })
                        else:
                            record_exsits.update({
                                'name': folder.get('name')
                                })
    
        
    
    def get_clickup_lists(self):
        """Lists from folders"""
        ProjectProject = self.env['project.project']
        ClickupFolder = self.env['clickup.folder']
        ClickupList = self.env['clickup.list']
        
        folders = ClickupFolder.search([])
        if folders:
            for folder in folders:
                url = "https://api.clickup.com/api/v2/folder/"+str(folder.clickup_id)+"/list"
                
                payload={}
                headers = {
                  'Authorization': self.token
                }
                response = requests.request("GET", url, headers=headers, data=payload)
                response = response.json()
                print(response)
                
                if 'lists' in response:
                    for list in response.get('lists'):
                        print(list)
                        record_exsits = ClickupList.search([('clickup_id','=',int(list.get('id')))], order='id desc', limit=1)
                        project_folder_id = ClickupFolder.search([('clickup_id','=',list.get('folder').get('id'))], order="id desc", limit=1) 
                        project_id = ProjectProject.search([('clickup_id','=',list.get('space').get('id'))], order="id desc", limit=1) 
                        
                        
                        if not record_exsits:
                            ClickupList.create({
                                'clickup_id': int(list.get('id')),
                                'name': list.get('name'),
                                'clickup_folder_id': list.get('space').get('id'),
                                'project_folder_id': project_folder_id.id,
                                'project_id': project_id.id
                                })
                        else:
                            record_exsits.update({
                                'name': list.get('name')
                                }) 
        
        
        """folderless lists"""   
        clickup_project_ids = self.get_clickup_space_ids()
        print(clickup_project_ids)
        
        if clickup_project_ids != []:
            for project_id in clickup_project_ids:
                url = "https://api.clickup.com/api/v2/space/"+str(project_id)+"/list"
                
                payload={}
                headers = {
                  'Authorization': self.token
                }
                response = requests.request("GET", url, headers=headers, data=payload)
                response = response.json()
                print(response)
                
                if 'lists' in response:
                    for list in response.get('lists'):
                        print(list)
                        record_exsits = ClickupList.search([('clickup_id','=',int(list.get('id')))], order='id desc', limit=1)
                        project_folder_id = ClickupFolder.search([('clickup_id','=',list.get('folder').get('id'))], order="id desc", limit=1) 
                        project_id = ProjectProject.search([('clickup_id','=',list.get('space').get('id'))], order="id desc", limit=1) 
                        
                        
                        if not record_exsits:
                            ClickupList.create({
                                'clickup_id': int(list.get('id')),
                                'name': list.get('name'),
                                'clickup_folder_id': list.get('space').get('id'),
                                'project_folder_id': project_folder_id.id,
                                'project_id': project_id.id
                                })
                        else:
                            record_exsits.update({
                                'name': list.get('name')
                                }) 
                        
            

    def link_project_with_status(self, project_id, status_ids):
        status_ids = self.env['project.task.type'].browse(status_ids)
        print('status_ids--',status_ids)
        project_id = project_id.id
        
        for status_id in status_ids:
            project_ids = status_id.project_ids.ids
            print('link proj status--',project_ids)
            print('project_id--',project_id)
            
            if project_id not in project_ids:
                status_id.project_ids = [(4, project_id)]
                            
    
    
    def verify_clickup_team(self):
        """just to check if team/ workspace is selected in configuration!"""
        team_id = self.workspace_id.clickup_id
        
        if not team_id:
            raise UserError('Please select Workspace/Team!')
        
        return team_id
        
    
    def _get_space(self, space):
        team_id = self.verify_clickup_team()
        ProjectProject = self.env['project.project']
        ProjectTaskType = self.env['project.task.type']
        
        """status management"""
        status_ids = []
        for status in space.get('statuses'):
            print(status.get('status'))
            status_name = status.get('status').lower()
 
            sql = """ select id as id from project_task_type where lower(name)='""" +str(status_name)+"""' """
            self.env.cr.execute(sql)
            record_exsits = self.env.cr.dictfetchall()
                
                
            if not record_exsits:
                task_type_id = ProjectTaskType.create({
                    'name': status_name
                    })
                status_ids.append(task_type_id.id)
            else:
                status_ids.append(record_exsits[0].get('id'))
        print('status_ids-',status_ids) 
        """status management"""       
                
        
        project_instance = None    
        if 'id' and 'name' in space:
            record_exsits = ProjectProject.search([('clickup_id','=',int(space.get('id')))])
            
            if not record_exsits:
                project_instance = ProjectProject.create({
                    'clickup_id': int(space.get('id')),
                    'clickup_team_id': team_id,
                    'name': space.get('name')
                    })
            else:
                record_exsits.update({
                    'name': space.get('name'),
                    'clickup_team_id': team_id,
                    })
                project_instance = record_exsits
            
            
            print('project_instance---',project_instance)
            self.link_project_with_status(project_instance, status_ids)
                        
                                
    
    def get_clickup_space_projects(self):
        team_id = self.verify_clickup_team()
        
        url = "https://api.clickup.com/api/v2/team/"+str(team_id)+"/space?archived=false"
        
        payload={}
        headers = {
          'Authorization': self.token
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        response = response.json()
        print(response)
        
        
#         ProjectProject = self.env['project.project']
#         ProjectTaskType = self.env['project.task.type']
        
        if 'spaces' in response:
            for space in response.get('spaces'):
                self._get_space(space)
                
#                 """status management"""
#                 status_ids = []
#                 for status in space.get('statuses'):
#                     print(status.get('status'))
#                     status_name = status.get('status').lower()
#          
#                     sql = """ select id as id from project_task_type where lower(name)='""" +str(status_name)+"""' """
#                     self.env.cr.execute(sql)
#                     record_exsits = self.env.cr.dictfetchall()
#                         
#                         
#                     if not record_exsits:
#                         task_type_id = ProjectTaskType.create({
#                             'name': status_name
#                             })
#                         status_ids.append(task_type_id.id)
#                     else:
#                         status_ids.append(record_exsits[0].get('id'))
#                 print('status_ids-',status_ids) 
#                 """status management"""       
#                         
#                 
#                 project_instance = None    
#                 if 'id' and 'name' in space:
#                     record_exsits = ProjectProject.search([('clickup_id','=',int(space.get('id')))])
#                     
#                     if not record_exsits:
#                         project_instance = ProjectProject.create({
#                             'clickup_id': int(space.get('id')),
#                             'clickup_team_id': team_id,
#                             'name': space.get('name')
#                             })
#                     else:
#                         record_exsits.update({
#                             'name': space.get('name'),
#                             'clickup_team_id': team_id,
#                             })
#                         project_instance = record_exsits
#                     
#                     
#                     print('project_instance---',project_instance)
#                     self.link_project_with_status(project_instance, status_ids)



    def synch_project_tags(self):
        self.push_project_tags_to_clickup()
        self.pull_project_tags_from_clickup()

    
    
    def push_project_tags_to_clickup(self):
        project_tag_ids = self.env['project.tags'].search([])
        
        if project_tag_ids:
            clickup_project_ids = self.get_clickup_space_ids()
            
            if clickup_project_ids != []:
                for clickup_project_id in clickup_project_ids:
                    for tag_id in project_tag_ids:
                        url = "https://api.clickup.com/api/v2/space/"+str(clickup_project_id)+"/tag"
                        
                        payload = json.dumps({
                          "tag": {
                            "name": tag_id.clickup_tag_name,
                            "tag_fg": "#000000",
                            "tag_bg": "#000000"
                          }
                        })

                        headers = {
                          'Authorization': self.token,
                          'Content-Type': 'application/json'
                        }
                        
                        response = requests.request("POST", url, headers=headers, data=payload)
                        response = response.json()
                        print(response)
    
    
    
    def pull_project_tags_from_clickup(self):
        tags_list = []
        ProjectTags = self.env['project.tags']
        clickup_project_ids = self.get_clickup_space_ids()
        print(clickup_project_ids)
        
        if clickup_project_ids != []:
            for project_id in clickup_project_ids:
                url = "https://api.clickup.com/api/v2/space/"+str(project_id)+"/tag"
                
                payload={}
                headers = {
                  'Authorization': self.token,
                  'Content-Type': 'application/json'
                }
                response = requests.request("GET", url, headers=headers, data=payload)
                response = response.json()
                print(response)
                
                if response.get('tags') != []:
                    for tag in response.get('tags'):
                        tags_list.append(tag.get('name'))
            print(tags_list)
            for tag in set(tags_list):
                tag_name = tag.strip().lower()
         
                sql = """ select lower(clickup_tag_name) from project_tags where lower(clickup_tag_name)='""" +str(tag_name)+"""' """
                self.env.cr.execute(sql)
                record_exsits = self.env.cr.fetchone()
                
                    
                if not record_exsits:
                    ProjectTags.create({
                        'name': tag.title(),
                        'clickup_tag_name': tag
                        })
                    
                    
    
    def _create_task(self, task, team_id):
        """(task parameter: is from click api task json)"""
        
        ProjectTask = self.env['project.task']
        ProjectProject = self.env['project.project']
        ClickupList = self.env['clickup.list']
        ProjectTags = self.env['project.tags']
        
        
        if 'id' and 'name' in task:
            record_exsits = ProjectTask.search([('clickup_id','=',task.get('id'))])
            
            list_id = None
            list = task.get('list')
            if 'id' in list:
                list_id = list.get('id') 
                list_id = ClickupList.search([('clickup_id','=',list_id)], order='id desc', limit=1)
            
            folder_id = None
            folder = task.get('folder')
            if 'id' in folder:
                folder_id = folder.get('id')
                        
            space_id = None
            space = task.get('space')
            if 'id' in space:
                space_id = space.get('id') 
                
            tag_ids = []
            if task.get('tags') != []:
                for tag in task.get('tags'):
                    tag_exists = ProjectTags.search([('clickup_tag_name','=',tag.get('name'))], order='id desc', limit=1)
                    if tag_exists:
                        tag_ids.append(tag_exists.id)
            print(tag_ids)
            
            date_deadline = None
            if task.get('due_date') != None:
                date_deadline = self.posxi_to_date(int(task.get('due_date')))
                        
                
            project_id = ProjectProject.search([('clickup_id','=',space_id)], order="id desc", limit=1) 
            if not record_exsits:
                ProjectTask.create({
                    'clickup_list_id': list_id.id,
                    'clickup_folder_id': folder_id,
                    'clickup_space_id': space_id,
                    'clickup_task_url': task.get('url'),
                    'clickup_team_id': team_id,
                    'name': task.get('name'),
                    'description': task.get('description'),
                    'project_id': project_id.id,
                    'date_deadline': date_deadline,
                    'tag_ids': tag_ids,
                    'clickup_id': task.get('id'),
                    })
            else:
                record_exsits.update({
                    'clickup_list_id': list_id.id,
                    'clickup_folder_id': folder_id,
                    'clickup_space_id': space_id,
                    'clickup_task_url': task.get('url'),
                    'clickup_team_id': team_id,
                    'name': task.get('name'),
                    'description': task.get('description'),
                    'date_deadline': date_deadline,
                    'tag_ids': tag_ids,
                    })
        
        
    
    def get_clickup_task(self, clickup_task_id): 
        team_id = self.verify_clickup_team()
        url = "https://api.clickup.com/api/v2/task/"+str(clickup_task_id)+"/"
        
        payload={}
        headers = {
          'Authorization': self.token,
          'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        response = response.json()
        print(response)
        
        self._create_task(response, team_id)

           
        
        
    def get_clickup_team_tasks(self):
        team_id = self.verify_clickup_team()
        
        url = "https://api.clickup.com/api/v2/team/"+str(team_id)+"/task"
        
        payload={}
        headers = {
          'Content-Type': 'application/json',
          'Authorization': self.token
        }
        
        response = requests.request("GET", url, headers=headers, data=payload)
        response = response.json()
        print(response)
        
        if 'tasks' in response:
            for task in response.get('tasks'):
                self._create_task(task, team_id)

    
    
    def update_task_stage(self, clickup_task_id, status):
        ProjectTaskType = self.env['project.task.type']
        ProjectTask = self.env['project.task']
        new_stage_id = None
        
        
        task_id = ProjectTask.search([('clickup_id','=',clickup_task_id)], order='id desc', limit=1)
        
        if task_id:
            stage_ids = ProjectTaskType.search([('name','=',status)])
            
            for stage_id in stage_ids:
                if task_id.project_id.id in stage_ids.project_ids.ids:
                    new_stage_id = stage_id.id
                    break
            
            task_id.update({'stage_id': new_stage_id})
    
    
    def get_as_base64(self, url):
        return base64.b64encode(requests.get(url).content)
        
        
    def _create_update_attachment(self, task_id, attachment_json):
        print('in attachment methodddd')
        IrAttachment = self.env['ir.attachment']

        for attachment in attachment_json:
            if 'type' in attachment and attachment.get('type') == 'attachment':
                attachment = attachment.get('attachment')
                attachment_id = attachment.get('id')

                attachment_exists = IrAttachment.search([('clickup_id','=',attachment_id)], order='id desc', limit=1)
                if not attachment_exists:
                    url = attachment.get('url')
                    print(url)
                    datas = self.get_as_base64(url)
                    vals = {
                        'name': str(attachment.get('title')),
                        'res_model': 'project.task',
                        'res_id': task_id.id,
                        'type': 'binary',
                        'datas': datas,
                        'clickup_id': attachment_id,
                        'clickup_attachment_url': url,
                        }
                    obj  = IrAttachment.create(vals)

        
    
    def _update_task(self, clickup_task_id, field_name, field_val, attachments):
        task_id = self.env['project.task'].search([('clickup_id','=',clickup_task_id)], order='id desc', limit=1)
        
        if task_id:
            if field_name == 'name':
                task_id.update({'name': field_val})
            if field_name == 'content':
                task_id.update({'description': field_val})
            if attachments != False:
                self._create_update_attachment(task_id, attachments)    
            
                
    
    
    def _update_task_tag(self, clickup_task_id, before, after):
        ProjectTags = self.env['project.tags']
        task_id = self.env['project.task'].search([('clickup_id','=',clickup_task_id)], order='id desc', limit=1)

        
        if after != None:
            print(after)
            tag_name = after[0].get('name')
            tag_id = ProjectTags.search([('clickup_tag_name','=',tag_name)], order='id desc', limit=1)
            
            if tag_id:
                task_id.tag_ids = [(4, tag_id.id)]
                
            
        if before != None:
            print(before)
            tag_name = before[0].get('name')
            tag_id = ProjectTags.search([('clickup_tag_name','=',tag_name)], order='id desc', limit=1)
            
            if tag_id:
                task_id.tag_ids = [(2, tag_id.id)]    
            
            
            
    
    def _delete_task(self, clickup_task_id):
        task_id = self.env['project.task'].search([('clickup_id','=',clickup_task_id)], order='id desc', limit=1)
        
        if task_id:
            task_id.unlink()
            
    
    def update_task_due_date(self, clickup_task_id, due_date):
        task_id = self.env['project.task'].search([('clickup_id','=',clickup_task_id)], order='id desc', limit=1)
        
        if task_id:
            if due_date == None:
                task_id.update({'date_deadline': None})
            else:
                task_id.update({'date_deadline': self.posxi_to_date(int(due_date))})
                    
                    
    
    def post_task_comment(self, clickup_task_id, clickup_comment_id, comment_text, comment_user_name, comment_user_email):
        print('in config post task commm--------')
        task_id = self.env['project.task'].search([('clickup_id','=',clickup_task_id)], order='id desc', limit=1)
        
        if task_id:
            print(comment_text)
            task_id._create_mail_message(clickup_comment_id, comment_text, comment_user_name, comment_user_email)
    
    
    
    def _create_list(self, list_name, clickup_list_id, clickup_folder_id, clickup_space_id):
        ClickupList = self.env['clickup.list']
        record_exsits = ClickupList.search([('clickup_id','=',clickup_list_id)], order='id desc', limit=1)
        
        if not record_exsits:
            project_id = self.env['project.project'].search([('clickup_id','=',clickup_space_id)], order="id desc", limit=1) 
            project_folder_id = self.env['clickup.folder'].search([('clickup_id','=',clickup_folder_id)], order="id desc", limit=1) 
            
            if not project_folder_id:
                project_folder_id = None
            else:
                project_folder_id = project_folder_id.id
                
            ClickupList.create({
                'clickup_id': int(clickup_list_id),
                'name': list_name,
                'clickup_folder_id': clickup_folder_id,
                'project_folder_id': project_folder_id,
                'project_id': project_id.id
                })
        else:
            record_exsits.update({
                'name': list_name
                }) 
    
        
    
    def _get_folder(self, clickup_folder_id):
        ClickupFolder = self.env['clickup.folder']
        ProjectProject = self.env['project.project']
        url = "https://api.clickup.com/api/v2/folder/"+str(clickup_folder_id)
        
        payload={}
        headers = {
          'Authorization': self.token
        }
        
        response = requests.request("GET", url, headers=headers, data=payload)
        response = response.json()
        print(response)
        
        if 'id' and 'name' in response:
            clickup_list_name = response.get('lists')[0].get('name')
            clickup_list_id = response.get('lists')[0].get('id')
            clickup_folder_id = int(response.get('id'))
            clickup_space_id = response.get('space').get('id')
            
            record_exsits = ClickupFolder.search([('clickup_id','=',clickup_folder_id)], order='id desc', limit=1)
            project_id = ProjectProject.search([('clickup_id','=',clickup_space_id)], order="id desc", limit=1) 
            
            if not record_exsits:
                ClickupFolder.create({
                    'clickup_id': clickup_folder_id,
                    'name': response.get('name'),
                    'clickup_team_id': response.get('space').get('id'),
                    'project_id': project_id.id
                    })
            else:
                record_exsits.update({
                    'name': response.get('name')
                    })
                
            self._create_list(clickup_list_name, clickup_list_id, clickup_folder_id, clickup_space_id)
        
        
        
    def _delete_folder(self, clickup_folder_id):
        folder_id = self.env['clickup.folder'].search([('clickup_id','=',clickup_folder_id)], order='id desc', limit=1)
        
        if folder_id:
            folder_id.unlink()
        
                
    def _get_list(self, clickup_list_id):
        url = "https://api.clickup.com/api/v2/list/"+str(clickup_list_id)
        
        payload={}
        headers = {
          'Authorization': self.token
        }
        
        response = requests.request("GET", url, headers=headers, data=payload)
        response = response.json()
        print(response)
        
        clickup_list_name = response.get('name')
        clickup_list_id = response.get('id')
        clickup_folder_id = response.get('folder').get('id')
        clickup_space_id = response.get('space').get('id')
        self._create_list(clickup_list_name, clickup_list_id, clickup_folder_id, clickup_space_id)

    
    
    def _delete_list(self, clickup_list_id):
        list_id = self.env['clickup.list'].search([('clickup_id','=',clickup_list_id)], order='id desc', limit=1)
        
        if list_id:
            list_id.unlink() 
            
    
    
    def _get_clickup_space(self, clickup_space_id):  
        url = "https://api.clickup.com/api/v2/space/"+str(clickup_space_id)
        
        payload={}
        headers = {
          'Authorization': self.token
        }
        
        response = requests.request("GET", url, headers=headers, data=payload)
        response = response.json()
        print(response)
        self._get_space(response)


    
    def _delete_space(self, clickup_space_id):
        project_id = self.env['project.project'].search([('clickup_id','=',clickup_space_id)], order='id desc', limit=1)
        
        if project_id:
            task_ids = self.env['project.task'].search([('project_id','=',project_id.id)])
            
            for task_id in task_ids:
                task_id.unlink()
            project_id.unlink()
        
        

    def posxi_to_date(self, posxi): 
        dt = datetime.fromtimestamp(posxi/1000).strftime('%Y-%m-%d %H:%M:%S')
        dt = datetime.strptime(str(dt), '%Y-%m-%d %H:%M:%S').astimezone(pytz.timezone('Asia/Karachi'))
        print(dt) 
        return dt                  
    

    
    def get_task_comments(self):
        ProjectTask = self.env['project.task']
        
        task_ids = ProjectTask.search([('clickup_id','!=',False)])
        if task_ids:
            for task_id in task_ids:
                task_id.pull_task_comments()
                
    
    
    def push_task_comments(self):
        ProjectTask = self.env['project.task']
        
        task_ids = ProjectTask.search([('clickup_id','!=',False)])
        if task_ids:
            for task_id in task_ids:
                task_id.push_task_comments()
                
    
    
    def import_webhooks(self):
        ClickupWebhook = self.env['clickup.webhook']
        ClickupWorkspace = self.env['clickup.workspace']
        team_id = self.verify_clickup_team()
        
        url = "https://api.clickup.com/api/v2/team/"+str(team_id)+"/webhook"
        
        payload={}
        headers = {
          'Authorization': self.token
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        response = response.json()
        print(response)
        
        if response.get('webhooks') != []:
            for webhook in response.get('webhooks'):
                record_exsits = ClickupWebhook.search([('clickup_id','=',webhook.get('id'))])
                team_id = ClickupWorkspace.search([('clickup_id','=',webhook.get('team_id'))], order='id desc', limit=1)
                       
                if not record_exsits:
                    ClickupWebhook.create({
                        'clickup_id': webhook.get('id'),
                        'team_id': team_id.id,
                        'end_point': webhook.get('endpoint'),
                        'status': webhook.get('health').get('status'),
                        })
                else:
                    record_exsits.update({
                        'clickup_id': webhook.get('id'),
                        'team_id': team_id.id,
                        'end_point': webhook.get('endpoint'),
                        'status': webhook.get('health').get('status'),
                        })
                    



    
    def create_webhook(self):
        ClickupWorkspace = self.env['clickup.workspace']
        ClickupWebhook = self.env['clickup.webhook']
        record_exists = ClickupWebhook.search([])

        if not record_exists:
            team_id = self.verify_clickup_team()
            url = "https://api.clickup.com/api/v2/team/"+str(team_id)+"/webhook"
            
            payload = json.dumps({
#             "endpoint": "http://faf9-111-119-178-149.ngrok.io/webhook",
            "endpoint": self.redirect_url +"/webhook",
              "events": [
                "taskCreated",
                "taskUpdated",
                "taskDeleted",
                "taskPriorityUpdated",
                "taskStatusUpdated",
                "taskAssigneeUpdated",
                "taskDueDateUpdated",
                "taskTagUpdated",
                "taskMoved",
                "taskCommentPosted",
                "taskCommentUpdated",
                "taskTimeEstimateUpdated",
                "taskTimeTrackedUpdated",
                "listCreated",
                "listUpdated",
                "listDeleted",
                "folderCreated",
                "folderUpdated",
                "folderDeleted",
                "spaceCreated",
                "spaceUpdated",
                "spaceDeleted",
                "goalCreated",
                "goalUpdated",
                "goalDeleted",
                "keyResultCreated",
                "keyResultUpdated",
                "keyResultDeleted"
              ]
            })
            headers = {
              'Authorization': self.token,
              'Content-Type': 'application/json'
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            response = response.json()
            print(response)
            
            
            if 'id' in response:
                webhook = response.get('webhook')
                api_team_id = webhook.get('team_id')
                end_point = webhook.get('endpoint')
                status = webhook.get('health').get('status')
                team_id = ClickupWorkspace.search([('clickup_id','=',api_team_id)], order='id desc', limit=1)

                ClickupWebhook.create({
                    'clickup_id': response.get('id'),
                    'team_id': team_id.id,
                    'end_point': end_point,
                    'status': status,
                    })

        
        
