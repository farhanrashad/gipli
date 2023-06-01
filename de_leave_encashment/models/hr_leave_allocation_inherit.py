# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class HrLeaveAllocationInherit(models.Model):
    _inherit = 'hr.leave.allocation'

    encasement_id = fields.Many2many('leave.encashment')
