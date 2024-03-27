import json
import requests
from odoo import models, api
from odoo.exceptions import UserError
from odoo.addons.base.models.assetsbundle import AssetsBundle

class DiscordWebsocketHandler(models.AbstractModel):
    _name = 'discord.websocket.handler'
    _description = 'Discord WebSocket Handler'

    def get_gateway_url(self):
        response = requests.get("https://discord.com/api/v9/gateway")
        if response.status_code == 200:
            data = response.json()
            return data.get("url")
        else:
            raise UserError("Failed to fetch Gateway URL from Discord API")

    @api.model
    def start_websocket(self):
        gateway_url = self.get_gateway_url()
        if gateway_url:
            # Get token from Odoo model or configuration
            token = self.env['ir.config_parameter'].sudo().get_param('de_discord_connector.discord_bot_token')

            # Initialize WebSocket using Odoo AssetsBundle
            websocket = AssetsBundle().websocket(gateway_url)

            try:
                websocket.connect()
                heartbeat_interval = self.receive_json_response(websocket)["d"]["heartbeat_interval"]
                
                payload = {
                    "op": 2,
                    "d": {
                        "token": token,
                        "intents": 513,
                        "properties": {
                            "$os": "linux",
                            "$browser": "chrome",
                            "device": "pc",
                        }
                    }
                }
                self.send_json_request(websocket, payload)

                while True:
                    event = self.receive_json_response(websocket)
                    try:
                        event_type = event['t']
                        if event_type == 'CHANNEL_CREATE':
                            # Extract channel creation data
                            channel_data = event['d']
                            channel_id = channel_data['id']
                            channel_name = channel_data['name']
                            # Create a new discuss channel in Odoo
                            discuss_channel = self.env['discuss.channel'].create({
                                'name': channel_name,
                                'description': f'Discord Channel: {channel_name}',
                                'discord_channel_id': channel_id,
                                # Add other relevant fields as needed
                            })
                    except Exception as e:
                        pass
            except Exception as e:
                raise UserError(f"An error occurred: {e}")
        else:
            raise UserError("Failed to fetch Gateway URL from Discord API")

        # If WebSocket connection is successfully established
        self.env.user.discord_websocket_status = 'Connected'  # Example: Update status in user's profile

    def send_json_request(self, websocket, request):
        websocket.send(json.dumps(request))

    def receive_json_response(self, websocket):
        response = websocket.recv()
        if response:
            return json.loads(response)
