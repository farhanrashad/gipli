# -*- coding: utf-8 -*-

from odoo import fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    #openai_key = fields.Char(string="API Key", help="Provide the API key here", config_parameter="de_chatgpt.openapi_api_key")
    gpt_model_id = fields.Many2one('gpt.model', 'GPT Model', ondelete='cascade',   config_parameter="de_chatgpt.gpt_model")

    openai_key = fields.Char(related="company_id.openai_key", readonly=False)
    #gpt_model_id = fields.Many2one(
    #    comodel_name='gpt.model',
    #    #related="company_id.gpt_model_id", 
    #    check_company=True,
    #    readonly=False,
    #)
    gpt_model = fields.Selection(string="GPT Model", readonly=False, related='company_id.gpt_model')

