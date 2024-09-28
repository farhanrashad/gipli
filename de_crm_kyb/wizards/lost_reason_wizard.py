# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from markupsafe import Markup
from odoo import api, fields, models, _
from odoo.tools.mail import is_html_empty


class CrmLeadLost(models.TransientModel):
    _inherit = 'crm.lead.lost'

    def action_lead_kyb_lost(self):
        self.ensure_one()
        if not is_html_empty(self.lost_feedback):
            self.lead_ids._track_set_log_message(
                Markup('<div style="margin-bottom: 4px;"><p>%s:</p>%s<br /></div>') % (
                    _('Lost Comment'),
                    self.lost_feedback
                )
            )
            message_content = Markup('<div style="margin-bottom: 4px;"><p>%s:</p>%s<br /></div>') % (
                _('Reject'),
                self.lost_feedback
            )

            self.lead_ids.message_post(
                    body=message_content,
                    subtype_id=self.env.ref('mail.mt_note').id  # This ensures the message is marked as a note in chatter
                )
            
            stage_id = self.env['crm.stage'].search([('stage_category','=','cancel'),('is_kyb','=',True)],limit=1)
            self.lead_ids.write({
                'stage_id': stage_id.id,
                'active': False,
            })

            for lead in lead_ids:
                lead._update_company_status('Verified', comment=self.lost_feedback)
        
        res = self.lead_ids.action_set_lost(lost_reason_id=self.lost_reason_id.id)
        return res