# -*- coding: utf-8 -*-

from odoo import models, fields, api,_


class AccountMove(models.Model):
    _inherit = 'account.move'
    
    gatepass_sequence = fields.Char(string="Gatepass#")
    
    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE
        if any('state' in vals and vals.get('state') == 'posted' for vals in vals_list):
            raise UserError(_('You cannot create a move already in the posted state. Please create a draft move and post it after.'))
            

        vals_list = self._move_autocomplete_invoice_lines_create(vals_list)
        rslt = super(AccountMove, self).create(vals_list)
        rslt.action_gatepass_sequence()
        for i, vals in enumerate(vals_list):
            if 'line_ids' in vals:
                rslt[i].update_lines_tax_exigibility()
        return rslt
    
    
    def action_gatepass_sequence(self):
        for line in self:
            line.update({
                'gatepass_sequence': self.env['ir.sequence'].next_by_code('account.move.gatepass') or _('New')
            })
            
            
            
            
            
            
            
            
            
            
            
            
            
