from odoo import api,fields,models,_
import logging
_logger = logging.getLogger(__name__)



class deSalesTaxInvoiceReport(models.AbstractModel):
    _name = 'report.de_sale_invoice_report.report_sale_invoices'
                    
     
    @api.model
    def _get_report_values(self, docids, data=None):
        try:
            acct_invoice = self.env["account.move"].search([("id","in",docids)])
            if acct_invoice.seq_name:
                voucher_no = acct_invoice.seq_name.split('/')[0]+'/'+acct_invoice.seq_name.split('/')[2]
#              model = self.env.context.get('active_model')
#              docs = self.env[model].browse(self.env.context.get('active_id'))

            return {
                'account':acct_invoice,
                'voucher':voucher_no

                }
         
        except Exception as e:
            _logger.exception(e)
            print(e)