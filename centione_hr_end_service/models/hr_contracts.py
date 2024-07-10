# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

LOGGER = logging.getLogger(__name__)

class HrContract(models.Model):
    _inherit = 'hr.contract'

    end_incentive = fields.Float(string="End of Service Incentive", required=False, )
    end_incentive_month = fields.Float(string="EoS Months Incentives Per Year",  required=False, )

    def get_end_of_service(self):
            if (self.date_end and self.date_start) and (self.date_end > self.date_start):
                if self.env["ir.config_parameter"].get_param("is_calculated"):
                    date_end_o = fields.Datetime.from_string(self.date_end)
                    date_start_o = fields.Datetime.from_string(self.date_start)
                    delta = date_end_o - date_start_o
                    diff_years = delta.days / 365
                    if 4 > diff_years >= 2:
                        num_month_incentive = 0.5
                    elif diff_years >= 4:
                        num_month_incentive = 1
                    else:
                        num_month_incentive = 0
                    contract_incentive_month = int(diff_years) * num_month_incentive
                    contract_incentive = contract_incentive_month * self.wage
                    return contract_incentive
                else:
                    return self.end_incentive

            else:
                return 0

    @api.model
    def end_of_contract_notification(self):
        today = datetime.now().date()
        after_two_months = today + relativedelta(months=2)
        users = self.env.ref('centione_hr_end_service.group_end_of_service_notifications').users
        emails_list = users.mapped('email')
        emails_str = ','.join(emails_list)
        contracts = self.search([
            ('state', 'not in', ('close','cancel')),
            ('date_end', '<=', str(after_two_months)),
            ('date_end', '>=', str(today))
        ])
        for contract in contracts:
            notification_temp = self.env.ref('centione_hr_end_service.mail_template_end_of_contract')
            mail_id = notification_temp.with_context(mail_to=emails_str).send_mail(contract.id)

    def action_active(self):
        return self.write({'state': 'active'})
