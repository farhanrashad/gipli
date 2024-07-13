# -*- coding: utf-8 -*-

from odoo import fields, models, api,_
from odoo.exceptions import UserError, ValidationError


class NotifyDisc(models.Model):
    _name = 'notify.disc'

    name = fields.Char()
    date = fields.Date(string="التاريخ", store=True)
    serial = fields.Char('مسلسل')
    amount = fields.Float('تم استقطاع مبلغ وقدرة')
    vendor_id = fields.Many2one(comodel_name="res.partner", string="من السادة ", store=True)
    invoice = fields.Many2one(comodel_name="account.move", store=True, string='فاتورة رقم')
    user_id = fields.Many2one(comodel_name="res.users", default=lambda self: self.env.user, store=True)
    national_id = fields.Char(string="بطاقة رقم ", store=True)
    file_no = fields.Char('ملف ضريبي')
    task = fields.Char('مأمورية')
    value = fields.Float('قيمة 1%')
    value2 = fields.Float('قيمة3%')
    value3 = fields.Float('قيمة5%')
    value_deserved = fields.Float('النسبة المستحقة من مبلغ')
    invoice_id = fields.Char('فاتورة رقم')
    responsible = fields.Char('الموظف المسئول')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'notify.disc.seq') or '/'

        return super(NotifyDisc, self).create(vals)

    @api.constrains('invoice')
    def check_invoice(self):
        for rec in self:
            if rec.invoice:
                notify_objs = self.env['notify.disc'].search([('invoice', '=', rec.invoice.id), ('id', '!=', rec.id)], limit=1)
                print('....................', notify_objs)
                if notify_objs:
                    raise ValidationError("You have created a notify discount for this invoice before")





class AccountInvoice(models.Model):
    _inherit = 'account.move'

    def create_notify(self):
        if self.partner_id:
            taxes=0
            tax_id1=0
            tax_id2=0
            tax_id3=0
            if self.tax_totals:
                groups_by_subtotal = self.tax_totals.get('groups_by_subtotal')
                if groups_by_subtotal:
                    values = groups_by_subtotal.get(_('Untaxed Amount'))
                    if values:
                        for value in values:
                            tax_id = self.env['account.tax'].sudo().search(
                                [('tax_group_id', '=', int(value.get('tax_group_id')))], limit=1)
                            if tax_id.amount < 0:
                                if abs(tax_id.amount)==1 :
                                    tax_id1+=abs(value.get('tax_group_amount'))
                                if abs(tax_id.amount)==3 :
                                    tax_id2+=abs(value.get('tax_group_amount'))
                                if abs(tax_id.amount)==5 :
                                    tax_id3+=abs(value.get('tax_group_amount'))
                                taxes+=abs(value.get('tax_group_amount'))
            notify = self.env['notify.disc'].create({
                'date': self.invoice_date,
                'value_deserved': self.amount_untaxed ,
                'amount': taxes,
                'vendor_id': self.partner_id.id,
                'file_no': self.partner_id.vat,
                'invoice': self.id,
                'invoice_id': self.name,
                'value': tax_id1,
                'value2': tax_id2,
                'value3': tax_id3,
                'responsible': self.env.user.name,
            })
            return {
                'name': 'notify discount',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'notify.disc',
                'type': 'ir.actions.act_window',
                'res_id': notify.id,
                'flags': {'initial_mode': 'edit'},
                'target': 'current',
            }

