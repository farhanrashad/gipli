# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

LOGGER = logging.getLogger(__name__)

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    employee_custody_ids = fields.One2many(comodel_name="hr.custody", inverse_name="employee_id", string="", required=False, )
    employee_mobile_ids = fields.One2many(comodel_name="mobile.set", inverse_name="employee_id", string="", required=False, )

    custody_count = fields.Integer(string="", compute='compute_custody_count' )

    def action_open_custody(self):
        return {
            'name': _('Employee ' + self.name + ' custody'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.custody',
            'type': 'ir.actions.act_window',
            'domain': [('id','in',self.employee_custody_ids.ids)],
            'context': {
                'default_employee_id': self.id,
            },
        }

    def compute_custody_count(self):
        for rec in self:
            rec.custody_count = len(rec.employee_custody_ids)