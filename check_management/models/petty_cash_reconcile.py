from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime

class PettyCash(models.Model):
    _name='petty.cash.reconcile'
    def get_currency(self):
        return self.env.company.currency_id.id
    name = fields.Char(string='Name',required=True)
    ref = fields.Char(string='Reference',required=True)
    date = fields.Date(string='Accounting Date',required=True)
    journal_id = fields.Many2one(comodel_name='account.journal',string='Journal',required=True)
    move_id = fields.Many2one(comodel_name='account.move',string='Jounral Entry',copy=False)
    amount = fields.Float(string='Amount',required=False)
    converted_amount = fields.Float(string='Converted Amount',compute='_calc_converted_amount',store=True)
    currency_id = fields.Many2one(comodel_name="res.currency", default=get_currency,track_visibility='onchange')
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company,track_visibility='onchange')

    state = fields.Selection(
        string='Status',
        selection=[('draft', 'Draft'),
                   ('canceled', 'Canceled'),
                   ('posted', 'Posted'),
                   ],
        required=False,default='draft' )
    line_ids = fields.One2many(
        comodel_name='petty.cash.line',
        inverse_name='petty_id',
        string='Lines',
        required=False)


    @api.depends('amount','currency_id','date','company_id')
    def _calc_converted_amount(self):
        for rec in self:
            if rec.currency_id.id!=rec.company_id.currency_id.id:
                rec.converted_amount = rec.currency_id._convert(rec.amount, rec.company_id.currency_id, rec.company_id, rec.date or datetime.today())
            else:
                rec.converted_amount=rec.amount

    def posted(self):
        if self.move_id:
            if self.amount != sum(self.line_ids.mapped('amount')):
                raise ValidationError("Unbalanced!")
            self.state = 'posted'
            lines = []
            for line in self.line_ids:
                lines.append((0, 0, {
                    "name": line.name,
                    'currency_id': self.currency_id.id,
                    "partner_id": line.partner_id.id,
                    "debit": line.converted_amount,
                    'amount_currency': line.amount,
                    "credit": 0,
                    "account_id": line.account_id.id,
                    "analytic_distribution": line.analytic_distribution,
                }))
            lines.append(
                (0, 0, {
                    "name": self.name,
                    'currency_id': self.currency_id.id,
                    "debit": 0,
                    'amount_currency': -1*self.amount,
                    "credit": self.converted_amount,
                    "account_id": self.journal_id.default_account_id.id,
                })
            )
            self.move_id.line_ids.unlink()
            self.move_id.write({
                'custom_invoice_date': self.date,
                'date': self.date,
                'ref': self.ref,
                'journal_id': self.journal_id.id,
                'line_ids': lines,
            })

            self.move_id.action_post()

        else:
            if self.amount!=sum(self.line_ids.mapped('amount')):
                raise ValidationError("Unbalanced!")
            self.state = 'posted'
            lines=[]
            for line in self.line_ids:
                lines.append((0,0,{
                    "name": line.name,
                    "partner_id": line.partner_id.id,
                    'currency_id': self.currency_id.id,
                    "debit": line.converted_amount,
                    'amount_currency':  line.amount,
                    "credit": 0,
                    "account_id": line.account_id.id,
                    "analytic_distribution": line.analytic_distribution,
                }))
            lines.append(
                (0, 0, {
                    "name": self.name,
                    'currency_id': self.currency_id.id,
                    "debit": 0,
                    "credit": self.converted_amount,
                    'amount_currency': -1 * self.amount,
                    "account_id": self.journal_id.default_account_id.id,
                })
            )
            print("D>D>D",lines)
            move=self.env['account.move'].create({
                'custom_invoice_date':self.date,
                'date':self.date,
                'ref':self.ref,
                'journal_id':self.journal_id.id,
                'line_ids':lines,
            })
            self.move_id=move.id
            move.action_post()
    def reset(self):
        if self.move_id:
            self.state = 'draft'
            self.move_id.button_draft()
    def cancel(self):
        if self.move_id:
            self.state='canceled'
            self.move_id.button_cancel()

    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('petty.cash.code')
        res = super(PettyCash, self).create(values)
        return res


class PettyCashLine(models.Model):
    _name='petty.cash.line'
    name = fields.Char(string='Label')
    petty_id = fields.Many2one(comodel_name='petty.cash.reconcile')
    partner_id = fields.Many2one(comodel_name='res.partner',string='Partner')
    account_id = fields.Many2one(comodel_name='account.account',string='Account')
    amount = fields.Float(string='Amount')
    converted_amount = fields.Float(string='Converted Amount',compute='_calc_converted_amount',store=True)
    analytic_distribution = fields.Json(
    )  # add the inverse function used to trigger the creation/update of the analytic lines accordingly (field originally defined in the analytic mixin)
    analytic_precision = fields.Integer(
        store=False,
        default=lambda self: self.env['decimal.precision'].precision_get("Percentage Analytic"),
    )

    @api.depends('amount', 'petty_id.currency_id', 'petty_id.date','petty_id.company_id')
    def _calc_converted_amount(self):
        for rec in self:
            if rec.petty_id.currency_id.id != rec.petty_id.company_id.currency_id.id:
                rec.converted_amount = rec.petty_id.currency_id._convert(rec.amount,  rec.petty_id.company_id.currency_id,
                                                                         rec.petty_id.company_id, rec.petty_id.date or datetime.today())
            else:
                rec.converted_amount = rec.amount



