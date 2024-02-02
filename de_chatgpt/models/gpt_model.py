# -*- coding: utf-8 -*-

from odoo import fields, models, _


class GPTModel(models.TransientModel):
    _name = "gpt.model"
    _description = 'GPT Model'

    name = fields.Char(string="name", required=True)