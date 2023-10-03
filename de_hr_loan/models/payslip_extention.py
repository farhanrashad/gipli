from odoo import models, api

# Define the method you want to add
def compute_loan_lines(self):
    # Your custom logic here to compute loan lines
    loan_lines = []  # Replace with your actual code to calculate loan lines
    return loan_lines

# Monkey patch the method into the 'hr.payslip' model
hr_payslip = self.env['hr.payslip']
hr_payslip.compute_loan_lines = compute_loan_lines
