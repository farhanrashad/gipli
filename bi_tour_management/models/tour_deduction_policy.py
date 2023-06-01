from odoo import models, fields, api


class TourDeductionPolicy(models.Model):
    _name = 'tour.deduction.policy'
    _description = 'Tour Deduction Policy'

    name = fields.Char('Minimum Limit (Days)', required=True)
    max_limit = fields.Float('Maximum Limit (Days)')
    deduction_percentage = fields.Float('Deduction Percentage')
