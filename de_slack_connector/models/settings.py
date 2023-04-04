import socket
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
# from slackclient import SlackClient
from slack import WebClient
from datetime import datetime
import requests
from openerp.exceptions import Warning, ValidationError, UserError


class ConnectionSett(models.TransientModel):
    _inherit = 'res.config.settings'

    de_sk_check = fields.Boolean('Slack', default=False)
    de_sk_client_id = fields.Char('Client Id')
    de_sk_client_secret = fields.Char('Client Secret')

    def set_values(self):
        res = super(ConnectionSett, self).set_values()
        self.env['ir.config_parameter'].set_param('de_slack_connector.de_sk_check', self.de_sk_check)
        self.env['ir.config_parameter'].set_param('de_slack_connector.de_sk_client_id', self.de_sk_client_id)
        self.env['ir.config_parameter'].set_param('de_slack_connector.de_sk_client_secret', self.de_sk_client_secret)

        return res

    @api.model
    def get_values(self):
        res = super(ConnectionSett, self).get_values()
        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        is_slack = IrConfigParameter.get_param('de_slack_connector.de_sk_check')
        client_id = IrConfigParameter.get_param('de_slack_connector.de_sk_client_id')
        client_secret = IrConfigParameter.get_param('de_slack_connector.de_sk_client_secret')

        res.update(
            de_sk_check=True if is_slack == 'True' else False,
            de_sk_client_id=client_id,
            de_sk_client_secret=client_secret,
        )

        return res

    def test_credentials(self):
        # cr = self._cr
        # print('sql test')
        #
        # query = "SELECT attachment_id FROM partner_ir_attachments_rel WHERE partner_id=" + str(self.id) + ""
        # cr.execute(query)
        # result = cr.fetchall()
        #
        # print('sql test end')

        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        de_client_id = IrConfigParameter.get_param('de_slack_connector.de_sk_client_id')
        return {
            'name': 'Go to website',
            'res_model': 'ir.actions.act_url',
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': 'https://slack.com/oauth/v2/authorize?user_scope=channels:history,channels:read,'
                   'channels:write,users:read,users:read.email,files:write,im:write,chat:write&client_id=' + de_client_id
        }

    def de_sk_users_import(self):
        try:
            de_sk_token = self.env['ir.config_parameter'].get_param('de_slack_connector.access_token')
            if not de_sk_token:
                raise UserError(_('Please Check Your Credentials.Token Not Found!'))
            de_sc = WebClient(de_sk_token)
            de_slack_users = de_sc.api_call('users.list')
            de_users = de_slack_users['members']
            for de_user in de_users:
                if de_user['name'] != 'slackbot' and 'email' in de_user['profile']:
                    de_odoo_user = self.env['res.users'].search([('login', '=', de_user['profile']['email'])])
                    if not de_odoo_user:
                        self.env['res.users'].create({
                            'de_sk_user_id': de_user['id'],
                            'de_sk_user_name': de_user['profile']['real_name'],
                            'name': de_user['profile']['real_name'],
                            'login': de_user['profile']['email'],
                            'email': de_user['profile']['email'],
                            'sel_groups_1_8_9': 8
                        })
                    else:
                        de_odoo_user.write({
                            'de_sk_user_id': de_user['id'],
                            'de_sk_user_name': de_user['profile']['real_name'],
                        })
                    self.env.cr.commit()

            context = dict(self._context)
            context['message'] = 'Operation Successful!'
            return self.message_wizard(context)

        except UserError as e:
            raise UserError('Please Check Your Credentials.Token Not Found!')

        except Exception as e:
            raise ValueError(str(e))

    def message_wizard(self, context):
        return {
            'name': ('Success'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'message.wizard',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context
        }

    def schdular_function(self):
        self.de_sk_channels_import()

    def sync_data_auto(self):
        done = False
        while not done:
            try:
                scheduler = self.env['ir.cron'].search([('name', '=', 'Auto:Slack Conversation')])
                if not scheduler:
                    scheduler = self.env['ir.cron'].search([('name', '=', 'Auto:Slack Conversation'),
                                                            ('active', '=', False)])
                scheduler.active = True
                scheduler.interval_number = 1
                scheduler.interval_type = 'minutes'

                self.env.cr.commit()
                done = True
            except Exception as e:
                raise ValidationError(str(e))

    def de_sk_channels_import(self):
        try:
            de_token = self.env['ir.config_parameter'].get_param('de_slack_connector.access_token')
            if not de_token:
                raise UserError('Please Check Your Credentials.Token Not Found!')
            de_sc = WebClient(de_token)
            de_slack_channels = de_sc.api_call('conversations.list')
            de_channels = de_slack_channels['channels']
            for de_channel in de_channels:
                # de_partner_ids = self._de_get_channel_users(de_sc, de_channel['id'])
                partner = self.env.ref('de_slack_connector.res_partner_slack_bot')
                # de_messages_ids = self._de_get_channel_messages(de_sc, de_channel['id'])
                odoo_channel = self.env['mail.channel'].search([('name', '=', de_channel['name'])])

                if not odoo_channel:
                    odoo_channel = self.env['mail.channel'].create({
                        'de_sk_channel_id': de_channel.get('id'),
                        'name': de_channel.get('name'),
                        'alias_user_id': self.env.user.id,
                        'is_subscribed': True,
                        # 'channel_partner_ids': [[6, 0, de_partner_ids]],
                        'channel_partner_ids': [[6, 0, [partner.id]]],
                        # 'channel_message_ids': [[6, 0, de_messages_ids]]
                    })

                de_channel_messages = de_sc.conversations_history(channel=de_channel['id'])
                de_messages = de_channel_messages['messages']
                for de_message in de_messages:
                    user_name = de_sc.users_info(user=de_message['user']).data['user']['real_name']
                    if 'client_msg_id' in de_message:
                        de_mail_message = self.env['mail.message'].search(
                            [('client_message_id', '=', de_message['client_msg_id'])])
                        if not de_mail_message:
                            de_ts = float(de_message['ts'])
                            de_date_time = datetime.fromtimestamp(de_ts)
                            # msg_dict = {
                            #     'txt': de_message['text'],
                            #     'uname': user_name,
                            # }
                            # rendered_template = self.env.ref('de_slack_connector.message_message_notification').render(
                            #     msg_dict)

                            odoo_channel.message_post(
                                body='<p><b>Message by ' + user_name + ':</b><br><br></p>' + de_message['text'],
                                # body=rendered_template,
                                date=de_date_time,
                                client_message_id=de_message['client_msg_id'],
                                author_id=partner.id,
                                email_from='partner_email',
                                channel_ids=odoo_channel.ids
                            )
                            de_mail_message.write({
                                'client_message_id': de_message['client_msg_id'],
                            })
                    elif 'files' in de_message:
                        for file in de_message['files']:
                            de_mail_message = self.env['mail.message'].search(
                                [('client_message_id', '=', file['id'])])

                            if not de_mail_message:
                                de_ts = float(file['timestamp'])
                                de_date_time = datetime.fromtimestamp(de_ts)

                                my_dict = {
                                    'url': file['url_private_download'],
                                    'file_name': file['name'],
                                }
                                rendered_template = self.env.ref(
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

                self.env.cr.commit()

            context = dict(self._context)
            context['message'] = 'Operation Successful!'
            return self.message_wizard(context)

        except UserError as e:
            raise UserError('Please Check Your Credentials.Token Not Found!')

        except Exception as e:
            raise ValueError(str(e))

    def _de_get_channel_users(self, de_sc, channel_id):
        try:
            partner_ids = []
            # channel_users = sc.api_call('users.list', channel=channel_id)
            de_channel_users = de_sc.users_list(channel=channel_id)
            if 'members' in de_channel_users:
                de_users = de_channel_users['members']
                for de_user in de_users:
                    if de_user['name'] != 'slackbot' and 'email' in de_user['profile']:
                        odoo_user = self.env['res.users'].search([('login', '=', de_user['profile']['email'])])
                        if not odoo_user:
                            odoo_user = self.env['res.users'].create({
                                'de_sk_user_id': de_user['id'],
                                'name': de_user['profile']['real_name'],
                                'de_sk_user_name': de_user['profile']['real_name'],
                                'login': de_user['profile']['email'],
                                'email': de_user['profile']['email'],
                                'sel_groups_1_8_9': 8
                            })
                        else:
                            odoo_user.write({
                                'de_sk_user_id': de_user['id'],
                                'de_sk_user_name': de_user['profile']['real_name'],
                            })
                        self.env.cr.commit()
                        partner_ids.append(odoo_user.partner_id.id)
            return partner_ids
        except Exception as e:
            raise ValueError(str(e))

    def _de_get_channel_messages(self, de_sc, channel_id):
        try:
            messages_ids = []
            # channel_messages = sc.api_call('conversations.history', channel=channel_id)
            de_channel_messages = de_sc.conversations_history(channel=channel_id)
            de_messages = de_channel_messages['messages']
            for de_message in de_messages:
                # de_messages[0]['files'][0]['url_private_download']
                if 'client_msg_id' in de_message:
                    de_mail_message = self.env['mail.message'].search(
                        [('client_message_id', '=', de_message['client_msg_id'])])
                    if not de_mail_message:
                        de_ts = float(de_message['ts'])
                        de_date_time = datetime.fromtimestamp(de_ts)
                        de_message_creator = self.env['res.users'].search([('de_sk_user_id', '=', de_message['user'])])
                        de_mail_message = self.env['mail.message'].create({
                            'subject': de_message['text'],
                            'date': de_date_time,
                            'body': de_message['text'],
                            'client_message_id': de_message['client_msg_id'],
                            'email_from': de_message_creator.email,
                            'author_id': de_message_creator.partner_id.id,
                            'message_type': 'comment'
                        })
                    messages_ids.append(de_mail_message.id)
                elif 'files' in de_message:
                    for file in de_message['files']:
                        de_mail_message = self.env['mail.message'].search(
                            [('client_message_id', '=', file['id'])])

                        if not de_mail_message:
                            de_ts = float(file['timestamp'])
                            de_date_time = datetime.fromtimestamp(de_ts)
                            de_message_creator = self.env['res.users'].search(
                                [('de_sk_user_id', '=', file['user'])])
                            de_mail_message = self.env['mail.message'].create({
                                'subject': file['name'],
                                'date': de_date_time,
                                'body': file['url_private_download'],
                                'client_message_id': file['id'],
                                # 'email_from': de_message_creator.email,
                                'author_id': de_message_creator.partner_id.id,
                                'message_type': 'comment'
                            })
                        messages_ids.append(de_mail_message.id)
            return messages_ids
        except Exception as e:
            raise ValueError(str(e))
