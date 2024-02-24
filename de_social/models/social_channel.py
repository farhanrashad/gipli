# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SocialChannel(models.Model):
    _name = 'sm.channel'
    _description = 'Social Channel'
    _inherit = ['mail.thread']

    name = fields.Char('Name', required=True, translate=True)
    name_handle = fields.Char('Handle', required=True, translate=True,
                              help="Social media channel or handle name"
                             )
    image = fields.Binary('Image', readonly=True)
    active = fields.Boolean(default=True)

    social_media_id = fields.Many2one('sm.media', string="Social Media", required=True, readonly=True,
        help="Related Social Media (Facebook, Twitter, ...).", ondelete='cascade')
    