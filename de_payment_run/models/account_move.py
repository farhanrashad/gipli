# -*- coding: utf-8 -*-

from odoo import models, fields, api

PAYMENT_BLOCK_REASONS = [
    ('B', 'Blocked For Payment'), 
    ('P', 'Free for Payment'),  
]

class AccountMove(models.Model):
    _inherit = "account.move"

    payment_block_reason = fields.Selection(
        string='Payment Block',
        selection=PAYMENT_BLOCK_REASONS,
        store=True, index='btree_not_null', tracking=True, 
        readonly=True,
        compute='_compute_payment_block_reason',
    )

    @api.depends(
        'payment_state',
        'state',
    )
    def _compute_payment_block_reason(self):
        for move in self:
            if move.payment_state in ('in_payment','paid') or move.state != 'posted':
               move.write({
                    'payment_block_reason': False,
                })
            elif move.state == 'posted':
                move.write({
                    'payment_block_reason': 'P',
                })
                
    def button_mark_payment_unblock(self):
        for move in self:
            move.write({
                'payment_block_reason': 'P'
            })

    def button_mark_payment_block(self):
        for move in self:
            move.write({
                'payment_block_reason': 'B'
            })

    