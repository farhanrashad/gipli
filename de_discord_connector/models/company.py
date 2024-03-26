# -*- coding: utf-8 -*-

import requests
from odoo import models, fields
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import json
import base64
from urllib.parse import urlencode

import http.client

DISCORD_BASE_URL = 'https://discord.com/api/v10'

class ResCompany(models.Model):
    _inherit = 'res.company'

    is_discord = fields.Boolean('Discord')
    discord_client_id = fields.Char(string='Client ID')
    discord_client_secret = fields.Char(string='Client secret')
    discord_webhook_signing_key = fields.Char(string='Webhook signing key')
        
    discord_access_token = fields.Char(string='Access Token')
    discord_refresh_token = fields.Char(string='Refresh Token')
    discord_token_validity = fields.Datetime('Token Validity', copy=False)
    discord_generated_access_token = fields.Boolean(string='Access Token Generated')