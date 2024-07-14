# -*- coding: utf-8 -*-

from collections import defaultdict
from datetime import datetime, date, time
import pytz

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.osv import expression


class hr_payslip(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def create(self, vals):
        res = super(hr_payslip, self).create(vals)
        #return date to as original of payslip not termination date set in addon hr_end_service
        res.date_to=vals['date_to']
        return res





