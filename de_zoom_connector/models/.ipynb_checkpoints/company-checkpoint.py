# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from zoomus import ZoomClient
import json
import requests
from datetime import datetime


class CompanySettings(models.Model):
    """
    Zoom API Key, API Secret, Test Connection etc
    """

    _inherit = "res.company"

    meeting_event_mail_notification = fields.Boolean("Meeting event mail notification", default=True)
    zoom_admin_user_id = fields.Many2one('res.users')
    api_key = fields.Char("API Key")
    api_secret = fields.Char("API Secret")

    def test_connection(self):

        company_rec = self.env.user.company_id
        if company_rec.api_key and company_rec.api_secret:
            try:
                client = ZoomClient(company_rec.api_key, company_rec.api_secret)

            except Exception as e:
                raise UserError(_('API credential invalid', e))
            if self.env.user.zoom_login_email:
                users = client.user.list()
                if users.status_code == 200:
                    user_response = json.loads(users.content.decode('utf-8'))
                    all_users = user_response['users']

                else:
                    raise UserError(_('Please Check Your Zoom Credentials!'))

            else:
                raise UserError(_('You Have Not Sett Zoom Email In Users!'))

            context = dict(self._context)
            context['message'] = 'Connection Successful!'
            return self.message_wizard(context)

        else:
            raise UserError(_('Please Enter Credentials First!'))

    def message_wizard(self, context):
        return {
            'name': ('Success'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'message.wizard',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context
        }
