# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ResUsers(models.Model):
    _inherit = 'res.users'

    target_ticket_closed = fields.Integer(string='Target Tickets to Close', default=1)
    target_ticket_rating = fields.Float(string='Target Rating', default=85)
    target_ticket_success = fields.Float(string='Target Success Rate', default=85)