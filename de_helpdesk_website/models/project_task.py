# -*- coding: utf-8 -*-

from odoo import api, Command, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.addons.http_routing.models.ir_http import slug


class ProjectTask(models.Model):
    _inherit = 'project.task'

    