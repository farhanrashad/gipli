# -*- coding: utf-8 -*-

from odoo import api, fields, Command, models, _
from odoo.exceptions import UserError, AccessError
from odoo.tools import html_escape as escape

import requests
import json

class ApolloResults(models.Model):
    _name = 'apl.results'
    _description = 'Apollo Results'

    name = fields.Char('Name')
    title = fields.Char('title')
    email = fields.Char('Email')