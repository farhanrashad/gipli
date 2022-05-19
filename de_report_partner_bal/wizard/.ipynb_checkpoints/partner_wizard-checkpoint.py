from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PartnerWizard(models.TransientModel):
    _name = "partner.wizard"
    _description = 'Partner Ledger Wizard'
    
    
    date =  fields.Date(string='Date')
        
    partner_ids = fields.Many2many('res.partner')
    state = fields.Selection(selection=[
            ('draft', 'All Draft Entries'),
            ('posted', 'All Posted Entries'),
            ('all', 'All'),
        ], string='Target Moves', default='draft')
    
    def print_report(self):
        #order_ids = self.env['stock.transfer.order'].browse(self._context.get('active_ids',[]))
        data = {
            
            'date': self.date,
            'partner_ids': self.partner_ids.ids,
            'state': self.state,
        }
        
        return self.env.ref('de_report_partner_bal.partner_bal_report_xlsx').report_action(self, data=data)