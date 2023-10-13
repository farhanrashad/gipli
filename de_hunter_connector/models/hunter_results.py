# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError

class HunterResults(models.Model):
    _name = 'hunter.results'
    _description = 'Hunter Search Results'

    name = fields.Char(string='Name')
    email = fields.Char(string='Email')
    position = fields.Char(string='Position', readonly=True)
    department = fields.Char(string='Department', readonly=True)
    phone = fields.Char(string='Phone', readonly=True)
    website = fields.Char(string='Website', readonly=True)

    country = fields.Char(string='Country', readonly=True)
    state = fields.Char(string='State', readonly=True)
    city = fields.Char(string='City', readonly=True)
    street = fields.Char(string='Street', readonly=True)
    postal_code = fields.Char(string='Postal Code', readonly=True)

    company_name = fields.Char(string='Company Name')
    description = fields.Html(string='Description')

    lead_id = fields.Many2one('crm.lead', string="Lead")
    partner_id = fields.Many2one('res.partner', string="Partner")

    status_converted = fields.Selection([
        ('lead', 'Lead'), ('contact', 'Contact')
    ])

    def action_convert_contacts(self):
        ''' Open the apl.convert.data.wizard wizard to convert search results into Odoo contacts
        '''
        return {
            'name': _('Convert into Contacts'),
            'res_model': 'hunter.convert.data.wizard',
            'view_mode': 'form',
            'context': {
                'active_model': 'hunter.results',
                'active_ids': self.ids,
                'op_name': 'contacts',
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def action_convert_leads(self):
        ''' Open the apl.convert.data.wizard wizard to convert search results into Odoo leads
        '''
        return {
            'name': _('Convert into Leads'),
            'res_model': 'hunter.convert.data.wizard',
            'view_mode': 'form',
            'context': {
                'active_model': 'hunter.results',
                'active_ids': self.ids,
                'op_name': 'leads',
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def action_open_details(self):
        return {
            'name': 'Contact Detail',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hunter.results',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }