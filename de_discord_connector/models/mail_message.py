# -*- coding: utf-8 -*-

from odoo import models, fields

class MailMessage(models.Model):
    _inherit = 'mail.message'

    discord_message_id = fields.Char(string='Discord Message ID', readonly=True)
