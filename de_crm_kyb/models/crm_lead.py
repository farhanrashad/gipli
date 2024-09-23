# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError
import base64
import requests
import json
class Lead(models.Model):
    _inherit = "crm.lead"

    is_kyb = fields.Boolean(default=False, 
                            #compute='_compute_kyb', store=True
    )
    xpl_id = fields.Char('Xpendless ID', readonly=True)
    
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
    
    usage_est_users = fields.Selection([
        ('1', 'Just Me'), 
        ('2-20', '2 - 20 Employees'),
        ('21-100', '21 - 100 Employees'),
        ('100+', '100+ Employees')
    ],string="Expected Users")
    usage_est_spending = fields.Selection([
        ('0-50000', '0.00 QAR - 50,000.00 QAR'), 
        ('50000-100000', '50,000.00 QAR - 100,000.00 QAR'), 
        ('100000-500000', '100,000.00 QAR - 500,000.00 QAR'), 
        ('500000+', 'Over 500,000.00 QAR')
    ],string="Expected Spending")
    usage_card = fields.Selection([
        ('qatar', 'Qatar Only'), 
        ('international', 'International'),
        ('both', 'Both'),
    ],string="Card Usage")
    work_type = fields.Char('Nature of Work')

    crc = fields.Binary(string="Commercial Registration Certificate", )
    crc_filename = fields.Char(string="CRC Filename")
    
    aoa = fields.Binary(string="Articles of Association", )
    aoa_filename = fields.Char(string="AoA Filename")
    
    c_card = fields.Binary(string="Computer Card", )
    cc_filename = fields.Char(string="CC Filename")
    
    iban_cert = fields.Binary(string="IBAN Certificate", )
    iban_cert_filename = fields.Char(string="IBAN Filename")
    
    trade_license = fields.Binary(string="Trade License")
    trade_license_filename = fields.Char(string="TL Filename")

    count_contacts = fields.Integer('Contacts', computer='_compute_contacts_count')

    first_stage_id = fields.Many2one('crm.stage', compute='_compute_first_kyb_stage')
    allow_verification_stage_id = fields.Many2one('crm.stage', compute='_compute_allow_verification_stage')

    def _compute_first_kyb_stage(self):
        stage_id = self.env['crm.stage']
        for record in self:
            stage_id = self.env['crm.stage'].search([('is_kyb','=',True)],limit=1,order='sequence')
            record.first_stage_id = stage_id.id

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

    # -------------------------------------------------------------
    # Actions
    # -------------------------------------------------------------
    def action_accept_kyb_lead(self):
        stage_id = self.env['crm.stage'].search([('is_kyb','=',True),('sequence','>',self.stage_id.sequence)],limit=1)
        self.write({
            'stage_id': stage_id.id,
        })

    def action_kyb_verification(self):
        instance_id = self.company_id._get_instance()
        api_name = '/kybOdoo/setKybOdooStatus'

        api_data = {
            "companyId": int(self.xpl_id),
            "kybStatus": "Verified"
        }
        response = instance_id._put_api_data(api_name, api_data)

        formatted_response = json.dumps(response, indent=4)  # Pretty-print JSON response
        raise UserError(formatted_response)
    
        stage_id = self.env['crm.stage'].search([('is_kyb','=',True),('sequence','>',self.stage_id.sequence)],limit=1)
        self.write({
            'stage_id': stage_id.id,
        })
        
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
        
    def _cron_import_company_from_xpl(self):
        raise UserError('hello')

    @api.model
    def create_or_update_opportunity(self, json_data):
        opportunity_values = {}
        partner_vals = {}

        # Access the payload part of the JSON data
        payload = json_data.get('payload', {})
        #payload = json_data

        companyId = int(payload.get('companyId'))
        companyName = payload.get('companyName')
        registrationNumber = payload.get('registrationNumber')
        addressLine1 = payload.get('addressLine1')
        addressLine2 = payload.get('addressLine2')
        city = payload.get('city')
        postalCode = payload.get('postalCode')
        companyEmail = payload.get('companyEmail')
        companyPhone = payload.get('companyPhone')
        crCreationDate = payload.get('crCreationDate')
        crExpiryDate = payload.get('crExpiryDate')
        activationDate = payload.get('activationDate')
        subscribingDate = payload.get('subscribingDate')
        createdAt = payload.get('createdAt')
        updatedAt = payload.get('updateAt')
        status = payload.get('status')
        kybStatus = payload.get('kybStatus')
        termsConditions = payload.get('termsConditions')
        submittedFields = payload.get('submittedFields', [])
        attachments = payload.get('attachments', [])
        companySettings = payload.get('CompanySettings', {})
        owners = payload.get('Owners', [])
        attachments = payload.get('attachments', [])

        team_id = self.env['crm.team'].sudo().search([
            ('is_kyb', '=', True)
        ], limit=1)

        stage_id = self.env['crm.stage'].sudo().search([
            ('is_kyb', '=', True)
        ], order='sequence', limit=1)

        opportunity_values = {
            'name': companyName,
            'partner_name': companyName,
            'reg_no': registrationNumber,
            'phone': companyPhone,
            'email_from': companyEmail,
            'street': f"{addressLine1}, {addressLine2}" if addressLine2 else addressLine1,
            'city': city,
            'zip': postalCode,
            #'date_open': crCreationDate,
            #'date_deadline': crExpiryDate,
            #'date_action': activationDate,
            #'date_conversion': subscribingDate,
            #'create_date': createdAt,
            #'write_date': updatedAt,
            #'state': status,
            #'kyb_status': kybStatus,
            #'terms_conditions': termsConditions,
        }

        lead_id = opportunity = self.env['crm.lead']

        existing_lead = self.env['crm.lead'].sudo().search([('xpl_id', '=', companyId)], limit=1)
        if existing_lead:
            lead_id = opportunity.write(opportunity_values)
        else:
            opportunity_values.update({
                'xpl_id': companyId,
                'is_kyb': True,
                'type': 'opportunity',
                #'team_id': team_id.id,
                #'user_id': 1,
            })

            lead_id = opportunity.create(opportunity_values)
            lead_id.partner_id = self.env['res.partner'].create({
                'name': companyName,
                'company_type': 'company',
                'is_xpendless': True,
                'xpl_id': lead_id.xpl_id,
            })
            if stage_id:
                lead_id.write({
                    'stage_id': stage_id.id,
                })
            lead_id.convert_opportunity(lead_id.partner_id, user_ids=[1], team_id=team_id.id)

            for owner in owners:
                partner_vals = {
                    'name': owner.get('fullName'),
                    'email': owner.get('email'),
                    'mobile': owner.get('mobileNumber'),
                    'xpl_id': owner.get('employeeId'),
                    'parent_id': lead_id.partner_id.id,
                    'company_type': 'person',
                    'type': 'other',
                    'is_xpendless': True,
                }

                existing_partner = self.env['res.partner'].search([('xpl_id', '=', owner.get('employeeId'))], limit=1)
                if existing_partner:
                    existing_partner.write(partner_vals)
                else:
                    self.env['res.partner'].create(partner_vals)

        attachment_ids = []
        for attachment in attachments:
            response = requests.get(attachment['attachmentPath'])
            if response.status_code == 200:
                attachment_vals = {
                    'name': f"{attachment['companyDocId']}_{companyName}.pdf",
                    'datas': base64.b64encode(response.content),
                    'res_model': 'crm.lead',
                    'res_id': lead_id.id,
                    'mimetype': 'application/pdf'
                }
                attachment_id = self.env['ir.attachment'].create(attachment_vals)
                attachment_ids.append(attachment_id.id)

        if attachment_ids:
            message_id = self.env['mail.message'].create({
                'body': 'Attached documents for the company.',
                'model': 'crm.lead',
                'res_id': lead_id.id,
                'record_name': lead_id.name,
                'message_type': 'comment',
                'subtype_id': self.env.ref('mail.mt_comment').id,
                'author_id': 1,
                'attachment_ids': [(6, 0, attachment_ids)]
            })

        return lead_id