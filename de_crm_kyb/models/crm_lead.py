# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Lead(models.Model):
    _inherit = "crm.lead"

    is_kyb = fields.Boolean(default=False)
    usage_est_users = fields.Selection([
        ('1', 'Just Me'), 
        ('2-20', '2 - 20 Employees'),
        ('21-100', '21 - 100 Employees'),
        ('100+', '100+ Employees')
    ],string="Expected Users")
    usage_est_spending = fields.Selection([
        ('0-50000', '0.00 QAR - 50,000.00 QAR'), 
        ('50000-100000', '50,000.00 QAR - 100,000.00 QAR'), 
        ('100000-500000', '100,000.00 QAR - 500,000.00 QAR'), 
        ('500000+', 'Over 500,000.00 QAR')
    ],string="Expected Spending")
    usage_card = fields.Selection([
        ('qatar', 'Qatar Only'), 
        ('international', 'International'),
        ('both', 'Both'),
    ],string="Card Usage")
    work_type = field.Char('Nature of Work')

