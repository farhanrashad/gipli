# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
import odoo.addons.decimal_precision as dp

from odoo.exceptions import ValidationError
from odoo.exceptions import ValidationError,UserError
import num2words


class normal_payments(models.Model):
    _name = 'normal.payments'
    _rec_name = 'name'
    _description = 'Payments'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def get_user(self):
        return self._uid

    def get_currency(self):
        return self.env.company.currency_id.id

    payment_No = fields.Char(track_visibility='onchange')
    name = fields.Char(string="", required=False,track_visibility='onchange')
    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner Name", required=False,track_visibility='onchange')
    payment_date = fields.Date(string="Payment Date", required=True, default=datetime.today(),track_visibility='onchange')
    amount = fields.Float(string="Amount", compute="change_checks_ids", store=True,track_visibility='onchange')
    amount1 = fields.Float(string="Amount",track_visibility='onchange')
    payment_method = fields.Many2one(comodel_name="account.journal", string="Payment Journal", required=True,
                                     domain=[('type', 'in', ('bank', 'cash'))],track_visibility='onchange')
    destination_journal_id = fields.Many2one(comodel_name="account.journal", string="Destination Journal",track_visibility='onchange')

    bank_required= fields.Boolean( string='Bank Required',realted='payment_method.bank_required',store=True,track_visibility='onchange')

    payment_subtype = fields.Selection(related='payment_method.payment_subtype',track_visibility='onchange')
    user_id = fields.Many2one(comodel_name="res.users", default=get_user,track_visibility='onchange')
    currency_id = fields.Many2one(comodel_name="res.currency", default=get_currency,track_visibility='onchange')
    state = fields.Selection(selection=[('draft', 'Draft'), ('posted', 'Posted'),('cancel','Canceled'),('payment_refund_notes_receivable','Payment Refund Notes Receivable') ], default='draft',
                             track_visibility='onchange')
    pay_check_ids = fields.One2many('native.payments.check.create', 'nom_pay_id', string=_('Checks'),track_visibility='onchange')
    send_rec_money = fields.Selection(string="Payment Type",
                                      selection=[('send', 'Send Money'), ('rece', 'Receive Money')], default='rece',track_visibility='onchange')
    receipt_number = fields.Char(string="Reference",track_visibility='onchange')
    account_id = fields.Many2one('account.account', string="Account",track_visibility='onchange')
    select_account_id = fields.Many2one('account.account', string="Select Account",track_visibility='onchange')
    account_emp_type = fields.Selection(string="Employee Type",
                                        selection=[('t1', 'سلف'), ('t2', 'عهد'), ('t3', 'مصروف رواتب مستحقة'),
                                                   ('t4', 'مصروف عمولات مستحقة')], required=False,track_visibility='onchange')
    custom_account_id = fields.Many2one(comodel_name="account.account", string="Account", required=False,track_visibility='onchange')

    analyitc_id = fields.Many2one('account.analytic.account', string="Analytic Account",track_visibility='onchange')
    analytic_precision = fields.Integer(
        store=False,
        default=lambda self: self.env['decimal.precision'].precision_get("Percentage Analytic"),
    )

    request_reservation_id = fields.Many2one(comodel_name="request.reservation", string="Request Reservation", required=False, readonly=False,track_visibility='onchange')
    reservation_id = fields.Many2one(comodel_name="res.reservation", string="Reservation", required=False, readonly=False,track_visibility='onchange')
    custoemr_payment_id = fields.Many2one(comodel_name="customer.payment", string="Customer Payment", required=False,readonly=True,track_visibility='onchange')
    property_id = fields.Many2one(related="reservation_id.property_id", comodel_name="product.product", string="Unit",required=False, store=True, readonly=False,track_visibility='onchange')
    state_payment = fields.Selection([('cash', 'Cash'),
                                      ('visa', 'Visa'),
                                      ('cheque', 'Cheque'),
                                      ('bank', 'Bank'),
                                      ], default="cheque",track_visibility='onchange')

    multi_accounts = fields.Boolean(string="Multi Accounts?",track_visibility='onchange')
    multi_account_ids = fields.One2many(comodel_name="payment.multi.accounts", inverse_name="normal_payment_id", string="Accounts", required=False)
    from_check_number = fields.Char(string=_("From Check Number"),required=False,default="0",track_visibility='onchange')
    from_check_date = fields.Date(string=_("From Check Date"),required=False,track_visibility='onchange')
    old_payment_id = fields.Many2one(
        comodel_name='account.payment',
        string='Old_payment',
        required=False,track_visibility='onchange')
    old_payment_id_id=fields.Integer(compute='_calc_old_payment_id_url',store=True,string='Old Payment ID',readonly=False,track_visibility='onchange')
    old_payment_id_url=fields.Char(compute='_calc_old_payment_id_url',store=True,string='Old Payment Url',track_visibility='onchange')
    is_internal_transfer2 = fields.Boolean(compute='_calc_old_payment_id_url',store=True,string='Is Internal Transfer',track_visibility='onchange')
    document_type_id = fields.Many2one(comodel_name="move.doc.type", string="نوع المستند", required=False,track_visibility='onchange')
    customer_type_id = fields.Many2one(comodel_name="customer.types", string="Customer Type", required=False,track_visibility='onchange')
    external_document_number = fields.Char(string="رقم المستند الخارجي", required=False,track_visibility='onchange')
    external_document_type = fields.Char(string="نوع المستند الخارجي", required=False,track_visibility='onchange')
    accounting_allocation = fields.Selection(
        string='Accounting Allocation',
        selection=[('maintenance', 'Maintenance'),
                   ('deposit', 'Deposit'),
                   ('insurance', 'Insurance'),
                   ('eoi', 'EOI'),
                   ],
        required=False, )

    @api.onchange('accounting_allocation')
    @api.depends('accounting_allocation')
    def onchange_accounting_allocationd(self):
        account=self.env['account.account'].search([('accounting_allocation','=',self.accounting_allocation)],limit=1)
        if account:
            if self.partner_type=='select_account':
                self.select_account_id=account.id
            else:
                self.account_id=account.id
        return {
            'domain': {'account_id': [('accounting_allocation','=',self.accounting_allocation)],'select_account_id':[('accounting_allocation','=',self.accounting_allocation)]}
        }



    def _calc_old_payment_id_url(self):
        for rec in self:
            if rec.old_payment_id:
                rec.old_payment_id_id=rec.old_payment_id.id
                rec.old_payment_id_url="""https://themarq2020-themarq-test-13-master-9334849.dev.odoo.com/web#id={id}&action=173&model=account.payment&view_type=form&cids=14,1,2,3,9,10,11,12,13&menu_id=163""".format(id=rec.old_payment_id.id)
                rec.is_internal_transfer2=rec.old_payment_id.is_internal_transfer
            else:
                rec.old_payment_id_id=0
                rec.old_payment_id_url=''
                rec.is_internal_transfer2=rec.old_payment_id.is_internal_transfer




    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company,track_visibility='onchange')



    check_state = fields.Selection(selection=[('holding','Posted'),('depoisted','Under collection'),
                                         ('approved','Withdrawal'),
                                        ('rejected','Rejected'),
                                        ('send_to_lagel', 'Send To Legal'),
                                        ('deliver', 'Deliver'),
                                        ('refund_deliver', 'Refund Deliver'),
                                        ('refund', 'Refund'),
                                        ('refund_send_to_lagel','Refund Send To Legal')
                                         , ('returned', 'Refund Under collection'), ('handed', 'Handed'),
                                        ('debited', 'Withdrawal Payable'),
                                        ('canceled', 'Canceled'),
                                        ('cs_return','Refund Notes Receivable'),
                                        ('payment_cancel','Payment Canceled'),
                                        ('payment_draft','Payment Draft'),
                                        ('delivery_to_customer', 'Delivery To Customer'),

                                        ]
                            ,related='check_id.state',store=True,string="Check Status",track_visibility='onchange',readonly=False)
    check_id = fields.Many2one('check.management',string="Check Number",store=True,track_visibility='onchange',readonly=False)
    check_amount = fields.Float(string=_('Check Amount'),digits=dp.get_precision('Product Price'),related='check_id.amount',store=True,readonly=False,track_visibility='onchange')
    check_number = fields.Char(string=_("Check Number"),required=False,related='check_id.check_number',store=True,readonly=False,track_visibility='onchange')
    check_date = fields.Date(string=_("Check Date"),related='check_id.check_date',store=True,track_visibility='onchange',readonly=False)


    @api.depends('pay_check_ids')
    def _calc_checque_state(self):
        for rec in self:
            check_id=self.env['check.management'].sudo().search([('check_payment_id','=',rec.id)],limit=1)
            if check_id:
                rec.check_id=check_id.id
                rec.check_state=check_id.state
            else:

                rec.check_id = False
                rec.check_state =False










    @api.onchange('account_emp_type','partner_type')
    def onchange_account_emp_type5(self):
        if self.partner_type=='employee':
            if self.account_emp_type == 't1':
                domain = [('petty', '=', True)]
                return {
                    'domain': {'custom_account_id': domain,'partner_id':[('is_employee','=',True)]}
                }
            if self.account_emp_type == 't2':
                domain = [('custody', '=', True)]
                return {
                    'domain': {'custom_account_id': domain,'partner_id':[('is_employee','=',True)]}
                }
            if self.account_emp_type == 't3':
                domain = [('accrued', '=', True)]
                return {
                    'domain': {'custom_account_id': domain,'partner_id':[('is_employee','=',True)]}
                }
            if self.account_emp_type == 't4':
                domain = [('other', '=', True)]
                return {
                    'domain': {'custom_account_id': domain,'partner_id':[('is_employee','=',True)]}
                }
        else:
            return {
                'domain': {'partner_id': []}
            }


    @api.onchange('partner_id', 'account_emp_type')
    def onchange_partner_id7(self):
        if self.partner_id:
            if self.account_emp_type == 't1':
                self.custom_account_id = self.partner_id.petty_account.id
            if self.account_emp_type == 't2':
                self.custom_account_id = self.partner_id.custody_account.id
            if self.account_emp_type == 't3':
                self.custom_account_id = self.partner_id.accrued_account.id
            if self.account_emp_type == 't4':
                self.custom_account_id = self.partner_id.other_account.id

    @api.constrains('pay_check_ids')
    def check_pay_check_ids(self):
        for rec in self:
            for line in rec.pay_check_ids:
                if rec.payment_subtype=='issue_check':
                    if len(self.env['native.payments.check.create'].search([("check_number", "=", line.check_number),
                                                                            ('cheque_books_id','=',line.cheque_books_id.id)])) > 1:
                        raise ValidationError("Check Number already Taken")




    @api.model
    def _populate_choice(self):
        choices1 = [
            ('customer', 'Customer'), ('supplier', 'Vendor'),('employee','Employee'), ('select_account', 'Select Account')
            ,('internal', 'Internal Transfer')
        ]
        choices2 = [
            ('select_account', 'Select Account')
        ]
        # if self.env.context.get('default_partner_type'):
        #     return choices2
        # else:
        return choices1

    partner_type = fields.Selection(selection=_populate_choice,
                                    tracking=True, readonly=True, default='customer',
                                    states={'draft': [('readonly', False)]},track_visibility='onchange')

    description = fields.Char(_('Description'),track_visibility='onchange')
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Type', oldname="payment_method",track_visibility='onchange')
    parent_payment_id = fields.Many2one('normal.payments', string="Parent  Payment",track_visibility='onchange')
    cheque_books_ids = fields.Many2many(comodel_name='cheque.books', compute='calc_cheque_books_ids',store=True)

    # cheque_state = fields.Selection(selection=[('holding', 'Posted'), ('depoisted', 'Under collection'),
    #                                     ('approved', 'Withdrawal'),
    #                                     ('rejected', 'Rejected'),
    #                                     ('send_to_lagel', 'Send To Legal'),
    #                                     ('deliver', 'Deliver'),
    #                                     ('refund_deliver', 'Refund Deliver'),
    #                                     ('refund', 'Refund'),
    #                                     ('refund_send_to_lagel', 'Refund Send To Legal')
    #     , ('returned', 'Refund Under collection'), ('handed', 'Handed'),
    #                                     ('debited', 'Withdrawal Payable'),
    #                                     ('canceled', 'Canceled'),
    #                                     ('cs_return', 'Refund Notes Receivable'),
    #                                     ('payment_cancel', 'Payment Canceled'),
    #                                     ('payment_draft', 'Payment Draft'),
    #                                     ('delivery_to_customer', 'Delivery To Customer'),
    #
    #                                     ]
    #                          , track_visibility='onchange')



    @api.depends('payment_method')
    def calc_cheque_books_ids(self):
        for rec in self:
            rec.cheque_books_ids=[(6, 0, [x.id for x in rec.payment_method.cheque_books_ids])]



    @api.constrains('pay_check_ids','payment_subtype')
    def check_therapist_id(self):
        if self.pay_check_ids and self.payment_subtype=='issue_check':
            for line in self.pay_check_ids:
                if line.cheque_books_id and line.check_number:
                    if float(line.check_number) not in range(int(line.cheque_books_id.start_from),int(line.cheque_books_id.end_in)+1):
                        raise ValidationError("Check Number Not In Range Of This Book")
















    @api.constrains('amount')
    def _total_amount(self):
        for rec in self:
            if rec.payment_subtype:
                if (rec.amount) == 0.0:
                    raise exceptions.ValidationError('amount for checks must be more than zerO!')
            else:
                if (rec.amount1) == 0.0:
                    raise exceptions.ValidationError('amount for payment must be more than zerO!')

    @api.constrains('pay_check_ids', 'multi_accounts', 'multi_account_ids')
    def check_total_amount(self):
        for rec in self:
            if rec.multi_accounts and rec.multi_account_ids and rec.pay_check_ids:
                total1=sum(rec.multi_account_ids.mapped('amount'))
                total2=sum(rec.pay_check_ids.mapped('amount'))
                if total1 != total2:
                    raise exceptions.ValidationError('Multi Account Amount Must  = Cheque Amount')

    @api.onchange('partner_id', 'send_rec_money','partner_type','select_account_id','custom_account_id','multi_accounts','multi_account_ids')
    def get_partner_acc(self):

        if self.partner_type!='select_account':
            if self.send_rec_money == 'send':
                # self.account_id = self.partner_id.property_account_payable_id.id
                self.payment_method = self.env['account.journal'].search([('payment_subtype','=','issue_check'),('type','=','bank')],limit=1).id
            elif self.send_rec_money == 'rece':
            #     # self.account_id = self.partner_id.property_account_receivable_id.id
                self.payment_method = self.env['account.journal'].search([('payment_subtype','=','rece_check'),('type','=','bank')],limit=1).id

        if self.partner_type=='customer':
            self.account_id = self.partner_id.property_account_receivable_id.id
        if self.partner_type == 'supplier':
            self.account_id = self.partner_id.property_account_payable_id.id

        if self.partner_type == 'select_account':
            if self.multi_accounts:
                if self.multi_account_ids:
                    self.account_id=self.multi_account_ids[0].account_id.id
                else:
                    self.account_id = self.select_account_id.id
            else:
                self.account_id = self.select_account_id.id

        if self.partner_type == 'employee':
            self.account_id = self.custom_account_id.id

        if self.partner_type == 'internal':
            self.account_id = self.company_id.transfer_account_id.id


    def get_partner_acc2(self):
        if self.send_rec_money == 'send':
            self.account_id = self.partner_id.property_account_payable_id.id
        elif self.send_rec_money == 'rece':
            self.account_id = self.partner_id.property_account_receivable_id.id

    @api.depends('pay_check_ids','multi_accounts','multi_account_ids')
    def change_checks_ids(self):
        for rec in self:
            if rec.multi_accounts:
                rec.amount = sum(rec.multi_account_ids.mapped('amount'))
                rec.amount1 = sum(rec.multi_account_ids.mapped('amount'))
            else:
                tot_amnt = 0.0
                if rec.sudo().payment_subtype:
                    if rec.sudo().pay_check_ids:
                        for x in rec.sudo().pay_check_ids:
                            tot_amnt += x.amount
                rec.amount = tot_amnt
                if rec.pay_check_ids:
                    rec.amount1 = tot_amnt




    # def button_journal_entries(self):
    #     return {
    #         'name': ('Journal Items'),
    #         'view_type': 'form',
    #         'view_mode': 'tree,form',
    #         'res_model': 'account.move.line',
    #         'view_id': False,
    #         'type': 'ir.actions.act_window',
    #         'domain': [('jebal_con_pay_id', 'in', self.ids)],
    #     }

    # @api.depends('partner_id')
    # def get_title(self):
    #     for rec in self:
    #         if rec.partner_id:
    #             rec.name = "Payment for Partner" + str(rec.partner_id.name)
    #         else:
    #             rec.name = '*'
    #         return True

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals['send_rec_money']=='send':
                vals['name'] = self.env['ir.sequence'].next_by_code('check.payment.out') or _("New")
            else:
                vals['name'] =  self.env['ir.sequence'].next_by_code('check.payment.in' ) or _("New")
        return super().create(vals_list)

    def button_journal_entries(self):
        return {
            'name': _('Journal Items'),
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': ['|',('move_id.check_payment_id', 'in', self.ids),('jebal_con_pay_id', 'in', self.ids)],
        }

    def action_confirm(self):
        move = self.env['account.move'].sudo().search([('check_payment_id', '=', self.id)], limit=1)
        check_id=self.env['check.management'].search([('check_payment_id','=',self.id),('state','in', ['payment_draft','holding','handed','payment_cancel'])],limit=1)
        print("D>>D>>D",check_id)
        if check_id:
            if self.send_rec_money == 'rece':
                check_state = 'holding'
            else:
                check_state = 'handed'
            check_id.write({'state':check_state})


        if move:
            if move.state=='cancel':
                move.button_draft()
            if move.state != 'posted':
                move.action_post()
            self.state = 'posted'
        else:
            pay_amt = 0
            if self.payment_subtype:
                pay_amt = self.amount
            else:
                pay_amt = self.amount1
            move = {
                'journal_id': self.payment_method.id,
                'ref': self.receipt_number,
                'company_id': self.env.company.id,
            }
            move_line = {
                'partner_id': self.partner_id.id,
                'ref': self.receipt_number,
                'jebal_con_pay_id': self.id,
            }
            if self.send_rec_money == 'send':
                debit_account = [{'account': self.account_id.id, 'percentage': 100,
                                  'analyitc_id':self.analyitc_id.id,
                                  }]
                credit_account = [{'account': self.payment_method.default_debit_account_id.id, 'percentage': 100,

                                   'analyitc_id': False
                                   }]
            else:
                credit_account = [{'account': self.account_id.id, 'percentage': 100,
                                   'analyitc_id':self.analyitc_id.id,
                                   }]
                debit_account = [{'account': self.payment_method.default_debit_account_id.id, 'percentage': 100,
                                  'analyitc_id':False
                                  }]
            move_id=self.env['create.moves'].create_move_lines2(move=move, move_line=move_line,
                                                       debit_account=debit_account,
                                                       credit_account=credit_account,
                                                       src_currency=self.currency_id,
                                                       check_payment_id=self.id,
                                                       amount=pay_amt,
                                                       cheque=self.pay_check_ids[0].check_number if self.pay_check_ids else "",
                                                       check_id=self.pay_check_ids[0].id if self.pay_check_ids else False,
                                                       reservation_id=self.reservation_id.id,
                                                       date=self.payment_date,company_id=self.company_id.id,
                                                                due_date=self.pay_check_ids[0].check_date if self.pay_check_ids else False
                                                                )
            if self.partner_type=='internal':
                if self.send_rec_money == 'send':
                    internal_credit_account = [{'account': self.account_id.id, 'percentage': 100,
                                      'analyitc_id': self.analyitc_id.id,
                                      }]
                    internal_debit_account = [{'account': self.destination_journal_id.default_debit_account_id.id, 'percentage': 100,

                                       'analyitc_id': False
                                       }]
                else:
                    internal_debit_account = [{'account': self.account_id.id, 'percentage': 100,
                                       'analyitc_id': self.analyitc_id.id,
                                       }]
                    internal_credit_account = [{'account': self.destination_journal_id.default_debit_account_id.id, 'percentage': 100,
                                      'analyitc_id': False
                                      }]
                    move_id2 = self.env['create.moves'].create_move_lines2(move=move, move_line=move_line,
                                                                      debit_account=internal_debit_account,
                                                                      credit_account=internal_credit_account,
                                                                      src_currency=self.currency_id,
                                                                      check_payment_id=self.id,
                                                                      amount=pay_amt,
                                                                      cheque=self.pay_check_ids[
                                                                          0].check_number if self.pay_check_ids else "",
                                                                      check_id=self.pay_check_ids[
                                                                          0].id if self.pay_check_ids else False,
                                                                      reservation_id=self.reservation_id.id,
                                                                      date=self.payment_date,
                                                                      company_id=self.company_id.id,
                                                                      due_date=self.pay_check_ids[
                                                                          0].check_date if self.pay_check_ids else False
                                                                      )

            print('D>D>D>D>D',move_id.company_id.name)
            self.state = 'posted'
            if self.payment_subtype:
                for check in self.pay_check_ids:
                    check_line_val = {}
                    check_line_val['check_number'] = check.check_number
                    check_line_val['check_date'] = check.check_date
                    check_line_val['check_bank'] = check.bank.id
                    check_line_val['dep_bank'] = check.dep_bank.id
                    if self.send_rec_money == 'rece':
                        check_line_val['state'] = 'holding'
                        check_line_val['check_type'] = 'rece'
                    else:
                        check_line_val['state'] = 'handed'
                        check_line_val['handed_move_id'] = move_id.id
                        check_line_val['check_type'] = 'pay'
                    check_line_val['amount'] = check.amount
                    check_line_val['open_amount'] = check.amount
                    check_line_val['type'] = 'regular'
                    check_line_val['notespayable_id'] = self.payment_method.default_debit_account_id.id
                    check_line_val['notes_rece_id'] = self.payment_method.default_debit_account_id.id
                    check_line_val['investor_id'] = self.partner_id.id
                    check_line_val['reservation_id'] = self.reservation_id.id
                    check_line_val['custoemr_payment_id'] = self.custoemr_payment_id.id
                    check_line_val['check_payment_id'] = self.id
                    check_line_val['from_check_number'] = self.from_check_number
                    check_line_val['from_check_date'] = self.from_check_date
                    check_line_val['company_id'] = self.company_id.id
                    check_line_val['currency_id'] = self.currency_id.id
                    chk=self.env['check.management'].create(check_line_val)
                    self.check_id=chk.id
                    move_id.write({'check_id':chk.id})
        return True
    def action_confirm2(self):
        pay=self.env['payment.imported'].sudo().search([('payment_id','=',self.old_payment_id.id)],limit=1)
        if pay.state!='draft':
            if pay.state=='payment_refund_notes_receivable':
                self.state = 'payment_refund_notes_receivable'
            else:
                self.state = 'posted'
            if self.payment_subtype:
                for check in self.pay_check_ids:
                    check_line_val = {}
                    check_line_val['check_number'] = check.check_number
                    check_line_val['check_date'] = check.check_date
                    check_line_val['check_bank'] = check.bank.id
                    check_line_val['dep_bank'] = check.dep_bank.id
                    if self.send_rec_money == 'rece':
                        check_line_val['state'] = 'holding'
                        check_line_val['check_type'] = 'rece'
                    else:
                        check_line_val['state'] = 'handed'
                        if self.old_payment_id:
                            check_line_val['handed_move_id'] =self.old_payment_id.move_id.id
                        check_line_val['check_type'] = 'pay'
                    check_line_val['amount'] = check.amount
                    check_line_val['open_amount'] = check.amount
                    check_line_val['type'] = 'regular'
                    check_line_val['notespayable_id'] = self.payment_method.default_debit_account_id.id
                    check_line_val['notes_rece_id'] = self.payment_method.default_debit_account_id.id
                    check_line_val['investor_id'] = self.partner_id.id
                    check_line_val['reservation_id'] = self.reservation_id.id
                    check_line_val['custoemr_payment_id'] = self.custoemr_payment_id.id
                    check_line_val['check_payment_id'] = self.id
                    check_line_val['from_check_number'] = self.from_check_number
                    check_line_val['from_check_date'] = self.from_check_date
                    check_line_val['company_id'] = self.company_id.id
                    if pay.state:
                        check_line_val['state'] =pay.state
                    chk = self.env['check.management'].create(check_line_val)
                    self.check_id = chk.id
                    # if self.old_payment_id:
                    #     self.old_payment_id.move_id.sudo().write({'check_payment_id':self.id})
                    # paym = self.env['payment.move'].sudo().search(
                    #     [('payment_id', '=', self.old_payment_id.id)])
                    # for pay in paym:
                    #     moves = self.env['account.move'].sudo().search([('id', '=', pay.move_id)])
                    #     for move in moves:
                    #         move.sudo().write({'check_id': chk.id})
                    # move_id.write({'check_id': chk.id})
        return True

    def action_cancel(self):
        check_id=self.env['check.management'].search([('check_payment_id','=',self.id),('state','in', ['draft','holding','handed','payment_cancel','payment_draft'])],limit=1)
        if check_id:
            move = self.env['account.move'].sudo().search([('check_payment_id', '=', self.id)], limit=1)
            move.button_draft()
            move.button_cancel()
            move.unlink()
            check_id.unlink()
            self.state='cancel'
        else:
            move = self.env['account.move'].sudo().search([('check_payment_id', '=', self.id)], limit=1)
            move.button_draft()
            move.button_cancel()
            move.unlink()
            self.state = 'cancel'


    def action_reset_draft(self):
        check_id=self.env['check.management'].search([('check_payment_id','=',self.id),('state','in', ['draft','holding','handed','payment_cancel','payment_draft'])],limit=1)
        if check_id:
            check_id.write({'state': 'payment_draft'})
            move = self.env['account.move'].sudo().search([('check_payment_id', '=', self.id)],limit=1)
            move.button_draft()
            move.unlink()
            check_id.unlink()
        else:
            move = self.env['account.move'].sudo().search([('check_payment_id', '=', self.id)], limit=1)
            move.button_draft()
            move.unlink()

        self.state = 'draft'

    def amount_to_text(self):
        from num2words import num2words
        payment_amount = self.get_convert_amount2()
        t1 = round(int(payment_amount), 2)
        t2 = round((payment_amount - int(payment_amount)), 2)
        st1 = num2words(t1, lang='ar').title() + " جنيها مصربا و "
        st2 = num2words(t2 * 100, lang='ar').title() + " قرشا "
        return st1 + st2

    def get_convert_amount2(self):
        if self.currency_id != self.company_id.currency_id:
            amount = self.amount or self.amount1
            famount = self.currency_id._convert(amount, self.company_id.currency_id,
                                                self.company_id, self.payment_date)
            return famount
        else:
            return self.amount or self.amount1

    def change_duo_date(self):
        if self.sudo().old_payment_id:
            self.sudo().check_id.write({'check_date': self.sudo().old_payment_id.due_date})
            self.sudo().pay_check_ids.write({'check_date': self.sudo().old_payment_id.due_date})
            self.sudo().write({'payment_date': self.sudo().old_payment_id.date})

    def ar_amount_to_text(self, amount):
        convert_amount_in_words = num2words.num2words(amount, lang='ar_EG')
        return convert_amount_in_words


class payments_check_create(models.Model):
    _name = 'native.payments.check.create'
    _order = 'check_number asc'

    check_number = fields.Char(string=_("Check number"), required=True)
    check_date = fields.Date(string=_('Check Date'), required=True)
    amount = fields.Float(string=_('Amount'), required=True)
    dep_bank = fields.Many2one('payment.bank', string=_("Depoist Bank"))
    nom_pay_id = fields.Many2one('normal.payments', ondelete="cascade",)
    bank = fields.Many2one('payment.bank', _("Bank Name"))
    cheque_books_id = fields.Many2one(comodel_name='cheque.books')

    @api.constrains('nom_pay_id','cheque_books_id')
    def check_nom_pay_id(self):
        for rec in self:
            if rec.nom_pay_id.payment_subtype=='issue_check':
                if not rec.cheque_books_id:
                    raise ValidationError("Check Book Required")



class PaymentMultiAccounts(models.Model):
    _name='payment.multi.accounts'
    partner_required_in_journal_entry = fields.Boolean(
        string='Partner Required In Journal Entry?',
        related='account_id.partner_required_in_journal_entry',store=True)
    account_id = fields.Many2one(comodel_name="account.account", string="Account", required=True)
    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner", required=False)
    label = fields.Char(string="Label", required=False)
    normal_payment_id = fields.Many2one(comodel_name="normal.payments")
    payment_id = fields.Many2one(comodel_name="account.payment")
    amount = fields.Float(string="Amount", required=False)
    analyitc_id = fields.Many2one('account.analytic.account', string="Analytic Account")
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account")
    analytic_precision = fields.Integer(
        store=False,
        default=lambda self: self.env['decimal.precision'].precision_get("Percentage Analytic"),
    )









class ImportPayments(models.Model):
    _name='payment.imported'
    payment_id = fields.Integer(string='Payment_id')
    state = fields.Char(string='State')
    to_state = fields.Selection(selection=[('draft', 'Draft'),('holding', 'Posted'), ('depoisted', 'Under collection'),
                                        ('approved', 'Withdrawal'),
                                        ('rejected', 'Rejected'),
                                        ('delivery_to_customer', 'Delivery To Customer'),
                                        ('send_to_lagel', 'Send To Legal'),
                                        ('deliver', 'Deliver'),
                                        ('refund_deliver', 'Refund Deliver'),
                                        ('refund', 'Refund'),
                                        ('refund_send_to_lagel', 'Refund Send To Legal')
        , ('returned', 'Refund Under collection'), ('handed', 'Handed'),
                                        ('debited', 'Withdrawal Payable'), ('canceled', 'Canceled'),
                                        ('cs_return', 'Refund Notes Receivable')]
                             , )



class Importmoves(models.Model):
    _name='payment.move'
    payment_id = fields.Integer(string='Payment_id')
    move_id = fields.Integer(string='Move_id')
    matched = fields.Boolean()




class AccountPayment(models.Model):
    _inherit='account.payment'

    created_chck_pay = fields.Boolean(
        string=' created_chck_pay',
        required=False)

    def create_all_chk_payments(self):
        records = self.sudo().search([('created_chck_pay', '=', False)])
        for rec in records:
            rec.create_ch_payms()

    def create_ch_payms(self):
        if self.created_chck_pay == False:
            multi_account_ids = []
            val = {
                'company_id': self.company_id.id,
                'old_payment_id': self.id,
                'receipt_number': self.ref,
                'partner_id': self.partner_id.id,
                'reservation_id': self.reservation_id.id,
                'state_payment': self.state_payment2,
                'payment_method_id': self.payment_method_id.id,
                'description': self.ref,
                'payment_date': self.date,
                'send_rec_money': "send" if self.payment_type == "outbound" else "rece",
                'payment_method': self.journal_id.id,
                'amount': self.amount,
                'amount1': self.amount,
                'partner_type': self.partner_type,
                'account_id': self.destination_account_id.id,
                'select_account_id': self.select_account_id.id,
                'custom_account_id': self.custom_account_id.id,
                'request_reservation_id': self.request_id.id,
                'multi_accounts': self.multi_accounts,
                'name': self.name,
                'payment_No': self.name,
                'account_emp_type': self.account_emp_type,
            }
            if self.payment_method_code == "batch_payment" and self.check_number:
                val['pay_check_ids'] = [(0, 0, {
                    'check_number': self.check_number,
                    'check_date': self.date,
                    'amount': self.amount,
                    'bank': self.payment_bank_id.id,
                    'cheque_books_id': self.cheque_books_id.id,
                })]
            if self.payment_method_code == "check_printing" and self.cheque_number:
                val['pay_check_ids'] = [(0, 0, {
                    'check_number': self.cheque_number,
                    'check_date': self.date,
                    'amount': self.amount,
                    'bank': self.payment_bank_id.id,
                    'cheque_books_id': self.cheque_books_id.id,
                })]



            if self.multi_accounts:
                if self.multi_account_ids:
                    for line in self.multi_account_ids:
                        multi_account_ids.append((0, 0, {
                            'account_id': line.account_id.id,
                            'partner_id': line.partner_id.id,
                            'label': line.label,
                            'amount': line.amount,
                        }))
                    val.update({
                        'multi_account_ids': multi_account_ids
                    })
            pay = self.env['normal.payments'].create(val)
            pay.get_partner_acc2()
            # pay.action_confirm2()
            self.created_chck_pay = True

            print("D>D>>D", pay)

    def _synchronize_from_moves(self, changed_fields):
        ''' Update the account.payment regarding its related account.move.
        Also, check both models are still consistent.
        :param changed_fields: A set containing all modified fields on account.move.
        '''
        if self._context.get('skip_account_move_synchronization'):
            return

        for pay in self.with_context(skip_account_move_synchronization=True):

            # After the migration to 14.0, the journal entry could be shared between the account.payment and the
            # account.bank.statement.line. In that case, the synchronization will only be made with the statement line.
            if pay.move_id.statement_line_id:
                continue

            move = pay.move_id
            move_vals_to_write = {}
            payment_vals_to_write = {}

            if 'journal_id' in changed_fields:
                if pay.journal_id.type not in ('bank', 'cash'):
                    raise UserError(_("A payment must always belongs to a bank or cash journal."))

            if 'line_ids' in changed_fields:
                all_lines = move.line_ids
                liquidity_lines, counterpart_lines, writeoff_lines = pay._seek_for_lines()

                # if len(liquidity_lines) != 1:
                #     raise UserError(_(
                #         "Journal Entry %s is not valid. In order to proceed, the journal items must "
                #         "include one and only one outstanding payments/receipts account.",
                #         move.display_name,
                #     ))
                #
                # if len(counterpart_lines) != 1:
                #     raise UserError(_(
                #         "Journal Entry %s is not valid. In order to proceed, the journal items must "
                #         "include one and only one receivable/payable account (with an exception of "
                #         "internal transfers).",
                #         move.display_name,
                #     ))
                #
                # if any(line.currency_id != all_lines[0].currency_id for line in all_lines):
                #     raise UserError(_(
                #         "Journal Entry %s is not valid. In order to proceed, the journal items must "
                #         "share the same currency.",
                #         move.display_name,
                #     ))
                #
                # if any(line.partner_id != all_lines[0].partner_id for line in all_lines):
                #     raise UserError(_(
                #         "Journal Entry %s is not valid. In order to proceed, the journal items must "
                #         "share the same partner.",
                #         move.display_name,
                #     ))

                if counterpart_lines.account_id.account_type == 'asset_receivable':
                    partner_type = 'customer'
                else:
                    partner_type = 'supplier'

                liquidity_amount = liquidity_lines.amount_currency

                move_vals_to_write.update({
                    'currency_id': self.currency_id.id,
                    'partner_id': liquidity_lines.partner_id.id,
                })
                payment_vals_to_write.update({
                    'amount': abs(liquidity_amount),
                    'partner_type': partner_type,
                    'currency_id': self.currency_id.id,
                    'destination_account_id': counterpart_lines.account_id.id,
                    'partner_id': liquidity_lines.partner_id.id,
                })
                if liquidity_amount > 0.0:
                    payment_vals_to_write.update({'payment_type': 'inbound'})
                elif liquidity_amount < 0.0:
                    payment_vals_to_write.update({'payment_type': 'outbound'})

            move.write(move._cleanup_write_orm_values(move, move_vals_to_write))
            pay.write(move._cleanup_write_orm_values(pay, payment_vals_to_write))
