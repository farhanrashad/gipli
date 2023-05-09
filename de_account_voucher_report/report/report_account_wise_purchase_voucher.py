from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import ValidationError, UserError

class ReportAccountWisePurchase(models.AbstractModel):
    _name = 'report.de_account_voucher_report.account_wise_bill_report'
    
    
    @api.model
    def _get_report_values(self, docids, data=None):
        print(data)
        model = self.env.context.get('active_model')
        rec = self.env[model].browse(self.env.context.get('active_id'))
        journal_item_obj=self.env['account.move.line'].search([('account_id','=',rec.account_id.id),('parent_state','=','posted')])
        je_objs= journal_item_obj.mapped('move_id')
        
        
        # emp_recs = self.env['employee.shift.alloc'].search([('date_from','>=',rec.date_from),('date_to','<=',rec.date_to)])
        return {
            'doc_ids' : docids,
             'data' : data,
            'je_objs' : je_objs,
            'account':rec.account_id,
            
            
           
        }