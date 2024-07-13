# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime
TYPE_SELECTION = [('sale', _('Sale')),
                  ('sale_refund', _('Sale Refund')),
                  ('purchase', _('Purchase')),
                  ('purchase_refund', _('Purchase Refund')),
                  ('cash', _('Cash')),
                  ('bank', _('Bank and Checks')),
                  ('general', _('General')),
                  ('situation', _('Opening/Closing Situation'))]


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


class MergeCustomerWizard(models.TransientModel):
    _name = 'merge.customer.wizard'

    date = fields.Date(required=True)
    parent_id = fields.Many2one(comodel_name="account.payment", string="Payments", required=False, )
    payment_method_id = fields.Many2one(related="parent_id.payment_method_id", comodel_name="account.payment.method",string="Payment Method	", required=False, )
    partner_id = fields.Many2one(comodel_name="res.partner", string="Customer", required=False, )
    journal_id = fields.Many2one(comodel_name="account.journal", string="Journal", required=False, )
    reservation_id = fields.Many2one(comodel_name="res.reservation", string="", required=False,readonly=True )
    property_id = fields.Many2one(related="reservation_id.property_id", comodel_name="product.product",string="Unit", required=False, )
    merge_ids = fields.One2many(comodel_name="merge.customer.line.wizard", inverse_name="merge_id", string="Lines", required=False, )
    amount = fields.Monetary(string='Amount', required=True, tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=True,  default=lambda self: self.env.company.currency_id)
    amount_paid = fields.Float(string="Amount Paid", required=False,readonly=True)
    amount_due = fields.Float(string="Amount Due",)

    communication = fields.Char(string='Reference')



    date = fields.Date(required=False, default=fields.Date.context_today)
    bank_name_id = fields.Many2one('payment.bank', _("Bank Name"))
    payment_method_id2= fields.Many2one(comodel_name='account.payment.method', string='Payment Method',
                                        required=False,
                                        help="The payment method used by the payments in this batch.")
    cheque_no_start = fields.Char(string="Cheque Start No", required=False)
    cheque_start_date = fields.Date(string='Due Date Start')
    duration = fields.Selection(string="Duration Type For Cheques", selection=duration, required=False)
    no_of_cheques = fields.Integer(string="Number Of Cheques", required=False)
    cheque_seq = fields.Char()
    amount_by = fields.Selection(
        string='Amount By',
        selection=[('amount', 'Amount'),
                   ('percentage', 'Percentage'), ],
        required=False, )
    value = fields.Float(string="Value", required=False)
    payment_type = fields.Selection([('inbound', 'Inbound'), ('outbound', 'Outbound')], required=False)
    partner_type = fields.Selection([('customer', 'Customer'), ('supplier', 'Vendor')], tracking=True)




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
        self.date=False
        self.bank_name_id=False
        self.payment_method_id2=False
        self.payment_type=''
        self.duration=''
        self.no_of_cheques=0
        self.cheque_start_date=False
        self.cheque_no_start=''
        self.cheque_seq=''
        self.amount_by=''
        self.value=0

    def add_line(self,amount,date):
        print('DD>>D',self.date)
        return {
            'amount': amount,
            'date': self.date,
            'payment_method_id': self.payment_method_id2.id,
            'due_date': date,
            'check_number': self.cheque_seq,
            "bank_name_id": self.bank_name_id.id,
            "payment_type": self.payment_type,
            "journal_id": self.journal_id.id,
            "partner_id": self.partner_id.id,
            "partner_type": self.partner_type,

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
        lines=[]

        for repeat in range(0, self.no_of_cheques):
            line = self.add_line(div_amount, date)
            print("D>D>",line)
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
        self.merge_ids = lines
        self.clear_fields()

        return {
            'type': 'ir.actions.act_window',
            'res_model': "merge.customer.wizard",
            'res_id': self.id,
            'view_mode': 'form,tree',
            'name': 'Merge Customer',
            'target': 'new'
        }









    # def _compute_amount_duo(self):
    #     print("here come")
    #     for line in self:
    #         payment_obj = self.env['account.payment']
    #         payment = payment_obj.search([('parent_id', '=', line.parent_id.id)])
    #         total = 0
    #         print("payment :: ",payment)
    #         if payment:
    #             for p in payment:
    #                 total += p.amount
    #             line.amount_duo = total
    #         else:
    #             line.amount_duo = 0
    def confirm_merge_customer(self):
        for rec in self:
            account_payment = self.env['account.payment']
            amount = 0
            for line in rec.merge_ids:
                amount += line.amount

            if rec.amount == rec.amount_paid:
                raise UserError(_("You Must Add Amount Lines Equal  base Amount"))

            # if rec.parent_id.state == "posted":
            #     print("herreee")
            #     rec.parent_id.move_date = rec.date
            #     print("rec.parent_id.move_date :: %s",rec.parent_id.move_date)
            #     rec.parent_id.multi_select = True
            #     rec.parent_id.refund_notes(ref_notes_batch=1)
            # if rec.parent_id.state == 'refunded_under_collection':
            #     account_batch_payment = self.env['account.batch.payment'].search([
            #         ('id', '=', rec.parent_id.batch_payment_id.id), ("state", '=', 'refunded_under_collection')
            #     ])
            #     # for account_batch in account_batch_payment:
            #     #     for line in account_batch.payment_ids:
            #     #         if rec.parent_id.id == line.id:
            #     #             line.write({
            #     #                 'ref_coll_batch': rec.date(),
            #     #                 'multi_select': True,
            #     #             })
            #     # account_batch.refund_under_collections(ref_und_coll_batch=1)
            #     rec.parent_id.refund_notes(ref_notes_batch=1)
            total_add = 0
            for line in  rec.merge_ids:
                total_add += line.amount

            amount_base = rec.amount_paid + total_add
            if amount_base > rec.amount:
                raise UserError(_("You Must Add Amount Lines Equal  base Amount"))


            for line in  rec.merge_ids:
                if line.journal_id.type != 'cash':
                    pay = account_payment.create({
                        'state': 'draft',
                        'payment_type': line.payment_type,
                        'partner_type': line.partner_type,
                        'partner_id': line.partner_id.id,
                        'communication': line.merge_id.communication,
                        'journal_id':line.journal_id.id,
                        'currency_id':line.journal_id.currency_id.id or self.env.company.currency_id.id,
                        'amount': line.amount,
                        'date': line.date,
                        'due_date': line.due_date,
                        'actual_date': line.due_date,
                        'bank_name': line.bank_name_id.name,
                        'payment_bank_id': line.bank_name_id.id,
                        'check_number': line.check_number,
                        'payment_method_id': line.payment_method_id.id,
                        'parent_id_split':rec.parent_id.id,
                        'reservation_id':rec.reservation_id.id,
                        'is_contract': True,
                        'create_date': datetime.now().date(),

                    })
                    pay.post()
                    pay.set_check_amount_in_words()
                else:
                    pay = account_payment.create({
                        'state': 'draft',
                        'payment_type': line.payment_type,
                        'partner_type': line.partner_type,
                        'partner_id': line.partner_id.id,
                        'communication': line.merge_id.communication,
                        'journal_id': line.journal_id.id,
                        'currency_id': line.journal_id.currency_id.id or  self.env.company.currency_id.id,
                        'amount': line.amount,
                        'date': line.date,
                        'payment_method_id': line.payment_method_id.id,
                        'parent_id_split': rec.parent_id.id,
                        'reservation_id': rec.reservation_id.id,
                        'is_contract': True,
                        'create_date': datetime.now().date(),
                        'payment_bank_id': line.bank_name_id.id,
                        'due_date': line.due_date,
                        'bank_name': line.bank_name_id.name,
                        'payment_bank_id': line.bank_name_id.id,
                        'check_number': line.check_number,


                    })
                    print(">DSS????????",pay)
                    pay.post()
                    pay.set_check_amount_in_words()



class MergeCustomerLineWizard(models.TransientModel):
    _name = 'merge.customer.line.wizard'

    # def _get_defualt_batch(self):
    #     payment_method_obj = self.env['account.payment.method']
    #     payment  = payment_method_obj.search([('name','not ilike','Manu')],limit=1)
    #     if payment:
    #         return payment.id
    merge_id = fields.Many2one(comodel_name="merge.customer.wizard", string="Merge Customer", required=False, )
    due_date = fields.Date(required=False)
    actual_date = fields.Date(required=False)
    payment_type = fields.Selection([('inbound', 'Inbound'), ('outbound', 'Outbound')], required=True)
    partner_type = fields.Selection([('customer', 'Customer'), ('supplier', 'Vendor')], tracking=True)
    partner_id = fields.Many2one('res.partner', string='Partner', tracking=True)
    journal_id = fields.Many2one('account.journal', string='Journal', required=True,  tracking=True, domain="[('type', 'in', ('bank', 'cash')), ('company_id', '=', company_id)]")
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company')
    amount = fields.Monetary(string='Amount', required=True, tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=True,  default=lambda self: self.env.company.currency_id)
    type = fields.Selection(selection=TYPE_SELECTION, related='journal_id.type', store=True, string='Payment Type')

    @api.onchange('journal_id')
    def onchange_method_journal_id(self):
        if self.journal_id.type == 'bank':
            method = self.env['account.payment.method'].sudo().search([
                ('name', '=', 'Batch Deposit')
            ], limit=1)
            # self.payment_method_id = method.id
        elif self.journal_id.type == 'cash':
            method = self.env['account.payment.method'].sudo().search([
                ('name', '=', 'Manual')
            ], limit=1)
            # self.payment_method_id = method.id
    date = fields.Date(required=True, default=fields.Date.context_today)
    bank_name_id = fields.Many2one('payment.bank', _("Bank Name"))
    bank_name = fields.Char()
    check_number = fields.Char()
    # payment_method_id = fields.Many2one(comodel_name='account.payment.method', string='Payment Method',
    # required=True,
    # default = _get_defualt_batch,
    #  help="The payment method used by the payments in this batch.")
    payment_method_id = fields.Many2one(comodel_name='account.payment.method', string='Payment Method',
                                        required=True,
                                        help="The payment method used by the payments in this batch.")
    #payment_method_code = fields.Char(related='payment_method_id.code',
    #    help="Technical field used to adapt the interface to the payment type selected.", readonly=True)
    active_cheque_number = fields.Char(related='journal_id.check_next_number')

    cheque_number = fields.Integer(copy=False)

class MergeVendorWizard(models.TransientModel):
    _name = 'merge.vendor.wizard'

    date = fields.Date(required=True)
    parent_id = fields.Many2one(comodel_name="account.payment", string="Payments", required=False, )
    payment_method_id = fields.Many2one(related="parent_id.payment_method_id", comodel_name="account.payment.method",string="Payment Method	", required=False, )
    partner_id = fields.Many2one(comodel_name="res.partner", string="Customer", required=False, )
    journal_id = fields.Many2one(comodel_name="account.journal", string="Journal", required=False, )
    reservation_id = fields.Many2one(comodel_name="res.reservation", string="", required=False, readonly=True)
    property_id = fields.Many2one(related="reservation_id.property_id", comodel_name="product.product", string="Unit",
                                  required=False, )
    merge_ids = fields.One2many(comodel_name="merge.vendor.line.wizard", inverse_name="merge_id", string="Lines",
                                required=False, )
    amount = fields.Monetary(string='Amount', required=True, tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=True,
                                  default=lambda self: self.env.company.currency_id)

    amount_paid = fields.Float(string="Amount Paid", required=False, readonly=True)
    amount_due = fields.Float(string="Amount Due",)


    communication = fields.Char(string='Reference')

    #
    # def _compute_amount_duo(self):
    #     for line in self:
    #         payment_obj = self.env['account.payment']
    #         payment = payment_obj.search([('parent_id', '=', line.parent_id.id)])
    #         total = 0
    #         if payment:
    #             for p in payment:
    #                 total += p.amount
    #             line.amount_duo = total
    #         else:
    #             line.amount_duo = 0
    def confirm_merge_vendor(self):
        for rec in self:
            account_payment = self.env['account.payment']
            amount = 0
            for line in rec.merge_ids:
                amount += line.amount

            if rec.amount == rec.amount_paid:
                raise UserError(_("You Must Add Amount Lines Equal  base Amount"))

            # if parent_id posted
            # if rec.parent_id.state == "posted":
            #     rec.parent_id.refund_date = rec.date
            #     rec.parent_id.multi_select = True
            #     rec.parent_id.refund_payable(refund2=1)
            #

            # if refunded_under_collection
            # if rec.parent_id.state == 'refunded_under_collection':
            #     account_batch_payment = self.env['account.batch.payment'].search([
            #         ('id', '=', rec.parent_id.batch_payment_id.id), ("state", '=', 'refunded_under_collection')
            #     ])
            #     rec.parent_id.refund_payable(refund2=1)

            total_add = 0
            for line in rec.merge_ids:
                total_add += line.amount

            amount_base = rec.amount_paid + total_add
            if amount_base > rec.amount:
                raise UserError(_("You Must Add Amount Lines Equal  base Amount"))

            for line in rec.merge_ids:
                print("enter hererere ")
                if line.journal_id.type != 'cash':
                    print("cash :> if ")
                    pay = self.env['account.payment'].create({

                        # 'state': 'draft',
                        # 'payment_type': line.payment_type,
                        # 'partner_type': line.partner_type,
                        # 'partner_id': line.partner_id.id,
                        # 'journal_id': line.journal_id.id,
                        # 'amount': line.amount,
                        # 'date': line.date,
                        # 'due_date': line.date,
                        # 'bank_name': line.bank_name,
                        # 'check_number': line.check_number,
                        # 'payment_method_id': line.payment_method_id.id,
                        # 'parent_id': rec.parent_id.id,
                        # 'reservation_id': rec.reservation_id.id,
                        # 'is_contract': True,

                        'state': 'draft',
                        'payment_type': line.payment_type,
                        'partner_type': line.partner_type,
                        'partner_id': line.partner_id.id,
                        'journal_id': line.journal_id.id,
                        'communication': line.merge_id.communication,
                        'currency_id': line.journal_id.currency_id.id or self.env.company.currency_id.id,
                        'amount': line.amount,
                        'date': line.date,
                        'cheque_books_id': line.cheque_books_id.id,
                        'cheque_number': line.cheque_number,
                        'payment_method_id': line.payment_method_id.id,
                        'due_date': line.due_date,
                        'actual_date': line.due_date,
                        # 'refund_date': line.date,
                        'parent_id_split': rec.parent_id.id,
                        'reservation_id': rec.reservation_id.id,
                        'is_contract': True,
                        'create_date': datetime.now().date(),
                        'bank_name': line.bank_name_id.name,
                        'payment_bank_id': line.bank_name_id.id,

                    }).sudo()
                    print("cash :> if pay :>",pay)

                    pay.post()
                    pay.set_check_amount_in_words()
                else:
                    print("else ")
                    pay = account_payment.create({
                        'state': 'draft',
                        'payment_type': line.payment_type,
                        'partner_type': line.partner_type,
                        'partner_id': line.partner_id.id,
                        'journal_id': line.journal_id.id,
                        'communication': line.merge_id.communication,
                        'currency_id': line.journal_id.currency_id.id or self.env.company.currency_id.id,
                        'amount': line.amount,
                        'date': line.date,
                        'cheque_books_id': line.cheque_books_id.id,
                        'cheque_number_rel': line.cheque_number_rel,
                        'payment_method_id': line.payment_method_id.id,
                        'parent_id_split': rec.parent_id.id,
                        'reservation_id': rec.reservation_id.id,
                        'is_contract': True,
                        'create_date': datetime.now().date(),
                        'due_date': line.due_date,
                        'cheque_number': line.cheque_number,
                        'payment_bank_id': line.bank_name_id.id,

                    })
                    print("pay :> ",pay)
                    pay.post()
                    pay.set_check_amount_in_words()
class MergeVendorLineWizard(models.TransientModel):
    _name = 'merge.vendor.line.wizard'

    def get_cheque_number(self):

        """""
            default domain for cheque book

            :return list of cheque books in the domain depends on the input of journal

        """

        bank_account = False
        if self.journal_id:
            bank_account = self.journal_id
        else:
            if 'params' in self._context:
                if 'id' in self._context['params']:
                    obj = self.env['account.payment'].browse(self._context['params']['id'])
                    bank_account = obj.journal_id

        if bank_account:
            if not bank_account.multi_cheque_book:
                if bank_account.cheque_books_ids:
                    cheque_book_object = [r for r in bank_account.cheque_books_ids if r.activate == True]
                    if cheque_book_object:
                        return [('id', '=', cheque_book_object[0].id)]
            else:
                if bank_account.cheque_books_ids:
                    cheque_book_object = [r.id for r in bank_account.cheque_books_ids]
                    return [('id', 'in', cheque_book_object)]

    # def _get_defualt_batch(self):
    #     payment_method_obj = self.env['account.payment.method']
    #     payment  = payment_method_obj.search([('name','not ilike','Manu')],limit=1)
    #     if payment:
    #         return payment.id
    merge_id = fields.Many2one(comodel_name="merge.vendor.wizard", string="Merge Vendor", required=False, )
    payment_type = fields.Selection([('inbound', 'Inbound'), ('outbound', 'Outbound')], required=True)
    due_date = fields.Date()
    actual_date = fields.Date()
    partner_type = fields.Selection([('customer', 'Customer'), ('supplier', 'Vendor')], tracking=True)
    partner_id = fields.Many2one('res.partner', string='Partner', tracking=True)
    journal_id = fields.Many2one('account.journal', string='Journal', required=True,  tracking=True, domain="[('type', 'in', ('bank', 'cash')), ('company_id', '=', company_id)]")

    @api.onchange('journal_id')
    def onchange_method_journal_id(self):
        if self.journal_id.type == 'bank':
            method = self.env['account.payment.method'].sudo().search([
                ('name', '=', 'Batch Deposit')
            ], limit=1)
            # self.payment_method_id = method.id
        elif self.journal_id.type == 'cash':
            method = self.env['account.payment.method'].sudo().search([
                ('name', '=', 'Manual')
            ], limit=1)
            # self.payment_method_id = method.id
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company')
    amount = fields.Monetary(string='Amount', required=True, tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=True,  default=lambda self: self.env.company.currency_id)

    date = fields.Date(required=True, default=fields.Date.context_today)
    bank_name_id = fields.Many2one('payment.bank', _("Bank Name"))
    bank_name = fields.Char()
    check_number = fields.Char()
    payment_method_id = fields.Many2one(comodel_name='account.payment.method', string='Payment Method',
    required=True,
     help="The payment method used by the payments in this batch.")
    #payment_method_code = fields.Char(related='payment_method_id.code',
    #    help="Technical field used to adapt the interface to the payment type selected.", readonly=True)
    cheque_books_id = fields.Many2one(comodel_name='cheque.books', domain=lambda self: self.get_cheque_number())
    cheque_number_rel = fields.Char()
    multi_check_payment = fields.Boolean(related='journal_id.multi_cheque_book')
    active_cheque_number = fields.Char(related='journal_id.check_next_number')
    cheque_number = fields.Integer(copy=False)
    type = fields.Selection(selection=TYPE_SELECTION, related='journal_id.type', store=True, string='Payment Type')

    @api.onchange('multi_check_payment', 'cheque_books_id')
    def get_cheque_number_name(self):
        for rec in self:
            if rec.journal_id:
                bank_account = rec.journal_id
            else:
                if 'params' in self._context:
                    if 'id' in self._context['params']:
                        obj = self.env['account.payment'].browse(self._context['params']['id'])
                        bank_account = obj.journal_id
                        print('bank_account ',bank_account)
            if rec.cheque_books_id:
                if not bank_account.multi_cheque_book:
                    if bank_account.cheque_books_ids:
                        cheque_book_object = [r for r in bank_account.cheque_books_ids if r.activate == True][0]
                        rec.cheque_number_rel = str(rec.active_cheque_number)

                else:
                    rec.active_cheque_number = rec.cheque_number
            else:
                rec.cheque_number_rel = False
                return False
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.CHECK", rec.cheque_books_id, rec.cheque_number_rel)

class Me(models.Model):
    _inherit='mail.message'

    @api.model_create_multi
    def create(self, values):
        for val in values:
            val['parent_id']=False
        # Add code here
        return super(Me, self).create(values)
