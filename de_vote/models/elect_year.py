# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import random

from babel.dates import format_date
from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.release import version


class ElectionYear(models.Model):
    _name = "vote.elect.year"
    _description = "Election Year"
    _order = "name asc"

    READONLY_STATES = {
        'progress': [('readonly', True)],
        'close': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    
    active = fields.Boolean(default=True)
    name = fields.Char(string='Name', required=True, index='trigram', translate=True)
    date_start = fields.Date(string='Start Date',  compute='_compute_all_dates', store=True, readonly=False, required=True, states=READONLY_STATES,)
    date_end = fields.Date(string='End Date',  compute='_compute_all_dates', store=True, readonly=False, required=True, states=READONLY_STATES,)
    description = fields.Html(string='Description')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('progress', 'Open'),
        ('close', 'Closed'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)


    def unlink(self):
        for record in self:
            if record.state != 'draft' and record.no_of_applicants > 0:
                raise exceptions.UserError("You cannot delete a record with applicants when the status is not 'Draft'.")
        return super(AdmissionRegister, self).unlink()

    def button_draft(self):
        self.write({'state': 'draft'})
        return {}

    def button_open(self):
        self.write({'state': 'progress'})
        return {}

    def button_close(self):
        self.write({'state': 'close'})
        return {}
        
    def button_cancel(self):
        self.write({'state': 'draft'})
        return {}