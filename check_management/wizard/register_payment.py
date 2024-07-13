from odoo import api, fields, models,_
from datetime import date, datetime, time, timedelta


class RegisterPaymentWiz(models.TransientModel):
    _name='check.register.payment'
    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner", required=False)
    payment_method = fields.Many2one(comodel_name="account.journal", string="Payment Journal", required=True,domain=[('type', 'in', ('bank', 'cash'))], track_visibility='onchange')
    payment_date = fields.Date(string="Payment Date", required=True, default=datetime.today(),track_visibility='onchange')
    amount = fields.Float(string="Amount")
    payment_subtype = fields.Selection(related='payment_method.payment_subtype',track_visibility='onchange')
    check_number = fields.Char(string=_("Check number"), required=True)
    check_date = fields.Date(string=_('Check Date'), required=True)
    bank = fields.Many2one('payment.bank', _("Bank Name"))
    receipt_number = fields.Char(string="Reference",track_visibility='onchange')
    state_payment = fields.Selection([('cash', 'Cash'),
                                      ('visa', 'Visa'),
                                      ('cheque', 'Cheque'),
                                      ('bank', 'Bank'),
                                      ], default="cheque",track_visibility='onchange')
    cheque_books_id = fields.Many2one(comodel_name='cheque.books')
    cheque_books_ids = fields.Many2many(comodel_name='cheque.books', compute='calc_cheque_books_ids',store=True)

    def create_payment(self):
        inv = self.env['account.move'].search([('id', 'in', self.env.context['active_ids'])])
        val = {
            'receipt_number': self.receipt_number,
            'partner_id': self.partner_id.id,
            'reservation_id': inv.reservation_id.id,
            'state_payment': self.state_payment,
            'description': inv.name,
            'payment_date': self.payment_date,
            'partner_type': "customer" if inv.move_type=='out_invoice' else 'supplier',
            'send_rec_money': "rece" if inv.move_type=='out_invoice' else 'send',
            'payment_method': self.payment_method.id,
            'account_id': self.payment_method.default_debit_account_id.id,
            'amount': self.amount,
            'amount1': self.amount,
        }
        if self.state_payment == "cheque":
            val['pay_check_ids'] = [(0, 0, {
                'cheque_books_id': self.cheque_books_id.id if self.cheque_books_id else False,
                'check_number': self.check_number,
                'check_date': self.check_date,
                'amount': self.amount,
                'bank': self.bank.id,
            })]
        pay = self.env['normal.payments'].create(val)
        pay.get_partner_acc2()
        pay.action_confirm()

    @api.depends('payment_method')
    def calc_cheque_books_ids(self):
        for rec in self:
            rec.cheque_books_ids = [(6, 0, [x.id for x in rec.payment_method.cheque_books_ids])]

