from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PartnerWizard(models.TransientModel):
    _name = "partner.wizard"
    _description = 'Partner Ledger Wizard'
    
    
    date = fields.Date(string='Date')
    
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company.id)
    account_type = fields.Selection(selection=[
            ('payable', 'Payable'),
            ('receivable', 'Receivable'),
        ], string='Target Moves', default='payable')
    
    
 
    
    
    
    def print_report(self):
        data = {}
        data['form'] = self.read(['date', 'company_id', 'account_type'])[0]
        return self._print_report(data)
    
    def _print_report(self, data):
        data['form'].update(self.read(['date', 'company_id', 'account_type'])[0])
        return self.env.ref('de_report_partner_bal.partner_bal_report_xlsx').report_action(self, data=data, config=False)
    
    
    
    
    
    
    