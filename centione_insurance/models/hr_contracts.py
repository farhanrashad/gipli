# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging
from math import ceil

LOGGER = logging.getLogger(__name__)

class HrContract(models.Model):
    _inherit = 'hr.contract'

    fixed_insurance = fields.Float(string="Fixed Insurance Amount", required=False, )
    variable_insurance = fields.Float(string="Variable Insurance Amount", required=False, ) # To be removed, not used anymore.
    is_insured = fields.Boolean(string="Is Insured?", default=True)

    def get_employee_over_sixty_rule(self, date_from=None, date_to=None):
        result = self.get_insurance_primary_wage(date_from, date_to)
        employee_birth_date = self.employee_id.birthday
        age = 0
        if employee_birth_date:
            age = ceil(((datetime.now().date() - employee_birth_date).total_seconds()) / (60*60*24*365))
        return result if age >= 60 else 0

    def get_insurance_primary_wage(self, date_from=None, date_to=None):
        date_from_o = fields.Date.from_string(date_from)
        if self.is_insured:
            insurance_fixed = self.env['hr.insurance.year'].search([('year', '=', str(date_from_o.year)), ('type', '=', 'fixed')], limit=1)
            if not insurance_fixed:
                insurance_fixed = self.env['hr.insurance.year'].search([('type', '=', 'fixed')], order="year desc", limit=1)

            max_insurance_amount = insurance_fixed.insurance_amount_max
            min_insurance_amount = insurance_fixed.insurance_amount_min

            if min_insurance_amount <= self.fixed_insurance <= max_insurance_amount:
                return self.fixed_insurance
            elif self.fixed_insurance < min_insurance_amount:
                return min_insurance_amount
            elif self.fixed_insurance > max_insurance_amount:
                return max_insurance_amount

        else:
            return 0


    """
        Dead code.
        This function is related to type: variable which is disabled, so it is no longer used.
    """
    # @api.multi
    # def get_insurance_variable_wage(self, date_from, date_to=None):
    #     if self.is_insured:
    #         if self.variable_insurance:
    #             return self.variable_insurance
    #         date_from_o = fields.Date.from_string(date_from)
    #         insurance_variable = self.env['hr.insurance.year'].search(
    #             [('year', '=', str(date_from_o.year)), ('type', '=', 'variable')], limit=1)
    #         if not insurance_variable:
    #             insurance_variable = self.env['hr.insurance.year'].search([('type', '=', 'variable')], order="year desc", limit=1)
    #         variable_insurance_limit = insurance_variable and insurance_variable.insurance_amount or 3360
    #         primary_insurance = self.get_insurance_primary_wage(date_from,date_to)
    #         if self.wage < primary_insurance:
    #             return 0
    #         variable_insurance = min((self.wage - primary_insurance), variable_insurance_limit)
    #         return variable_insurance
    #     else:
    #         return 0



