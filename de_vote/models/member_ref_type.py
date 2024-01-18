# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
from random import randint


class MemberRefType(models.Model):
    _name = 'vote.member.ref.type'
    _description = 'Member References'
    name = fields.Char(string='Type', required=True, index=True, translate=True) 