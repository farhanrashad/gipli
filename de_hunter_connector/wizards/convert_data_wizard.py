# -*- coding: utf-8 -*-

import requests
import json

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import pprint

from urllib.parse import urlparse

class ConvertDataWizard(models.TransientModel):
    _name = "hunter.convert.data.wizard"
    _description = 'Convert Hunter Data into Odoo (Wizard)'

    op_name = fields.Char(string='Operation')

    type = fields.Selection([
        ('lead', 'Lead'), ('opportunity', 'Opportunity')], required=True, tracking=15, index=True,
        default=lambda self: 'lead' if self.env['res.users'].has_group('crm.group_use_lead') else 'opportunity')

    @api.model
    def default_get(self, fields):
        res = super(ConvertDataWizard, self).default_get(fields)
        if 'op_name' in self._context:
            res['op_name'] = self._context.get('op_name')
        return res
    
    def action_process(self):
        active_model = self.env.context.get('active_model')
        active_ids = self.env.context.get('active_ids', [])
        record_ids = self.env[active_model].search([('id','in',active_ids)])
        for record in record_ids:
            country_id = self.env['res.country'].search([('name','=',record.country)],limit=1)
            state_id = self.env['res.country.state'].search([('name','=',record.state)],limit=1)
            if self.op_name == 'contacts' and record.status_converted != 'contact':
                vals = {
                    'name': record.name,
                    'function': record.position,
                    'email': record.email,
                    'phone': record.phone,
                    'website': record.website,
                    'city': record.city,
                    'country_id': country_id.id,
                    'state_id': state_id.id,
                    'street': record.street,
                    'zip': record.postal_code,
                    'comment': record.description,
                    'company_type': 'person',
                }
                partner_id = self.env['res.partner'].create(vals)
                if record.company_name:
                    company_partner_id = self.env['res.partner'].search([('name','=',record.company_name),('company_type','=','company')],limit=1)
                    if not company_partner_id:
                        comp_vals = {
                            'name': record.company_name,
                            'website': record.website,
                            'city': record.city,
                            'country_id': country_id.id,
                            'state_id': state_id.id,
                            'company_type': 'company',
                        }
                        company_partner_id = self.env['res.partner'].create(comp_vals)
                    partner_id.write({
                        'parent_id': company_partner_id.id,
                    })
                record.write({
                    'status_converted': 'contact',
                })
            elif self.op_name == 'leads'  and record.status_converted != 'lead':
                vals = {
                    'name': record.name,
                    'contact_name': record.name,
                    'function': record.position,
                    'email_from': record.email,
                    'city': record.city,
                    'country_id': country_id.id,
                    'state_id': state_id.id,
                    'street': record.street,
                    'zip': record.postal_code,
                    'type': self.type,
                    'partner_name': record.company_name,
                    'website': record.website,
                    'description': record.description,
                }
                lead_id = self.env['crm.lead'].create(vals)
                record.write({
                    'status_converted': 'lead',
                })

        