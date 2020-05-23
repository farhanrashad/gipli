# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning

from odoo.addons import decimal_precision as dp


class AccountMove(models.Model):
    _inherit = 'account.move'
    
#      @api.multi
    def write(self, values):
        for rec in self:
            res = super(AccountMove, rec).write(values)
            rec.team_id = rec.invoice_line_ids.product_id.product_tmpl_id.categ_id 
            return res


    @api.onchange('invoice_line_ids.product_id.categ_id')
    def onchange_product_id(self):
        super(AccountMove, self).onchange_product_id()
        self.team_id = self.invoice_line_ids.product_id.product_tmpl_id.categ_id 
        
#         or False
