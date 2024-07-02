# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError


class Lead(models.Model):
    _inherit = "crm.lead"

    is_kyb = fields.Boolean(default=False, compute='_compute_kyb', store=True)
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

    # Actions
    def _cron_import_company_from_xpl(self):
        raise UserError('hello')

    from odoo import models, fields, api

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def create_or_update_opportunity(self, json_data):
        opportunity_values = {}

        partner_vals = {}
        
        companyId = int(json_data.get('id'))
        companyName = json_data.get('companyName')
        registrationNumber = json_data.get('registrationNumber')
        addressLine1 = json_data.get('addressLine1')
        addressLine2 = json_data.get('addressLine2')
        city = json_data.get('city')
        postalCode = json_data.get('postalCode')
        companyEmail = json_data.get('companyEmail')
        companyPhone = json_data.get('companyPhone')
        crCreationDate = json_data.get('crCreationDate')
        crExpiryDate = json_data.get('crExpiryDate')
        activationDate = json_data.get('activationDate')
        subscribingDate = json_data.get('subscribingDate')
        createdAt = json_data.get('createdAt')
        updatedAt = json_data.get('updateAt')
        status = json_data.get('status')
        kybStatus = json_data.get('kybStatus')
        termsConditions = json_data.get('termsConditions')
        submittedFields = json_data.get('submittedFields', [])
        attachments = json_data.get('attachments', [])
        companySettings = json_data.get('CompanySettings', {})
        
        owners = json_data.get('Owners', [])

        team_id = self.env['crm.team'].sudo().search([
            ('is_kyb','=',True)
        ],limit=1)
        # Example: Creating or updating an Opportunity record
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
                    'is_xpendless':True,
                }
            
                # Check if partner already exists
                existing_partner = self.env['res.partner'].search([('xpl_id', '=', owner.get('employeeId'))], limit=1)
                if existing_partner:
                    existing_partner.write(partner_vals)
                else:
                    self.env['res.partner'].create(partner_vals)
                
           
        return lead_id

