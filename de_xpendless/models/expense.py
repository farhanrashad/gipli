# -*- coding: utf-8 -*-

from odoo import api, fields, Command, models, _
from odoo.exceptions import UserError, AccessError

class Expenses(models.Model):
    _name = 'xpl.expense'
    _description = 'Xpendless Expense'

    