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

    channel_ids = fields.One2many('sm.channel', 'social_media_id', string='Channels')
    max_post_length = fields.Integer('Max Post Length',
        help="Set a maximum number of characters can be posted in post. 0 for no limit.")
    
    def action_add_channel(self):
        pass
