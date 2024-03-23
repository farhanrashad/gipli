# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class CalendlyEventType(models.Model):
    _name = 'calendly.event.type'
    _description = 'Calendly Event Type'

    name = fields.Char(string='Name', required=True)
    uri = fields.Char(string='URI', required=True)
    description = fields.Text(string='Description')
    duration = fields.Integer(string='Duration')
    location = fields.Char(string='Location')

    _sql_constraints = [
        ('unique_uri', 'UNIQUE(uri)', 'URI must be unique!'),
    ]
    