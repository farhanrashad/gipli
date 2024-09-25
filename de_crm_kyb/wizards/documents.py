# -*- coding: utf-8 -*-

from odoo import _, api, fields, models, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.tools import format_date, frozendict


class Employee(models.TransientModel):
    _name = 'xpl.kyb.docs'
    _description = "Xpendless KYB Documents"

    xpl_id = fields.Char(string='Document ID')
    name = fields.Char(string='Name')
    url = fields.Char(string='URL')

    def open_document(self):
        return {
            'type': 'ir.actions.act_url',
            'url': self.url,
            'target': 'new', 
        }
        