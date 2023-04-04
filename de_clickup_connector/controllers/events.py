# -*- coding: utf-8 -*-
from odoo import http
import requests
from odoo.exceptions import ValidationError
import json
from odoo.http import request
import yaml
from datetime import datetime
import urllib.request



class EventsHandler(http.Controller):
    
    
    @http.route('/webhook', auth='public', type='json')
    def connection_event(self, **kwarg):
        print('----------------connection clickup event--------------')
        try:
            data = request.httprequest.data
#             print(data)
            try:
                kw_json = yaml.load(data)
                print(kw_json)
                clickup_conf = request.env['clickup.config'].sudo().search([], order='id desc', limit=1)
                
                if clickup_conf: 
                    """TASK CREATED"""
                    if kw_json.get('event') == 'taskCreated':
                        clickup_conf.get_clickup_task(kw_json.get('task_id'))
                    
                    
                    """TASK UPDATED"""
                    if kw_json.get('event') == 'taskUpdated':
                        #######################################################
#                         attachments = False
                        attachments = kw_json.get('history_items')[0].get('comment').get('comment')
                        print('-ddddddddddd----',attachments)
                        
#                         for comment in comments:
#                             if 'type' in comment:
#                                 if comment.get('type') == 'attachment':
#                                     attachments = comments
#                                     print(attachments)
#                                     break
#                                     print('attachment event----')
#                                     print(attachments)
                                
#                                 print(attachment.get('id'))
#                                 print(attachment.get('title'))
#                                 print(attachment.get('id'))
#                                 print(comment.get('attachment'))
#                                 print('333')
                                
                        clickup_task_id = kw_json.get('task_id')
                        field_name = kw_json.get('history_items')[0].get('field')
                        field_val = kw_json.get('history_items')[0].get('after')
                        
                        if field_name == 'content':
                            desc_str = ""
                            for line in eval(field_val).get('ops'):
                                desc_str += line.get('insert')
                                
                            print(desc_str)
                            field_val = desc_str.replace("\n", "<br />")
                        clickup_conf._update_task(clickup_task_id, field_name, field_val, attachments)
                        
                        
#                             pass
#                         imgURL = 'https://t36016680.p.clickup-attachments.com/t36016680/1ba8b17e-ddbe-4d7a-a8cf-ccfd49d84aed/clickup.png'
#                         urllib.request.urlretrieve(imgURL, "cccccc.png")
                    
                    
                    """TASK DELETED"""
                    if kw_json.get('event') == 'taskDeleted':
                        clickup_task_id = kw_json.get('task_id')
                        clickup_conf._delete_task(clickup_task_id)
                    
                    
                    """TASK STATUS UPDATED"""
                    if kw_json.get('event') == 'taskStatusUpdated':
                        status = kw_json.get('history_items')[0].get('after').get('status')
                        clickup_task_id = kw_json.get('task_id')
                        
                        clickup_conf.update_task_stage(clickup_task_id, status)
    
                    
                    """TASK DUE DATE UPDATED"""
                    if kw_json.get('event') == 'taskDueDateUpdated':    
                        due_date = kw_json.get('history_items')[0].get('after') 
                        clickup_task_id = kw_json.get('task_id')
                        
                        clickup_conf.update_task_due_date(clickup_task_id, due_date) 

                    
                    """TASK COMMENT POSTED"""
                    if kw_json.get('event') == 'taskCommentPosted' or kw_json.get('event') == 'taskCommentUpdated': 
                        clickup_task_id = kw_json.get('task_id')
                        clickup_comment_id = kw_json.get('history_items')[0].get('comment').get('id')
                        comment_text = kw_json.get('history_items')[0].get('comment').get('text_content')
                        comment_user_name = kw_json.get('history_items')[0].get('user').get('username')
                        comment_user_email = kw_json.get('history_items')[0].get('user').get('email')
                        
                        clickup_conf.post_task_comment(clickup_task_id, clickup_comment_id, comment_text, comment_user_name, comment_user_email)
                    
                    
                    """TASK TAG UPDATED"""
                    if kw_json.get('event') == 'taskTagUpdated': 
                        before = kw_json.get('history_items')[0].get('before')
                        after = kw_json.get('history_items')[0].get('after')
                        clickup_task_id = kw_json.get('task_id')
                        clickup_conf._update_task_tag(clickup_task_id, before, after)
                            
                        
                    
                    """FOLDER CREATED or UPDATED"""
                    if kw_json.get('event') == 'folderCreated' or kw_json.get('event') == 'folderUpdated': 
                        clickup_conf._get_folder(kw_json.get('folder_id'))
                    
                    
                    """FOLDER DELETED"""
                    if kw_json.get('event') == 'folderDeleted': 
                        clickup_conf._delete_folder(kw_json.get('folder_id'))
                        
                    
                    """LIST CREATED or UPDATED"""
                    if kw_json.get('event') == 'listCreated' or kw_json.get('event') == 'listUpdated': 
                        clickup_conf._get_list(kw_json.get('list_id'))
                    
                    
                    """LIST DELETED"""
                    if kw_json.get('event') == 'listDeleted': 
                        clickup_conf._delete_list(kw_json.get('list_id'))
                        
                    
                    """SPACE CREATED"""
                    if kw_json.get('event') == 'spaceCreated' or kw_json.get('event') == 'spaceUpdated':
                        clickup_conf._get_clickup_space(kw_json.get('space_id'))
                        
                    
                    """SPACE DELETED"""
                    if kw_json.get('event') == 'spaceDeleted':
                        clickup_conf._delete_space(kw_json.get('space_id'))
                        

            except Exception as e:
                raise ValidationError(str(e))

        except Exception as e:
            raise ValidationError(str(e))
        
        
        