# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Genre(models.Model):
    _name = 'lib.genre'
    _description = 'Book Genre'

    name = fields.Char(string='Name', required=True)