from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PayslipBatchWise(models.TransientModel):
    _name = 'pay.slip.report.wizard'
    _description = 'Employee Batch Wise Salary'

    payroll_batch = fields.Many2one('hr.payslip.run', string='Batch 1')
    payroll_batch_id = fields.Many2one('hr.payslip.run', string='Batch 2')

    def generate_report(self):
        data = {
            'ids': [],
            'model': 'pay.slip.report.wizard',
            'form': {
                'payroll_batch': self.payroll_batch.id,
                'payroll_batch_id': self.payroll_batch_id.id
            },
        }
        return self.env.ref('de_payslip_batches_comparison.batch_wise_payroll_act').report_action(self, data=data)
