# -*- coding: utf-8 -*-
from odoo import api, fields, models


class DeliveryToCustomerWiz(models.TransientModel):

    _name = 'delivery.to_customer.wiz'
    delivery_to_customer_date = fields.Date(string='Delivery To Customer Date',required=True)

    def to_delivery_to_customer(self):
        res = self.env['account.payment'].browse(self._context.get('active_ids', []))
        for rec in res:
            print("D>>DD>",res)
            rec.delivery_to_customer_date=self.delivery_to_customer_date
            rec.to_delivery_to_customer()
class RefundNotesWiz(models.TransientModel):

    _name = 'refund.notes.wiz'
    move_date = fields.Date(string='Notes Refund Date',required=True)

    def refund_notes(self):
        res = self.env['account.payment'].browse(self._context.get('active_ids', []))
        for rec in res:
            rec.move_date=self.move_date
            rec.with_context({'ref_notes_batch':True}).refund_notes()




class DeliveryToVendorWiz(models.TransientModel):

    _name = 'delivery.to_vendor.wiz'
    delivery_to_vendor_date = fields.Date(string='Delivery Date(Vendor)',required=True)

    def to_delivery_to_vendor(self):
        res = self.env['account.payment'].browse(self._context.get('active_ids', []))
        for rec in res:
            rec.delivery_date=self.delivery_to_vendor_date
            rec.delivery_aml()
            
class BankWithdrawalWiz(models.TransientModel):

    _name = 'bank.withdrawal.wiz'
    withdrawal_date = fields.Date(string="Withdrawal Date")

    def to_withdrawal(self):
        res = self.env['account.payment'].browse(self._context.get('active_ids', []))
        for rec in res:
            rec.withdrawal_date=self.withdrawal_date
            rec.with_context({'bank_aml':1}).post()

