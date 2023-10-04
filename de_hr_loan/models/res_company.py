# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

class Company(models.Model):
    _inherit = 'res.company'

    default_repayment_model_id = fields.Many2one('ir.model', readonly=False, string="Repayment Mode", default_model="hr.loan.type", domain=lambda self: self._compute_model_domain(),
        help="Repayment mode defines the default method employees will use to repay their loans."
    )
    default_payment_product_id = fields.Many2one('product.product', string="Product", domain="[('type','=','service')]")

    default_loan_frequency = fields.Selection(
        [
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
            ('semi_annual', 'Semi-Annually'),
            ('annual', 'Annually'),
            ('custom', 'Custom')
        ],
        string="Frequency", default='custom',
        help="Loan frequency determines how often an employee can apply for the next loan."
    )
    default_loan_frequency_interval = fields.Integer(string='Frequency Interval', default=-1,
            help="Employees can apply for a new loan based on a custom-defined interval")
    
    default_interval_loan_mode = fields.Selection([
        ('fix', 'Fixed'),
        ('max', 'Maximum'),
    ], string='Interval Mode', default='fix',
        help="Loan interval specifies the number of months within which an employee must repay the loan, with options for a maximum limit or a fixed number of intervals."
    )
    
    default_interval_loan = fields.Integer(string='Interval', default=1)

    

    @api.model
    def _compute_model_domain(self):
        allowed_model_ids = self.env['ir.model'].search([('model', 'in', ['hr.payslip', 'account.move'])]).ids
        return [('id', 'in', allowed_model_ids)]
