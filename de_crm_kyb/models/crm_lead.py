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
    work_type = fields.Char('Nature of Work')

    crc = fields.Binary(string="Commercial Registration Certificate", required=True)
    crc_filename = fields.Char(string="CRC Filename")
    
    aoa = fields.Binary(string="Articles of Association", required=True)
    aoa_filename = fields.Char(string="AoA Filename")
    
    c_card = fields.Binary(string="Computer Card", required=True)
    cc_filename = fields.Char(string="CC Filename")
    
    iban_cert = fields.Binary(string="IBAN Certificate", required=True)
    iban_cert_filename = fields.Char(string="IBAN Filename")
    
    trade_license = fields.Binary(string="Trade License")
    trade_license_filename = fields.Char(string="TL Filename")

