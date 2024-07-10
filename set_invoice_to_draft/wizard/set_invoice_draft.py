# -*- coding: utf-8 -*-

from odoo import fields, models, api,_
from odoo.exceptions import UserError, ValidationError

class SetInvoiceDraft(models.TransientModel):
    _name = 'set.invoice.draft'
    _description = 'Set Invoice Draft'

    invoice_ids = fields.Many2many('account.move', 'set_invoice_draft_rel_transient', 'payment_id', 'invoice_id', string="Invoices", copy=False, readonly=True)




    def action_set_invoice_draft(self):
        active_ids = self.env.context.get('active_ids')
        if not active_ids:
            return ''
        return {
            'name': _('Set To Draft'),
            'res_model': 'set.invoice.draft',
            'view_mode': 'form',
            'view_id':  self.env.ref('set_invoice_to_draft.custom_view_set_invoice_draft_form_multi').id,

            'context': {'default_invoice_ids': active_ids,},
            'target': 'new',
            'type': 'ir.actions.act_window',
        }


    def set_invoice_draft(self):
        for move in self.invoice_ids:
            move.mapped('line_ids.analytic_line_ids').unlink()
            move.mapped('line_ids').remove_move_reconcile()
            move.write({'state': 'draft'})



