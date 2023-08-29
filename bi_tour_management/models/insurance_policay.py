from odoo import fields, models, api


class InsurancePolicy(models.Model):
    _name = 'insurance.policy'
    _description = 'Insurance Policy'

    name = fields.Char(string='Insurance Name')
    insurance_type_id = fields.Many2one('insurance.type', string='Insurance Type')
    insurance_adult_cost = fields.Float(string='Insurance Cost For Adult', related='insurance_type_id.adult_cost')
    insurance_child_cost = fields.Float(string='Insurance Cost For Child', related='insurance_type_id.child_cost')
    total_cost = fields.Float(string='total_cost', compute='_compute_total_cost')
    coverage_line_ids = fields.One2many('insurance.coverage.line', 'policy_id', string='Coverage Lines',
                                        )
    tour_booking_id = fields.Many2one('tour.booking')
    state = fields.Selection(
        string='State',
        selection=[('draft', 'Draft'),
                   ('confirm', 'Confirm'), ],
        required=False, default='draft')

    @api.depends('insurance_adult_cost', 'insurance_child_cost')
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = rec.insurance_adult_cost + rec.insurance_child_cost

    def confirm_policy(self):
        for rec in self:
            rec.state = 'confirm'


class InsuranceCoverageLines(models.Model):
    _name = 'insurance.coverage.line'
    _description = 'Insurance Coverage Lines'

    policy_id = fields.Many2one('insurance.type', string='Policy Type')
    product_id = fields.Many2one('product.product', string='Policy Id')
    benefit_cost = fields.Float(string='Benefit Cost')
