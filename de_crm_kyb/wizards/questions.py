# -*- coding: utf-8 -*-

from odoo import _, api, fields, models, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.tools import format_date, frozendict


class Employee(models.TransientModel):
    _name = 'xpl.kyb.questions'
    _description = "Xpendless KYB Questions"

    name = fields.Char(string='Name')
    desc = fields.Char(string='Description')