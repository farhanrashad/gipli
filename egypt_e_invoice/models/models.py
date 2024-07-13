# -*- coding: utf-8 -*-

from odoo import fields, models, api


class EinvoiceUom(models.Model):
    _name = "einvoice.uom"

    name = fields.Char('Name')
    name_ar = fields.Char('Arabic Name')
    code = fields.Char('Code')


class EinvoiceActivityType(models.Model):
    _name = "einvoice.activity.type"

    name = fields.Char('Name')
    name_ar = fields.Char('Arabic Name')
    code = fields.Char('Code')



class EinvoiceTaxType(models.Model):
    _name = "einvoice.tax.type"

    name = fields.Char('Name')
    name_ar = fields.Char('Arabic Name')
    code = fields.Char('Code')
    subtype_ids = fields.One2many('einvoice.tax.subtype','einvoice_tax_type_id','Subtypes')



class EinvoiceTaxSubtype(models.Model):
    _name = "einvoice.tax.subtype"

    name = fields.Char('Name')
    name_ar = fields.Char('Arabic Name')
    code = fields.Char('Code')
    einvoice_tax_type_id = fields.Many2one('einvoice.tax.type',"Tax Type")



class Uom(models.Model):
    _inherit = "uom.uom"

    einvoice_uom_id = fields.Many2one('einvoice.uom','E-invoice UOM')


class AccountTax(models.Model):
    _inherit = "account.tax"

    einvoice_tax_type_id = fields.Many2one('einvoice.tax.type',"E-invoice Tax Type")
    einvoice_tax_subtype_id = fields.Many2one('einvoice.tax.subtype',"E-invoice Tax Subtype")


class ResCompany(models.Model):
    _inherit = "res.company"

    einvoice_activity_ids = fields.Many2many('einvoice.activity.type',
        "einvoice_company_activities",
        "company_id",
        "activity_id",
        string="E-invoice Activity Types",
    )


class ResPartner(models.Model):
    _inherit = "res.partner"

    einvoice_branch_number = fields.Char(string="E-invoice Branch Number")
    einvoice_partner_type = fields.Selection([
        ('B', 'Business in Egypt'),
        ('P', 'Natural Person'),
        ('F', 'Foreigner')],'Receiver Type')
    einvoice_partner_number = fields.Char('Receiver Number',help='Registration number. For business in Egypt must be registration number. For residents must be national ID. For foreign buyers must be VAT ID of the foreign company.')


class ProductTemplate(models.Model):
    _inherit = "product.template"

    einvoice_code_type = fields.Selection([
        ('GS1', 'GS1'),
        ('EGS', 'EGS'),],string="E-invoice Code Type")
    einvoice_code = fields.Char(string="E-invoice Code")