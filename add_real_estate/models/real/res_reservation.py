# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import datetime
from datetime import datetime, date, timedelta
from odoo.tools.translate import _
import calendar
from odoo.exceptions import ValidationError, UserError
import xlrd
import tempfile
import binascii
from operator import attrgetter
from odoo.tools import float_compare
import time
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import logging
import math

import logging
from ..account.num2words import num2words




class requestReservation(models.Model):
    _name = 'res.reservation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Property Reservation"
    _rec_name = 'name'

    created_date = fields.Datetime(string="Created on", default=fields.datetime.today())

    _defaults = {
        'created_date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }
    state = fields.Selection(string="State",
                             selection=[('draft', 'Draft'),
                                        ('reserved', 'Reserved'),
                                        ('initial_contracted', 'Initial Contracted'),
                                        ('income', 'Create Income'),
                                        ('contracted', 'Installments'),
                                        ('blocked', 'Cancelled'),
                                        ('release', 'Release'),
                                        ('transfer', 'Transfer'), ], required=False, default='draft')

    installment_created = fields.Boolean(string='Installment Created')

    def onchange_method_state(self):
        print("enter herer state ")
        req_id = self.env['history.reservation'].create({
            # 'name':'Initial Contract',
            'date': datetime.now(),
            'name': self.reservation_code,
            'state': self.state,
            'unit_id': self.property_id.id,
            'res_id': self.id,

        })

    name = fields.Char(string="Name", compute="_compute_name_res_and_amen")

    def _compute_name_res_and_amen(self):
        for rec in self:
            if rec.custom_type == "Reservation":
                rec.name = rec.reservation_code
            elif rec.custom_type == "Accessories":
                rec.name = rec.accessories_code
            else:
                rec.name = rec.reservation_code

    custom_type = fields.Selection(string="Type",
                                   selection=[('Reservation', 'Reservation'), ('Accessories', 'Amendment'), ],
                                   required=False, default="Reservation")
    reservation_code = fields.Char(string="Reservation Code", readonly=True, copy=False, store=True)
    accessories_code = fields.Char(string="Accessories Code", readonly=True, copy=False, store=True, tracking=True)
    date = fields.Date(string="Date", required=False, default=fields.Date.today())

    # Accessories
    related_res_id = fields.Many2one(comodel_name="res.reservation", string="Related Reservation", required=False,
                                     domain=[('custom_type', '=', 'Reservation')])

    group_commision_with_payment = fields.Boolean(compute='_calc_group_commision_with_payment',store=False)
    def _calc_group_commision_with_payment(self):
        for rec in self:
            rec.group_commision_with_payment=self.env.user.has_group('add_real_estate.group_commision_with_payment')

    policy_commission_id= fields.Many2one(comodel_name='policy.commision',string='Commission')
    policy_bonous_id= fields.Many2one(comodel_name='policy.bonous',string='Bonus')
    policy_nts_id= fields.Many2one(comodel_name='policy.nts',string='Nts')




    @api.onchange('related_res_id')
    def onchange_method(self):
        if self.related_res_id:
            self.related_unit_id = self.related_res_id.property_id.id
            self.project_id = self.related_res_id.project_id.id
            self.phase_id = self.related_res_id.phase_id.id
            self.sale_person_2_id = self.related_res_id.sale_person_2_id.id
            self.customer_id = self.related_res_id.customer_id.id

    related_unit_id = fields.Many2one('product.product', _('Related Unit '), store=True)

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

        # return my_date

    is_eoi = fields.Boolean(string="EOI", )
    project_id = fields.Many2one('project.project', _("Project"), required=False)
    show_garden = fields.Boolean(string="Show Garden", related='project_id.show_garden', store=True)

    # terms_and_conditions = fields.Text(string="Terms and Conditions", required=False,related='project_id.terms_and_conditions' )
    phase_id = fields.Many2one('project.phase', _('Phase'), required=False)
    # property information
    property_id = fields.Many2one('product.product', _('Unit'), required=False,
                                  context="{'form_view_ref': 'add_real_estate.rs_property_product2_form_view2'}",
                                  domain=[('state', '=', 'available')], )
    property_code = fields.Char(string="Property Code", copy=False, related='property_id.property_code')
    finish_of_property_id = fields.Many2one('property.finished.type', _('Finishing Type'),
                                            related='property_id.finish_of_property_id')
    finish_of_property = fields.Selection(string="Finishing Type", selection=[('Finish', 'Finish'), ('Core&Shell', 'Core&Shell'), ],
                                          related='property_id.finish_of_property')

    is_select_all = fields.Boolean(string="Select All", )
    is_select_all_print = fields.Boolean(string="", )

    @api.onchange('is_select_all_print')
    def onchange_method_is_select_all_print(self):
        for rec in self:
            if rec.is_select_all_print == True:
                if rec.payment_strg_ids:
                    for payment in rec.payment_strg_ids:
                        payment.is_print = True

            if rec.is_select_all_print == False:
                if rec.payment_strg_ids:
                    for payment in rec.payment_strg_ids:
                        payment.is_print = False

    @api.onchange('is_select_all')
    def onchange_method_is_select_all(self):
        for rec in self:
            if rec.is_select_all == True:
                if rec.payment_strg_ids:
                    for payment in rec.payment_strg_ids:
                        if payment.display_type=='line_section':
                            payment.is_selected_to_action = False
                        else:
                            payment.is_selected_to_action = True

            if rec.is_select_all == False:
                if rec.payment_strg_ids:
                    for payment in rec.payment_strg_ids:
                        payment.is_selected_to_action = False

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
    sales_type = fields.Selection([('direct', _("Direct")), ('Broker', _("Broker"))], _('Sales Type'), default='direct')
    broker_id = fields.Many2one(comodel_name="res.partner", string="Broker", required=False,
                                domain=[('is_broker', '=', True)])
    # customer details
    customer_id = fields.Many2one('res.partner', string="Customer", domain=[('customer_rank', '>=', 1)])
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
    social_status = fields.Selection(string="Social Status", selection=[('married', 'Married'), ('single', 'Single'), ],related='customer_id.social_status', required=False, default='single')
    positon = fields.Char(string="Position",related='customer_id.positon',store=True)
    work_side = fields.Char(string="جهة العمل" ,related='customer_id.work_side',store=True)
    national_issue_date = fields.Date(string="National Issue Date",related='customer_id.national_issue_date',store=True)
    national_issue_date_month = fields.Integer(related='customer_id.national_issue_date_month', store=True)
    national_issue_date_year = fields.Integer(related='customer_id.national_issue_date_year', store=True)
    total_payment_lines = fields.Float(string="Total Payment Lines",compute='_calc_total_payment_lines',store=True)
    customer_details_readonly = fields.Boolean(compute='_calc_customer_details_readonly')

    def _calc_customer_details_readonly(self):
        for rec in self:
            rec.customer_details_readonly=not self.env.user.has_group('add_real_estate.group_real_state_inventory')


    @api.depends('payment_strg_ids')
    def _calc_total_payment_lines(self):
        for rec in self:
            total=0
            for payment in rec.payment_strg_ids:
                total+=payment.amount
            rec.total_payment_lines=total


    @api.onchange('customer_id')
    def onchange_method_customer_id(self):
        self.id_no = self.customer_id.id_def

    # lead
    lead_id = fields.Many2one('crm.lead', string="Lead")

    # internal information

    # sale_person_id = fields.Many2one(comodel_name="res.users", string="SalesPerson", required=True,default=lambda self: self.env.user )
    # Sales_Teams_id = fields.Many2one(related='sale_person_id.sale_team_id',comodel_name="crm.team", string="Sales Teams", required=True,)
    # manager_tesm_id = fields.Many2one(related='Sales_Teams_id.user_id',comodel_name="res.users", string="Team Leader	", required=True,default=lambda self: self.env.user )
    sale_person_2_id = fields.Many2one(comodel_name="res.partner", string="SalesPerson", )

    @api.onchange('customer_id')
    def onchange_customer(self):
        if self.customer_id:
            self.sale_person_2_id = self.customer_id.user_id.partner_id.id


    Sales_Teams_2_id = fields.Many2one(related='sale_person_2_id.company_team_id', comodel_name="company.team",
                                       string="Company Teams", )
    manager_tesm_2_id = fields.Many2one(related='Sales_Teams_2_id.user_id', comodel_name="res.partner",
                                        string="Team Leader", )
    company_id = fields.Many2one('res.company', string='Company', store=True, readonly=False,related='project_id.company_id')



    currency_id = fields.Many2one(string='Currency', store=True, readonly=True,
                                  related='company_id.currency_id', change_default=True)

    # attachment
    id_no = fields.Char(string="Identification No.")
    id_type = fields.Selection([('id', _("ID")), ('passport', _("Passport"))], string="Identification Type")
    id_photo = fields.Binary("Photo ID")

    # request come
    req_reservation_id = fields.Many2one(comodel_name="request.reservation", string="Request Reservation",
                                         required=False, )
    added_paid_amount = fields.Float(compute='_calc_added_paid_amount',string='Previous Paid Amount')
    amount_due22 = fields.Float(compute='_calc_added_paid_amount',string='Amount Due')

    @api.depends('req_reservation_id','payment_strg_ids')
    def _calc_added_paid_amount(self):
        for rec in self:
            sum_lines=0
            for line in rec.payment_strg_ids:
                if line.add_to_paid_amount:
                    sum_lines+=line.amount
            rec.added_paid_amount=rec.req_reservation_id.get_added_paid_amount()+sum_lines
            rec.amount_due22=rec.property_price-(rec.req_reservation_id.get_added_paid_amount()+sum_lines)
    #
    payment_code = fields.Char(string="Payment Code", required=False, )
    use_manual_payment = fields.Boolean(string="Use Manual Payment Strategy Lines")

    # create method
    @api.model
    def create(self, values):
        # print(" values ::> ",values)

        if values['custom_type'] == 'Reservation':
            values['reservation_code'] = self.env['ir.sequence'].next_by_code('real.estate.reservation.id.seq.finish')
            # values['name'] = self.env['ir.sequence'].next_by_code('real.estate.reservation.id.seq.finish')
        elif values['custom_type'] == 'Accessories':
            values['accessories_code'] = self.env['ir.sequence'].next_by_code('real.estate.Accessories.id.seq.finish')
            # values['name'] = self.env['ir.sequence'].next_by_code('real.estate.Accessories.id.seq.finish')

        values['payment_code'] = self.env['ir.sequence'].next_by_code('payment.cheque.seq')
        return super(requestReservation, self).create(values)

    def convert_to_reserved(self):
        for rec in self:
            if rec.state in ['draft','initial_contracted']:
                # TODO: remove no empty
                # start
                # if rec.id_no == False:
                #     raise ValidationError(_(
                #         "Identification No Empty  !!"))
                #
                # if rec.id_type == False:
                #     raise ValidationError(_(
                #         "Identification Type Empty  !!"))
                # end
                # if rec.id_photo == False:
                #     raise ValidationError(_(
                #         "Photo ID Empty  !!"))
                # if rec.payment_strg_ids.ids == []:
                #     raise ValidationError(_(
                #         "Payment Strategy Empty  !!"))
                if rec.customer_id.id == False:
                    raise ValidationError(_(
                        "Customer Empty  !!"))
                # if rec.sale_person_2_id.id == False:
                #     raise ValidationError(_(
                #         "SalesPerson Empty  !!"))
                res_res = self.env['res.reservation'].search([('property_id', '=', rec.property_id.id),
                                                              ('state', 'in', ['reserved'])])
                if len(res_res) == 0:
                    rec.state = 'reserved'
                    if rec.custom_type == 'Reservation':
                        rec.property_id.state = 'reserved'
                        rec.req_reservation_id.state = 'reserved'

                    rec.onchange_method_state()

                else:
                    if rec.custom_type == 'Reservation':

                        raise ValidationError(_(
                            "Sorry .. you must Create One Reservation Form For Reservation Form for This Property  %s!!") % self.property_id.name)
                    else:
                        rec.state = 'reserved'

    def convert_to_block(self):
        for rec in self:
            if rec.state in ['reserved', 'draft']:
                rec.state = 'blocked'
                rec.onchange_method_state()
                rec.req_reservation_id.state = 'blocked'
                # res_res = self.env['res.reservation'].search([('property_id', '=', rec.property_id.id),
                #                                      ('state', 'in', ['reserved'])])
                # if len(res_res) != 0:
                rec.property_id.state = 'available'

    def convert_to_draft(self):
        for rec in self:
            if rec.state in ['blocked', 'reserved', 'contracted']:

                rec.state = 'draft'
                rec.installment_created =False
                rec.onchange_method_state()
                rec.req_reservation_id.state = 'draft'
                res_res = self.env['res.reservation'].search([('property_id', '=', rec.property_id.id),
                                                              ('state', 'in', ['reserved'])])
                if len(res_res) != 0:
                    rec.property_id.state = 'available'


    # part payment and lins

    pay_strategy_id = fields.Many2one('account.payment.term', string="Payment Strategy")
    payment_strg_name = fields.Char(string="Payment Strategy", related='pay_strategy_id.name', store=True)
    payment_term_discount = fields.Float(string="Payment Term Discount",
                                         related="pay_strategy_id.payment_term_discount", store=True, digits=(16, 2))
    is_Custom_payment = fields.Boolean(string="Custom Strategy", )
    payment_strg_ids = fields.One2many('payment.strg', 'reserve_id', _('Payment'))

    # Description_payment = fields.Text(string="Description Payment Strategy	", required=False, )
    Description_payment = fields.Many2one(comodel_name="description.payment", string="Description Payment Strategy", required=False)
    Description_payment_description = fields.Text(string="Description")

    @api.onchange('Description_payment')
    def onchange_Description_payment(self):
        if self.Description_payment:
            self.Description_payment_description=self.Description_payment.description

    # new_field_ids = fields.One2many(comodel_name="", inverse_name="", string="", required=False, )

    discount = fields.Float(string="Discount Percentage", digits=(16, 15))
    total_discount = fields.Float('Total Discount', compute='_compute_total_discount', store=True)

    property_price = fields.Float(string="Property Price", readonly=True, related='property_id.final_unit_price',
                                  digits=(16, 2),track_visibility = 'always')
    net_price = fields.Float(string="Net Price", compute='_calc_net_price', store=True, digits=(16, 2),track_visibility = 'always')

    payment_due = fields.Float(string="Payment Due", required=False, compute="_calc_net_price")
    payment_lines = fields.Float(string="Payment Lines", required=False, store=True)
    # @api.depends("req_reservation_id")
    # def _compute_payments(self):
    #     amount = 0
    #     for rec  in self:



    def ar_amount_to_text(self, amount):
        convert_amount_in_words = num2words(amount, lang='ar_EG')
        return convert_amount_in_words


    more_discount = fields.Float(string="Discount%", required=False,track_visibility = 'always' )
    amount_discount = fields.Float(string="Amount Discount", required=False,track_visibility = 'always' )
    line_count = fields.Integer(
        string='Count', compute="_calc_line_count",store=False)
    @api.depends('payment_strg_ids')
    def _calc_line_count(self):
        for rec in self:
            rec.line_count=len(rec.payment_strg_ids.filtered(lambda line:line.state_payment == 'cheque' and line.display_type not in ['line_note','line_section']))


    @api.onchange('amount_discount')
    def onchange_method_amount_discount(self):
        if self.property_price > 0:
            self.more_discount = (self.amount_discount / self.property_price) * 100.0

    @api.onchange('more_discount')
    def onchange_method_more_discount(self):
        self.amount_discount = self.property_price * (self.more_discount / 100.0)

    @api.depends('discount', 'payment_term_discount', 'property_price', 'more_discount')
    def _calc_net_price(self):
        amount = 0
        for record in self:
            if record.req_reservation_id.id != False:
                # print("enetr herer false")
                payments = self.env['account.payment'].search([('request_id', '=', record.req_reservation_id.id)])
                if payments:
                    for line in payments:
                        amount += line.amount

                    record.payment_due = amount
                else:
                    amount = 0
                    record.payment_due = 0
            else:
                amount = 0
                record.payment_due = 0
            # print("record.payment_due :: %s", record.payment_due)
            if record.is_Custom_payment == False:

                first_discount = record.property_price - (
                            record.property_price * (record.payment_term_discount / 100.0))
                # net_price_first = first_discount - ((
                #         first_discount * (record.discount / 100.0))) - amount - record.payment_lines
                net_price_first = first_discount - ((
                        first_discount * (record.discount / 100.0)))  - record.payment_lines
                # record.amount_discount = net_price_first * (record.more_discount/100.0)
                record.net_price = net_price_first - (net_price_first * (record.more_discount / 100.0))
            else:
                total = 0
                for line in record.payment_strg_ids:
                    total += line.amount
                net_price_first = total - record.payment_lines
                # record.amount_discount = net_price_first * (record.more_discount/100.0)
                record.net_price = net_price_first - (net_price_first * (record.more_discount / 100.0))

    @api.depends('discount', 'payment_term_discount')
    def _compute_total_discount(self):
        for record in self:
            record.total_discount = record.discount + record.payment_term_discount

    date_start_installment = fields.Date(string="Start Installment", required=True, default=fields.datetime.today())

    number_day = fields.Integer(string="Number Of day", required=False, )

    @api.onchange('pay_strategy_id', 'discount', 'date_start_installment', 'number_day')
    def _onchange_pay_strategy(self):
        if self.use_manual_payment==False:
            inbound_payments = self.env['account.payment.method'].search([('payment_type', '=', 'inbound')])
            for rec in self:
                payment_due = rec.payment_due
                payments = []
                payment_descriptions = []
                for payment in rec.payment_strg_ids:
                    payment.write({
                        'reserve_id': False
                    })
                if rec.pay_strategy_id and rec.pay_strategy_id.id:
                    for payment_line in rec.pay_strategy_id.line_ids:
                        if payment_line.payment_description not in payment_descriptions:
                            payment_descriptions.append(payment_line.payment_description)
                            #Add Section
                            payments.append((0, 0, {
                                'name': payment_line.payment_description,
                                'display_type': 'line_section',
                            }))



                        payment_methods = inbound_payments and payment_line.journal_id.inbound_payment_method_ids or \
                                          payment_line.journal_id.outbound_payment_method_ids
                        # if rec.created_date:
                        #     date_order_format = datetime.strptime(rec.created_date+ ' 01:00:00', "%Y-%m-%d %H:%M:%S")
                        # else:
                        # print(
                        #     "datetime.date.today() :: %S",datetime.today()
                        # )
                        # date_order_format = rec.date_start_installment
                        date_order_format = rec.date_start_installment
                        date = date_order_format
                        if payment_line.days > 0:
                            _logger.info("enter here :: ")
                            no_months = payment_line.days / 30
                            _logger.info("enter here no_months :: %s", no_months)

                            date_order_day = date_order_format.day
                            date_order_month = date_order_format.month
                            date_order_year = date_order_format.year
                            date = date(date_order_year, date_order_month, date_order_day) + relativedelta(
                                months=math.ceil(no_months))
                        cheque_status = 'draft'

                        if payment_line.deposit:
                            cheque_status = 'received'

                        first_discount = rec.property_price - (
                                rec.property_price * (rec.payment_term_discount / 100.0))
                        net_price = first_discount - (
                                first_discount * (rec.discount / 100.0))
                        net_price = rec.property_price - (
                                rec.property_price * ((rec.discount + rec.payment_term_discount) / 100))

                        # Todo If line is Maintenance Fee
                        if payment_line.add_extension:
                            print("1111")
                            payment_amount = payment_line.value_amount * rec.property_price

                        else:
                            print("2222")
                            # payment_amount = payment_line.value_amount * rec.net_price
                            payment_amount = payment_amount1 = payment_line.value_amount * rec.property_price
                            payments_ids=self.env['account.payment'].search([('request_id', '=', rec.req_reservation_id.id)])
                            if payment_amount>payment_due and payment_line.days==0:
                                payment_duo_arr = {
                                    'amount': payment_due,
                                    'amount_pay': payment_due,
                                    'base_amount': payment_due,
                                    'date': date,
                                    'journal_id': payment_line.journal_id.id,
                                    'description': "Down Payment",
                                    'cheque_status': "received",
                                    'is_pay': True,
                                    'property_ids': [(6, 0, [rec.property_id.id])],
                                    'payments_ids': [(4, id) for id in payments_ids.ids]

                                }
                                payments.append((0, 0, payment_duo_arr))
                            if payment_amount < payment_due and payment_line.days == 0:
                                payment_duo_arr = {
                                    'amount': payment_due-payment_amount,
                                    'amount_pay': payment_due-payment_amount,
                                    'base_amount': payment_due,
                                    'date': date,
                                    'journal_id': payment_line.journal_id.id,
                                    'description': "Down Payment",
                                    'cheque_status': "received",
                                    'is_pay': True,
                                    'property_ids': [(6, 0, [rec.property_id.id])],
                                    'payments_ids': [(4, id) for id in payments_ids.ids]

                                }
                                payments.append((0, 0, payment_duo_arr))


                            is_pay = False
                            amount_pay=0
                            if payment_due > 0:
                                if payment_amount > payment_due:
                                    payment_amount = payment_amount - payment_due
                                else:
                                    is_pay = True
                            payment_due -= payment_amount1
                        if is_pay:
                            amount_pay=payment_amount
                        payment_arr = {
                            'amount': payment_amount,
                            'base_amount': payment_amount,
                            'date': date,
                            'journal_id': payment_line.journal_id.id,
                            'description': payment_line.payment_description,
                            'deposite': payment_line.deposit,
                            'cheque_status': cheque_status,
                            'add_extension': payment_line.add_extension,
                            # 'payment_method_id': payment_methods.id and payment_methods[0].id or False,
                            'property_ids': [(6, 0, [rec.property_id.id])],
                            "is_maintainance": payment_line.add_extension,
                            "is_pay": is_pay,
                            "amount_pay":amount_pay

                        }
                        if is_pay:
                            payment_arr['payments_ids']= [(4, id) for id in payments_ids.ids]

                        payments.append((0, 0, payment_arr))
                rec.payment_strg_ids = payments

    def button_delete_lines_selected(self):
        for rec in self:
            if rec.payment_strg_ids:
                for payment in rec.payment_strg_ids:
                    if payment.is_selected_to_action == True:
                        if payment.is_receive == False:
                            payment.unlink()
                        else:
                            raise UserError(_("You Cant Delete Payment Received."))
                for payment in rec.payment_strg_ids:
                    payment.is_selected_to_action = False

    def button_receive_lines_selected(self):
        for rec in self:
            if rec.payment_strg_ids:
                for payment in rec.payment_strg_ids:
                    # if payment.type != 'cash':
                    if payment.is_selected_to_action == True:
                        payment.is_receive = True

                for payment in rec.payment_strg_ids:
                    payment.is_selected_to_action = False

    def generate_report(self):
        if (not self.env.company.logo):
            raise UserError(_("You have to set a logo or a layout for your company."))
        elif (not self.env.company.external_report_layout_id):
            raise UserError(_("You have to set your reports's header and footer layout."))
        data = {}
        counter = 0
        for line in self.payment_strg_ids:
            print("line.is_selected_to_action ", line.is_selected_to_action)
            if line.is_selected_to_action == True:
                counter += 1
                print("counter11", counter)
            print("counter22", counter)
        #
        # if counter > 1:
        #     print("counter",counter)
        #     raise ValidationError(_("Sorry .. you must Select Once line  !!"))
        if counter == 0:
            print("counter", counter)
            raise ValidationError(_("Sorry .. you must Select Once line  !!"))
        for rec in self:
            if rec.payment_strg_ids:
                request_reservation = []
                for payment in rec.payment_strg_ids:
                    if payment.is_selected_to_action == True:
                        payment.is_print = True
                        amount_to_text = rec.company_id.currency_id.ar_amount_to_text(payment.amount or payment.amount_pay)
                        request_reservation.append({
                            'model': 'payment.strg.request',
                            'date': payment.date,
                            'description': payment.description,
                            'amount': payment.amount or payment.amount_pay,
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
                            'receipt_date': payment.receipt_date,
                        })

        data['request_reservation'] = request_reservation
        return self.sudo().env.ref('add_real_estate.payment_reservation_report_id').report_action([], data=data)

        # return self.env.ref('add_real_estate.payment_stag_request_id').report_action(
        #     self,
        #     data=datas)

        # for payment in rec.payment_strg_ids:
        #     payment.is_selected_to_action = False

    def create_initial_contract(self):
        contract_id= self.env['contract.reservation'].search([('reservation_id','=',self.id)],limit=1)
        if contract_id:
            contract_id.write({
            'name':'عقد بيع وحدة سكنية بمشروع '+self.project_id.name+'-'+self.property_code,
            'date':datetime.now().date(),
            'partner_id':self.customer_id.id,
            'property_id':self.property_id.id,
            'property_price':self.net_price,
            'property_space':0,
            'state':'draft'
        })
        else:
            self.env['contract.reservation'].create({
                'name': 'عقد بيع وحدة سكنية بمشروع ' + self.project_id.name + '-' + self.property_code,
                'date': datetime.now().date(),
                'partner_id': self.customer_id.id,
                'property_id': self.property_id.id,
                'property_price': self.net_price,
                'property_space': 0,
                'reservation_id': self.id,
            })

        self.write({'state': 'initial_contracted'})
        self.property_id.write({'state' :'initial_contracted'})
        action = self.env.ref('add_real_estate.action_contract_reservation').read()[0]
        action['domain'] = [
            ('reservation_id', '=', self.id)
        ]
        return action


    def create_initial_income(self):
        account = self.env['account.account'].search([('id', '=', 2)], limit=1)
        journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)

        total_ins = 0

        for line in self.payment_strg_ids:
            print("line.reserve_id.id,", line.reserve_id.id)
            print("line.reserve_id.id,", line.cheque)
            print("line.reserve_id.id,", line.id)
            # if line.cheque:
            #     strg = self.env['payment.strg'].search([('id', '=', self.payment_strg_ids.ids),('cheque','=',line.cheque),('id','!=',line.id)])
            #     if strg:
            #         raise ValidationError(_('Error !,Number Cheque Duplicate.'))

            if line.is_maintainance == False and line.is_no_enter_total == False:
                total_ins += line.amount

        print("self.env.user.has_group('add_real_estate.group_custom_payment') :> ",
              self.env.user.has_group('add_real_estate.group_custom_payment'))
        if self.env.user.has_group('add_real_estate.group_custom_payment') == False:
            # if  self.user_has_groups('add_real_estate.group_custom_payment'):

            print("total_ins  :> ", total_ins)
            print("total_ins  :> ", round(total_ins))
            print("self.net_price  :> ", self.net_price)
            print("self.net_price  :> ", round(self.net_price))
            if self.pay_strategy_id:
                if round(total_ins) != round(self.net_price):
                    raise ValidationError(_('Error !,The Total installment is not equal The net Price.'))

        lines = []
        print("self.property_id.propert_account_id.id :: %s", self.property_id.propert_account_id.name)
        lines.append((0, 0, {
            'product_id': self.property_id.id,
            'name': self.property_id.name,
            'analytic_account_id': self.property_id.analytic_account_id.id,
            'price_unit': self.net_price,

        }))
        print("lines :: %s", lines)
        req_id = self.env['account.move'].create({
            # 'name':'Initial Contract',
            'date': datetime.now(),
            'invoice_date': datetime.now(),
            'partner_id': self.customer_id.id,
            'ref': self.reservation_code,
            'move_type': 'out_invoice',
            'is_contract': True,
            'reservation_id': self.id,
            'journal_id': journal.id

        })

        print("req_id :: %s", req_id.id)
        req_id.update({
            # 'move_id': req_id.id,
            'invoice_line_ids': lines,

        })
        self.write({'state': 'income'})
        self.property_id.write({'state': 'initial_contracted'})
        view = self.env.ref('add_real_estate.view_contract_form')

        return {'name': (
            'Contract'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': req_id.id,
            'views': [
                (view.id, 'form')
            ],
            'view_id': view.id,
            'view_type': 'form',
            'view_mode': 'form',
            'context': {'name': ' Income'},

        }

    is_create_contract = fields.Boolean(string="Is Request Resveration", compute="_compute_view_button_create")

    def _compute_view_button_create(self):
        for rec in self:
            res = self.env['account.move'].search(
                [('reservation_id', '=', rec.id), ("state", '!=', 'cancel'),("move_type", '=', 'out_invoice')
                 ], limit=1)

            if len(res) > 0:
                rec.is_create_contract = True
            else:
                rec.is_create_contract = False


    amount_total = fields.Float(string="Amount", required=False, compute="_compute_amount")
    amount_total2 = fields.Float(string="Amount", required=False, compute="_compute_amount")
    main_total = fields.Float(string="Maintance And Insurrance", required=False, compute="_compute_amount")
    amount_residual = fields.Float(string="Amount Due", required=False, compute="_compute_amount")
    contract_date = fields.Date(string="Contract Date", required=False)

    # @api.constrains('payment_strg_ids','state')
    # def _check_amount_total(self):
    #     for field in self:
    #         if field.state=='reserved':
    #             if int(field.amount_total2)>int(field.property_price):
    #                 print("field.amount_total",field.amount_total2,field.property_price)
    #                 raise ValidationError("Amount Must less than or equal to  Property Price ")




    def _compute_amount(self):
        amount = 0
        amount2 = 0
        main_total = 0
        due = 0
        amount_discount = 0
        for rec in self:
            if rec.payment_strg_ids:
                for line in rec.payment_strg_ids:
                    amount2+=line.amount
                    if line.is_maintainance == False and line.is_no_enter_total == False:
                        amount += line.amount
                    if line.is_maintainance == True:
                        main_total += line.amount
                    due += line.amount_due
                rec.amount_total = amount
                rec.amount_total2 = amount2
                # amount_discount = rec.amount_total * (rec.more_discount /100.00)
                # rec.amount_discount = amount_discount
                rec.amount_residual = due
                rec.main_total = main_total
            else:
                rec.amount_total = 0
                rec.amount_total2 = 0
                rec.amount_residual = 0
                rec.main_total = 0
                # rec.amount_discount = 0

    bank_name = fields.Many2one('payment.bank', _("Bank Name"))
    # start_cheque = fields.Integer(string="Start", required=False, size=20)
    # end_cheque = fields.Integer(string="End", required=False,size=20 )
    start_cheque = fields.Char(string="Start", required=False, size=20)
    end_cheque = fields.Char(string="End", required=False, size=20)

    amount_ins = fields.Float(string="Amount Ins.", required=False, )

    def update_ins_amount_data(self):
        for line in self.payment_strg_ids:
            if line.is_selected_to_action == True:
                line.amount = self.amount_ins
                line.base_amount = self.amount_ins

    def update_bank_data(self):
        counter = int(self.start_cheque)
        end = int(self.end_cheque)
        print("counter :: %s", counter)
        for line in self.payment_strg_ids:
            if line.is_selected_to_action == True:
                if line.type != 'cash':
                    if int(self.start_cheque) == int(self.end_cheque):
                        line.cheque = int(self.start_cheque)
                    else:
                        print("D>DDDDDDDDDDDDDDDDDDDdd777",int(self.end_cheque), counter)
                        line.bank_name = self.bank_name.id
                        if int(self.end_cheque) >= counter:
                            line.cheque = counter
                            counter += 1

    is_release = fields.Boolean(string="Is Release", )
    odoo_reservation_id = fields.Many2one(comodel_name="res.reservation", string="Old Reservation", required=False, )

    counter_contract = fields.Integer(string="Counter Contract", required=False, compute="_compute_counter_contract")
    counter_installments = fields.Integer(string="Counter Installments", required=False, compute="_compute_counter_installments")
    counter_contract_reservation = fields.Integer(string="Counter Contract", required=False, compute="_compute_counter_contract")
    installment_ids = fields.Many2many(comodel_name='account.move', string='Installments',relation="install_resv")


    def _compute_counter_installments(self):
        for rec in self:
            rec.counter_installments = len(rec.installment_ids)
    def _compute_counter_contract(self):
        for rec in self:
            invoices = self.env['account.move'].sudo().search(
                [('reservation_id', '=', rec.id),("move_type", '=', 'out_invoice')])

            contracts = self.env['contract.reservation'].sudo().search(
                [('reservation_id', '=', rec.id)])
            rec.counter_contract = len(invoices)
            rec.counter_contract_reservation = len(contracts)

    counter_amendments = fields.Integer(string="Counter Contract", required=False, compute="_compute_counter_amen")

    def _compute_counter_amen(self):
        for rec in self:
            contracts = self.env['res.reservation'].sudo().search(
                [('related_res_id', '=', rec.id)])
            rec.counter_amendments = len(contracts)

    def action_view_invoices(self):
        self.ensure_one()
        action = self.env.ref('add_real_estate.action_move_out_invoice_type_contract').read()[0]
        action['domain'] = [
            # ('state', 'in', ['draft','reserved']),
            ('reservation_id', '=', self.id),("move_type", '=', 'out_invoice')
        ]
        print("action %s", action)
        return action
    def action_view_contract_reservation(self):
        self.ensure_one()
        action = self.env.ref('add_real_estate.action_contract_reservation').read()[0]
        action['domain'] = [
            ('reservation_id', '=', self.id)
        ]
        print("action %s", action)
        return action

    def action_view_contract_Accessories(self):
        self.ensure_one()
        action = self.env.ref('add_real_estate.accessories_list_action').read()[0]
        action['domain'] = [
            # ('state', 'in', ['draft','reserved']),
            ('related_res_id', '=', self.id),
        ]
        print("action %s", action)
        return action

    # def create_payment_lines_selected(self):
    #     counter = 0
    #     # req_id = []
    #     for line in self.payment_strg_ids:
    #         if line.is_selected_to_action == True:
    #             counter += 1
    #     if counter > 1:
    #         raise ValidationError(_("Sorry .. you must Select Once line  !!"))
    #     if counter == 0:
    #         raise ValidationError(_("Sorry .. you must Select Once line  !!"))
    #     method = self.env['account.payment.method'].sudo().search([
    #         ('name', '=', 'Manual')
    #     ], limit=1)
    #     method_batch = self.env['account.payment.method'].sudo().search([
    #         ('name', '=', 'Batch Deposit')
    #     ], limit=1)
    #     data_bank = self.env['data.bank.cheque']
    #
    #     for line in self.payment_strg_ids:
    #         if line.type == 'cash':
    #             if line.is_selected_to_action == True and line.is_create_payment == True:
    #                 raise ValidationError(_("Sorry .. you Create Payment Before  !!"))
    #             if line.is_selected_to_action == True and line.is_create_payment == False:
    #                 req_id = self.env['account.payment'].create({
    #                     'state': 'draft',
    #                     'date': datetime.now(),
    #                     'payment_type': 'inbound',
    #                     'partner_type': 'customer',
    #                     'partner_id': self.customer_id.id,
    #                     'amount': line.amount,
    #                     'journal_id': line.journal_id.id,
    #                     'payment_method_id': method.id,
    #                     'reservation_id': self.id,
    #                     'payment_strg_id': line.id,
    #                     'is_contract': True,
    #                     'is_payment_lines': True,
    #
    #                 })
    #                 print("req_id :: ", req_id)
    #                 line.is_create_payment = True
    #                 line.is_pay = True
    #
    #                 p = []
    #
    #                 p.append(pay2.id)
    #                 for rec in pay_strg.payments_ids:
    #                     p.append(rec.id)
    #
    #                 line.update({
    #                     'payments_ids': [(6, 0, p)],
    #                 })
    #                 # self.payment_lines = line.amount
    #                 break
    #         else:
    #             if line.is_selected_to_action == True and line.is_create_payment == True:
    #                 raise ValidationError(_("Sorry .. you Create Payment Before  !!"))
    #             if line.is_selected_to_action == True and line.is_create_payment == False:
    #                 req_id = self.env['account.payment'].create({
    #                     'state': 'draft',
    #                     'date': datetime.now(),
    #                     'payment_type': 'inbound',
    #                     'partner_type': 'customer',
    #                     'partner_id': self.customer_id.id,
    #                     'amount': line.amount,
    #                     'journal_id': line.journal_id.id,
    #                     'payment_method_id': method_batch.id,
    #                     'reservation_id': self.id,
    #                     'payment_strg_id': line.id,
    #                     'bank_name': line.bank_name.name,
    #                     'check_number': line.cheque,
    #                     'due_date': line.date,
    #                     'actual_date': line.date,
    #                     'is_contract': True,
    #                     'is_payment_lines': True,
    #
    #                 })
    #                 print("req_id :: ", req_id)
    #                 line.is_create_payment = True
    #                 line.is_pay = True
    #                 data_bank_id = data_bank.create({
    #                     'bank_id': line.bank_name.id,
    #                     'cheque_number': line.cheque,
    #                     'reservation_id': self.id,
    #                     'payment_id': req_id.id,
    #
    #                 })
    #                 l = []
    #                 p = []
    #                 l.append(data_bank_id.id)
    #                 for line2 in line.bank_ids:
    #                     l.append(line2.id)
    #                 p.append(req_id.id)
    #                 for rec in line.payments_ids:
    #                     p.append(rec.id)
    #                 line.update({
    #                     'bank_ids': [(6, 0, l)],
    #                     'payments_ids': [(6, 0, p)],
    #                 })
    #                 # self.payment_lines = line.amount
    #                 break
    #     # return {'name': (
    #     #                     'Payment'),
    #     #                 'type': 'ir.actions.act_window',
    #     #                 'res_model': 'account.payment',
    #     #                 'res_id': req_id.id,
    #     #                 'view_type': 'form',
    #     #                 'view_mode': 'form',
    #     #             }
    def create_payment_lines_selected(self):
        for line in self.payment_strg_ids:
            if line.is_selected_to_action and line.display_type==False and line.is_create_payment==False:
                val = {
                    'receipt_number': line.name,
                    'partner_id': self.customer_id.id,
                    'reservation_id': self.id,
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
                pay.get_partner_acc2()
                pay.write({
                    'amount': line.amount,
                    'amount1': line.amount,
                })
                line.check_payment_id=pay.id
                pay.action_confirm()



    # @api.onchange('payment_strg_ids')
    # def _onchange_payment_strg_ids(self):
    #     for rec in self:
    #         total_ins = 0
    #         for line in rec.payment_strg_ids:
    #             if line.is_maintainance== False:
    #                 total_ins += line.amount
    #
    #         if not self.user_has_groups('add_real_estate.group_custom_payment'):
    #             if total_ins != rec.net_price:
    #                 raise ValidationError(_('Error !.'))

    # @api.constrains('payment_strg_ids')
    # def check_payment_strg_ids(self):
    #     total_ins = 0
    #
    #     for line in self.payment_strg_ids:
    #         print("line.reserve_id.id,",line.reserve_id.id)
    #         print("line.reserve_id.id,",line.cheque)
    #         print("line.reserve_id.id,",line.id)
    #         if line.cheque:
    #             strg = self.env['payment.strg'].search([('id', '=', self.payment_strg_ids.ids),('cheque','=',line.cheque),('id','!=',line.id)])
    #             if strg:
    #                 raise ValidationError(_('Error !,Number Cheque Duplicate.'))
    #
    #         if line.is_maintainance == False:
    #             total_ins += line.amount
    #
    #     if not self.user_has_groups('add_real_estate.group_custom_payment'):
    #         print("total_ins  :> ",total_ins)
    #         print("total_ins  :> ",round(total_ins))
    #         print("self.net_price  :> ",self.net_price)
    #         print("self.net_price  :> ",round(self.net_price))
    #         if self.pay_strategy_id:
    #             if round(total_ins) != round(self.net_price):
    #                 raise ValidationError(_('Error !,The Total installment is not equal The net Price.'))
    #

    notes_cash = fields.Text(string="Notes (Cash)", required=False, )
    notes_visa = fields.Text(string="Notes (Visa)", required=False, )
    notes_cheque = fields.Text(string="Notes (Cheque)", required=False, )
    notes_bank = fields.Text(string="Notes (Bank)", required=False, )

    amount_cheques = fields.Float(string="Amount Cheques", required=False, compute="_compute_amount_cheques")

    def _compute_amount_cheques(self):
        for rec in self:
            if rec.payment_strg_ids:
                totol = 0
                for line in rec.payment_strg_ids:
                    if line.state_payment == 'cheque':
                        totol += line.amount

                    if line.is_print and line.state_payment == 'cheque':
                        totol -= line.amount

                rec.amount_cheques = totol
            else:
                rec.amount_cheques = 0

    number_ins = fields.Integer(string="", required=False, compute="_compute_number_ins")

    def _compute_number_ins(self):
        for rec in self:
            if rec.payment_strg_ids:
                counter = 0
                for line in rec.payment_strg_ids:
                    if line.state_payment == 'cheque':
                        counter += 1
                    if line.is_print and line.state_payment == 'cheque':
                        counter -= 1
                rec.number_ins = counter
            elif counter < 0:
                rec.number_ins = 0
            else:
                rec.number_ins = 0

    receipt_date = fields.Date(string="Receipt Date", required=False, )

    def update_ins_receipt_date(self):
        for line in self.payment_strg_ids:
            if line.is_selected_to_action == True:
                line.receipt_date = self.receipt_date

    reason = fields.Many2one(comodel_name="cancel.reason.res", string="Reason", required=False, )
    date_cancel_unit = fields.Datetime(string="Cancel Date", required=False, )

    # edit by Yasser
    def get_childs_of_contact(self):
        action = self.env.ref('contacts.action_contacts').read()[0]
        action['domain'] = [('parent_id', '=', self.customer_id.id)]
        # action['context']={'default_parent_id':self.customer_id.id,'default_company_type':'person'}
        return action

    def recompute_payments(self):
        inbound_payments = self.env['account.payment.method'].search([('payment_type', '=', 'inbound')])
        for rec in self:
            payment_due = rec.payment_due
            payments = []
            for payment in rec.payment_strg_ids:
                if payment.is_receive==False:
                    payment.write({
                        'reserve_id': False
                    })
            if rec.pay_strategy_id and rec.pay_strategy_id.id:
                for payment_line in rec.pay_strategy_id.line_ids:
                    payment_methods = inbound_payments and payment_line.journal_id.inbound_payment_method_ids or \
                                      payment_line.journal_id.outbound_payment_method_ids
                    # if rec.created_date:
                    #     date_order_format = datetime.strptime(rec.created_date+ ' 01:00:00', "%Y-%m-%d %H:%M:%S")
                    # else:
                    # print(
                    #     "datetime.date.today() :: %S",datetime.today()
                    # )
                    # date_order_format = rec.date_start_installment
                    date_order_format = rec.date_start_installment
                    date = date_order_format
                    if payment_line.days > 0:
                        _logger.info("enter here :: ")
                        no_months = payment_line.days / 30
                        _logger.info("enter here no_months :: %s", no_months)

                        date_order_day = date_order_format.day
                        date_order_month = date_order_format.month
                        date_order_year = date_order_format.year
                        date = date(date_order_year, date_order_month, date_order_day) + relativedelta(
                            months=math.ceil(no_months))
                    cheque_status = 'draft'

                    if payment_line.deposit:
                        cheque_status = 'received'

                    first_discount = rec.property_price - (
                            rec.property_price * (rec.payment_term_discount / 100.0))
                    net_price = first_discount - (
                            first_discount * (rec.discount / 100.0))
                    net_price = rec.property_price - (
                            rec.property_price * ((rec.discount + rec.payment_term_discount) / 100))

                    # Todo If line is Maintenance Fee
                    if payment_line.add_extension:
                        print("1111")
                        payment_amount = payment_line.value_amount * rec.property_price

                    else:
                        print("2222")
                        # payment_amount = payment_line.value_amount * rec.net_price
                        payment_amount = payment_amount1 = payment_line.value_amount * rec.property_price
                        payments_ids = self.env['account.payment'].search(
                            [('request_id', '=', rec.req_reservation_id.id)])
                        print("D:::::::;", [(6, 0, p.id) for p in payments_ids])
                        if payment_amount > payment_due and payment_line.days == 0:
                            payment_duo_arr = {
                                'amount': payment_due,
                                'amount_pay': payment_due,
                                'base_amount': payment_due,
                                'date': date,
                                'journal_id': payment_line.journal_id.id,
                                'description': "Down Payment",
                                'cheque_status': "received",
                                'is_pay': True,
                                'property_ids': [(6, 0, [rec.property_id.id])],
                                'payments_ids': [(4, id) for id in payments_ids.ids]

                            }
                            payments.append((0, 0, payment_duo_arr))
                        if payment_amount < payment_due and payment_line.days == 0:
                            payment_duo_arr = {
                                'amount': payment_due - payment_amount,
                                'amount_pay': payment_due - payment_amount,
                                'base_amount': payment_due,
                                'date': date,
                                'journal_id': payment_line.journal_id.id,
                                'description': "Down Payment",
                                'cheque_status': "received",
                                'is_pay': True,
                                'property_ids': [(6, 0, [rec.property_id.id])],
                                'payments_ids': [(4, id) for id in payments_ids.ids]

                            }
                            payments.append((0, 0, payment_duo_arr))

                        is_pay = False
                        amount_pay = 0
                        if payment_due > 0:
                            if payment_amount > payment_due:
                                payment_amount = payment_amount - payment_due
                            else:
                                is_pay = True
                        payment_due -= payment_amount1
                    if is_pay:
                        amount_pay = payment_amount
                    payment_arr = {
                        'amount': payment_amount,
                        'base_amount': payment_amount,
                        'date': date,
                        'journal_id': payment_line.journal_id.id,
                        'description': payment_line.payment_description,
                        'deposite': payment_line.deposit,
                        'cheque_status': cheque_status,
                        'add_extension': payment_line.add_extension,
                        # 'payment_method_id': payment_methods.id and payment_methods[0].id or False,
                        'property_ids': [(6, 0, [rec.property_id.id])],
                        "is_maintainance": payment_line.add_extension,
                        "is_pay": is_pay,
                        "amount_pay": amount_pay

                    }
                    if is_pay:
                        payment_arr['payments_ids'] = [(4, id) for id in payments_ids.ids]

                    payments.append((0, 0, payment_arr))
            rec.payment_strg_ids = payments

    def chunks(self, l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]

    @api.constrains('property_id')
    def check_one_form_property_id(self):
        if self.property_id:
            if len(self.env['res.reservation'].search([("property_id", "=", self.property_id.id),('state','not in',['blocked','release'])])) > 1:
                raise ValidationError("غير مسموح بعمل اكثر من استمارة حجز")


    def create_installments(self):
        invoice_line_ids=[]
        val={}
        for line in self.payment_strg_ids:
            if line.is_selected_to_action==True and line.display_type not in ['line_section','line_note'] and line.merge_in_one_installment==False:
                move = self.env['account.move'].create({
                    'ref': line.name,
                    'reservation_id': self.id,
                    'partner_id': self.customer_id.id,
                    'invoice_date': line.receipt_date,
                    'custom_invoice_date': line.receipt_date,
                    'invoice_date_due': line.date,
                    'state_payment': line.state_payment,
                    'cheque': line.cheque,
                    'deposite': line.deposite,
                    'is_maintainance': line.is_maintainance,
                    'installment_type': line.description,
                    'deposite': line.deposite,
                    'is_maintainance': line.is_maintainance,
                    'journal_id': self.company_id.invoice_journal_id.id,
                    'invoice_line_ids':[(0,0,{
                        'name':line.name,
                        'price_unit':line.amount,
                    })] ,
                    'move_type': 'out_invoice'
                })
                line.invoice_id=move.id
                self.installment_ids = [(4,move.id)]
            if line.is_selected_to_action==True and line.display_type not in ['line_section','line_note'] and line.merge_in_one_installment==True:
                invoice_line_ids.append(
                    (0, 0, {
                        'name': line.name,
                        'price_unit': line.amount,
                    })
                )
                val.update({
                    'ref': line.name,
                    'reservation_id': self.id,
                    'partner_id': self.customer_id.id,
                    'invoice_date': line.receipt_date,
                    'custom_invoice_date': line.receipt_date,
                    'invoice_date_due': line.date,
                    'state_payment': line.state_payment,
                    'cheque': line.cheque,
                    'deposite': line.deposite,
                    'is_maintainance': line.is_maintainance,
                    'installment_type': line.description,
                    'deposite': line.deposite,
                    'is_maintainance': line.is_maintainance,
                    'journal_id': self.company_id.invoice_journal_id.id,
                    'move_type': 'out_invoice'
                })
        val['invoice_line_ids']=invoice_line_ids
        move = self.env['account.move'].create(val)
        payment_strg_ids=self.payment_strg_ids.filtered(lambda line:line.is_selected_to_action==True and line.display_type not in ['line_section','line_note'] and line.merge_in_one_installment==True)
        payment_strg_ids.write({'invoice_id':move.id})
        self.installment_ids = [(4,move.id)]
        self.installment_created=True

    def open_installments(self):
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        action['domain'] = [('id', '=', self.installment_ids.ids)]
        return action
