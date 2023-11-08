# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
import math

class RentalWizard(models.TransientModel):
    _name = 'oe.library.fee.config.wizard'
    _description = 'Configure the Library Fee'

    