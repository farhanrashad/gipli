# -*- coding: utf-8 -*-

from . import models
from . import wizard
from . import reports
from . import controller

from odoo import api, SUPERUSER_ID
#from odoo import HrPayslip
from odoo.addons.hr_payroll.models.hr_payslip import HrPayslip


def _extend_payslip(env):
    hr_loan_line_model = env['ir.model'].search([('model', '=', 'hr.loan.line')])
    if hr_loan_line_model:
        hr_loan_line_model.write({
            'field_id': [(0, 0, {
                'name': 'x_payslip_id',
                'field_description': 'Payslip Reference',
                'model_id': hr_loan_line_model.id,
                'ttype': 'many2one',
                'relation': 'hr.payslip',
                'store': True,
                'copied': False,
                'help': 'Reference to the associated payslip',
            })]
        })
        hr_payslip_model = env['ir.model'].search([('model', '=', 'hr.payslip')])
        compute_method = '''
for record in self:
    # Compute the related loan lines based on x_payslip_id
    try:
        loan_lines = self.env['hr.loan.line'].search([('employee_id', '=', record.employee_id.id),('date', '>=', record.date_from),('date', '<=', record.date_to),('state', 'in', ['draft','pending'])])
        record['x_loan_lines'] = loan_lines
    except:
        pass
        '''
        if hr_payslip_model:
            hr_payslip_model.write({
                'field_id': [(0, 0, {
                    'name': 'x_loan_lines',
                    'field_description': 'Loan Lines',
                    'model_id': hr_payslip_model.id,
                    'ttype': 'one2many',
                    'relation': 'hr.loan.line',
                    'relation_field': 'x_payslip_id',
                    'store': True,
                    'copied': False,
                    'depends': 'employee_id,date_from,date_to',
                    'compute': compute_method,
                    'help': 'Reference to associated loan lines',
                })]
            })
            
            # Create a new record in the hr.salary.rule model
            python_code_for_loan = """
result = employee.compute_loan_from_payslip(payslip.id,'hr.payslip')
            """
            category_id = env['hr.salary.rule.category'].search([('code','=','DED')],limit=1)
            struct_id = env['hr.payroll.structure'].browse(1)
            salary_rule_id = env['hr.salary.rule'].create({
                'name': 'Loan Deduction',
                'category_id': category_id.id,
                'code': 'LOAN',
                'sequence': 1,
                'struct_id': struct_id.id,
                'amount_select': 'code',
                'amount_python_compute': python_code_for_loan,                
            })
    
            #def compute_sheet(self):
            #    res = super(HrPayslip, self).compute_sheet()
            #    self.x_loan_lines.write({
            #        'model': 'hr.payslip'
            #    })
            #    return res

            HrPayslip.compute_sheet = compute_sheet

def _de_hr_loan_post_init(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _extend_payslip(env)
