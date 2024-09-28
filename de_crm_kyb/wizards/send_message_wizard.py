# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from markupsafe import Markup
from odoo import api, fields, models, _
from odoo.tools.mail import is_html_empty


class send_message(models.TransientModel):
    _name = 'crm.kyb.message'
    _description = 'KYB Message'

    lead_ids = fields.Many2many('crm.lead', string='Leads')
    note = fields.Html(
        'Note', sanitize=True
    )
    
    def action_send_message(self):
        self.ensure_one()
        if not is_html_empty(self.note):
            message_content = Markup('<div style="margin-bottom: 4px;"><p>%s:</p>%s<br /></div>') % (
                _('Request Changes'),
                self.note
            )
            
            # Post the message to the chatter
            self.lead_ids.message_post(
                body=message_content,
                subtype_id=self.env.ref('mail.mt_note').id  # This ensures the message is marked as a note in chatter
            )
            stage_id = self.env['crm.stage'].search([('stage_category','=','progress'),('is_kyb','=',True)],limit=1)
            self.lead_ids.write({
                'stage_id': stage_id.id
            })

        
        #res = self.lead_ids.action_set_lost(lost_reason_id=self.lost_reason_id.id)
        #return res