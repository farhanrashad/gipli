# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _
import datetime
from datetime import datetime, date,timedelta
from  dateutil.relativedelta import relativedelta

from re import findall as regex_findall, split as regex_split

payment_types=[
    ('type1','دفعة حجز'),
    ('type2','اقساط الوحدة'),
    ('type3','وديعة الصيانة'),
    ('type4','دفعة تعاقد'),
    ('type5','	تأمين التشطيب'),
]


duration=[
    ('type1','سنوي'),
    ('type2','ربع سنوي'),
    ('type3','نصف سنوي'),
    ('type4','شهري'),
    ('type5','تأمين 5%'),
    ('type6','وديعة الصيانة 8%'),
    ('type7','وديعة الصيانة 10%'),
]


class CreatePaymentLines(models.TransientModel):
    _name = 'create.payments.lines'
    type = fields.Selection(
        string='Type',
        selection=[('visa', 'شيكات'),
                   ('cash', 'نقدي'), ],
        required=False,default='visa' )
        
    payment_type = fields.Selection(string="Payment Types", selection=payment_types, required=False)
    no_of_cheques = fields.Integer(string="Number Of Cheques", required=False)
    cheque_start_date = fields.Date(string="Cheque Start Date", required=False)
    cheque_no_start = fields.Char(string="Cheque Start No", required=False)
    payment_method_id= fields.Many2one(comodel_name="account.journal", string="Method Of Payment", required=False)
    duration = fields.Selection(string="Duration Type For Cheques", selection=duration, required=False)
    cheque_seq = fields.Char()
    bank_name = fields.Many2one('payment.bank', _("Bank Name"))
    state_payment = fields.Selection([('cash', 'Cash'),
                                      ('visa', 'Visa'),
                                      ('cheque', 'Cheque'),
                                      ('bank', 'Bank'),
                                      ], default="cheque")
    amount_by = fields.Selection(
        string='Amount By',
        selection=[('amount', 'Amount'),
                   ('percentage', 'Percentage'), ],
        required=False, )

    value = fields.Float(string="Amount", required=False)
    amount = fields.Float(string="Total Amount", required=False)
    due_amount = fields.Float(string="Paid Amount")
    receipt_date = fields.Date(string="Receipt Date", required=False, )
    add_to_paid_amount = fields.Boolean(string="Add To Payment Amount")
    lines = fields.One2many(comodel_name="payments.lines", inverse_name="wiz_id", string="", required=False)
    reservation_id = fields.Many2one(comodel_name="res.reservation")
    merge_in_one_installment = fields.Boolean(string='Merge In One Installment')




    def action_apply(self):
        self.cheque_seq = self.cheque_no_start
        date=self.cheque_start_date
        if not  date:
            raise UserError("Add Cheque Start Date")
        lines=[]
        amount = 0
        div_amount = 0
        if self.amount_by == 'amount':
            amount = self.value
        elif self.amount_by == 'percentage':
            amount = self.amount * (self.value / 100)
        else:
            amount = 0
        try:

            div_amount = amount / self.no_of_cheques
        except:
            div_amount = self.reservation_id.net_price / 1
        for reservation in self.reservation_id:
            line2 = self.add_line(div_amount, date, reservation.property_id.id, True)
            lines.append((0, 0, line2))
            for repeat in range(0, self.no_of_cheques):
                line=self.add_line(div_amount,date,reservation.property_id.id,False)
                lines.append((0,0,line))
                if self.duration=='type1':
                    date =date+relativedelta(years=1)
                if self.duration=='type2':
                    date =date+relativedelta(months=3)
                if self.duration=='type3':
                    date =date+relativedelta(months=6)
                if self.duration=='type4':
                    date =date+relativedelta(months=1)
                if self.duration=='type5':
                    date =date+relativedelta(months=1)
                if self.duration=='type6':
                    date =date+relativedelta(months=1)
                if self.duration=='type7':
                    date =date+relativedelta(months=1)
                if self.type=='visa':
                    self.cheque_seq = self.generate_serial_in()
            print("lines",lines)
            self.lines=lines
            self.clear_fields()
            return {
                'type': 'ir.actions.act_window',
                'res_model': "create.payments.lines",
                'res_id': self.id,
                'view_mode': 'form,tree',
                'name': 'Add Payment Strategy Lines',
                'target': 'new'
            }
            # reservation.payment_strg_ids=lines
            # reservation._compute_amount()



    def add_line(self,amount,date,property_id,section):
        des=""
        if self.payment_type=='type1':des=payment_types[0][1]
        if self.payment_type=='type2':des=payment_types[1][1]
        if self.payment_type=='type3':des=payment_types[2][1]
        if self.payment_type=='type4':des=payment_types[3][1]
        if self.payment_type=='type5':des=payment_types[4][1]
        print(">>>",self.due_amount,amount)
        if amount>self.due_amount and self.add_to_paid_amount:
            amount-=self.due_amount
        if section:
            return {
                'name': des,
                'description': des,
                'display_type': 'line_section',

            }
        else:
            return{
            'amount': amount,
            'amount_pay': 0,
            'base_amount': amount,
            'date': date,
            'journal_id': self.payment_method_id.id,
            'description': des,
            'is_pay': False,
            'cheque':self.cheque_seq ,
            'property_ids': [(6, 0, [property_id])],
            "is_maintainance":True if self.payment_type in ['type3','type5'] else False,
            "bank_name":self.bank_name.id,
            "state_payment":self.state_payment,
            "receipt_date":self.receipt_date,
            "merge_in_one_installment":self.merge_in_one_installment,

        }


    def generate_serial_in(self):
        if self.cheque_seq:
            caught_initial_number = regex_findall("\d+", self.cheque_seq)
            if not caught_initial_number:
                raise UserError(_('The serial number must contain at least one digit.'))
            # We base the serie on the last number find in the base serial number.
            initial_number = caught_initial_number[-1]
            padding = len(initial_number)
            # We split the serial number to get the prefix and suffix.
            splitted = regex_split(initial_number, self.cheque_seq)
            # initial_number could appear several times in the SN, e.g. BAV023B00001S00001
            prefix = initial_number.join(splitted[:-1])
            suffix = splitted[-1]
            initial_number = int(initial_number)
            st = prefix + str(initial_number + 1).zfill(padding) + suffix
            self.cheque_seq = st
            return st
        else:
            return "/"

    def approve(self):
        lines=[]
        for line in self.lines:
            if line.display_type!='line_section':
                lines.append((0,0,
                              {
                                  'amount': line.amount,
                                  'amount_pay': line.amount_pay,
                                  'base_amount': line.base_amount,
                                  'date': line.date,
                                  'journal_id': line.journal_id.id,
                                  'description': line.description,
                                  'is_pay': line.is_pay,
                                  'cheque': line.cheque,
                                  'property_ids': [(6, 0, [self.reservation_id.property_id.id])],
                                  "is_maintainance": line.is_maintainance,
                                  "bank_name": line.bank_name.id,
                                  "state_payment": line.state_payment,
                                  "receipt_date": line.receipt_date,
                                  'display_type': line.display_type,
                                  'merge_in_one_installment': line.merge_in_one_installment,

                              }))
            else:
                lines.append((0,0,
                              {
                                  'name': line.description,
                                  'display_type': line.display_type,

                              }))


        self.reservation_id.payment_strg_ids=lines
        self.reservation_id._compute_amount()


    def clear_fields(self):
        self.type=''
        self.payment_type=''
        self.duration=''
        self.no_of_cheques=0
        self.value=0
        self.cheque_start_date=False
        self.payment_method_id=False
        self.receipt_date=False
        self.bank_name=False
        self.cheque_no_start=''
        self.state_payment=''
        self.cheque_seq=''
        self.amount_by=''
        self.add_to_paid_amount=False
        self.merge_in_one_installment=False










class PaymentLines(models.TransientModel):
    _name = 'payments.lines'
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    name = fields.Char(string="", required=False)
    wiz_id = fields.Many2one('create.payments.lines')
    bank_name = fields.Many2one('payment.bank', _("Bank Name"))
    amount = fields.Float(string="Amount", required=False)
    amount_pay = fields.Float(string="Amount Pay", required=False)
    base_amount = fields.Float(string="Base Amount", required=False)
    state_payment = fields.Selection([('cash', 'Cash'),
                                      ('visa', 'Visa'),
                                      ('cheque', 'Cheque'),
                                      ('bank', 'Bank'),
                                      ],)
    receipt_date = fields.Date(string="Receipt Date", required=False, )
    is_maintainance = fields.Boolean(string="Is Maintainance")
    is_pay = fields.Boolean(string="Is Pay")
    journal_id= fields.Many2one(comodel_name="account.journal", string="Method Of Payment", required=False)
    cheque = fields.Char(string="Cheque", required=False)
    description = fields.Char(string="Description", required=False)
    date = fields.Date(string="Payment Date", required=False)
    property_ids = fields.Many2many(comodel_name="product.product", relation="payments_wiz_lines")
    merge_in_one_installment = fields.Boolean(string='Merge In One Installment')
