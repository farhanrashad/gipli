from odoo import api, fields, models,_
from odoo.exceptions import ValidationError,UserError
from datetime import date, datetime, time, timedelta

duration=[
    ('type1','سنوي'),
    ('type2','ربع سنوي'),
    ('type3','نصف سنوي'),
    ('type4','شهري'),
    ('type5','تأمين 5%'),
    ('type6','وديعة الصيانة 8%'),
    ('type7','وديعة الصيانة 10%'),
]
from  dateutil.relativedelta import relativedelta

from re import findall as regex_findall, split as regex_split

class SplitWiz(models.TransientModel):

    _name = 'check.split.wiz'

    check_id = fields.Many2one('check.management', string="Check Number")
    amount = fields.Float(string='Amount')
    amount_paid = fields.Float(string='Amount Paid')
    amount_due = fields.Float(string='Amount Due')

    lines = fields.One2many(
        comodel_name='check.split.lines',
        inverse_name='wiz_id',
        string='Lines',
        required=False)

    journal_id = fields.Many2one('account.journal', string="Payment Method")
    cheque_no_start = fields.Char(string="Cheque Start No", required=False)
    cheque_start_date = fields.Date(string='Due Date Start')
    bank = fields.Many2one('payment.bank', _("Bank Name"))
    duration = fields.Selection(string="Duration Type For Cheques", selection=duration, required=False)
    no_of_cheques = fields.Integer(string="Number Of Cheques", required=False)
    cheque_seq = fields.Char()
    amount_by = fields.Selection(
        string='Amount By',
        selection=[('amount', 'Amount'),
                   ('percentage', 'Percentage'), ],
        required=False, )
    value = fields.Float(string="Value", required=False)
    receipt_number = fields.Char(string="Reference")
    payment_date = fields.Date(string="Payment Date", required=True, default=datetime.today(),track_visibility='onchange')




    def split(self):
        total_amount=0
        for line in self.lines:
            val = {
                'receipt_number': self.receipt_number,
                'partner_id': self.check_id.check_payment_id.partner_id.id,
                'custoemr_payment_id': self.check_id.check_payment_id.custoemr_payment_id.id,
                'reservation_id': self.check_id.check_payment_id.reservation_id.id,
                'payment_method_id': self.check_id.check_payment_id.payment_method_id.id,
                'payment_method': line.journal_id.id,
                'account_id': self.check_id.check_payment_id.account_id.id,
                'state_payment': self.check_id.check_payment_id.state_payment,
                'description': self.check_id.check_payment_id.description,
                'payment_date': line.payment_date,
                'amount': line.amount,
                'amount1': line.amount,
                'partner_type': self.check_id.check_payment_id.partner_type,
                'send_rec_money': "rece",
                'parent_payment_id': self.check_id.check_payment_id.id,
                'from_check_number': self.check_id.check_number,
                'from_check_date': self.check_id.check_date,
            }
            if line.payment_subtype :
                val['pay_check_ids'] = [(0, 0, {
                    'check_number': line.check_number,
                    'check_date': line.check_date,
                    'amount': line.amount,
                    'bank': line.bank.id,
                })]
            pay = self.env['normal.payments'].create(val)
            pay.get_partner_acc2()
            pay.action_confirm()
            self.check_id.write({
                'is_split':True
            })
            total_amount+=line.amount
        if total_amount>self.amount_due:
            raise ValidationError("Total Amount > Amount Due")


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

    def clear_fields(self):
        self.duration=False
        self.bank=False
        self.duration=''
        self.no_of_cheques=0
        self.cheque_start_date=False
        self.cheque_no_start=''
        self.cheque_seq=''
        self.amount_by=''
        self.value=0

    def add_line(self, amount, date):
        return {
            'amount': amount,
            'journal_id': self.journal_id.id,
            'payment_date': self.payment_date,
            'payment_subtype': self.journal_id.payment_subtype,
            'check_date': date,
            'check_number': self.cheque_seq,
            "bank": self.bank.id,

        }

    def create_lines(self):
        self.cheque_seq = self.cheque_no_start
        date = self.cheque_start_date
        if not date:
            raise UserError("Add Cheque Start Date")
        lines = []
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
            div_amount = self.amount / 1
        lines = []

        for repeat in range(0, self.no_of_cheques):
            line = self.add_line(div_amount, date)
            print("D>D>", line)
            lines.append((0, 0, line))
            if self.duration == 'type1':
                date = date + relativedelta(years=1)
            if self.duration == 'type2':
                date = date + relativedelta(months=3)
            if self.duration == 'type3':
                date = date + relativedelta(months=6)
            if self.duration == 'type4':
                date = date + relativedelta(months=1)
            if self.duration == 'type5':
                date = date + relativedelta(months=1)
            if self.duration == 'type6':
                date = date + relativedelta(months=1)
            if self.duration == 'type7':
                date = date + relativedelta(months=1)
            self.cheque_seq = self.generate_serial_in()
        self.lines = lines
        self.clear_fields()

        return {
            'type': 'ir.actions.act_window',
            'res_model': "check.split.wiz",
            'res_id': self.id,
            'view_mode': 'form,tree',
            'name': 'Split',
            'target': 'new'
        }




class SplitWizLine(models.TransientModel):
    _name = 'check.split.lines'

    journal_id = fields.Many2one('account.journal', string="Payment Method")
    payment_subtype = fields.Selection(related='journal_id.payment_subtype')
    wiz_id = fields.Many2one('check.split.wiz')
    amount = fields.Float(string='Amount')
    bank = fields.Many2one('payment.bank', _("Bank Name"))
    check_number = fields.Char(string=_("Check number"), required=False)
    check_date = fields.Date(string=_('Check Date'), required=False)
    payment_date = fields.Date(string="Payment Date", required=True, default=datetime.today(),track_visibility='onchange')


