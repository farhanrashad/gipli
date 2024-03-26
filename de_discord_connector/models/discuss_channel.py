# -*- coding: utf-8 -*-

from odoo import models, fields

class DiscussChannel(models.Model):
    _inherit = 'discuss.channel'

    discord_channel_id = fields.Char(string='Discord Channel ID', readonly=True)
