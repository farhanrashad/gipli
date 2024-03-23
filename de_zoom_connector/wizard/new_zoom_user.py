# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

from odoo.exceptions import UserError, ValidationError
import json
from zoomus import ZoomClient


class CreateNewZoomUser(models.TransientModel):
    _name = "create.zoom.account"

    first_name = fields.Char('First Name')
    last_name = fields.Char('Last Name')

    user_id = fields.Many2one('res.users')
    email = fields.Char('Email')

    type_of_user = fields.Selection([
        ('basic', 'Basic'),
        ('licensed', 'Licensed')
    ], string='User Type', default='basic')

    @api.onchange('user_id')
    def setting_fname_lname_email(self):
        # print('funtion')

        if self.user_id:
            name = self.user_id.name.split(" ", 1)
            self.first_name = name[0]
            if len(name) != 1:
                self.last_name = name[1]
            else:
                self.last_name = ''
            self.email = self.user_id.email

    def new_user_creation(self):
        # print('funtion')

        client = self.api_connection()
        if self.type_of_user == 'basic':
            type = 1
        else:
            type = 2

        kwargs = {'email': self.email,
                  'type': type,
                  'first_name': self.first_name,
                  'last_name': self.last_name
                  }

        responce = client.user.create(action="create", user_info=kwargs)

        responce_value = json.loads(responce.content.decode('utf-8'))

        if responce.status_code == 201:
            self.user_id.zoom_login_email = self.email

        else:
            raise UserError(_('Zoom API Exception:\n %s.') % responce_value['message'])

    def api_connection(self):
        """
         Checking Crediontionals With The Zoom API
        """
        # print('funtion')

        company_rec = self.env.user.company_id
        if company_rec.api_key and company_rec.api_secret:
            try:
                client = ZoomClient(company_rec.api_key, company_rec.api_secret)

            except Exception as e:
                raise UserError(_('You Might Have Entered Wrong Credential Of Zoom!', e))

            return client
        else:
            raise UserError(_('You Might Have Entered Wrong Credential Of Zoom!'))