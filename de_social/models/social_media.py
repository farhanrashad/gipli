# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SocialMedia(models.Model):
    _name = 'sm.media'
    _description = 'Social Media'
    _inherit = ['mail.thread']

    name = fields.Char('Name', readonly=True, required=True, translate=True)
    media_description = fields.Char('Description', readonly=True)
    image = fields.Binary('Image', readonly=True)
    active = fields.Boolean('Active')

    def action_add_channel(self):
        pass
