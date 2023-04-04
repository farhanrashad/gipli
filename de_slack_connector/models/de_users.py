from odoo import models, fields, api


class SlackUserData(models.Model):
    _inherit = 'res.users'

    de_sk_user_id = fields.Char('Slack User Id')
    de_sk_user_name = fields.Char('Slack Username', readonly=True)
