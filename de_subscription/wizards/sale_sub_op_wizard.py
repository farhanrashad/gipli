# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class OperationWizard(models.TransientModel):
    _name = 'sale.sub.op.wizard'
    _description = 'Subscription Operations Wizard'

    op_type = fields.Selection([
        ('renew', 'Renewal'),  
        ('upsell', 'Upsell'),  
        ('revise', 'Revision'),
        ('close', 'Close'),
    ], 
        string='Operation', required=True, default="renew",
    )
    subscription_close = fields.Boolean('Close', default=True)
    sub_close_reason_id = fields.Many2one('sale.sub.close.reason', string='Close Reason', ondelete='restrict', copy=False)

    def run_process(self):
        raise UserError('hello')