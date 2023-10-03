from odoo import api, fields, models

# Check if the 'hr.payslip' model exists in ir.models before applying monkey patch
if 'hr.payslip' in self.env['ir.model'].search([]).mapped('model'):
    # Monkey patch the hr.payslip model to add a one2many reference to hr.loan.line
    @api.model
    def _compute_loan_lines(self):
        loan_lines = self.env['hr.loan.line'].search([('payslip_id', '=', self.id)])
        self.loan_lines = loan_lines

    models.HrPayslip._compute_loan_lines = _compute_loan_lines
    models.HrPayslip.loan_lines = fields.One2many(
        'hr.loan.line',
        'payslip_id',
        string='Loan Lines',
        compute='_compute_loan_lines',
    )

    # Monkey patch the hr.loan.line model to add a many2one reference to hr.payslip
    @api.model
    def _compute_payslip(self):
        payslip = self.env['hr.payslip'].search([('loan_lines', 'in', self.ids)])
        self.payslip_id = payslip

    models.HrLoanLine._compute_payslip = _compute_payslip
    models.HrLoanLine.payslip_id = fields.Many2one(
        'hr.payslip',
        string='Payslip',
        compute='_compute_payslip',
    )

    # Monkey patch the hr.payslip model to add a custom method
    @api.multi
    def custom_method(self):
        # Your custom method logic here
        pass

    models.HrPayslip.custom_method = custom_method
