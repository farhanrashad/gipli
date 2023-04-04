# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import requests
import json
from datetime import datetime,date
import time
from odoo.http import request
import re



class ProjectTask(models.Model):
    _inherit = 'project.task'
    
    
    def posxi_to_date(self, datee):
        format_str = '%m-%d-%Y'
        formatted_date = datetime.strftime(datee, format_str)
        datetime_obj = datetime.strptime(formatted_date, format_str)
        date_obj = datetime_obj.date()
        
        dt = time.mktime(date_obj.timetuple()) * 1000
        return dt
        
        
        
    def get_clickup_config(self):
        clickup_conf = self.env['clickup.config'].search([], order="id desc", limit=1)
        if not clickup_conf:
            raise UserError('Clickup is not configured!')
            
            
        team_id = clickup_conf.workspace_id.clickup_id
        if not team_id:
            raise UserError('Please select Workspace/Team!')
        
        return clickup_conf
    
    
    def export_task_to_clickup(self):
        ClickupList = self.env['clickup.list']
        ProjectTaskType = self.env['project.task.type']
        task_ids = self.search([('clickup_id','=',False),('id','in',self.ids)])
        clickup_conf = self.get_clickup_config()
            
        for task_id in task_ids:
            if not task_id.clickup_list_id:
                raise UserError('Please select Click List on task: '+str(task_id.name))
        
            
        for task_id in task_ids:
            if not task_id.clickup_list_id.clickup_id:
                task_id.clickup_list_id.push_list_to_clickup()
            
            tags_list = []
            if task_id.tag_ids:
                for tag in task_id.tag_ids:
                    tags_list.append(tag.name)
            
            state_id = ProjectTaskType.browse(task_id.stage_id.id)
            print(state_id.name)
            
            description = None
            if task_id.description:
                description = self.cleanhtml(task_id.description)
            
            due_date = None
            if task_id.date_deadline:
                due_date = int(self.posxi_to_date(task_id.date_deadline))
                print(due_date)
                
            url = "https://api.clickup.com/api/v2/list/"+str(task_id.clickup_list_id.clickup_id)+"/task"
            
            payload = json.dumps({
              "name": task_id.name,
              "description": description,
              "assignees": [],
              "tags": tags_list,
              "status": state_id.name,
              "priority": 3,
              "due_date": due_date, #1508369194377,
              "due_date_time": False,
              "time_estimate": False,
              "start_date": False,
              "start_date_time": False,
              "notify_all": True,
              "parent": None,
              "links_to": None,
              "check_required_custom_fields": True,
              "custom_fields": []
            })
            headers = {
              'Authorization': clickup_conf.token,
              'Content-Type': 'application/json'
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            response = response.json()
            print(response)
            
            if 'id' in response:
                list_id = response.get('list').get('id')
                list_id = ClickupList.search([('clickup_id','=',list_id)], order='id desc', limit=1)

                
                task_id.update({
                    'clickup_id': response.get('id'),
                    'clickup_list_id': list_id.id,
                    'clickup_folder_id': response.get('folder').get('id'),
                    'clickup_space_id': response.get('space').get('id'),
                    'clickup_task_url': response.get('url'),
                    'clickup_team_id': clickup_conf.workspace_id.clickup_id,
                    })
    
    
    def _create_mail_message(self, clickup_comment_id, comment_text, comment_user_name, comment_user_email):
        print('in main mail creatorrrrr--------')
        print(comment_text)
        MailMessage = self.env['mail.message']
        author_id = self.env['res.partner'].search([('name','=','Clickup')], order='id desc', limit=1)
        record_exists = MailMessage.search([('clickup_id','=',clickup_comment_id)])
        print(str(comment_text)+"<br />"+"Comment By@ "+str(comment_user_name)+"::"+str(comment_user_email))
        
        comment_vals = {
            'clickup_id': clickup_comment_id,
            'body': str(comment_text)+"<br />"+"Comment By@ "+str(comment_user_name)+"::"+str(comment_user_email) ,
            'model': 'project.task',
            'res_id': self.id,
            'email_from': "Comment By@ "+str(comment_user_name)+"::"+str(comment_user_email),
            'author_id': author_id.id,
            'message_type': 'comment',
            }
        
        if not record_exists:
            MailMessage.create(comment_vals)
        else:
            record_exists.update(comment_vals)
            
                        
                                    
    
    def pull_task_comments(self):
        MailMessage = self.env['mail.message']
        url = "https://api.clickup.com/api/v2/task/"+str(self.clickup_id)+"/comment/?custom_task_ids=&team_id=&start=&start_id="
        
        payload={}
        headers = {
          'Authorization': self.get_clickup_config().token,
          'Content-Type': 'application/json'
        }
        
        response = requests.request("GET", url, headers=headers, data=payload)
        response = response.json()
        print(response)
        
        if 'comments' in response:
            if response.get('comments') != []:
                author_id = self.env['res.partner'].search([('name','=','Clickup')], order='id desc', limit=1)
                 
                for comment in response.get('comments'):
                    clickup_comment_id = comment.get('id')
                    comment_text = comment.get('comment_text')
                    comment_user_name = comment.get('user').get('username')
                    comment_user_email = comment.get('user').get('email')
                    
                    self._create_mail_message(clickup_comment_id, comment_text, comment_user_name, comment_user_email)
#                     record_exists = MailMessage.search([('clickup_id','=',comment.get('id'))])
                    
#                     if not record_exists:
#                         comment_vals = {
#                             'clickup_id': comment.get('id'),
#                             'body': str(comment.get('comment_text'))+"-->\n"+"Comment By@ "+str(comment.get('user').get('username'))+"::"+str(comment.get('user').get('email')) ,
#                             'model': 'project.task',
#                             'res_id': self.id,
#                             'email_from': "Comment By@ "+str(comment.get('user').get('username'))+"::"+str(comment.get('user').get('email')),
#                             'author_id': author_id.id,
#                             'message_type': 'comment',
#                             }
#                         MailMessage.create(comment_vals)
                    print(comment.get('id'))
                    print(comment.get('comment_text'))
                    print(comment.get('user').get('id'))
                    print(comment.get('user').get('username'))
                    print(comment.get('user').get('email'))
                    print('======================================')



    def push_task_comments(self):
        MailMessage = self.env['mail.message']
        mail_messages_exists = MailMessage.search([('model','=','project.task'),('res_id','=',self.id),('clickup_id','=',False)])
        
        if mail_messages_exists:
            for mail_message in mail_messages_exists:
                if mail_message.body:
                    clean_message = self.cleanhtml(mail_message.body)
                    url = "https://api.clickup.com/api/v2/task/"+str(self.clickup_id)+"/comment"
                    payload = json.dumps({
                      "comment_text": clean_message,
                      "notify_all": True
                    })
                    headers = {
                      'Authorization': self.get_clickup_config().token,
                      'Content-Type': 'application/json'
                    }
                    response = requests.request("POST", url, headers=headers, data=payload)
                    response = response.json()
                    print(response)
                    
                    if 'id' in response:
                        mail_message.update({
                            'clickup_id': response.get('id')
                            })

    
    def cleanhtml(self, raw_html):
        CLEANR = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});') 
        cleantext = re.sub(CLEANR, '', raw_html)
        return cleantext



    clickup_task_url = fields.Char(string='Task URL', copy=False)
    clickup_list_id = fields.Many2one('clickup.list', string='List', domain="[('project_id','=',project_id)]", copy=False)
    clickup_folder_id = fields.Many2one('clickup.folder', related='clickup_list_id.project_folder_id', string='Folder', copy=False)
    clickup_space_id = fields.Integer(string='Space ID', copy=False)
    clickup_team_id = fields.Integer(string='Team ID', copy=False)
    clickup_id = fields.Char(string='Task ID', copy=False)
    
    _sql_constraints = [
    ('clickup_id_uniq', 'unique (clickup_id)', "Clickup ID already exists!"),
    ]               
          
          
         
