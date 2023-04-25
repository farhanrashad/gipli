from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PayslipBatchWise(models.TransientModel):
    _name = 'pay.slip.report.wizard'
    _description = 'Employee Batch Wise Salary'

    from_batch_id = fields.Many2one('hr.payslip.run', string='Previous Batch')
    to_batch_id = fields.Many2one('hr.payslip.run', string='Current Batch')
    
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company, required=True)


    def generate_report(self):
        data = {
            'ids': [],
            'model': 'pay.slip.report.wizard',
            'form': {
                'from_batch_id': self.from_batch_id.id,
                'to_batch_id': self.to_batch_id.id,
                'company_id': self.company_id.id,
            },
        }
        return self.env.ref('de_payslip_batches_comparison.batch_wise_payroll_act').report_action(self, data=data)
