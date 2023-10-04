# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    default_repayment_model_id = fields.Many2one('ir.model', related='company_id.default_repayment_model_id',
                                readonly=False, string="Repayment Mode", default_model="hr.loan.type")
    default_payment_product_id = fields.Many2one('product.product', 
            related='company_id.default_payment_product_id', 
            readonly=False, string="Product", default_model="hr.loan.type")
    default_loan_frequency = fields.Selection(related='company_id.default_loan_frequency',
                            readonly=False, string="Loan Frequency", default_model="hr.loan.type")  
    default_loan_frequency_interval = fields.Integer(related='company_id.default_loan_frequency_interval',
                            readonly=False, string="Frequency Interval", default_model="hr.loan.type")

    default_interval_loan_mode = fields.Selection(related='company_id.default_interval_loan_mode',
                            readonly=False, string="Interval Mode", default_model="hr.loan.type")
    default_interval_loan = fields.Integer(related='company_id.default_interval_loan',
                            readonly=False, string="Interval", default_model="hr.loan.type")

