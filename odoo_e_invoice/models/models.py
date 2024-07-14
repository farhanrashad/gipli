# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"

    po_ref = fields.Char(string="PO Ref ", )

class AccountEdiFormat(models.Model):
    _inherit = 'account.edi.format'

    # @api.model
    # def _l10n_eg_eta_prepare_eta_invoice(self, invoice):
    #     eta_invoice=super()._l10n_eg_eta_prepare_eta_invoice(invoice)
    #     eta_invoice['purchaseOrderReference']= invoice.po_ref or "",
    #     eta_invoice['salesOrderReference']= invoice.draft_no or "",
    #     eta_invoice['salesOrderDescription']= invoice.name or "",
    #     eta_invoice['proformaInvoiceNumber']= invoice.name or "",
    #     return eta_invoice

    @api.model
    def _l10n_eg_eta_prepare_eta_invoice(self, invoice):

        def group_tax_retention(base_line, tax_values):
            tax = tax_values['tax_repartition_line'].tax_id
            return {'l10n_eg_eta_code': tax.l10n_eg_eta_code.split('_')[0]}

        date_string = invoice.invoice_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        grouped_taxes = invoice._prepare_edi_tax_details(grouping_key_generator=group_tax_retention)
        invoice_line_data, totals = self._l10n_eg_eta_prepare_invoice_lines_data(invoice, grouped_taxes[
            'tax_details_per_record'])
        eta_invoice = {
            'issuer': self._l10n_eg_eta_prepare_address_data(invoice.journal_id.l10n_eg_branch_id, invoice,
                                                             issuer=True, ),
            'receiver': self._l10n_eg_eta_prepare_address_data(invoice.partner_id, invoice),
            'documentType': 'i' if invoice.move_type == 'out_invoice' else 'c' if invoice.move_type == 'out_refund' else 'd' if invoice.move_type == 'in_refund' else '',
            'documentTypeVersion': '1.0',
            'dateTimeIssued': date_string,
            'taxpayerActivityCode': invoice.journal_id.l10n_eg_activity_type_id.code,
            'internalID': invoice.name,
            'salesOrderDescription': invoice.name or "",
            'proformaInvoiceNumber': invoice.name or "",
            # 'purchaseOrderReference':invoice.po_ref if invoice.po_ref else invoice.ref or "",
            # 'salesOrderReference': invoice.external_document_number if invoice.draft_no else invoice.invoice_origin or ""
            'salesOrderReference': invoice.external_document_number or ""
        }
        if invoice.po_ref:
            eta_invoice['purchaseOrderReference'] = invoice.po_ref
        # if invoice.invoice_origin:
        #     eta_invoice['salesOrderReference'] = invoice.invoice_origin
        eta_invoice.update({
            'invoiceLines': invoice_line_data,
            'taxTotals': [{
                'taxType': tax['l10n_eg_eta_code'].split('_')[0].upper(),
                'amount': self._l10n_eg_edi_round(abs(tax['tax_amount'])),
            } for tax in grouped_taxes['tax_details'].values()],
            'totalDiscountAmount': self._l10n_eg_edi_round(totals['discount_total']),
            'totalSalesAmount': self._l10n_eg_edi_round(totals['total_price_subtotal_before_discount']),
            'netAmount': self._l10n_eg_edi_round(abs(invoice.amount_untaxed_signed)),
            'totalAmount': self._l10n_eg_edi_round(abs(invoice.amount_total_signed)),
            'extraDiscountAmount': 0.0,
            'totalItemsDiscountAmount': 0.0,
        })
        _logger.info("eta_invoice ========= :: %s", eta_invoice)
        # if invoice.ref:
        #     eta_invoice['purchaseOrderReference'] = invoice.po_ref or invoice.ref or ""
        # if invoice.invoice_origin:
        #     eta_invoice['salesOrderReference'] = invoice.draft_no or invoice.invoice_origin or ""
        return eta_invoice