class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def create_loan_reconcile_entry(self, loan_id, loan_line_id, account_move_id):
        reconcile_record = self.env['hr.loan.reconcile'].create({
            'loan_id': loan_id,
            'loan_line_id': loan_line_id,
            'account_move_id': account_move_id,
        })
        return reconcile_record

