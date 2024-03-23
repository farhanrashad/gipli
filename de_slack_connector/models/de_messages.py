# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
# from slackclient import SlackClient
from slack import WebClient
from odoo.exceptions import UserError, ValidationError, Warning


class MailMessage(models.Model):
    _inherit = 'mail.message'

    client_message_id = fields.Char('Client Message Id')

    @api.model
    def create(self, values):
        try:
            IrConfigParameter = self.env['ir.config_parameter'].sudo()
            is_slack = IrConfigParameter.get_param('de_slack_connector.de_sk_check')
            if is_slack == 'True':
                token = IrConfigParameter.get_param('de_slack_connector.access_token')
                sc = WebClient(token)
                if values['body'] == 'Contact created':
                    return super(MailMessage, self).create(values)
                elif 'client_message_id' not in values:
                    if values['model'] == 'mail.channel':
                        channel = self.env['mail.channel'].search([('id', '=', values['res_id'])])
                        if channel.channel_type == 'channel' and values['message_type'] != 'notification':
                            # values['attachment_ids'][0]
                            # if values['attachment_ids']:
                            #     for file in values['attachment_ids']:
                            #         file_ref = self.env['ir.attachment'].search([('id', '=', file[1])])
                            #         sc.files_upload(channel=channel['de_sk_channel_id'], file='hello.xlsx', content=file_ref.datas.decode('utf-8'))
                            #         print('test')

                            # sc.files_upload(file=self.env['ir.attachment'].search([('id', '=', 4)]).datas,
                            #                 channels=channel['de_sk_channel_id'], filename='test')
                            sc.chat_postMessage(
                                channel=channel['de_sk_channel_id'],
                                text=f'Message by "{self.env.user.name}"\n' + values['body'],
                                username=self.env.user.de_sk_user_name,
                                # username='slackbot',
                                icon_emoji='true'
                            )
                            return super(MailMessage, self).create(values)
                        elif channel.channel_type == 'chat' and values['message_type'] != 'notification':
                            slack_user = \
                            self.env['mail.channel'].search([('id', '=', values['res_id'])]).channel_partner_ids[0]
                            slack_user_id = slack_user.user_ids[0].de_sk_user_id
                            userChannel = sc.conversations_open(users=slack_user_id)
                            if userChannel:
                                # if values['attachment_ids']:
                                #     for file in values['attachment_ids']:
                                #         file_ref = self.env['ir.attachment'].search([('id', '=', 286)])
                                #         print('stop')
                                #         # sc.files_upload(channel=userChannel['channel']['id'],
                                #         #                 content=file_ref.datas.decode('utf-8'))
                                #         sc.files_upload(channel=userChannel['channel']['id'], filename='hello.xlsx',
                                #                         file=file_ref.datas)
                                #         print('test')
                                send_message = sc.chat_postMessage(
                                    channel=userChannel['channel']['id'],
                                    text=f'Message by "{self.env.user.name}"\n' + values['body'],
                                    username=self.env.user.de_sk_user_name,
                                    # username='slackbot',
                                    icon_emoji='true'
                                )
                                return super(MailMessage, self).create(values)
                        else:
                            return super(MailMessage, self).create(values)
                    elif 'OdooBot' in values['email_from']:
                        return super(MailMessage, self).create(values)

                    else:
                        return super(MailMessage, self).create(values)
                else:
                    return super(MailMessage, self).create(values)
            else:
                return super(MailMessage, self).create(values)
        except Exception as e:
            raise UserError(_('Please invite logged in user to slack before sending a message or please '
                              'disable slack to just send a normal message!'))
            # raise ValueError(str(e))