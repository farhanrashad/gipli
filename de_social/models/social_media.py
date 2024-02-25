# -*- coding: utf-8 -*-

from odoo import _, fields, models
from odoo.tools import hmac
from odoo.exceptions import UserError


class SocialMedia(models.Model):
    _name = 'sm.media'
    _description = 'Social Media'
    _inherit = ['mail.thread']

    name = fields.Char('Name', required=True, translate=True)
    description = fields.Char('Description', readonly=True)
    image = fields.Binary('Image', readonly=True)
    active = fields.Boolean(default=True)
    color = fields.Integer(string='Color Index', help="The color of the channel")

    channel_ids = fields.One2many('sm.channel', 'social_media_id', string='Channels')
    limit_post_length = fields.Integer('Limit Post Length',
        help="Set a maximum number of characters can be posted in post. 0 for no limit.")

    csrf_token = fields.Char('CSRF Token', compute='_compute_csrf_token',
        help="This token can be used to verify that an incoming request from a social provider has not been forged.")

    def _compute_csrf_token(self):
        for media in self:
            media.csrf_token = hmac(self.env(su=True), 'social_social-account-csrf-token', media.id)
            
    def action_add_channel(self):
        return self._action_add_channel()

    def _action_add_channel(self):
        pass

    def action_social_media_config(self):
        pass