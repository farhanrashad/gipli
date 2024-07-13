from odoo import api, fields, models
from odoo.exceptions import ValidationError



class Payments(models.Model):
    _inherit='normal.payments'
    budget_company_id = fields.Many2one(comodel_name='res.company', string='Budget Company', required=True)
    branch_id = fields.Many2one(comodel_name='address.branch', string='Branch')
    project_id = fields.Many2one(comodel_name='project.project', string='Project')
    franchise_id = fields.Many2one(comodel_name='franchise.type', string='Franchise')
    department_id = fields.Many2one('hr.department', string="Department")

class PaymentMultiAccounts(models.Model):
    _inherit='payment.multi.accounts'
    budget_company_id = fields.Many2one(comodel_name='res.company', string='Budget Company', required=True)
    branch_id = fields.Many2one(comodel_name='address.branch', string='Branch')
    project_id = fields.Many2one(comodel_name='project.project', string='Project')
    franchise_id = fields.Many2one(comodel_name='franchise.type', string='Franchise')
    department_id = fields.Many2one('hr.department', string="Department")

class create_moves(models.Model):
    _inherit = 'create.moves'

    def create_move_lines(self, **kwargs):
        move=super().create_move_lines(**kwargs)
        for line in move.line_ids:
            if line.debit>0:
                line.write({
                    'budget_company_id':line.check_payment_id.budget_company_id.id,
                    'branch_id':line.check_payment_id.branch_id.id,
                    'project_id':line.check_payment_id.project_id.id,
                    'franchise_id':line.check_payment_id.franchise_id.id,
                    'department_id':line.check_payment_id.department_id.id,
                })
        return move
    def create_move_lines2(self, **kwargs):
        move = super().create_move_lines2(**kwargs)
        for line in move.line_ids:
            if line.debit > 0:
                line.write({
                    'budget_company_id': line.check_payment_id.budget_company_id.id,
                    'branch_id': line.check_payment_id.branch_id.id,
                    'project_id': line.check_payment_id.project_id.id,
                    'franchise_id': line.check_payment_id.franchise_id.id,
                    'department_id': line.check_payment_id.department_id.id,
                })
        return move
class CustomerPayment(models.Model):
    _inherit = 'customer.payment'
    budget_company_id = fields.Many2one(comodel_name='res.company', string='Company', required=True)
    branch_id = fields.Many2one(comodel_name='address.branch', string='Branch')
    project_id = fields.Many2one(comodel_name='project.project', string='Project')
    franchise_id = fields.Many2one(comodel_name='franchise.type', string='Franchise')
    department_id = fields.Many2one('hr.department', string="Department")

    def approved(self):
        if not self.loan_line.filtered(lambda line: line.is_pay):
            raise ValidationError("Please Select One Line!")
        account = self.env['account.account'].search([('accounting_allocation', '=', self.accounting_allocation)],
                                                     limit=1)
        for line in self.loan_line:
            if line.is_pay:

                val = {
                    'receipt_number': self.ref,
                    'partner_id': self.partner_id.id,
                    'custoemr_payment_id': self.id,
                    'reservation_id': self.reservation_id.id,
                    'state_payment': self.state_payment,
                    'payment_method_id': line.payment_method_id.id,
                    'description': line.description,
                    'payment_date': self.date,
                    'send_rec_money': "rece",
                    'payment_method': self.journal_id.id,
                    'accounting_allocation': self.accounting_allocation,
                    'account_id': account.id if account else self.journal_id.default_debit_account_id.id,
                    'amount': line.amount,
                    'amount1': line.amount,
                    'budget_company_id': self.budget_company_id.id,
                    'branch_id': self.branch_id.id,
                    'project_id': self.project_id.id,
                    'franchise_id': self.franchise_id.id,
                    'department_id': self.department_id.id,
                }
                if self.state_payment == "cheque":
                    val['pay_check_ids'] = [(0, 0, {
                        'check_number': line.cheque,
                        'check_date': line.date,
                        'amount': line.amount,
                        'bank': line.bank_name.id,
                    })]
                pay = self.env['normal.payments'].create(val)
                print("D>D>D>>D", pay)
                pay.get_partner_acc2()
                pay.write({'account_id': account.id})
                pay.action_confirm()
        self.state = "approved"


