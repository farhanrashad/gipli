# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class User(models.Model):
    """
    Storing user email along id and timezone
    """

    _inherit = "res.users"

    zoom_login_email = fields.Char("Account")

    zoom_login_user_id = fields.Char("Zoom user id")

    zoom_user_timezone = fields.Char("Zoom user timezone")