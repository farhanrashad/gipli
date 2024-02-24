# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SocialPipeline(models.Model):
    _name = 'sm.pipeline'
    _description = 'Social Pipeline'

    name = fields.Char('Name', required=True)
    