# -*- coding: utf-8 -*-

import requests
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import json
import base64
from urllib.parse import urlencode

import http.client
import urllib.parse

import logging

_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
    _inherit = 'res.users'

    # -------------------------------------------------------------------
    # ------------------- Discord Token Busines Logic  ------------------
    # -------------------------------------------------------------------
    @api.model
    def _get_discord_config(self):
        client_id = self.env['ir.config_parameter'].sudo().get_param('discord.client_id')
        client_secret = self.env['ir.config_parameter'].sudo().get_param('discord.client_secret')

        access_token = self.env['ir.config_parameter'].sudo().get_param('discord.access_token')
        refresh_token = self.env['ir.config_parameter'].sudo().get_param('discord.refresh_token')
        token_validity = self.env['ir.config_parameter'].sudo().get_param('discord.token_validity')
        
        api_endpoint = 'https://discord.com/api/v10'
        
        return {
            'api_endpoint': api_endpoint, 
            'client_id': client_id, 
            'client_secret': client_secret,
            'access_token': access_token, 
            'refresh_token': refresh_token, 
            'token_validity': token_validity,
        }

    @api.model
    def _get_discord_access_token(self):
        discord = self._get_discord_config()
        self._refresh_discord_access_token()
        return discord['access_token']

    @api.model
    def _refresh_discord_access_token(self):
        discord = self._get_discord_config()
        token_validity_str = discord['token_validity']
        token_validity_dt = fields.Datetime.from_string(token_validity_str) if token_validity_str else None
        API_ENDPOINT = discord['api_endpoint'] + '/oauth2/token'
        if discord['token_validity'] and token_validity_dt > fields.Datetime.now():
            #raise UserError('no')
            return False
        else:
            #raise UserError('yes')
            data = {
                    'grant_type': 'refresh_token',
                    'refresh_token': discord['refresh_token'],
            }
            headers = {
                    'Content-Type': 'application/x-www-form-urlencoded'
            }
            auth = (discord['client_id'], discord['client_secret'])
            try:
                encoded_data = urllib.parse.urlencode(data)
                #raise UserError(encoded_data)
                response = requests.post(API_ENDPOINT, data=encoded_data, headers=headers, auth=auth)
                response.raise_for_status()
    
                expires_in = response.json().get('expires_in')
                token_validity = datetime.now() + timedelta(seconds=expires_in)
            
                self.env['ir.config_parameter'].sudo().set_param('discord.access_token', response.json().get('access_token'))
                self.env['ir.config_parameter'].sudo().set_param('discord.refresh_token', response.json().get('refresh_token'))
                self.env['ir.config_parameter'].sudo().set_param('discord.token_validity', token_validity.strftime('%Y-%m-%d %H:%M:%S'))
            except requests.exceptions.HTTPError as err:
                # Handle HTTP errors
                _logger.error(f"HTTP Error: {err}")
                _logger.error(f"Response text: {response.text}")
                #raise UserError(f"Response text: {response.text}")
            except Exception as e:
                # Handle other exceptions
                _logger.error(f"Error: {e}")
                #raise UserError(f"Error: {e}")

    # -------------------------------------------------------------------
    # ---------------- Discord Operations Busines Logic  ----------------
    # -------------------------------------------------------------------
    @api.model
    def _syn_all_discord(self):
        self._get_discord_guild_ids()
        
    def _get_discord_guild_ids(self):
        discord = self._get_discord_config()
        API_ENDPOINT = discord['api_endpoint'] + '/users/@me/guilds'
        access_token = self._get_discord_access_token()
        
        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        try:
            response = requests.get(API_ENDPOINT, headers=headers)
            response.raise_for_status()  # Check for HTTP errors
    
            guilds = response.json()
            guild_ids = [guild['id'] for guild in guilds]
            guild_ids_str = ','.join(guild_ids)
            self.env['ir.config_parameter'].sudo().set_param('discord.guild_ids', guild_ids_str)
            return True  # Successfully updated config parameter

        except requests.exceptions.HTTPError as err:
            # Handle HTTP errors
            _logger.error(f"HTTP Error: {err}")
            _logger.error(f"Response text: {response.text}")
            return False

        except Exception as e:
            # Handle other exceptions
            _logger.error(f"Error: {e}")
            return False



        
        
    