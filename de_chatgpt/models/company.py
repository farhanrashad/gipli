# -*- coding: utf-8 -*-

from odoo import fields, models, _

class ResCompany(models.Model):
    _inherit = "res.company"

    openai_key = fields.Char(string="API Key", help="Provide the API key here")
    #gpt_model_id = fields.Many2one("gpt.model", string="Exchange Gain or Loss Journal")
    gpt_model = fields.Selection(
        selection=[
            ('gpt-4', 'gpt-4'),
            ('gpt-3.5-turbo', 'gpt-3.5-turbo'),
            ('gpt-3.5-turbo-0301', 'gpt-3.5-turbo-0301'),
            ('gpt-3.5-turbo-0613', 'gpt-3.5-turbo-0613'),
            ('gpt-3.5-turbo-16k-0613', 'gpt-3.5-turbo-16k-0613'),
            ('gpt-3.5-turbo-16k', 'gpt-3.5-turbo-16k'),
            ('gpt-3.5-turbo-1106', 'gpt-3.5-turbo-1106'),
            ('gpt-3.5-turbo-instruct', 'gpt-3.5-turbo-instruct'),
            ('gpt-3.5-turbo-instruct-0914', 'gpt-3.5-turbo-instruct-0914'),
            ('gpt-4-0613', 'gpt-4-0613'),
            ('gpt-4-1106-preview', 'gpt-4-1106-preview'),
            ('gpt-4-vision-preview', 'gpt-4-vision-preview'),
            ('gpt-4-0314', 'gpt-4-0314'),
        ],
        string="GPT Model")



