# -*- coding: utf-8 -*-

from odoo import api, fields, Command, models, _
from odoo.exceptions import UserError, AccessError

class AplOpsWizard(models.TransientModel):
    _name = 'apl.ops.wizard'
    _description = 'APL Ops Wizard'

    total_pages = fields.Integer('Total Pages', default=1)
    duplicate_records = fields.Boolean('Ignore Duplicate Records')

    def run_process(self):
        # You can access the 'op_name' context variable here
        # It will contain the value passed from the button's context
        op_name = self._context.get('op_name')

        active_model = self.env.context.get('active_model')
        active_id = self.env.context.get('active_id', [])

        apl_instance_id = self.env['apl.instance'].browse(active_id)

        page = self.total_pages
        for i in range(1, page + 1):
            data = {
                "page" : i,
            }
            if op_name == 'contacts':
                json_data = apl_instance_id._post_apollo_data('contacts/search', data)
                if isinstance(json_data, list):
                    json_data_list = json_data
                elif isinstance(json_data, dict):
                    json_data_list = json_data.get('contacts', [])
    
                for obj in json_data_list:
                    partner_id = self.env['res.partner'].search([('apl_id','=',obj.get('id'))],limit=1)
                    state_id = self.env['res.country.state'].search([('name','=',obj.get('state'))],limit=1)
                    country_id = self.env['res.country'].search([('name','=',obj.get('country'))],limit=1)
                    
                    vals = {
                        'company_type': 'person',
                        'apl_id': obj.get('id'),
                        'apl_account_id': obj.get('account_id'),
                        'name': obj.get('name') + 'test',
                        'linkedin_url': obj.get('linkedin_url'),
                        'function': obj.get('title'),
                        'photo_url': obj.get('photo_url'),
                        'email': obj.get('email'),
                        'city': obj.get('state'),
                        'state_id': state_id.id,
                        'country_id': country_id.id,
                        'phone': obj.get('sanitized_phone'),
                    }
                    if partner_id: #Update Records
                        if self.duplicate_records:
                            partner_id = self.env['res.partner'].create(vals)
                        else:
                            partner_id.write(vals)
                    else:
                        partner_id = self.env['res.partner'].create(vals)
                    
                    partner_id._compute_image()
            # -------------------------------------------------
            # apollo accounts are the companies contact in odoo
            # -------------------------------------------------
            elif op_name == 'accounts':
                json_data = apl_instance_id._post_apollo_data('accounts/search', data)
                if isinstance(json_data, list):
                    json_data_list = json_data
                elif isinstance(json_data, dict):
                    json_data_list = json_data.get('contacts', [])
    
                for obj in json_data_list:
                    account_id = self.env['res.partner'].search([('apl_id','=',obj.get('id'))],limit=1)
                    countact_ids = self.env['res.partner'].search([('apl_account_id','=',obj.get('id'))])
                    vals = {
                        'company_type': 'company',
                        'apl_id': obj.get('id'),
                        'name': obj.get('name') + 'test',
                        'website_url': obj.get('website_url'),
                        'blog_url': obj.get('blog_url'),
                        'angellist_url': obj.get('angellist_url'),
                        'linkedin_url': obj.get('linkedin_url'),
                        'twitter_url': obj.get('twitter_url'),
                        'facebook_url': obj.get('facebook_url'),
                        'phone': obj.get('phone') + ',' + obj.get('sanitized_phone'),
                        'photo_url': obj.get('logo_url'),
                        'founded_year': obj.get('founded_year'),                        
                    }
                    if account_id: #Update Records
                        if self.duplicate_records:
                            account_id = self.env['res.partner'].create(vals)
                        else:
                            account_id.write(vals)
                    else:
                        account_id = self.env['res.partner'].create(vals)
                    
                    if len(contact_ids):
                        contact_ids.write({
                            'parent_id': account_id.id,
                        })
                    account_id._compute_image()
            # -------------------------------------------------
            # apollo opportunities are the companies contact in odoo
            # -------------------------------------------------
            elif op_name == 'leads':
                json_data = apl_instance_id._post_apollo_data('opportunities/search', data)

        #raise UserError(active_id)
        # You can now use the 'op_name' variable as needed
        # For example, print it or save it in the database.
        #self.env['your.model'].create({'name': op_name})

        return {'type': 'ir.actions.act_window_close'}
        
