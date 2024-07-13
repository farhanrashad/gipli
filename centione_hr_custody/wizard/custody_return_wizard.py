"""
    THIS MODULE WAS DEPENDING ON ACCOUNT MODULE BUT DUE TO CHANGE IN REQUIREMENTS ACCOUNT MODULE WAS REMOVED.

     THE COMMENTED LINES ARE THE PART OF CODE THAT DEPENDS ON ACCOUNT MODULE, THEY ARE COMMENTED FOR NOW UNTIL
        THE MODULE IS TESTED AND TO BE VERIFIED THAT IT IS STABLE.
"""

# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

LOGGER = logging.getLogger(__name__)

class CustodyReturnWizard(models.TransientModel):
    _name = 'custody.return.wizard'

    type = fields.Selection(string="Type", selection=[('item', 'Item'), ('money', 'Money'), ],default=lambda self:self.default_type())
    return_date = fields.Date(string="Return Date", required=False, )
    currency_id = fields.Many2one(comodel_name="res.currency", string="Currency", default=lambda self:self.env.user.company_id.currency_id.id)
    amount = fields.Monetary(string="Amount",  required=False, )
    status = fields.Selection(string="Status When Returned", selection=[('good', 'Good and Working'), ('fix','Need Some Fix'),('scrap', 'Scrap') ], required=False, )


    def confirm_action(self):
        custody = self.env['hr.custody'].browse(self.env.context.get('active_id'))
        custody.write({
            'state':'return',
            'return_date':self.return_date,
            'currency_id':self.currency_id.id,
            'return_amount':self.amount,
            'status':self.status,
        })
        # if custody.asset_id and custody.is_asset:
        #     custody.asset_id.write({'is_custody':False})

    def default_type(self):
        custody = self.env['hr.custody'].browse(self.env.context.get('active_id'))
        return custody.type
