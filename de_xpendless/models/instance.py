# -*- coding: utf-8 -*-

from odoo import api, fields, Command, models, _
from odoo.exceptions import UserError, AccessError
from odoo.tools import html_escape as escape

import requests
import json

from urllib.parse import urlparse


class XplInstance(models.Model):
    _name = 'xpl.instance'
    _description = 'Xpendless Instance'

    name = fields.Char(string='Name', required=True, readonly=False)
    api_key = fields.Char(string='API Key', related='company_id.xpl_api_key', 
                          required=True, help='API Key', readonly=False)
    api_secret = fields.Char(string='Secret',  related='company_id.xpl_api_secret', 
                             required=True, help=' API Secret', readonly=False)
    access_token = fields.Char(string='Token',  related='company_id.xpl_access_token', readonly=False)
    url = fields.Char(string='URL',  related='company_id.xpl_url', 
                      required=True, readonly=False, )
    url_sample = fields.Char(default='https://api.xpendless.com/')
    
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True, default=lambda self: self.env.company)


    state = fields.Selection([
        ('draft', 'Draft'), 
        ('verified', 'Verified'), 
        ('active', 'Active')], 
        string='Status',default='draft', required=True
    )

    # operations fields
    apl_date_import_companies = fields.Datetime(string='Companies import date')
    apl_date_import_employees = fields.Datetime(string='Employees import date')
    apl_date_import_expenses = fields.Datetime(string='Expenses import date')

    apl_date_export_companies = fields.Datetime(string='Companies export date')
    apl_date_export_employees = fields.Datetime(string='Employees export date')

    def button_draft(self):
        
        json_data = self._get_api_data('webhook/logs', api_data=None)
        json_formatted_str = json.dumps(json_data, indent=4)  # Convert dictionary to JSON string with indentation
        raise UserError(json_formatted_str)
        self.write({
            'state':'draft'
        })

    def button_confirm(self):
        self.write({
            'state':'active'
        })

    def connection_test(self):
        self.write({
                'state': 'verified'
            })
        
    def connection_test1(self):
        
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Connection to Expendless successful; explore its capabilities now.'),
                'type': 'warning',
                'sticky': False,  #True/False will display for few seconds if false
            },
        }

        url = self.url + 'auth/health' #"https://api.expendless.io/v1/auth/health"
        querystring = {
            "api_key": self.api_key
        }
        headers = {
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, params=querystring)
        if response.status_code == 200: 
            self.write({
                'state': 'verified'
            })
            notification['params'].update({
                'title': _('The connection to Expendless was successful.'),
                'type': 'success',
                'next': {'type': 'ir.actions.act_window_close'},
            })
            
        else:
            # The response indicates an error
            error_message = "API connection error. Please check the response."
            raise UserError(error_message)
        return notification

    def unlink(self):
        for record in self:
            if record.state != 'draft':
                raise UserError("You cannot delete a record with a state other than 'draft'.")
        return super(XplInstance, self).unlink()

        
    def button_import_labels(self):
        data = {
            #'api_key': 'GbYvCle7WbRW0lFKYXlArw',
        }
        tags_data = self._get_api_data('labels', data)
        category_id = self.env['res.partner.category']
        crm_tag_id = self.env['crm.tag']
        for tag in tags_data:
            if isinstance(tag, dict):  # Check if 'tag' is a dictionary
                category_id = self.env['res.partner.category'].search([('apl_id','=',tag.get('id'))],limit=1)
                crm_tag_id = self.env['crm.tag'].search([('apl_id','=',tag.get('id'))],limit=1)
                if tag.get('name'):
                    if category_id:
                        category_id.write({
                            'name': tag.get('name'),
                        })
                    else:
                        self.env['res.partner.category'].create({
                            'name': tag.get('name'),
                            'apl_id': tag.get('id'),
                        })
                    if crm_tag_id:
                        crm_tag_id.write({
                            'name': tag.get('name'),
                        })
                    else:
                        self.env['crm.tag'].create({
                            'name': tag.get('name'),
                            'apl_id': tag.get('id'),
                        })

    def button_import_stages(self):
        data = {}
        stages_data = self._get_api_data('opportunity_stages', data)
        #raise UserError(stages_data.get('opportunity_stages', []))
        stage_id = self.env['crm.stage']
        for stage in stages_data.get('opportunity_stages', []):
            if isinstance(stage, dict):  # Check if 'tag' is a dictionary
                stage_id = self.env['crm.stage'].search([('apl_id','=',stage.get('id'))],limit=1)
                if stage.get('name'):
                    if stage_id:
                        stage_id.write({
                            'name': stage.get('name'),
                            'requirements': stage.get('description'),
                            'is_won': stage.get('is_won'),
                        })
                    else:
                        self.env['crm.stage'].create({
                            'name': stage.get('name'),
                            'apl_id': stage.get('id'),
                            'requirements': stage.get('description'),
                            'is_won': stage.get('is_won'),
                        })

                        
    def button_import(self):
        raise UserError(self._get_sample_api_data())
        context = {
            'default_op_name': self.name,
        }
        return {
            'name': 'Operations',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'xpl.ops.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }
        #for partner in partners:

    def button_export(self):
        self.send_data_to_webhook()
        
    def button_export1(self):
        #partners = self.env['res.partner'].search([('active', '=', True), '|', ('apl_id', '=', False), ('apl_date', '<', fields.Datetime.now())])
        if self._context.get('op_name') == 'contacts':
            partner_ids = self.env['res.partner'].search([('active', '=', True),('update_required_for_xpendless', '=', True)])
            for partner in partner_ids:
                partner._send_to_xpendless(self)
            self.write({
                'apl_date_export_contacts': self.env.cr.now(),
            })
        elif self._context.get('op_name') == 'leads':
            lead_ids = self.env['crm.lead'].search([('active', '=', True),('update_required_for_expendless', '=', True)])
            for lead in lead_ids:
                lead._send_to_xpendless(self)
            self.write({
                'apl_date_export_leads': self.env.cr.now(),
            })
            
        #for partner in partners:


    # ---------------------------------------------------------
    # ---------------------- Operations for Expendless ------------
    # ---------------------------------------------------------
    
    @api.model
    def _post_api_data(self, api_name, api_data=None):
        
        headers = {
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/json'
        }
        try:
            url = self.url + api_name
            #raise UserError(url)
            # Initialize data as an empty dictionary if it's None
            if api_data is None:
                api_data = {}

            # Add the api_key field to the data dictionary
            api_data['api_key'] = self.api_key

            #raise UserError(api_data)
            
            response = requests.request("POST", url, headers=headers, json=api_data)   
            #raise UserError(response.text)
            json_data = json.loads(response.text)
            return json_data

        except requests.exceptions.RequestException as e:
            # Handle any request exceptions
            raise e

        except json.JSONDecodeError as e:
            # Handle JSON decoding errors
            raise e

    api.model
    def send_data_to_webhook(self):
        webhook_url = "https://g2020-xpl-13945246.dev.odoo.com/webhook/company"
        headers = {'Content-Type': 'application/json'}
        json_data = self._get_sample_api_data() #json.dumps(data)

        try:
            response = requests.post(webhook_url, headers=headers, data=json_data)
            response.raise_for_status()  # Raise an exception for HTTP errors

            # Handle response if needed
            return response.text  # Example: Return response text
        except requests.exceptions.RequestException as e:
            # Handle exception
            return {'error': str(e)}  # Example: Return error message
            

    @api.model
    def _get_api_data(self, api_name, api_data=None):
        token = self.access_token
        # Set the headers for the request
        headers = {
            'Authorization': f"Bearer {token}",
            'Content-Type': 'application/json',
        }
        try:
            url = self.url + api_name
            # Initialize data as an empty dictionary if it's None
            if api_data is None:
                api_data = {}

            # Add the api_key field to the data dictionary
            api_data['api_key'] = self.api_key

            response = requests.request("GET", url, headers=headers, params=api_data)
            #raise UserError(response.text)
            json_data = json.loads(response.text)
            return json_data

        except requests.exceptions.RequestException as e:
            # Handle any request exceptions
            raise e

        except json.JSONDecodeError as e:
            # Handle JSON decoding errors
            raise e

    @api.model
    def _put_api_data(self, api_name, api_data=None):
        headers = {
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/json'
        }
        try:
            url = self.url + api_name
            # Initialize data as an empty dictionary if it's None
            if api_data is None:
                api_data = {}

            # Add the api_key field to the data dictionary
            api_data['api_key'] = self.api_key

            response = requests.request("PUT", url, headers=headers, params=api_data)
            #raise UserError(response.text)
            json_data = json.loads(response.text)
            return json_data

        except requests.exceptions.RequestException as e:
            # Handle any request exceptions
            raise e

        except json.JSONDecodeError as e:
            # Handle JSON decoding errors
            raise e

