# -*- coding: utf-8 -*-

from __future__ import print_function

import xmlrpc.client

from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError

import base64



import sys
import requests
import json
import logging
import time




class AccountMove(models.Model):
    _inherit = "account.move"

    einvoice_activity_ids = fields.Many2many(related='company_id.einvoice_activity_ids')
    einvoice_branch_ids = fields.Many2many('res.partner',compute='_compute_einvoice_branch_ids')
    einvoice_activity_type_id = fields.Many2one('einvoice.activity.type','E-invoice Activity Type', copy=False)
    einvoice_branch_id = fields.Many2one('res.partner','E-invoice Branch')
    einvoice_sent = fields.Boolean('Invoice Sent To ETA', copy=False)
    einvoice_submission_id = fields.Char('Submission ID', copy=False)
    einvoice_uuid = fields.Char('UUID', copy=False)
    einvoice_long_id = fields.Char('Long ID', copy=False)
    einvoice_hash_key = fields.Char('Hash Key', copy=False)
    einvoice_pdf = fields.Binary(string='E-invoice PDF', copy=False)
    einvoice_state = fields.Selection([
                              ('Not Set Yet', 'Not Set Yet'),
                              ('Submitted', 'Submitted'),
                              ('Valid', 'Valid'),
                              ('Invalid', 'Invalid'),
                              ('Rejected', 'Rejected'),
                              ('Cancelled', 'Cancelled')], default='Not Set Yet' , string='E-invoice Status', copy=False, tracking=True)
    is_signed = fields.Boolean('Document Signed', copy=False)
    e_signature = fields.Text('Electronic Signature', copy=False)
    note_origin_id = fields.Many2one('account.move')

    @api.depends('company_id')
    def _compute_einvoice_branch_ids(self):
        for rec in self:
            rec.einvoice_branch_ids = self.env['res.partner'].search(['|',('id','=',rec.company_id.partner_id.id),('parent_id','=',rec.company_id.partner_id.id)]).ids


    def get_token(self):
        auth_server_url = "https://id.eta.gov.eg/connect/token"
        environment = self.env['ir.config_parameter'].sudo().get_param('egypt_e_invoice.environment')
        if environment == 'Pre Production':
            auth_server_url = "https://id.preprod.eta.gov.eg/connect/token"

        client_id = self.env['ir.config_parameter'].sudo().get_param('egypt_e_invoice.client_id')
        client_secret = self.env['ir.config_parameter'].sudo().get_param('egypt_e_invoice.client_pass')
        token_req_payload = {'grant_type': 'client_credentials'}

        token_response = requests.post(auth_server_url,
                                       data=token_req_payload, verify=False, allow_redirects=False,
                                       auth=(client_id, client_secret))
        if token_response.status_code != 200:
            raise ValidationError("Failed to obtain token from the OAuth 2.0 server", file=sys.stderr)

        tokens = json.loads(token_response.text)
        return tokens['access_token']

    def check_requirements(self):
        self.ensure_one()
        if not self.company_id.vat:
            raise ValidationError('You must fill field ( Company Registry ) in company profile with Registration number that you registered with in Einvoice portal')
        if not self.einvoice_branch_id:
            raise ValidationError('You must select E-invoice branch in invoice ( %s )' %( self.name ) )
        if not self.einvoice_branch_id.einvoice_branch_number:
            raise ValidationError('You selected E-invoice branch ( %s ) in invoice ( %s ) and this branch has no value in field (E-invoice Branch Number)' %( self.einvoice_branch_id.name,self.name ) )
        if not self.einvoice_branch_id.state_id or not self.einvoice_branch_id.city or not self.einvoice_branch_id.street :
            raise ValidationError('You selected E-invoice branch ( %s ) in invoice ( %s ) please make sure to fill the full address for following fields (State - city - street - street2 as building number)' %( self.einvoice_branch_id.name,self.name ) )
        if not self.partner_id:
            raise ValidationError('For invoice ( %s ) you must select partner' %( self.name ))
        if not self.partner_id.einvoice_partner_type or (self.partner_id.einvoice_partner_type == 'B' and not self.partner_id.einvoice_partner_number) or (self.partner_id.einvoice_partner_type == 'P' and not self.partner_id.einvoice_partner_number and self.amount_total > 50000):
            raise ValidationError('For invoice ( %s ) you must select (Receiver Type) and (Receiver Number) in partner' %( self.name ))
        if not self.partner_id.state_id or not self.partner_id.city or not self.partner_id.street :
            raise ValidationError('You selected Partner ( %s ) in invoice ( %s ) please make sure to fill the full address for following fields (State - city - street - street2 as building number)' %( self.partner_id.name,self.name ) )
        if not self.einvoice_activity_type_id:
            raise ValidationError('For invoice ( %s ) you must select (E-invoice Activity Type)' % (self.name))
        if not self.state == 'posted':
            raise ValidationError('All Invoices must be posted before being sent to E-invoice Portal' )
        if not self.invoice_line_ids:
            raise ValidationError('For invoice ( %s ) you must select at least one line' % (self.name))
        for line in self.invoice_line_ids:
            if not line.product_id:
                raise ValidationError('For invoice ( %s ) you must select product in all lines' % (self.name))
            if not line.product_id.einvoice_code_type or not line.product_id.einvoice_code:
                raise ValidationError('product ( %s ) must have (E-invoice Code Type) and (E-invoice Code) ' % (line.product_id.name))
            if line.product_uom_id and not line.product_uom_id.einvoice_uom_id:
                raise ValidationError('UOM ( %s ) must have (E-invoice UOM ) ' % (line.product_uom_id.name))
            for tax_id in line.tax_ids:
                if not tax_id.einvoice_tax_type_id or not tax_id.einvoice_tax_subtype_id:
                    raise ValidationError('Tax ( %s ) must have (E-invoice Tax Type	) and ( E-invoice Tax Subtype )  ' % (tax_id.name))

    def get_invoice_dics_cron(self,start_date=False):
        domain = [('move_type', 'in', ['out_invoice','out_refund','in_refund']),('state','=','posted'),('is_signed','=',False)]
        if start_date:
            domain.append(('invoice_date','>=',start_date))
        invoices = self.env['account.move'].search(domain)
        invoice_dics = []
        for invoice in invoices:
            try:
                invoice_dics.append(invoice.get_invoice_dic())
            except:
                continue

        return invoice_dics

    def sign_invoices(self, signed_invoices=False):
        for signed_invoice in signed_invoices:
            # invoice = self.env['account.move'].browse(int(signed_invoice['internalID']))
            invoice = self.env['account.move'].search([('name','=',signed_invoice['internalID'])])
            invoice.e_signature = signed_invoice['sign']
            invoice.is_signed = True
        return {}

    def get_invoice_dic(self):
        self.ensure_one()
        self.check_requirements()
        references = []
        if self.move_type == 'out_invoice':
            invoice_type = 'I'
        elif self.move_type == 'out_refund':
            invoice_type = 'C'
            if self.note_origin_id and self.note_origin_id.einvoice_uuid:
                references.append(self.note_origin_id.einvoice_uuid)
        elif self.move_type == 'in_refund':
            invoice_type = 'D'
            if self.note_origin_id and self.note_origin_id.einvoice_uuid:
                references.append(self.note_origin_id.einvoice_uuid)
        else:
            raise ValidationError('Vendor Bill Can not be sent to E-invoice System')
        e_invoice_version = self.env['ir.config_parameter'].sudo().get_param('egypt_e_invoice.version')

        invoice_lines = []
        inv_discount = 0
        inv_sales_total = 0
        inv_net_total = 0
        inv_taxes = {}
        for line in self.invoice_line_ids:
            # for multi currency
            price = round(line.price_unit, 5)
            sales_total = round(line.quantity * price, 5)
            inv_sales_total += sales_total
            discount_amount = round(line.discount * sales_total / 100, 5)
            inv_discount += discount_amount
            net_total = sales_total - discount_amount
            inv_net_total += net_total
            taxes = []
            totalTaxableFees = 0.0
            amount_to_tax = net_total
            for tax_id in line.tax_ids.sorted(key=lambda r: r.sequence):
                current_tax_amount = round(amount_to_tax * tax_id.amount / 100,5)
                taxes.append({
                    "taxType": tax_id.einvoice_tax_type_id.code,
                    "amount": abs(current_tax_amount),
                    "subType": tax_id.einvoice_tax_subtype_id.code,
                    "rate": abs(tax_id.amount)})
                if tax_id.einvoice_tax_type_id.code in inv_taxes.keys():
                    inv_taxes[tax_id.einvoice_tax_type_id.code] += current_tax_amount
                else:
                    inv_taxes[tax_id.einvoice_tax_type_id.code] = current_tax_amount
                if tax_id.include_base_amount:
                    amount_to_tax += current_tax_amount

            totalTaxableFees = round(sum(t['amount'] for t in taxes), 5)
            total = round(net_total + totalTaxableFees, 5)
            currency_rate = self.currency_id._get_rates(self.company_id, self.invoice_date)[self.currency_id.id]
            eg_currency = self.env.ref('base.EGP')
            if eg_currency != self.currency_id:
                unit_value = {
                    "currencySold": self.currency_id.name,
                    "currencyExchangeRate": round(currency_rate, 5),
                    "amountSold": line.price_unit,
                    "amountEGP": self.currency_id._convert(line.price_unit, eg_currency,
                                                           self.company_id, self.invoice_date)
                }
            else:
                unit_value = {
                    "currencySold": "EGP",
                    "amountEGP": line.price_unit
                }

            if line.product_id.einvoice_code_type == 'GS1':
                product_code = line.product_id.einvoice_code
            else:
                product_code = 'EG-' + self.company_id.vat + '-' + line.product_id.einvoice_code
            invoice_lines.append({
                "description": line.product_id.name,
                "itemType": line.product_id.einvoice_code_type,
                "itemCode": product_code,
                "unitType": line.product_uom_id and line.product_uom_id.einvoice_uom_id.code or "EA",
                "quantity": line.quantity,
                "internalCode": str(line.product_id.id),
                "salesTotal": sales_total,
                # "total": total,
                "total": round(line.price_total, 5),
                "valueDifference": 0.0,
                "totalTaxableFees": 0,
                "netTotal": round(net_total, 5),
                # "netTotal": round(line.price_total, 5),
                "itemsDiscount": 0.00,
                "unitValue": unit_value,
                "discount": {
                    "rate": line.discount,
                    "amount": discount_amount
                },
                "taxableItems": taxes
            })
        taxTotals = []
        for key, value in inv_taxes.items():
            taxTotals.append({
                "taxType": key,
                "amount": abs(round(value,5))
            })
        receiver = {
            "address": {
                "country": self.partner_id.country_id.code,
                "governate": self.partner_id.state_id.name,
                "regionCity": self.partner_id.city,
                "street": self.partner_id.street,
                "buildingNumber": self.partner_id.street2 and self.partner_id.street2 or '1',
                "postalCode": self.partner_id.zip and self.partner_id.zip or '',
            },
            "type": self.partner_id.einvoice_partner_type,
            "name": self.partner_id.name
        }
        if self.partner_id.einvoice_partner_number:
            receiver['id'] = self.partner_id.einvoice_partner_number

        inter_id = str(self.name).split("/")[-1]
        print("@@@@@@@@@",inter_id)


        invoice_dic = {
            "issuer": {
                "address": {
                    "branchID": self.einvoice_branch_id.einvoice_branch_number,
                    "country": "EG",
                    "governate": self.einvoice_branch_id.state_id.name,
                    "regionCity": self.einvoice_branch_id.city,
                    "street": self.einvoice_branch_id.street,
                    "buildingNumber": self.einvoice_branch_id.street2 and self.einvoice_branch_id.street2 or '1',
                    "postalCode": self.einvoice_branch_id.zip and self.einvoice_branch_id.zip or '',
                },
                "type": "B",
                "id": self.company_id.vat,
                "name": self.company_id.name
            },
            "receiver": receiver,
            "documentType": invoice_type,
            "documentTypeVersion": e_invoice_version and e_invoice_version or"1.0",
            "dateTimeIssued": self.invoice_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
            "taxpayerActivityCode": self.einvoice_activity_type_id.code,
            # "internalID": str(self.id),
            # "internalID": str(inter_id),
            # "internalID": str(inter_id),

            "internalID": str(self.name) or "",

            "purchaseOrderReference":  "",
            "purchaseOrderDescription": "",
            # "salesOrderReference": "",
            "salesOrderReference": self.name or "",
            # "salesOrderDescription": "",
            "salesOrderDescription": self.name or "",
            # "proformaInvoiceNumber": "SomeValue",
            # "proformaInvoiceNumber": str(self.id),
            "proformaInvoiceNumber": str(self.name) or "",
            "references": references,
            "payment": {
                "bankName": "SomeValue",
                "bankAddress": "SomeValue",
                "bankAccountNo": "SomeValue",
                "bankAccountIBAN": "",
                "swiftCode": "",
                "terms": "SomeValue"
            },
            "delivery": {
                "approach": "SomeValue",
                "packaging": "SomeValue",
                "dateValidity": "",
                "exportPort": "SomeValue",
                "grossWeight": 10.50,
                "netWeight": 20.50,
                "terms": "SomeValue"
            },

            "invoiceLines": invoice_lines,
            "totalDiscountAmount": round(inv_discount, 5),
            "totalSalesAmount": round(inv_sales_total, 5),
            "netAmount": round(inv_net_total, 5),
            "taxTotals": taxTotals,
            "totalAmount": round(self.amount_total, 5),
            "extraDiscountAmount": 0.00,
            # "extraDiscountAmount":round(self.ks_amount_discount, 5),

            "totalItemsDiscountAmount": 0.00,

        }
        return invoice_dic



    def send_to_e_invoice(self):
        token = self.get_token()
        # //////////////////////////////////////////////////////////////////////////////////////////

        api_url = 'https://api.invoicing.eta.gov.eg/api/v1.0/documentsubmissions'

        environment = self.env['ir.config_parameter'].sudo().get_param('egypt_e_invoice.environment')
        if environment == 'Pre Production':
            api_url = 'https://api.preprod.invoicing.eta.gov.eg/api/v1.0/documentsubmissions'

        # print(token)
        api_call_headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + token,
            'Content-type': 'application/json',
            }

        invoice_dics = []
        for inv in self:
            # ////////////////////////////////////////////////////////////////////////
            invoice_dic = inv.get_invoice_dic()
            print("D>D>D",invoice_dic)
            e_invoice_version = self.env['ir.config_parameter'].sudo().get_param('egypt_e_invoice.version')
            if not e_invoice_version or e_invoice_version == '1.0':
                invoice_dic["signatures"] = [
                    {
                        "signatureType": "I",
                        "value": inv.get_sign()
                    }
                ]
            invoice_dics.append(invoice_dic)
            # ////////////////////////////////////////////////////////////////////////
        data = {"documents": invoice_dics}
        data = json.dumps(data, ensure_ascii=False).encode('utf8')

        try:
            api_call_response = requests.post(api_url, data =data, headers=api_call_headers, verify=False)
            submission = api_call_response.json()
            if api_call_response.status_code not in [200,202]:
                raise ValidationError(submission.get('error'))
            for acceptedDocument in submission.get('acceptedDocuments'):
                # acceptedDocument_id = self.env['account.move'].browse(int(acceptedDocument.get('internalId')))
                acceptedDocument_id = self.env['account.move'].search([('name','=',acceptedDocument.get('internalId'))])
                acceptedDocument_id.einvoice_sent = True
                acceptedDocument_id.einvoice_submission_id = submission.get('submissionId')
                acceptedDocument_id.einvoice_uuid = acceptedDocument.get('uuid')
                acceptedDocument_id.einvoice_long_id = acceptedDocument.get('longId')
                acceptedDocument_id.einvoice_hash_key = acceptedDocument.get('hashKey')
                acceptedDocument_id.einvoice_state = 'Submitted'
                # acceptedDocument_id.update_e_invoice_status()
                # acceptedDocument_id.get_e_invoice_pdf(acceptedDocument.get('uuid'),api_call_headers)
            for rejectedDocument in submission.get('rejectedDocuments'):
                # rejectedDocument_id = self.env['account.move'].browse(int(rejectedDocument.get('internalId')))
                rejectedDocument_id = self.env['account.move'].search([('name','=',rejectedDocument.get('internalId'))])
                reject_error = rejectedDocument.get('error').get('message')+ 'in invoice with ID : '+ str(rejectedDocument_id.id)+ '\n'
                for detail in rejectedDocument.get('error').get('details'):
                    reject_error += 'Target :' + detail.get('target') + '\n'
                    reject_error += 'Message :' + detail.get('message') + '\n'
                    reject_error += 'Path :' + detail.get('propertyPath') + '\n'
                    reject_error += '=========================================== \n'
                msg = "Error Where Sending Invoice To ETA \n"
                rejectedDocument_id.message_post(body=msg)
                rejectedDocument_id.message_post(body=reject_error)
        except Exception as error:
            raise ValidationError(error)

        for inv in self:
            inv.update_e_invoice_status()

    def get_e_invoice_pdf(self):
        token = self.get_token()
        environment = self.env['ir.config_parameter'].sudo().get_param('egypt_e_invoice.environment')
        api_call_headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + token,
            'Content-type': 'application/json',
        }
        for rec in self:
            if not rec.einvoice_sent:
                raise ValidationError('Document not sent yet')
            if rec.einvoice_state not in ['Valid', 'Rejected','Cancelled']:
                raise ValidationError('you can get pdf for documents in [Valid, Rejected,Cancelled] states only')
            if not rec.einvoice_uuid:
                raise ValidationError('UUID is empty')

            get_document_url = 'https://api.invoicing.eta.gov.eg/api/v1.0/documents/' + rec.einvoice_uuid + '/pdf'
            if environment == 'Pre Production':
                get_document_url = 'https://api.preprod.invoicing.eta.gov.eg/api/v1.0/documents/' + rec.einvoice_uuid + '/pdf'
            try:
                einvoice_response = requests.get(get_document_url, headers=api_call_headers, verify=False)
                if einvoice_response.status_code == 400:
                    error_msg = 'file NotReady'
                    rec.message_post(body=error_msg)
                if einvoice_response.status_code == 404:
                    error_msg = 'file Not Found'
                    rec.message_post(body=error_msg)

                if einvoice_response.status_code == 200:
                    rec.einvoice_pdf = rec.einvoice_pdf = base64.b64encode(einvoice_response.content)

            except Exception as error:
                rec.message_post(body=error)

    def update_e_invoice_status(self):
        token = self.get_token()
        environment = self.env['ir.config_parameter'].sudo().get_param('egypt_e_invoice.environment')
        api_call_headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + token,
            'Content-type': 'application/json',
        }
        for rec in self:
            if rec.einvoice_sent and rec.einvoice_uuid:
                get_document_url = 'https://api.invoicing.eta.gov.eg/api/v1.0/documents/' + rec.einvoice_uuid + '/raw'
                if environment == 'Pre Production':
                    get_document_url = 'https://api.preprod.invoicing.eta.gov.eg/api/v1.0/documents/' + rec.einvoice_uuid + '/raw'
                try:
                    einvoice_response = requests.get(get_document_url, headers=api_call_headers, verify=False)
                    e_invoice_document = einvoice_response.json()
                    if einvoice_response.status_code != 200:
                        error_msg = 'Error in update status for this document : ' + e_invoice_document.get('error')
                        rec.message_post(body=error_msg)
                    rec.einvoice_state = e_invoice_document.get('status')

                except Exception as error:
                    rec.message_post(body=error)

    def get_sign(self):
        signature_type = self.env['ir.config_parameter'].sudo().get_param('egypt_e_invoice.signature_type')
        if not signature_type:
            raise ValidationError('Please Select Signature Type in configurations')

        if signature_type == 'Middleware':
            if not self.is_signed or not self.e_signature:
                raise ValidationError('You can not send invoice ( %s ) because is needs to be signed first' %( self.name ))
            return self.e_signature
        if signature_type == 'Middleware With Accessable IP':
            url = self.env['ir.config_parameter'].sudo().get_param('egypt_e_invoice.middleware_url')
            db = self.env['ir.config_parameter'].sudo().get_param('egypt_e_invoice.middleware_database')
            username = self.env['ir.config_parameter'].sudo().get_param('egypt_e_invoice.middleware_user')
            password = self.env['ir.config_parameter'].sudo().get_param('egypt_e_invoice.middleware_pass')
            if not (url and db and username and password):
                raise ValidationError('Please Make sure to insert Middleware Configurations')
            common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
            # common.version()
            uid = common.authenticate(db, username, password, {})
            models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
            sign = models.execute_kw(db, uid, password,
                                         'invoice.signer', 'get_sign', [[], self.get_invoice_dic()])
            return sign
        if signature_type == 'Same Server':
            return 'dddddddd'


class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"

    def _prepare_default_reversal(self, move):
        res = super(AccountMoveReversal, self)._prepare_default_reversal(move)
        res['note_origin_id'] = move.id
        return res
