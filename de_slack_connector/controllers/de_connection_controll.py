# -*- coding: utf-8 -*-
from odoo import http
import requests
from odoo.exceptions import ValidationError
import json
from odoo.http import request
import yaml
from slack import WebClient
from datetime import datetime


class TokenControll(http.Controller):
    @http.route('/slack_token/', auth='public')
    def connection_auth(self, **kw):
        try:
            if 'code' in kw:
                IrConfigParameter = request.env['ir.config_parameter'].sudo()
                de_client_id = IrConfigParameter.get_param('de_slack_connector.de_sk_client_id')
                de_client_secret = IrConfigParameter.get_param('de_slack_connector.de_sk_client_secret')

                headers = {
                    'Content-Type': "application/x-www-form-urlencoded",
                }
                url = "https://slack.com/api/oauth.v2.access"

                datas = {
                    "code": kw['code'],
                    "client_id": de_client_id,
                    "client_secret": de_client_secret
                }
                de_response = requests.request("POST", url, data=datas, headers=headers)

                if 'authed_user' in json.loads(de_response.text):
                    de_access_token = json.loads(de_response.text)['authed_user']['access_token']
                    request.env['ir.config_parameter'].set_param('de_slack_connector.access_token', de_access_token)
                    return request.render("de_slack_connector.sucess_message")
                else:
                    return request.render("de_slack_connector.failed_message")

            else:
                return request.render("de_slack_connector.failed_message")

        except Exception as e:
            raise ValidationError(str(e))


class EventsHandler(http.Controller):
    @http.route('/slack/', auth='public', type='json')
    def connection_event(self, **kwarg):
        try:
            data = request.httprequest.data
            try:
                kw_json = yaml.load(data)
                if 'challenge' in kw_json:
                    return kw_json['challenge']
                kw = kw_json['event']

            except Exception as e:
                kw_json = json.loads(data.decode('utf8').replace("'", '"'))
                if 'challenge' in kw_json:
                    return kw_json['challenge']
                kw = kw_json['event']

            IrConfigParameter = request.env['ir.config_parameter'].sudo()
            is_slack = IrConfigParameter.get_param('de_slack_connector.de_sk_check')
            de_token = IrConfigParameter.get_param('de_slack_connector.access_token')

            if de_token and is_slack == 'True':
                partner = request.env.ref('de_slack_connector.res_partner_slack_bot')
                odoo_channel = request.env['mail.channel'].sudo().search([('de_sk_channel_id', '=', kw['channel'])])
                if odoo_channel:
                    odoo_channel = odoo_channel[0]
                de_sc = WebClient(de_token)

                if not odoo_channel:
                    de_slack_channels = de_sc.conversations_info(channel=kw['channel'])
                    de_channels = de_slack_channels.data['channel']
                    odoo_channel = request.env['mail.channel'].sudo().create({
                        'de_sk_channel_id': kw['channel'],
                        'name': de_channels['name'],
                        'alias_user_id': request.env.user.id,
                        'is_subscribed': True,
                        # 'channel_partner_ids': [[6, 0, de_partner_ids]],
                        'channel_partner_ids': [[6, 0, [partner.id]]],
                        # 'channel_message_ids': [[6, 0, de_messages_ids]]
                    })
                user_name = de_sc.users_info(user=kw['user']).data['user']['real_name']
                if 'client_msg_id' in kw:
                    de_mail_message = request.env['mail.message'].sudo().search(
                        [('client_message_id', '=', kw['client_msg_id'])])
                    if not de_mail_message:
                        de_ts = float(kw['ts'])
                        de_date_time = datetime.fromtimestamp(de_ts)
                        # de_message_creator = request.env['res.users'].sudo().search([('de_sk_user_id', '=', de_mail_message['user'])])
                        odoo_channel.message_post(
                            body='<p><b>Message by ' + user_name + ':</b><br><br></p>' + kw['text'],
                            # body=rendered_template,
                            date=de_date_time,
                            client_message_id=kw['client_msg_id'],
                            author_id=partner.id,
                            email_from='partner_email',
                            channel_ids=odoo_channel.ids
                        )
                        de_mail_message.sudo().write({
                            'client_message_id': kw['client_msg_id'],
                        })
                elif 'files' in kw:
                    for file in kw['files']:
                        de_mail_message = request.env['mail.message'].sudo().search(
                            [('client_message_id', '=', file['id'])])

                        if not de_mail_message:
                            de_ts = float(file['timestamp'])
                            de_date_time = datetime.fromtimestamp(de_ts)

                            my_dict = {
                                'url': file['url_private_download'],
                                'file_name': file['name'],
                            }
                            rendered_template = request.env.ref(
                                'de_slack_connector.message_slack_notification').render(my_dict)
                            string = '<p><b>Message by ' + user_name + ':</b><br><br></p>'
                            odoo_channel.message_post(
                                subject=file['name'],
                                body=string.encode('utf-8') + rendered_template,
                                date=de_date_time,
                                client_message_id=file['id'],
                                author_id=partner.id,
                                email_from='partner_email',
                                channel_ids=odoo_channel.ids
                            )
                # channel in kw
                request.env.cr.commit()
        except Exception as e:
            raise ValidationError(str(e))

