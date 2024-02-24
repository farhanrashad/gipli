# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SocialMedia(models.Model):
    _name = 'sm.media'
    _description = 'Social Media'
    _inherit = ['mail.thread']

    name = fields.Char('Name', required=True, translate=True)
    description = fields.Char('Description', readonly=True)
    image = fields.Binary('Image', readonly=True)
    active = fields.Boolean(default=True)

    def action_add_channel(self):
        pass
