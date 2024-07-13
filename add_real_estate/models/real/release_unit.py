# -*- coding: utf-8 -*-
from odoo import api, fields, models,_
from odoo.exceptions import ValidationError,UserError

import logging
from datetime import datetime
LOGGER = logging.getLogger(__name__)

class ReleaseUnit(models.Model):
    _name = 'release.unit'
    _description = "Release Unit"

    date = fields.Date(string="Date", required=True,default=fields.Date.today() )

    state = fields.Selection(string="State", selection=[('draft', 'Draft'),('approved', 'Approved') ], required=False ,default='draft')
    name = fields.Char(string="Number", required=False, )
    journal_id = fields.Many2one(comodel_name="account.journal", string="Journal", required=False,domain=[('type', 'in', ['bank','cash'])],  )
    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner", required=True, )
    reservation_id = fields.Many2one(comodel_name="res.reservation", string="Reservation", required=True,domain=[('state', '=', 'reserved')] )
    # unit
    property_id = fields.Many2one(related="reservation_id.property_id",comodel_name="product.product", string="Unit", required=False, )
    net_price = fields.Float(related="reservation_id.net_price",string="Net Price")
    realse_unit = fields.Boolean()
    release_partner_id = fields.Many2one(comodel_name="res.partner", string="Release Partner", required=False, )
    release_property_id = fields.Many2one(comodel_name="product.product", string="Release Unit", required=False, )
    is_select_all = fields.Boolean(string="Select All",  )

    total_amount = fields.Float(string="Total Amount",  required=False,compute="_compute_amount" )
    amount_due = fields.Float(string="Amount Due",  required=False,compute="_compute_amount" )
    def _compute_amount(self):
        amount = 0
        for rec in self:
            payment_collected = self.env['account.payment'].search([
                ('reservation_id', '=', rec.reservation_id.id),
                ('partner_id', '=', rec.partner_id.id),
            ])
            payment_collected=payment_collected.filtered(lambda paym:paym.state=='collected' or (paym.state=='posted' and paym.payment_strg_id.state_payment!='cheque') )

            payment_open = self.env['account.payment'].search([
                ('reservation_id', '=', rec.reservation_id.id),
                ('partner_id', '=', rec.partner_id.id),
                ('state', 'in', ['posted', 'under_coll'])
            ])
            for line in payment_collected:
                amount += line.amount
            rec.total_amount = rec.net_price
            rec.amount_due = rec.net_price -  amount

    lines_ids = fields.One2many(comodel_name="release.payment.line", inverse_name="release_id", string="", required=False, )
    @api.onchange('reservation_id')
    def onchange_method_reservation_id(self):
        for rec in self:
            release_payment_line = self.env['release.payment.line']
            print("here")
            payment_collected = self.env['account.payment'].search([
                ('reservation_id', '=', rec.reservation_id.id),
                ('partner_id', '=', rec.partner_id.id),
            ])
            payment_collected=payment_collected.filtered(lambda paym:paym.state=='collected' or (paym.state=='posted' and paym.payment_strg_id.state_payment!='cheque') )
            payment_open = self.env['account.payment'].search([
                ('reservation_id', '=', rec.reservation_id.id),
                ('partner_id', '=', rec.partner_id.id),
                ('state', 'in', ['posted','under_coll'])
            ])
            if payment_collected:
                for line in payment_collected:
                    release_payment_line.create({
                        'date': line.date,
                        'state': line.state,
                        'name': line.name,
                        'journal_id': line.journal_id.id,
                        'amount': line.amount,
                        'reservation_id':line.reservation_id.id,
                        'release_id': rec.id,
                    })

            if payment_open:
                for line in payment_open:
                    release_payment_line.create({
                        'date': line.date,
                        'state': line.state,
                        'name': line.name,
                        'journal_id': line.journal_id.id,
                        'amount': line.amount,
                        'release_id': rec.id,
                    })

    @api.onchange('is_select_all')
    def onchange_method_is_select_all(self):
        print('ffffffff')
    payments_count = fields.Integer(compute='_compute_payment_count', string="Payment Count")

    def _compute_payment_count(self):
        for rec in self:
            release_payment_line = self.env['release.payment.line']
            print("here")
            payment_collected = self.env['account.payment'].search([
                ('reservation_id', '=', rec.reservation_id.id),
                ('partner_id', '=', rec.partner_id.id),
            ])
            rec.payments_count = len(payment_collected)


    def action_view_payment(self):
        self.ensure_one()
        action = self.env.ref('add_real_estate.act_payment_info_all_2').read()[0]
        print("action %s",action)
        context = {
            'default_reservation_id': self.reservation_id.id,
            'default_partner_id': self.partner_id.id,
        }

        action['domain'] = [('reservation_id', '=', self.reservation_id.id),('partner_id', '=', self.partner_id.id),]

        # action['domain'] = domain
        action['context'] = context
        print("action['context'] %s",action['context'])
        print("action['context'] %s",action['domain'])

        return action

    @api.model
    def create(self, values):

        values['name'] = self.env['ir.sequence'].next_by_code('release.unit.seq')
        return super(ReleaseUnit, self).create(values)

    new_reservation_id = fields.Many2one(comodel_name="res.reservation", string="Reservation", required=False,readonly=True )
    move_id = fields.Many2one(comodel_name="account.move", string="Move", required=False, )
    post_data = fields.Date(string="Refund Data", required=False,default=fields.Date.today()  )
    post_data_2 = fields.Date(string="Refund Data", required=False,default=fields.Date.today()  )
    collect_data = fields.Date(string="Collect Date", required=False,default=fields.Date.today()  )
    journal_miscellaneous_id = fields.Many2one(comodel_name="account.journal",domain=[('type','=','general')], string="", required=False, )

    def approved(self):
        for rec in self:
            if rec.realse_unit:
                rec.reservation_id.state = 'release'
                rec.new_reservation_id = rec.reservation_id.copy()
                rec.new_reservation_id.write({'property_id':rec.release_property_id.id,})
                for line in rec.reservation_id.payment_strg_ids:
                    line.write({'reserve_id':rec.new_reservation_id.id})
                    for payment in line.payments_ids:
                        payment.write({'reservation_id':rec.new_reservation_id.id})
                rec.state = 'approved'
                rec.reservation_id.write({
                    'state': 'blocked',
                    'date_cancel_unit': datetime.now(),
                    'reason': self.env['cancel.reason.res'].search([('name', '=', 'Change Unit')], limit=1).id,
                })

            else:
                lines2 = []
                lines3 = []
                lines4 = []
                total =0
                total_paid =0
                for line in rec.reservation_id.payment_strg_ids:
                    amount_col_line = 0
                    ids = []
                    for paym in line.payments_ids:
                        if paym.state == "collected":
                            amount_col_line += paym.amount
                            ids.append(paym.id)
                    payment_collected_line = self.env['account.payment'].search([
                        ('id', 'in', ids)
                    ])
                    ids_b = []
                    for bank in line.bank_ids:
                        if bank.payment_id.state == "collected":
                            ids_b.append(bank.id)
                    bank_line = self.env['data.bank.cheque'].search([
                        ('id', 'in', ids_b)
                    ])
                    if line.installment_state == 'paid':
                        lines2.append({
                            'description': line.description,
                            'amount': line.amount,
                            'date': line.date,
                            'journal_id': line.journal_id.id,
                            'deposite': line.deposite,
                            'state_payment': line.state_payment,
                            'amount_pay': line.amount_pay or line.amount,
                            'amount_due': line.amount_due,
                            'payments_ids': [(6, 0, payment_collected_line.ids)],
                            'bank_ids': [(6, 0, bank_line.ids)],
                            'force_posted': True

                        })
                        total_paid += line.amount
                    else:
                        if line.installment_state=='not_paid':
                            line.invoice_id.button_cancel()

                        total+=line.amount
                        lines3.append({
                            'description': line.description,
                            'amount': line.amount_pay,
                            'date': line.date,
                            'journal_id': line.journal_id.id,
                            'deposite': line.deposite,
                            'state_payment': line.state_payment,
                            'amount_pay': 0,
                            'amount_due': 0,
                            'payments_ids': [(6, 0, payment_collected_line.ids)],
                            'bank_ids': [(6, 0, bank_line.ids)],

                        })

                    # if line.state == 'collected' or (line.state == 'posted' and line.state_payment != 'cheque'):
                if lines2:
                    lines4.append(
                        {
                            'name': "Paid",
                            'display_type': "line_section",

                        })
                    for line in lines2:
                        lines4.append(line)
                if lines3:
                    lines4.append(
                        {
                            'name': "Draft",
                            'display_type': "line_section",

                        })
                    for line in lines3:
                        lines4.append(line)

                print("1")



                account_move = self.env['account.move']
                writeoff_lines = []
                total_currency = 0.0

                writeoff_lines.append({
                    'name': ('Release'),
                    'debit': total_paid,
                    'credit':  0.0,
                    'amount_currency': total_currency,
                    # 'currency_id': total_currency and writeoff_currency.id or False,
                    'journal_id': rec.journal_miscellaneous_id.id,
                    'account_id': rec.partner_id.property_account_receivable_id.id,
                    'partner_id': rec.partner_id.id,
                    'reservation_id': self.reservation_id.id,
                })
                writeoff_lines.append({
                    'name': ('Release'),
                    'debit': 0.0,
                    'credit': total_paid,
                    'amount_currency': total_currency,
                    # 'currency_id': total_currency and writeoff_currency.id or False,
                    'journal_id': rec.journal_miscellaneous_id.id,
                    'account_id': rec.release_partner_id.property_account_receivable_id.id if rec.realse_unit==False else rec.partner_id.id ,
                    'partner_id': rec.release_partner_id.id if rec.realse_unit==False else rec.partner_id.id,
                    'reservation_id': self.reservation_id.id,

                })
                move_id = account_move.create({
                    'ref': rec.name,
                    'date': fields.Date.today(),
                    'journal_id': self.journal_miscellaneous_id.id,
                    'line_ids':[(0, 0, line) for line in writeoff_lines],
                    'reservation_id': self.reservation_id.id,


                })

                rec.move_id = move_id
                res_reservation = self.env['res.reservation']



                print("lines : > ",lines3)
                if rec.realse_unit == False:
                    rec.reservation_id.write({
                        'state': 'blocked',
                        'date_cancel_unit': datetime.now(),
                        'reason': self.env['cancel.reason.res'].search([('name', '=', 'Change Customer')], limit=1).id,
                    })

                    rec.reservation_id.property_id.write({'state': 'available'})
                else:
                    rec.reservation_id.write({
                        'state': 'blocked',
                        'date_cancel_unit': datetime.now(),
                        'reason': self.env['cancel.reason.res'].search([('name', '=', 'Change Unit')], limit=1).id,
                    })

                res_id = res_reservation.create({
                    'custom_type': 'Reservation',
                    'date': fields.Date.today(),
                    'project_id': rec.reservation_id.project_id.id,
                    'phase_id': rec.reservation_id.phase_id.id,
                    'property_id': rec.reservation_id.property_id.id if rec.realse_unit==False else rec.release_property_id.id,
                    'pay_strategy_id': rec.reservation_id.pay_strategy_id.id,
                    'customer_id': rec.release_partner_id.id if rec.realse_unit==False else rec.partner_id.id,
                    'sale_person_2_id': rec.reservation_id.sale_person_2_id.id,
                    # 'payment_strg_ids': [(0, 0, line) for line in lines],
                    # 'payment_strg_ids': [(6,0,[(0, 0, line) for line in lines])],
                    'is_release': True,
                    'odoo_reservation_id': rec.reservation_id.id,
                    # 'state': rec.reservation_id.state,

                })
                print("[(0, 0, line) for line in lines] : ",[(0, 0, line) for line in lines4])
                res_id.payment_strg_ids = [(0, 0, line) for line in lines4]
                print("res_id :> ",res_id)
                rec.new_reservation_id = res_id.id
                rec.reservation_id.state = 'release'
                rec.state = 'approved'



class ReleaseUnitLine(models.Model):
    _name = 'release.payment.line'
    _description = "Release Unit payment line"

    release_id = fields.Many2one(comodel_name="release.unit", string="", required=False, )
    date = fields.Date(string="Date", required=True,default=fields.Date.today() )

    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted'), ('deliver', 'Deliver'),
                              ('under_coll', 'Under collection'),
                              ('collected', 'Withdrawal'),
                              ('sent', 'Sent'), ('reconciled', 'Reconciled'),
                              ('cancelled', 'Cancelled'),
                              ('discount', 'Discount'),
                              ('loan', 'Loan'),
                              ('refund_from_discount', "Refund From Discount"),
                              ('refunded_from_notes', 'Refund Notes Receivable'),
                              ('refunded_under_collection', 'Refund Under collection'),
                              ('check_refund', 'Refunded')],
                             readonly=True, default='draft', copy=False, string="Status")
    name = fields.Char(string="Number", required=False, )
    journal_id = fields.Many2one(comodel_name="account.journal", string="Journal", required=True,domain=[('type', 'in', ['bank','cash'])],  )
    amount = fields.Float(string="",  required=False, )
    reservation_id = fields.Many2one(comodel_name="res.reservation", string="", required=False,readonly=True )
