# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

LOGGER = logging.getLogger(__name__)


class MobileSet(models.Model):
    _name = 'mobile.set'
    _rec_name = 'name'
    _description = 'MODEL_NAME'
    _order = 'name asc, id desc'
    # _inherit = ['mail.thread', 'ir.needaction_mixin']

    name = fields.Char(string="Mobile Name", required=False, )
    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee", required=False, )
    brand_name = fields.Char(string="Brand Name")
    delivery_date = fields.Date(string="Delivery Date", required=False, )

