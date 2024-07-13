# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

LOGGER = logging.getLogger(__name__)

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    end_service_incentive = fields.Integer(string="EoS Months Incentives Per Year",  required=False, )
    is_calculated = fields.Boolean(string="Is Calculated",  )

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        default_end_service_incentive = self.env["ir.config_parameter"].get_param("end_service_incentive", default=2)
        default_is_calculated = self.env["ir.config_parameter"].get_param("is_calculated")
        res.update({'end_service_incentive':int(default_end_service_incentive) or 2})
        res.update({'is_calculated':default_is_calculated or False})
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('end_service_incentive',int(self.end_service_incentive) or 2 )
        self.env['ir.config_parameter'].sudo().set_param('is_calculated',self.is_calculated or False )





