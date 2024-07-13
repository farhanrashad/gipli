# -*- coding: utf-8 -*-

from odoo import fields, models, api

import sys
from odoo.exceptions import UserError, ValidationError



class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    e_invoice_environment = fields.Selection([
        ('Production', 'Production'),
        ('Pre Production', 'Pre Production'),
    ], string='Environment', default='Production', config_parameter='egypt_e_invoice.environment')
    e_invoice_version = fields.Selection([
        ('0.9', '0.9'),
        ('1.0', '1.0'),
    ], string='Environment', default='1.0', config_parameter='egypt_e_invoice.version')
    e_invoice_signature_type = fields.Selection([
        ('Same Server', 'Same Server'),
        ('Middleware', 'Middleware'),
        ('Middleware With Accessable IP', 'Middleware With Accessable IP'),
    ], string='Signature Type', default='Middleware', config_parameter='egypt_e_invoice.signature_type')
    e_invoice_token_pin = fields.Char('Token Pin', config_parameter='egypt_e_invoice.token_pin')
    e_invoice_card_name = fields.Char('Card Name', config_parameter='egypt_e_invoice.card_name')
    e_invoice_certificate = fields.Char('Certificate subjectCN', config_parameter='egypt_e_invoice.certificate')


    e_invoice_client_id = fields.Char('Client ID', config_parameter='egypt_e_invoice.client_id')
    e_invoice_client_pass = fields.Char('Client Secret', config_parameter='egypt_e_invoice.client_pass')

    middleware_url = fields.Char('Middleware URL', config_parameter='egypt_e_invoice.middleware_url')
    middleware_database = fields.Char('Middleware Database', config_parameter='egypt_e_invoice.middleware_database')
    middleware_user = fields.Char('Middleware User', config_parameter='egypt_e_invoice.middleware_user')
    middleware_pass = fields.Char('Middleware Pass', config_parameter='egypt_e_invoice.middleware_pass')


    def get_card_info(self):

        raise ValidationError('Ok')