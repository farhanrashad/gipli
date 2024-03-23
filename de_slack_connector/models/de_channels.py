# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ChannelData(models.Model):
    _inherit = "mail.channel"

    de_sk_channel_id = fields.Char('Slack Channel Id')
