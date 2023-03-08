# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class HrExpensePrepaymentRefuseWizard(models.TransientModel):
    """This wizard can be launched from an he.expense (an expense line)
    or from an hr.expense.sheet (En expense report)
    'hr_expense_refuse_model' must be passed in the context to differentiate
    the right model to use.
    """

    _name = "hr.expense.prepayment.refuse.wizard"
    _description = "Expense Prepayment Refuse Reason Wizard"

    reason = fields.Char(string='Reason', required=True)
    hr_expense_prepayment_id = fields.Many2one('hr.expense.prepayment')

    @api.model
    def default_get(self, fields):
        res = super(HrExpensePrepaymentRefuseWizard, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])
        refuse_model = self.env.context.get('hr_expense_prepayment_refuse_model')
        if refuse_model == 'hr.expense.prepayment':
            res.update({
                'hr_expense_prepayment_id': active_ids[0] if active_ids else False,
            })
        return res

    def request_refuse_reason(self):
        self.ensure_one()
        
        if self.hr_expense_prepayment_id:
            self.hr_expense_prepayment_id.refuse_prepayment(self.reason)
            
        #if self.hr_expense_ids:
        #    self.hr_expense_ids.refuse_expense(self.reason)

        return {'type': 'ir.actions.act_window_close'}
