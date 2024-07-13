from odoo import models, fields, api, _


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def create(self, vals):
        res = super(HrPayslip, self).create(vals)
        variable_allowance_deduction = self.env['hr.variable.allowance.deduction'] \
            .search([('employee_id', '=', res.employee_id.id),
                     ('date', '>=', res.date_from),
                     ('date', '<=', res.date_to)])
        data = {}
        for it in variable_allowance_deduction:
            if it.type.code not in data:
                # omara added to add work day option
                if it.type.calculation_method == 'work_day':
                    data.update(
                        {it.type.code: {'amount': it.amount * res.employee_id.contract_id.wage / 30, 'input_type_id': it.type.payslip_input_type_id.id}})
                #omara
                else:
                    data.update({it.type.code: {'amount': it.amount, 'input_type_id': it.type.payslip_input_type_id.id}})

            else:
                # omara added to add work day option
                if it.type.calculation_method == 'work_day':
                    data[it.type.code]['amount'] += it.amount * res.employee_id.contract_id.wage / 30
                #omara
                else:
                    data[it.type.code]['amount'] += it.amount

        for it in data:
            if data[it]['amount']:
                res.write({'input_line_ids': [(0, 0, {
                    'input_type_id': data[it]['input_type_id'],
                    'amount': data[it]['amount']
                })]})

        for it in variable_allowance_deduction:
            it.payslip_id = res.id

        return res
