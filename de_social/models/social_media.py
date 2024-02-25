# -*- coding: utf-8 -*-

from odoo import _, fields, models
from odoo.tools import hmac
from odoo.exceptions import UserError
from random import randint

class SocialMedia(models.Model):
    _name = 'sm.media'
    _description = 'Social Media'
    _inherit = ['mail.thread']

    def _default_color(self):
        return randint(1, 11)
        
    name = fields.Char('Name', required=True, translate=True)
    description = fields.Char('Description', readonly=True)
    image = fields.Binary('Image', readonly=True)
    active = fields.Boolean(default=True)

    channel_ids = fields.One2many('sm.channel', 'social_media_id', string='Channels')
    limit_post_length = fields.Integer('Limit Post Length',
        help="Set a maximum number of characters can be posted in post. 0 for no limit.")

    csrf_token = fields.Char('CSRF Token', compute='_compute_csrf_token',
        help="This token can be used to verify that an incoming request from a social provider has not been forged.")

    color = fields.Integer(default=_default_color, 
                           compute='_compute_color', store=True,
                          )
    def _compute_color(self):
        for record in self:
            record.color = randint(1, 11)
            
    def _compute_csrf_token(self):
        for media in self:
            media.csrf_token = hmac(self.env(su=True), 'social_social-account-csrf-token', media.id)
            
    def action_add_channel(self):
        return self._action_add_channel()

    def _action_add_channel(self):
        pass

    def action_social_media_config(self):
        pass