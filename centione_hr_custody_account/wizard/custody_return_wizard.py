from odoo import models, fields, api, _


class CustodyReturnWizard(models.TransientModel):
    _inherit = 'custody.return.wizard'

    def confirm_action(self):
        custody = self.env['hr.custody'].browse(self.env.context.get('active_id'))
        custody.write({
            'state': 'return',
            'return_date': self.return_date,
            'currency_id': self.currency_id.id,
            'return_amount': self.amount,
            'status': self.status,
        })
        if custody.asset_id and custody.is_asset:
            custody.asset_id.write({'is_custody': False})