# -*- coding: utf-8 -*-
from odoo import api, fields, models

class MultiCollection(models.TransientModel):

    _name = 'multi.collection.wiz'
    ref_coll_batch = fields.Date('[Refund/Collect] Date')

    def muli_collection(self):
        res = self.env['account.payment'].browse(self._context.get('active_ids', []))
        for rec in res:
            rec.ref_coll_batch=self.ref_coll_batch
            rec.multi_select=True
            rec.with_context({'bank_aml_batch': 1}).batch_payment_id.post_bank_entrie()

    def muli_refund(self):
        res = self.env['account.payment'].browse(self._context.get('active_ids', []))
        for rec in res:
            rec.ref_coll_batch = self.ref_coll_batch
            rec.multi_select = True
            rec.with_context({'ref_und_coll_batch': 1}).batch_payment_id.refund_under_collections()


