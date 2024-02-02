# -*- coding: utf-8 -*-

from openai import OpenAI

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Channel(models.Model):
    _inherit = 'discuss.channel'