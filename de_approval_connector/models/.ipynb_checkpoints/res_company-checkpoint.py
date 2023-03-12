# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError

from odoo.tools.misc import formatLang, format_date, get_lang

from datetime import date, timedelta


class ResCompany(models.Model):
    _inherit = 'res.company'
    
    def create_request(self,model,res_id,user_id):
        category_id = self.env['approval.category'].search([('model_id.model','=',model)],limit=1)
        model_id = self.env['ir.model'].search([('model','=',model)],limit=1)
        record_id = self.env[model].search([('id','=',res_id)],limit=1)
        
        name = ''
        company_id = False
        try:
            name = record_id.name
            company_id = record_id.company_id
        except:
            name = record_id.display_name
            company_id = self
            
        request_id = self.env['approval.request'].create({
            'name': name,
            'category_id': category_id.id,
            'company_id': company_id.id,
            'date': fields.Date.today(),
            'reference': name,
            'model_id': model_id.id,
            'res_id': res_id,
            'request_owner_id': user_id.id,
            'request_status': 'new',
            'user_status': 'new',
        })
        return request_id