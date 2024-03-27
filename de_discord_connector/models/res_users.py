# -*- coding: utf-8 -*-

import requests
from odoo import api, fields, models, tools, _
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

        bot_access_token = self.env['ir.config_parameter'].sudo().get_param('discord.bot_access_token')
        
        api_endpoint = 'https://discord.com/api/v10'

        guild_ids = self.env['ir.config_parameter'].sudo().get_param('discord.guild_ids')
        
        return {
            'api_endpoint': api_endpoint, 
            'client_id': client_id, 
            'client_secret': client_secret,
            'access_token': access_token, 
            'refresh_token': refresh_token, 
            'token_validity': token_validity,
            'guild_ids': guild_ids,
            'bot_access_token': bot_access_token,
        }

    @api.model
    def _get_discord_access_token(self, type):
        discord = self._get_discord_config()
        self._refresh_discord_access_token()
        if type == 'oauth':
            token = discord['access_token']
        elif type == 'bot':
            token = discord['bot_access_token']
        return token

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
        #self._get_discord_guild_ids()
        #self._get_discord_channels()
        self._get_discord_messages()
        
    def _get_discord_guild_ids(self):
        discord = self._get_discord_config()
        API_ENDPOINT = discord['api_endpoint'] + '/users/@me/guilds'
        access_token = self._get_discord_access_token('oauth')
        
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

    # Channels
    def _get_discord_channels_backup(self):
        discord = self._get_discord_config()
        #discord_api_token = "Manually given bot token"
        
        discord_api_token = discord['bot_access_token']
        guild_id = "1222329498972852295"  # Replace with the ID of the specific guild
        
        headers = {
            "Authorization": f"Bot {discord_api_token}"
        }
        
        url = f"https://discord.com/api/guilds/{guild_id}/channels"
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for non-200 status codes
        
            data = response.json()
            data_str = json.dumps(data, indent=4)
            raise UserError(data_str)
            raise UserError(data)  # Guild details will be printed here
        
        except requests.exceptions.RequestException as e:
            raise UserError(f"An error occurred: {e}")
    

    def _get_discord_channels(self):
        discord = self._get_discord_config()
        
        API_ENDPOINT = discord['api_endpoint']
        access_token = self._get_discord_access_token('bot')
        guild_ids = discord['guild_ids']
        headers = {
            "Authorization": f"Bot {access_token}"
        }

        if not guild_ids:
            return False  # Server IDs are not available

        server_ids = guild_ids.split(',')
        for server_id in server_ids:
            api_url = f'{API_ENDPOINT}/guilds/{server_id}/channels'
            #response = requests.get(api_url, headers=headers)
            #response.raise_for_status()  # Check for HTTP errors
            #channels = response.json()
            #data_str = json.dumps(channels, indent=4)
            #raise UserError(data_str)
        try:
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()  # Check for HTTP errors
            channels = response.json()
            data_str = json.dumps(channels, indent=4)
            for channel in channels:
                if channel['parent_id']:
                    existing_channel = self.env['discuss.channel'].search([
                        ('discord_channel_id', '=', channel['id'])
                    ], limit=1)
                    if existing_channel:
                        existing_channel.write(self._prepare_discuss_channel_values(channel))
                    else:
                        self.env['discuss.channel'].create(self._prepare_discuss_channel_values(channel))
        except requests.exceptions.HTTPError as err:
            # Handle HTTP errors
            _logger.error(f"HTTP Error: {err}")
            _logger.error(f"Response text: {response.text}")
            raise UserError(f"Response text: {response.text}")
            return False

        except Exception as e:
            # Handle other exceptions
            _logger.error(f"Error: {e}")
            raise UserError(f"Error: {e}")
            return False

    def _prepare_discuss_channel_values(self, channel):
        image_path = 'de_discord_connector/static/description/img/discord.png'
        img = base64.b64encode(tools.misc.file_open(image_path, 'rb').read())
        
        return {
            'name': channel.get('name'),
            'description': channel.get('topic'),
            'discord_channel_id': channel.get('id'),
            'image_128': img,
        }

    # Messages
    def _get_discord_messages(self):
        discord = self._get_discord_config()
        
        API_ENDPOINT = discord['api_endpoint']
        access_token = self._get_discord_access_token('bot')
        headers = {
            "Authorization": f"Bot {access_token}"
        }
        
        channel_ids = self.env['discuss.channel'].search([('discord_channel_id','!=', False)])
        for channel_id in channel_ids:
            api_url = f'{API_ENDPOINT}/channels/{channel_id.discord_channel_id}/messages'
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()  # Check for HTTP errors
            messages = response.json()
            for message in messages:
                self.env['mail.message'].create({
                    'model': 'discuss.channel',
                    'res_id': channel_id.id,
                    'record_name': channle_id.name,
                    'date': message.get('timestamp'),
                    'message_type': 'comment',
                    'subtype_id': ,
                })
            data_str = json.dumps(messages, indent=4)
            raise UserError(data_str)
        
        
    