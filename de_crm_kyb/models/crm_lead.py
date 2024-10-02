# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError
import base64
import requests
import json
import logging

_logger = logging.getLogger(__name__)

class CRMLead(models.Model):
    _inherit = "crm.lead"

    is_kyb = fields.Boolean(default=False, 
                            #compute='_compute_kyb', store=True
    )
    xpl_id = fields.Integer('Xpendless ID')
    
    stage_id = fields.Many2one(
        'crm.stage', string='Stage', index=True, tracking=True,
        compute='_compute_stage_id', 
        readonly=False, store=True,
        copy=False, 
        group_expand='_read_group_stage_ids', 
        ondelete='restrict',
        domain="[('id', 'in', stage_ids)]"
    )
    stage_ids = fields.Many2many('crm.stage', compute='_compute_conditional_tage_ids')
    allow_verify = fields.Boolean(related='stage_id.allow_verify')

    reg_no = fields.Char(string='Reg. No.')
    
    date_company_creation = fields.Date('Date Creation')
    date_company_expiry = fields.Date('Date Expiry')

    count_contacts = fields.Integer('Contacts', computer='_compute_contacts_count')

    allow_verification_stage_id = fields.Many2one('crm.stage', compute='_compute_allow_verification_stage')
    stage_category = fields.Selection(related='stage_id.stage_category', string="Stage Category", store=True)


    # ============================================================================
    # Computed Methods
    # ============================================================================
   

    
    def _compute_allow_verification_stage(self):
        stage_id = self.env['crm.stage']
        for record in self:
            stage_id = self.env['crm.stage'].search([('is_kyb','=',True),('allow_verify','=',True)],limit=1)
            record.allow_verification_stage_id = stage_id.id
            
    def _compute_contacts_count(self):
        partner_ids = self.env['res.partner']
        for record in self:
            partner_ids = self.env['res.partner'].search([
                ('parent_id','=',record.partner_id.id)
            ])
            record.count_contacts = len(partner_ids)
            
    @api.depends('team_id','stage_id')
    def _compute_kyb(self):
        for lead in self:
            lead.is_kyb = lead.team_id.is_kyb
            
    @api.depends('team_id', 'type','stage_ids','is_kyb')
    def _compute_stage_id(self):
        for lead in self:
            if not lead.stage_id:
                if lead.team_id.is_kyb or lead.is_kyb:
                    domain = [('is_kyb', '=', True)] if lead.team_id else [('fold', '=', False)]
                else:
                    domain = [('is_kyb', '!=', True)] if lead.team_id else [('fold', '=', False)]
                lead.stage_id = lead._stage_find(domain=domain).id

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        # retrieve team_id from the context and write the domain
        # - ('id', 'in', stages.ids): add columns that should be present
        # - OR ('fold', '=', False): add default columns that are not folded
        # - OR ('team_ids', '=', team_id), ('fold', '=', False) if team_id: add team columns that are not folded
        team_id = self._context.get('default_team_id')
        team = self.env['crm.team'].browse(team_id)
        search_domain = []
        if team:
            if team.is_kyb:
                search_domain = [('is_kyb', '=', True)]
            else:
                search_domain = [('is_kyb', '!=', True)]
                #search_domain = ['|', ('id', 'in', stages.ids), '|', ('team_id', '=', False), ('team_id', '=', team_id),('is_kyb', '!=', True)]
        #else:
        #    search_domain = ['|', ('id', 'in', stages.ids), ('team_id', '=', 100)]

        # perform search
        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)
        
    @api.depends('team_id')
    def _compute_conditional_tage_ids(self):
        stage_ids = self.env['crm.stage']
        for record in self:
            if record.team_id.is_kyb:
                stage_ids = self.env['crm.stage'].search([('is_kyb','=',True)])
            else:
                stage_ids = self.env['crm.stage'].search([('is_kyb','!=',True)])
            record.stage_ids = stage_ids

    def action_verification(self):
        pass

    # ============================================================================
    # CRUD Operations
    # =============================================================================
    
    def write(self, vals):
        res = super(CRMLead, self).write(vals)
        kyb_status = 'Submitted'
        if 'stage_id' in vals and not self.env.context.get('from_api'):
            for lead in self:
                if lead.stage_id.stage_category == 'close':
                    kyb_status = 'Verified'
                elif lead.stage_id.stage_category == 'cancel':
                    kyb_status = 'Unverified'
                else:
                    kyb_status = 'Submitted'

                self._update_company_status(kyb_status, kyb_status)

        # If the record is inactive and is KYB, find and set the "cancel" stage
        if vals.get('active') is False and self.is_kyb:
            cancel_stage = self.env['crm.stage'].sudo().search([('stage_category', '=', 'cancel')], limit=1)    
            if cancel_stage:
                self.sudo().write({'stage_id': cancel_stage.id})
        return res
    
    # ============================================================================
    # Actions
    # ============================================================================
    def action_accept_kyb_lead(self):
        stage_id = self.env['crm.stage'].search([('is_kyb','=',True),('sequence','>',self.stage_id.sequence)],limit=1)
        self.write({
            'stage_id': stage_id.id,
        })

    def action_kyb_verification1(self):
        instance_id = self.company_id._get_instance()
        api_name = '/kybOdoo/setKybOdooStatus'

        api_data = {
            "companyId": int(self.xpl_id),
            "kybStatus": "Verified"
        }
        response = instance_id._put_api_data(api_name, api_data)

        formatted_response = json.dumps(response, indent=4)  # Pretty-print JSON response
        #raise UserError(formatted_response)
    
        stage_id = self.env['crm.stage'].search([('is_kyb','=',True),('sequence','>',self.stage_id.sequence)],limit=1)
        self.write({
            'stage_id': stage_id.id,
        })

    def action_kyb_verification(self):
        response = self._update_company_status('Verified', comment)
        
    def _update_company_status(self,status, comment=False):
        instance_id = self.company_id._get_instance()
        api_name = '/kybOdoo/setKybOdooStatus'

        api_data = {
            "companyId": int(self.xpl_id),
            "kybStatus": status,
            "comment": comment,
        }
        #if comment:
        #    api_date["comment"] = comment

        
        response = instance_id._put_api_data(api_name, api_data)
        _logger.info(f"Stage changed to: {response}")
        return response
        
    def action_open_employees(self):
        action = self.env.ref('de_crm_kyb.action_partner_kyb_contacts').read()[0]
        action.update({
            'name': 'Employees',
            'view_mode': 'tree,form',
            'res_model': 'res.partner',
            'type': 'ir.actions.act_window',
            'domain': [('parent_id','=',self.partner_id.id)],
            'context': {
                'create': False,
                'edit': False,
            },
        })
        return action

    def action_get_owners(self):
        self.env['xpl.kyb.employees'].search([]).unlink()
        instance_id = self.company_id._get_instance()
        api_name = "/kybOdoo/getCompanyInformation"
        params_data = {
            "companyId": int(self.xpl_id)
        }
        response = instance_id._get_api_data(api_name, params_data=params_data, json_data=None)
        
        employees = response.get('data', {}).get('Owners', [])

        #raise UserError(f"API Response: {employees}")

        # Loop through the employees and create records in xpl.kyb.employees
        for employee in employees:
            name = employee.get('fullName')
            email = employee.get('email')
            mobile = employee.get('mobileNumber')
            self.env['xpl.kyb.employees'].create({
                'name': name,
                'email': email,
                'mobile': mobile,
            })

        return {
            'name': 'Employees',
            'view_mode': 'tree',
            'res_model': 'xpl.kyb.employees',
            'type': 'ir.actions.act_window',
            'target': '_blank',
            'context': {
                'create': False,
                'edit': False,
                'delete': False,
            },
        }


    def action_get_employees(self):
        self.env['xpl.kyb.employees'].search([]).unlink()
        instance_id = self.company_id._get_instance()
        api_name = "/kybOdoo/getCompanyInformation"
        params_data = {
            "companyId": int(self.xpl_id)
        }
        response = instance_id._get_api_data(api_name, params_data=params_data, json_data=None)
        
        employees = response.get('data', {}).get('Employees', [])

        #raise UserError(f"API Response: {employees}")

        # Loop through the employees and create records in xpl.kyb.employees
        for employee in employees:
            name = employee.get('fullName')
            email = employee.get('email')
            mobile = employee.get('mobileNumber')
            self.env['xpl.kyb.employees'].create({
                'name': name,
                'email': email,
                'mobile': mobile,
            })

        return {
            'name': 'Employees',
            'view_mode': 'tree',
            'res_model': 'xpl.kyb.employees',
            'type': 'ir.actions.act_window',
            'target': '_blank',
            'context': {
                'create': False,
                'edit': False,
                'delete': False,
            },
        }
        
    def action_get_documents(self):
        self.env['xpl.kyb.docs'].search([]).unlink()
        instance_id = self.company_id._get_instance()
        api_name = "/kybOdoo/getCompanyInformation"
        params_data = {
            "companyId": int(self.xpl_id)
        }
        response = instance_id._get_api_data(api_name, params_data=params_data, json_data=None)
        
        docs = response.get('data', {}).get('Attachments', [])
        for doc in docs:
            xpl_id = doc.get('companyDocId')
            url = doc.get('attachmentPath')
            name = doc.get('documentName')
            self.env['xpl.kyb.docs'].create({
                'xpl_id': xpl_id,
                'url': url,
                'name': name,
            })
            
        return {
            'name': 'Documents',
            'view_mode': 'tree',
            'res_model': 'xpl.kyb.docs',
            'type': 'ir.actions.act_window',
            'target': '_blank',
            'context': {
                'create': False,
                'edit': False,
                'delete': False,
            },
        }

    def action_get_questions(self):
        self.env['xpl.kyb.questions'].search([]).unlink()
        instance_id = self.company_id._get_instance()
        api_name = "/kybOdoo/getCompanyInformation"
        params_data = {
            "companyId": int(self.xpl_id)
        }
        response = instance_id._get_api_data(api_name, params_data=params_data, json_data=None)
        
        docs = response.get('data', {}).get('Questionnaire', [])
        for doc in docs:
            question = doc.get('question')
            answer = doc.get('answer')
            self.env['xpl.kyb.questions'].create({
                'name': question,
                'desc': answer,
            })
            
        return {
            'name': 'Questions',
            'view_mode': 'tree',
            'res_model': 'xpl.kyb.questions',
            'type': 'ir.actions.act_window',
            'target': '_blank',
            'context': {
                'create': False,
                'edit': False,
                'delete': False,
            },
        }
        
    def _cron_import_company_from_xpl(self):
        raise UserError('hello')

    @api.model
    def create_or_update_opportunity(self, json_data):
        # Access the payload part of the JSON data (list)
        payload_list = json_data.get('payload', [])
        
        # Process each company data within the payload list
        for payload in payload_list:
            opportunity_values = {}
            partner_vals = {}
    
            # Extract company details from payload safely
            companyId = payload.get('companyId')
            _logger.error(f"Company Found Value: {companyId}")
            
            if not companyId:
                _logger.warning("Company ID is missing in the payload.")
                #continue  # Skip if companyId is not found

            
            companyName = payload.get('companyName')
            registrationNumber = payload.get('registrationNumber')
            street = payload.get('addressLine1')
            street2 = payload.get('addressLine2')
            city = payload.get('city')
            postalCode = payload.get('postalCode')
            companyEmail = payload.get('companyEmail')
            companyPhone = payload.get('companyPhone')

            stage_name = payload.get('kybStatus')
            
            
            date_company_creation = payload.get('crCreationDate')
            date_company_expiry = payload.get('crExpiryDate')
    
            # Prepare opportunity values
            opportunity_values = {
                'name': companyName,
                'partner_name': companyName,
                'reg_no': registrationNumber,
                'phone': companyPhone,
                'email_from': companyEmail,
                'street': street,
                'street2': street2,
                'city': city,
                'zip': postalCode,
                'is_kyb': True,
                'date_company_creation': date_company_creation,
                'date_company_expiry':date_company_expiry,
                'description': str(companyId) + companyName,
            }

            stage_category = 'draft'
            if stage_name == 'Verification in progress':
                stage_category = 'progress'
            elif stage_name == 'Verified':
                stage_category = 'close'
            elif stage_name == 'Unverified':
                stage_category = 'cancel'
                
            stage_id = self.env['crm.stage'].search([('stage_category','=',stage_category),('is_kyb','=',True)],limit=1)
            if stage_id:
                opportunity_values["stage_id"] = stage_id.id

            #opportunity_values["user_id"] =  self.team_id.user_id.id
            
            # Search for an existing lead with the same xpl_id (companyId)
            existing_lead = self.env['crm.lead'].sudo().search([
                '|',('xpl_id', '=', int(companyId)),('xpl_id', '=', 504)
            ], limit=1)
            _logger.info(f"Payload: {payload_list}")
            if existing_lead:
                _logger.info(f"Existing Lead: {existing_lead}")
                _logger.info(f"Existing Lead: {opportunity_values}")
                existing_lead.with_context(from_api=True).write(opportunity_values)
                lead_id = existing_lead
            else:
                # Set xpl_id when creating new opportunity
                opportunity_values["xpl_id"] = companyId
                opportunity_values["type"] = 'opportunity'
                
                lead_id = self.env['crm.lead'].sudo().create(opportunity_values)

                self.action_create_kyb_activity(lead_id)
    
                # Create a new partner linked to this lead (company)
                lead_id.partner_id = self.env['res.partner'].sudo().create({
                    'name': companyName,
                    'company_type': 'company',
                    'is_xpendless': True,
                    'xpl_id': lead_id.xpl_id,
                })
    
                # Set the KYB-specific stage if any
                stage_id = self.env['crm.stage'].sudo().search([('is_kyb', '=', True)], order='sequence', limit=1)
                if stage_id:
                    lead_id.sudo().write({
                        'stage_id': stage_id.id,
                    })
    
                # Automatically convert the lead to an opportunity
                team_id = self.env['crm.team'].sudo().search([('is_kyb', '=', True)], limit=1)
                if team_id:
                    lead_id.sudo().convert_opportunity(lead_id.partner_id, user_ids=[1], team_id=team_id.id)

                lead_id.write({
                    'user_id': lead_id.team_id.user_id.id 
                })
            
        return lead_id


    def action_create_kyb_activity(self, lead):
        # Ensure that 'lead' is a single record
        if not lead:
            _logger.warning("No lead found to create KYB activity.")
            return
        lead.ensure_one()
    
        # Schedule an activity for the KYB verification
        activity_type = self.env.ref('mail.mail_activity_data_todo')  
        summary_message = _('KYB Verification')
        note = _('A new company has been created for KYB verification')
        
        lead.activity_schedule(
            activity_type_id=activity_type.id,
            summary=summary_message,
            note=note,
            user_id=lead.team_id.user_id.id,
            date_deadline=fields.Date.context_today(self)
        )


