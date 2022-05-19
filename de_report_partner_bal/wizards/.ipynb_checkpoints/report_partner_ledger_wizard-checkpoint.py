from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PartnerLedgerWizard(models.TransientModel):
    _name = "partner.ledger.wizard"
    _description = 'Partner Ledger Wizard'
    
    from_date =  fields.Date(string='From Date')
    to_date =  fields.Date(string='To Date')
        
    partner_ids = fields.Many2many('res.partner')
    state = fields.Selection(selection=[
            ('draft', 'All Draft Entries'),
            ('posted', 'All Posted Entries'),
            ('all', 'All'),
        ], string='Target Moves', default='draft')
    
    def print_report(self):
        #order_ids = self.env['stock.transfer.order'].browse(self._context.get('active_ids',[]))
        data = {
            'from_date': self.from_date, 
            'to_date': self.to_date,
            'partner_ids': self.partner_ids.ids,
            'state': self.state,
        }
        
        return self.env.ref('de_report_partner_ledger.partner_ledger_report').report_action(self, data=data)
