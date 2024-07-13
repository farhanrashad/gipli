# -*- coding: utf-8 -*-

from odoo import api, fields, models
import datetime
from datetime import datetime, date,timedelta
from odoo.tools.translate import _
import calendar
from odoo.exceptions import ValidationError,UserError
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

import xlrd
import tempfile
import binascii
from operator import attrgetter
from odoo.tools import float_compare
import time

import logging

_logger = logging.getLogger(__name__)

class requestReservation(models.Model):
    _name = 'request.reservation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Request Property Reservation"
    _rec_name = 'reservation_code'

    created_date = fields.Datetime(string="Created on", default=fields.datetime.today())

    _defaults = {
        'created_date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }
    state = fields.Selection(string="State", selection=[('draft', 'Draft'),('reserved', 'Reserved'), ('blocked', 'Blocked'), ], required=False ,default='draft')
    name = fields.Char(string="Request Reservation Name" ,store=True)
    reservation_code = fields.Char(string="Request Reservation Code", readonly=True, copy=False , store=True)
    date = fields.Date(string="Date", required=True,default=fields.Date.today() )
    @api.onchange('date')
    def onchange_date(self):
        if self.date:
            create_group_name = self.env['res.groups'].search(
                [('name', '=', 'Unlock_Date')])
            result = self.env.user.id in create_group_name.users.ids
            if result == False:
                if datetime.strptime(str(self.date), DEFAULT_SERVER_DATE_FORMAT).date() < datetime.now().date():
                    self.update({
                        'date': False
                    })
                    raise ValidationError('Please select a date equal/or greater than the current date')

    is_eoi = fields.Boolean(string="EOI",default=True  )

    project_id = fields.Many2one('project.project', _("Project"))
    # terms_and_conditions = fields.Text(string="Terms and Conditions", required=False,related='project_id.terms_and_conditions' )
    phase_id = fields.Many2one('project.phase', _('Phase'))
    # property information
    property_id = fields.Many2one('product.product', _('Property'),domain=[('state','=','available')])
    property_code = fields.Char(string="Property Code", copy=False,related='property_id.property_code')
    finish_of_property_id = fields.Many2one('property.finished.type', _('Finishing Type'),related='property_id.finish_of_property_id')
    finish_of_property = fields.Selection(string="Finishing Type",
                                          selection=[('Finish', 'Finish'), ('Core&Shell', 'Core&Shell'), ],
                                          related='property_id.finish_of_property')

    unit_ids = fields.Char()
    @api.onchange('project_id')
    def on_change_project(self):
        for rec in self:
            # rec.unit_ids = False
            all_phases = []
            if rec.phase_id.project_id.id != rec.project_id.id:
                rec.phase_id = False
            phases = self.env['project.phase'].search(
                [('project_id', '=', rec.project_id.id)])
            for phase in phases:
                all_phases.append(phase.id)
            return {'domain': {'phase_id': [('id', 'in', all_phases)]}}

    # sales details
    sales_type = fields.Selection([('direct', _("Direct")), ('Broker', _("Broker")) ], _('Sales Type'),default='direct')
    broker_id = fields.Many2one(comodel_name="res.partner", string="Broker", required=False,domain=[('is_broker','=',True)] )
    # customer details
    customer_id = fields.Many2one('res.partner', string="Customer")
    more_owner_ids = fields.Many2many(
        comodel_name='res.partner',
        string='More Owners',
        required=False)
    address = fields.Char(string="Address", related='customer_id.street')
    phone = fields.Char(string="Mobile1", related='customer_id.phone')
    mobile = fields.Char(string="Mobile2", related='customer_id.mobile')
    email = fields.Char(string="Email", related='customer_id.email')
    nationality = fields.Char(string="Nationality", related='customer_id.nationality')
    id_def = fields.Char(string="ID", related='customer_id.id_def')
    social_status = fields.Selection(string="Social Status", selection=[('married', 'Married'), ('single', 'Single'), ],related='customer_id.social_status' ,required=False,default='single' )
    positon = fields.Char(string="Position", related='customer_id.positon', store=True)
    work_side = fields.Char(string="جهة العمل", related='customer_id.work_side', store=True)
    national_issue_date = fields.Date(string="National Issue Date", related='customer_id.national_issue_date',
                                      store=True)
    national_issue_date_month = fields.Integer(related='customer_id.national_issue_date_month',store=True)
    national_issue_date_year = fields.Integer(related='customer_id.national_issue_date_year',store=True)

    # internal information
    sale_person_id = fields.Many2one(comodel_name="res.users", string="SalesPerson",default=lambda self: self.env.user  )
    sale_person_id_2 = fields.Many2one(comodel_name="res.partner", string="SalesPerson",  required=False  )

    @api.onchange('customer_id')
    def onchange_customer(self):
        if self.customer_id:
            self.sale_person_id_2=self.customer_id.user_id.partner_id.id


    Sales_Teams_2_id = fields.Many2one(related='sale_person_id_2.company_team_id', comodel_name="company.team",
                                       string="Company Teams", )
    manager_tesm_2_id = fields.Many2one(related='Sales_Teams_2_id.user_id', comodel_name="res.partner",
                                        string="Team Leader", )
    company_id = fields.Many2one('res.company', string='Company', store=True, readonly=False,related='project_id.company_id')




    # attachment
    id_no = fields.Char(string="Identification No.")
    id_type = fields.Selection([('id', _("ID")), ('passport', _("Passport"))], string="Identification Type")
    id_photo = fields.Binary("Photo ID")

    #notes
    notes_cash = fields.Text(string="Notes (Cash)", required=False, )
    notes_visa = fields.Text(string="Notes (Visa)", required=False, )
    notes_cheque = fields.Text(string="Notes (Cheque)", required=False, )
    notes_bank = fields.Text(string="Notes (Bank)", required=False, )
    customer_details_readonly = fields.Boolean(compute='_calc_customer_details_readonly')

    def _calc_customer_details_readonly(self):
        for rec in self:
            rec.customer_details_readonly = not self.env.user.has_group('add_real_estate.group_real_state_inventory')

    # create method
    @api.model
    def create(self, values):
        values['reservation_code'] = self.env['ir.sequence'].next_by_code('real.estate.reservation.id.seq')
        res=super(requestReservation, self).create(values)

        res.property_id.write({'state':'requested'})
        return res


    def convert_to_reserved(self):
        for rec in self:
            if rec.state in ['draft']:
                rec.state = 'reserved'
                rec.property_id.state = 'reserved'

    def convert_to_block(self):
        for rec in self:
            if rec.state in ['reserved','draft']:
                rec.state = 'blocked'
                res_res = self.env['res.reservation'].search([('property_id', '=', rec.property_id.id),
                                                     ('state', 'in', ['reserved'])])
                if len(res_res) != 0:
                    rec.property_id.state = 'available'


    # def create_payment_lines_selected(self):
    #     counter = 0
    #     # req_id = []
    #     for line in self.payment_strg_ids:
    #         if line.is_selected_to_action == True:
    #             counter +=1
    #     # if counter > 1:
    #     #     raise ValidationError(_("Sorry .. you must Select Once line  !!"))
    #     # if counter == 0:
    #     #     raise ValidationError(_("Sorry .. you must Select Once line  !!"))
    #     method = self.env['account.payment.method'].sudo().search([
    #         ('name', '=', 'Manual')
    #     ], limit=1)
    #     method_batch = self.env['account.payment.method'].sudo().search([
    #         ('name', '=', 'Batch Deposit')
    #     ], limit=1)
    #     for line in self.payment_strg_ids:
    #
    #         if line.is_selected_to_action == True and line.is_create_payment == True:
    #             raise ValidationError(_("Sorry .. you Create Payment Before  !!"))
    #         if line.is_selected_to_action == True and line.is_create_payment == False:
    #             if line.is_cheque  == True:
    #                 req_id = self.env['account.payment'].create({
    #                     'state': 'draft',
    #                     'date': datetime.now(),
    #                     'payment_type': 'inbound',
    #                     'partner_type': 'customer',
    #                     'partner_id': self.customer_id.id,
    #                     'amount': line.amount,
    #                     'journal_id': line.journal_id.id or self.env.company.payment_journal_id.id,
    #                     'payment_method_id':method_batch.id,
    #                     'bank_name':line.bank_name.name,
    #                     'check_number':line.cheque,
    #                     'due_date':line.Due_Date,
    #                     'actual_date':line.Due_Date,
    #                     'request_id': self.id,
    #                     'is_contract': True,
    #
    #                 })
    #             else:
    #                 req_id = self.env['account.payment'].create({
    #                     'state': 'draft',
    #                     'date': datetime.now(),
    #                     'payment_type': 'inbound',
    #                     'partner_type': 'customer',
    #                     'partner_id': self.customer_id.id,
    #                     'amount': line.amount,
    #                     'journal_id': line.journal_id.id or self.env.company.payment_journal_id.id,
    #                     'payment_method_id': method.id,
    #                     'request_id': self.id,
    #                     'is_contract': True,
    #
    #                 })
    #             print("req_id :: ",req_id)
    #             line.is_create_payment = True
    #             line.payments_ids=[(6, 0, [req_id.id])]

    def create_payment_lines_selected(self):
        for line in self.payment_strg_ids:
            if line.is_selected_to_action and line.display_type==False and line.is_create_payment==False:
                val = {
                    'receipt_number': line.name,
                    'partner_id': self.customer_id.id,
                    'state_payment': line.state_payment,
                    'payment_method_id': line.payment_method_id.id,
                    'description': line.description,
                    'payment_date': line.date,
                    'send_rec_money': "rece",
                    'payment_method': line.journal_id.id or self.env.company.payment_journal_id.id,
                    'account_id': line.journal_id.default_debit_account_id.id,
                    'amount': line.amount,
                    'amount1': line.amount,
                    'partner_type': "customer",
                    'request_reservation_id': self.id,
                    'property_id': self.property_id.id,

                }
                if line.state_payment == "cheque":
                    val['pay_check_ids'] = [(0, 0, {
                        'check_number': line.cheque,
                        'check_date': line.date,
                        'amount': line.amount,
                        'bank': line.bank_name.id,
                    })]
                line.is_create_payment = True
                line.is_pay = True
                pay = self.env['normal.payments'].create(val)
                pay.write({
                    'amount': line.amount,
                    'amount1': line.amount,
                })
                print('D>D>D',pay.id)
                pay.get_partner_acc2()
                line.check_payment_id=pay.id
                # pay.action_confirm()




    payment_due = fields.Float(string="Payment Due",  required=False,compute="_compute_payments" )
    def _compute_payments(self):
        amount = 0
        for rec  in self:
            payments = self.env['account.payment'].search([('request_id', '=', rec.id)])
            if payments:
                for line in payments:
                    amount+= line.amount

                rec.payment_due = amount
            else:
                rec.payment_due = 0
    def create_reservation(self):
        res_res = self.env['res.reservation'].search([('req_reservation_id', '=', self.id),('property_id', '=', self.property_id.id),
                                                      ('state', 'in', ['reserved'])])
        if len(res_res) != 0:
            raise ValidationError(_("Sorry .. you must Create One Reservation Form For Request Reservation for This Property  %s!!")% self.property_id.name)
        lines=[]
        if self.payment_strg_ids:
            for line in self.payment_strg_ids:
                lines.append(
                    (0, 0, {
                        'payment_code': line.payment_code,
                        'state_payment':line.state_payment,
                        'description': line.description,
                        'amount': line.amount,
                        'base_amount': line.base_amount,
                        'amount_due': line.amount_due,
                        'amount_pay': line.amount_pay,
                        'date': line.date,
                        'journal_id': line.journal_id.id,
                        'bank_name': line.bank_name.id,
                        'cheque': line.cheque,
                        'deposite': line.deposite,
                        'is_pay': line.is_pay,
                        'display_type': line.display_type,
                        'name': line.name,
                        'currency_id': line.currency_id.id,
                        'check_payment_id': line.check_payment_id.id,
                        'merge_in_one_installment': True,
                        'amount_currency': line.amount_currency,
                        'payments_ids':  [(6, 0, [x.id for x in line.payments_ids])],

                    }))

        req_id = self.env['res.reservation'].create({
            'date': datetime.now(),
            'project_id': self.project_id.id,
            'phase_id': self.phase_id.id,
            'property_id': self.property_id.id,
            'customer_id': self.customer_id.id,
            'more_owner_ids': [(6, 0, [x.id for x in self.more_owner_ids])],
            'sale_person_2_id': self.sale_person_id_2.id,
            'req_reservation_id': self.id,
            'id_no': self.id_no,
            'id_type': self.id_type,
            'id_photo': self.id_photo,
            'state': 'draft',
            'custom_type':'Reservation',
            'sales_type':self.sales_type,
            'broker_id':self.broker_id.id,
            'payment_strg_ids':lines

        })
        for strg in req_id.payment_strg_ids:
            for pay in strg.payments_ids:
                pay.write({
                    'reservation_id':req_id.id
                })

        return {'name': (
                            'Reservation'),
                        'type': 'ir.actions.act_window',
                        'res_model': 'res.reservation',
                        'res_id': req_id.id,
                        'view_type': 'form',
                        'view_mode': 'form',
                    }


    def action_view_partner_reservation(self):
        self.ensure_one()
        action = self.env.ref('add_real_estate.reservation_list_action').read()[0]
        action['domain'] = [
            ('state', 'in', ['draft','reserved']),
            ('req_reservation_id', '=', self.id),
        ]
        print("action %s",action)
        return action



    # part payment and lins

    pay_strategy_id = fields.Many2one('account.payment.term', string="Payment Strategy")
    payment_strg_name = fields.Char(string="Payment Strategy", related='pay_strategy_id.name', store=True)
    payment_term_discount = fields.Float(string="Payment Term Discount",
                                         related="pay_strategy_id.payment_term_discount", store=True, digits=(16, 6))

    payment_strg_ids = fields.One2many('payment.strg.request', 'reserve_id', _('Payment'))

    discount = fields.Float(string="Discount Percentage", digits=(16, 15))
    total_discount = fields.Float('Total Discount', compute='_compute_total_discount', store=True)

    property_price = fields.Float(string="Property Price", readonly=True,related='property_id.final_unit_price',
                                  digits=(16, 6))


    def get_added_paid_amount(self):
        sum=0
        for line in self.payment_strg_ids:
            if line.add_to_paid_amount:
                sum+=line.amount
        return sum

    @api.depends('discount', 'payment_term_discount')
    def _compute_total_discount(self):
        _logger.info("_compute_total_discount :: ")
        for record in self:
            record.total_discount = record.discount + record.payment_term_discount

    @api.onchange('pay_strategy_id', 'discount')
    def _onchange_pay_strategy(self):
        _logger.info("_onchange_pay_strategy :: ")
        inbound_payments = self.env['account.payment.method'].search([('payment_type', '=', 'inbound')])
        for rec in self:
            payments = []
            for payment in rec.payment_strg_ids:
                payment.write({
                    'reserve_id': False
                })
            if rec.pay_strategy_id and rec.pay_strategy_id.id:
                for payment_line in rec.pay_strategy_id.line_ids:
                    # Add Section
                    payments.append((0, 0, {
                        'name': payment_line.payment_description,
                        'display_type': 'line_section',
                    }))
                    payment_methods = inbound_payments and payment_line.journal_id.inbound_payment_method_ids or \
                                      payment_line.journal_id.outbound_payment_method_ids

                    date_order_format = datetime.today()
                    date = date_order_format
                    if payment_line.days > 0:
                        _logger.info("enter here :: ")
                        no_months = payment_line.days / 30
                        _logger.info("enter here no_months :: %s",no_months)

                        date_order_day = date_order_format.day
                        date_order_month = date_order_format.month
                        date_order_year = date_order_format.year
                        date = date(date_order_year, date_order_month, date_order_day) + relativedelta(
                            days=payment_line.days)
                    cheque_status = 'draft'

                    if payment_line.deposit:
                        cheque_status = 'received'

                    first_discount = rec.property_price - (
                            rec.property_price * (rec.payment_term_discount / 100.0))
                    net_price = first_discount - (
                            first_discount * (rec.discount / 100.0))
                    net_price = rec.property_price - (
                            rec.property_price * ((rec.discount + rec.payment_term_discount)/ 100))

                    # Todo If line is Maintenance Fee
                    if payment_line.add_extension:
                        payment_amount = payment_line.value_amount * rec.property_price

                    else:
                        payment_amount = payment_line.value_amount * net_price
                    payment_arr = {
                                    'amount': payment_amount,
                                    'base_amount': payment_amount,
                                    'date': date,
                                   'journal_id': payment_line.journal_id.id,
                                   'description': payment_line.payment_description,
                                   'deposite': payment_line.deposit,
                                   'add_extension': payment_line.add_extension,
                                   'property_ids': [(6,0,[rec.property_id.id])]

                                   }

                    payments.append((0, 0, payment_arr))
            rec.payment_strg_ids = payments

    def button_delete_lines_selected(self):
        for rec in self:
            if rec.payment_strg_ids:
                for payment in rec.payment_strg_ids:
                    if payment.is_selected_to_action == True:
                        if payment.is_pay == False:
                            payment.unlink()
                        else:
                            raise UserError(_("You Cant Delete Payment Paid."))

                for payment in rec.payment_strg_ids:
                    payment.is_selected_to_action = False

    def button_pay_lines_selected(self):
        account_payment = self.env['account.payment']
        data_bank = self.env['data.bank.cheque']


        for rec in self:
            if rec.payment_strg_ids:

                for payment in rec.payment_strg_ids:
                    if payment.is_selected_to_action == True:
                        if payment.type == 'bank':
                            method = self.env['account.payment.method'].sudo().search([
                                ('name', '=', 'Batch Deposit')
                            ], limit=1)
                            if payment.bank_name.id == False:
                                raise UserError(_("You Must Add Bank Name."))
                            if payment.cheque == False:
                                raise UserError(_("You Must Add Cheque Number."))

                        else:
                            method = self.env['account.payment.method'].sudo().search([
                                ('name', '=', 'Manual')
                            ], limit=1)
                        if payment.amount > payment.amount_due:
                            raise UserError(_("You Cant Payment begger than amount due."))
                        data_bank_id = data_bank.create({
                            'bank_id': payment.bank_name.id,
                            'cheque_number': payment.cheque,
                            'payment_strg_request_id': self.id,

                        })
                        l = []
                        l.append(data_bank_id.id)
                        for line in payment.bank_ids:
                            l.append(line.id)
                        pay = account_payment.create({
                            'payment_type': 'inbound',
                            'partner_type': 'customer',
                            'partner_id': rec.customer_id.id,
                            'journal_id': payment.journal_id.id,
                            'amount': payment.amount,
                            'date': payment.date,
                            'communication': str(rec.reservation_code),
                            'payment_method_id': method.id,
                            'bank_name': payment.bank_name.name,
                            'check_number': payment.cheque,
                            'due_date': payment.date,
                            'actual_date': payment.date,
                            'is_contract': True,
                        })
                        payment.update({
                            'bank_ids': [(6, 0, l)],
                        })
                        pay.post()
                        if payment.amount == payment.amount_due:
                            if payment.amount == payment.base_amount:
                                payment.is_pay = True
                                payment.amount_pay = payment.amount_pay + payment.amount
                                payment.amount = payment.base_amount
                            else:
                                payment.is_part = True
                                payment.amount_pay = payment.amount_pay + payment.amount
                                payment.amount = payment.base_amount
                        else:
                            if payment.amount == payment.amount_due:
                                payment.is_pay = True
                                payment.amount_pay = payment.amount_pay + payment.amount
                                payment.amount = payment.base_amount

                            else:
                                payment.is_part = True
                                payment.amount_pay = payment.amount_pay + payment.amount
                                payment.amount = payment.base_amount

                for payment in rec.payment_strg_ids:
                    payment.is_selected_to_action = False



    def generate_report(self):
        if (not self.env.company.logo):
            raise UserError(_("You have to set a logo or a layout for your company."))
        elif (not self.env.company.external_report_layout_id):
            raise UserError(_("You have to set your reports's header and footer layout."))
        data = {}
        for rec in self:
            if rec.payment_strg_ids:
                request_reservation = []
                for payment in rec.payment_strg_ids:
                    if payment.is_selected_to_action == True:
                        amount_to_text = rec.company_id.currency_id.ar_amount_to_text(payment.amount)
                        request_reservation.append({
                            'model': 'payment.strg.request',
                            'date': payment.date,
                            'Due_Date': payment.Due_Date,
                            'description': payment.description,
                            'amount': payment.amount,
                            'journal_id': payment.journal_id.name,
                            'is_receive': payment.is_receive,
                            'bank_name': payment.bank_name.name,
                            'cheque': payment.cheque,
                            'deposite': payment.deposite,
                            'add_extension': payment.add_extension,
                            'maintainance_fees': payment.maintainance_fees,
                            'customer': rec.customer_id.name,
                            'property': rec.property_id.name,
                            'project': rec.project_id.name,
                            'state_payment': payment.state_payment,
                            'payment_code': payment.payment_code,
                            'amount_to_text': amount_to_text,
                            'company_name_arabic': rec.company_id.name_arabic,
                            'user_name_arabic': rec.create_uid.name_Branch,
                            'notes_cash': rec.notes_cash,
                            'notes_visa': rec.notes_visa,
                            'notes_cheque': rec.notes_cheque,
                            'notes_bank': rec.notes_bank,
                        })
        data['request_reservation'] = request_reservation
        return self.env.ref('add_real_estate.payment_request_report_id').report_action([], data=data)




    amount_total = fields.Float(string="Amount",  required=False,compute="_compute_amount" )
    amount_residual = fields.Float(string="Amount Due",  required=False,compute="_compute_amount" )

    def _compute_amount(self):
        amount = 0
        due = 0
        for rec in self:
            if rec.payment_strg_ids:
                for line in rec.payment_strg_ids:
                    amount += line.amount
                    due += line.amount_due
                rec.amount_total = amount
                rec.amount_residual = due
            else:
                rec.amount_total = 0
                rec.amount_residual = 0


    # edit by Yasser
    def get_childs_of_contact(self):
        action = self.env.ref('contacts.action_contacts').read()[0]
        action['domain']=[('parent_id','=',self.customer_id.id)]
        return action

    def button_receive_lines_selected(self):
        for rec in self:
            if rec.payment_strg_ids:
                for payment in rec.payment_strg_ids:
                    if payment.is_selected_to_action == True:
                        payment.is_receive = True

                for payment in rec.payment_strg_ids:
                    payment.is_selected_to_action = False
