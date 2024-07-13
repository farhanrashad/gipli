# -*- coding: utf-8 -*-

from odoo import models, fields, api

class hr_contract_inherit(models.Model):
    _inherit = 'hr.contract'

    transportation_amount=fields.Float('Transportation')

