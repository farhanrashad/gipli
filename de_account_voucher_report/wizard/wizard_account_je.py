from odoo import api, fields, models, _

class AccountJEWizard(models.TransientModel):
    _name = "account.je.wizard"
    _description = "account journal entry report wizard"

    date_from = fields.Date(string='From Date', required='1', help='select start date')
    date_to = fields.Date(string='To Date', required='1', help='select end date')
    account_id= fields.Many2one("account.account", string="Account")
    
    
    def get_voucher_report(self):
        data = {
            # 'model': 'wizard.report.emp.shift',
            'ids': self.ids,
            'form': {
                'account_id': self.account_id,
            },
        }

        # ref `module_name.report_id` as reference.
        return self.env.ref('de_account_voucher_report.open_account_wise_purchase_voucher').report_action(self, data=data)