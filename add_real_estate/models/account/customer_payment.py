# -*- coding: utf-8 -*-
from odoo import api, fields, models
import datetime
from datetime import datetime, date,timedelta
from odoo.tools.translate import _
import calendar
from odoo.exceptions import ValidationError,UserError
import xlrd
import tempfile
import binascii
from operator import attrgetter
import logging
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

TYPE_SELECTION = [('sale', _('Sale')),
                  ('sale_refund', _('Sale Refund')),
                  ('purchase', _('Purchase')),
                  ('purchase_refund', _('Purchase Refund')),
                  ('cash', _('Cash')),
                  ('bank', _('Bank and Checks')),
                  ('general', _('General')),
                  ('situation', _('Opening/Closing Situation'))]
LOGGER = logging.getLogger(__name__)

class Customer_payment(models.Model):
    _name = 'customer.payment'
    _description = "Property Reservation"
    _inherit = ['mail.thread', 'mail.activity.mixin']


    date = fields.Date(string="Date", required=True,default=fields.Date.today() )
    # @api.onchange('date')
    # def onchange_date(self):
    #     if self.date:
    #         create_group_name = self.env['res.groups'].search(
    #             [('name', '=', 'Unlock_Date')])
    #         result = self.env.user.id in create_group_name.users.ids
    #         if result == False:
    #             if datetime.strptime(str(self.date), DEFAULT_SERVER_DATE_FORMAT).date() < datetime.now().date():
    #                 self.update({
    #                     'date': False
    #                 })
    #                 raise ValidationError('Please select a date equal/or greater than the current date')

    state = fields.Selection(string="State", selection=[('draft', 'Draft'),('approved', 'Approved') ], required=False ,default='draft')
    name = fields.Char(string="Number", required=False, )
    journal_id = fields.Many2one(comodel_name="account.journal", string="Journal", required=True,domain=[('type', 'in', ['bank','cash'])],  )
    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner", required=True, )
    reservation_id = fields.Many2one(comodel_name="res.reservation", string="Reservation", required=True, )
    is_select_all = fields.Boolean(string="Select All",  )
    loan_line= fields.One2many('loan.line.rs.wizard', 'loan_id')
    total_amount = fields.Float(string="Total Amount",compute="_compute_total_amount",  required=False, )
    total_count = fields.Float(string="Count",compute="_compute_total_amount",  required=False, )
    bank_name = fields.Many2one('payment.bank', _("Bank Name"))
    start_cheque = fields.Integer(string="Start", required=False, )
    end_cheque = fields.Integer(string="End", required=False, )
    ref = fields.Char(
        string='Reference',
        required=False)
    type = fields.Selection(selection=TYPE_SELECTION, related='journal_id.type', store=True, string='Payment Type')
    state_payment = fields.Selection([('cash', 'Cash'),
                                      ('visa', 'Visa'),
                                      ('cheque', 'Cheque'),
                              ('bank', 'Bank'),
                              ],default="cheque")
    cancel_res = fields.Boolean()
    number_ins = fields.Integer(string="", required=False, compute="_compute_number_ins")

    counter_payments = fields.Integer(string="Counter Payments", required=False, compute="_compute_counter_payments")
    accounting_allocation = fields.Selection(
        string='Accounting Allocation',
        selection=[('maintenance', 'Maintenance'),
                   ('deposit', 'Deposit'),
                   ('insurance', 'Insurance'),
                   ('eoi', 'EOI'),
                   ],
        required=False, )

    def _compute_counter_payments(self):
        for rec in self:
            payments = self.env['normal.payments'].sudo().search(
                [('custoemr_payment_id', '=', rec.id)])
            rec.counter_payments = len(payments)


    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            if self.cancel_res:
                return {'domain': {'reservation_id':[ ('customer_id', '=', self.partner_id.id)]}}
            else:
                return {'domain': {
                    'reservation_id':[ ('customer_id', '=', self.partner_id.id)]}}

    def update_bank_data(self):
        counter = self.start_cheque
        print("counter :: %s",counter)
        for line in self.loan_line:
            line.bank_name = self.bank_name.id
            if self.end_cheque >= counter:
                line.cheque = counter
                counter +=1
    def _compute_total_amount(self):
        for rec in self:
            sum=0
            c=0
            if rec.is_select_all == True:
                for line in rec.loan_line:
                    sum += line.amount
                    c += 1
            else:
                for line in rec.loan_line:
                    if line.is_pay == True:
                        sum += line.amount
                        c += 1
                    else:
                        c += 0
                        sum += 0
            rec.total_amount=sum
            rec.total_count=c
    @api.onchange('reservation_id','filter_by')
    def onchange_reservation_id(self):
        if self.reservation_id:
            loan_lines=[]
            for line in self.reservation_id.payment_strg_ids.filtered(lambda ll:ll.display_type not in ['line_section','line_note']):
                if line.check_payment_id:
                    continue
                strg = self.env['payment.strg'].sudo().search([
                    ('id', '=', line.id)
                ], limit=1)

                print(">D>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.",line.name,line.is_pay)
                if self.cancel_res:
                    if self.check_if_check_is_paid(line.id, self.reservation_id.id, self.partner_id.id) == False:
                        loan_lines.append((0, 0,
                                           {
                                               'date': line.date,
                                               'amount': line.amount,
                                               'description': line.description,
                                               'installment_line_id': line.id,
                                               'payment_strg_id': strg,
                                               'name': line.name,
                                               'cus_bank': line.cus_bank,
                                               'bank_name': line.bank_name.id,
                                               'cheque': line.cheque,
                                               'amount_due': line.amount_due,
                                               'is_main': line.is_maintainance,
                                               'state_payment': line.state_payment,
                                               'currency_id': line.currency_id.id,
                                               'amount_currency': line.amount_currency,
                                           }))
                else:
                    if not line.is_pay :
                        if line.state_payment == self.state_payment:
                            if self.check_if_check_is_paid(line.id,self.reservation_id.id,self.partner_id.id)==False:
                                loan_lines.append((0,0,
                                                   {
                                                       'date':line.date,
                                                       'amount':line.amount,
                                                       'description':line.description,
                                                       'installment_line_id': line.id,
                                                       'payment_strg_id': strg,
                                                       'name':line.name,
                                                       'cus_bank':line.cus_bank,
                                                       'bank_name':line.bank_name.id,
                                                       'cheque': line.cheque,
                                                       'amount_due':line.amount_due,
                                                       'is_main': line.is_maintainance,
                                                       'state_payment': line.state_payment,
                                                       'currency_id': line.currency_id.id,
                                                       'amount_currency': line.amount_currency,
                                                   }))
            # self.partner_id=self.reservation_id.customer_id.id
            self.loan_line = [(6,0,[])]
            self.loan_line=loan_lines

    # create method
    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('customer.payment.seq')
        return super(Customer_payment, self).create(values)

    @api.onchange('is_select_all')
    def onchange_method_is_select_all(self):
        if self.is_select_all == True:
            for line in  self.loan_line:
                line.is_pay = True
        else:
            for line in  self.loan_line:
                line.is_pay = False
    def approved(self):
        if not self.loan_line.filtered(lambda line:line.is_pay):
            raise ValidationError("Please Select One Line!")
        account=self.env['account.account'].search([('accounting_allocation', '=', self.accounting_allocation)], limit=1)
        for line in self.loan_line:
            if line.is_pay:

                val={
                    'receipt_number':self.ref,
                    'partner_id':self.partner_id.id,
                    'custoemr_payment_id':self.id,
                    'reservation_id':self.reservation_id.id,
                    'state_payment':self.state_payment,
                    'payment_method_id':line.payment_method_id.id,
                    'description':line.description,
                    'payment_date':self.date,
                    'send_rec_money':"rece",
                    'payment_method':self.journal_id.id,
                    'accounting_allocation': self.accounting_allocation,
                    'account_id': account.id if account else self.journal_id.default_debit_account_id.id,
                    'amount':line.amount,
                    'amount1':line.amount,
                }
                if self.state_payment=="cheque":
                    val['pay_check_ids']=[(0,0,{
                        'check_number':line.cheque,
                        'check_date':line.date,
                        'amount':line.amount,
                        'bank':line.bank_name.id,
                    })]
                pay=self.env['normal.payments'].create(val)
                print("D>D>D>>D",pay)
                pay.get_partner_acc2()
                pay.write({'account_id':account.id})
                pay.action_confirm()
        self.state="approved"

    def action_view_payments(self):
        self.ensure_one()
        action = self.env.ref('check_management.check_action_norm_pay_action').read()[0]
        action['domain'] = [
            ('custoemr_payment_id', '=', self.id)
        ]
        return action


    def _compute_number_ins(self):
        for rec in self:
            if rec.loan_line:
                rec.number_ins = len(rec.loan_line)
            else:
                rec.number_ins = 0


    def check_if_check_is_paid(self,installment_line_id,res_id,partner_id):
        res=self.env['loan.line.rs.wizard'].search([('installment_line_id','=',installment_line_id),('loan_id.reservation_id','=',res_id)
                                                       ,('loan_id.partner_id','=',partner_id),('is_pay','=',True)])
        print("Res/00054",res.loan_id)
        if res:
            return True
        else:
            return False



class loan_line_rs_wizard(models.Model):
    _name = 'loan.line.rs.wizard'

    loan_id= fields.Many2one('customer.payment', ondelete='cascade', readonly=True)
    res_id= fields.Many2one('res.reservation')
    installment_line_id= fields.Integer('id ')
    payment_strg_id = fields.Many2one(comodel_name="payment.strg", string="Payment Strg", required=False, )
    name = fields.Char(string='Name')
    partner_id = fields.Many2one('res.partner', string='Customer', )
    project_id = fields.Many2one('project.project', string='Project', )
    date = fields.Date(_('Date'))
    amount = fields.Float(_('Amount'), digits=(16, 6))
    amount_due = fields.Float(_('Amount Due'), digits=(16, 6) ,store=True)
    description = fields.Char(_('Description'))
    move_check = fields.Boolean(string='Paid')
    cus_bank = fields.Many2one('payment.bank.cus', _("Customer Bank Name"))
    bank_name = fields.Many2one('payment.bank', _("Bank Name"))
    cheque = fields.Char(_("Cheque Number"))
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Type', oldname="payment_method")
    is_pay = fields.Boolean(string="Is Pay",  )
    cheque = fields.Char(_("Cheque Number"))
    type = fields.Selection(selection=TYPE_SELECTION, related='loan_id.type', store=True, string='Payment Type')
    is_main = fields.Boolean(string="",  )
    state_payment = fields.Selection([('cash', 'Cash'),
                                      ('visa', 'Visa'),
                                      ('cheque', 'Cheque'),
                              ('bank', 'Bank'),
                              ],default="cheque")
    payment_id = fields.Many2one(comodel_name="account.payment", string="", required=False)
    currency_id = fields.Many2one(comodel_name="res.currency", string="Currency", required=False)
    amount_currency = fields.Float(string="Amount Currency", required=False)

    def button_journal_entries(self):
        return {
            'name': _('Journal Entries'),
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.payment_id.mapped('move_line_ids').mapped('move_id').ids)],
            'context': {
                'journal_id': self.payment_id.journal_id.id,
            }
        }

