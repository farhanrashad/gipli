# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
from pytz import UTC
from datetime import datetime, time
from random import choice
from string import digits
from werkzeug.urls import url_encode
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError
from odoo.osv import expression
from odoo.tools import format_date, Query


class HrEmployeePrivate(models.Model):
    _inherit = "hr.employee"

    user_id = fields.Many2one('res.users', 'User', related='resource_id.user_id', store=True, readonly=False, domain=lambda self: self._compute_user_domain())


    def _compute_user_domain(self):
        # Your logic to compute the domain
        enabled_feature = bool(self.env['ir.config_parameter'].sudo().get_param('de_portal_hr_service.allow_portal_user'))
        if enabled_feature:
            return []
        else:
            return [('share', '=', False)]
