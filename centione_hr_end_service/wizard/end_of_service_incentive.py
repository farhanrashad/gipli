# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

LOGGER = logging.getLogger(__name__)

class EndServiceIncentive(models.TransientModel):
    _name = 'end.service.incentive'

    end_incentive = fields.Float(string="End of Service Incentive",  required=False, )
    end_incentive_month = fields.Float(string="End of Service Months",default=lambda self:self.env["ir.config_parameter"].get_param("end_service_incentive"))
    is_incentive_calc = fields.Boolean(string="Is Incentive Calc",default=lambda self:self.env["ir.config_parameter"].get_param("is_calculated") )

    def action_approved(self):
        # check if the employee did not return custody
        termination_id = self.env.context.get('active_id')
        termination = self.env['hr.termination'].browse(termination_id)
        termination.end_incentive = self.end_incentive
        termination.end_incentive_month = self.end_incentive_month
        termination.action_approved()