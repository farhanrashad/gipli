# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_broker = fields.Boolean(_('Broker'))
    organization = fields.Char(_('Organization'))
    nationality = fields.Char(string="Nationality", required=False, )
    id_def = fields.Char(string="National ID", required=False, )
    social_status = fields.Selection(string="Social Status", selection=[('married', 'Married'), ('single', 'Single'), ],
                                     required=False, )
    positon = fields.Char(string="Position", required=False)
    work_side = fields.Char(string="جهة العمل", required=False)
    national_issue_date = fields.Date(string="National Issue Date", required=False)
    national_issue_date_month = fields.Integer()
    national_issue_date_year = fields.Integer()
    is_sales_person = fields.Boolean(string="IS SalesPerson?")
    partner_ttype_id = fields.Many2one(comodel_name="partner.ttype", string="Partner Type", required=False)
    phone = fields.Char(string="Mobile1")
    mobile = fields.Char(string="Mobile2")
    is_customer_char = fields.Char(string="Customer", compute='_calc_is_customer_char', store=True)
    is_supplier_char = fields.Char(string="Supplier", compute='_calc_is_customer_char', store=True)
    c_r = fields.Char(string="C.R")
    acc_manager = fields.Char(string="Account Manager")
    partner_file_no = fields.Char(string='رقم الملف')
    partner_mamoria = fields.Char(string='المأمورية')
    partner_tx_code = fields.Char(string='كود')

    is_customer = fields.Boolean(string='Is a Customer',
                                 help="Check this box if this contact is a customer. It can be selected in sales orders.")
    is_supplier = fields.Boolean(string='Is a Vendor',
                                 help="Check this box if this contact is a vendor. It can be selected in purchase orders.")
    is_salesperson = fields.Boolean(string='Is a SalesPerson',
                                    help="Check this box if this contact is a vendor. It can be selected in purchase orders.")
    national_issue_date = fields.Date(string="National issue date", required=False, )
    is_employee = fields.Boolean(string="Is Employee")
    petty_account = fields.Many2one(comodel_name="account.account", string="سلف", required=False,
                                    company_dependent=True)
    custody_account = fields.Many2one(comodel_name="account.account", string="عهد", required=False,
                                      company_dependent=True)
    accrued_account = fields.Many2one(comodel_name="account.account", string="مصروف رواتب مستحقة", required=False,
                                      company_dependent=True)
    other_account = fields.Many2one(comodel_name="account.account", string="مصروف عمولات مستحقة", required=False,
                                    company_dependent=True)

    is_unit_payments = fields.Boolean(string="دفعات‫ الوحدة")
    is_business_insurance = fields.Boolean(string="تامي‬ن ‫اعمال")
    is_maintenance = fields.Boolean(string="‫صيانة‬")
    is_eoi = fields.Boolean(string="‫‪eoi‬‬")
    engineering_services = fields.Boolean(string="‫خدمات‬‬‬ ‫‫هندسية")
    marketing = fields.Boolean(string="‫‫ماركتنج‬")
    generally = fields.Boolean(string="‫عمومومية‬ ‫وادارية")

    vendor_account_type = fields.Selection(string="Vendor Type",
                                           selection=[('t1', '‫خدمات‬‬‬ ‫‫هندسية‬'),
                                                      ('t2', '‫‫ماركتنج‬ '),
                                                      ('t3', '‫عمومومية‬ ‫وادارية‬ ')], required=False)

    company_team_id = fields.Many2one(
        'company.team', "User's company Team",
        help='Company Team the user is member of. Used to compute the members of a Company Team through the inverse one2many')

    # @api.model
    # def check_access_rights(self, operation, raise_exception=True):
    #     res = super(ResPartner, self).check_access_rights(operation, raise_exception=raise_exception)
    #     if operation == 'create':
    #         if self.env.user.has_group('add_real_estate.group_create_partner') == False:
    #             return False
    #         else:
    #             return res
    #     if operation == 'write':
    #         if self.env.user.has_group('add_real_estate.group_create_partner') == False:
    #             return False
    #         else:
    #             return res
    #     return res

    @api.depends('is_customer', 'is_supplier')
    def _calc_is_customer_char(self):
        for rec in self:
            if rec.is_customer:
                rec.is_customer_char = "Customer"
            else:
                rec.is_customer_char = ""

            if rec.is_supplier:
                rec.is_supplier_char = "Vendor"
            else:
                rec.is_supplier_char = ""

    # @api.constrains('id_def', 'phone', 'mobile')
    # def check_phone(self):
    #     for rec in self:
    #         if rec.phone:
    #             if len(self.env['res.partner'].search(
    #                     [("phone", "=", rec.phone), ('company_id', '=', rec.company_id.id)])) > 1:
    #                 raise ValidationError("Phone Number already exists")
    #         if rec.mobile:
    #             if len(self.env['res.partner'].search(
    #                     [("mobile", "=", rec.mobile), ('company_id', '=', rec.company_id.id)])) > 1:
    #                 raise ValidationError("Mobile Number already exists")
    #         if rec.id_def:
    #             if len(self.env['res.partner'].search(
    #                     [("id_def", "=", rec.id_def), ('company_id', '=', rec.company_id.id)])) > 1:
    #                 raise ValidationError("National ID already exists")


class PartnerType(models.Model):
    _name = 'partner.ttype'
    name = fields.Char(string="Name", required=True)
