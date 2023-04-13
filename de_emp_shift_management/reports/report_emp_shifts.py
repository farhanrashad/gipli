from odoo import models, fields, api,_
from datetime import datetime
from odoo.exceptions import ValidationError, UserError

class ReportEmpShiftPdf(models.AbstractModel):
    _name = 'report.de_emp_shift_management.employee_shift_report_pdf'
    
    
    @api.model
    def _get_report_values(self, docids, data=None):
        print(data)
        model = self.env.context.get('active_model')
        rec = self.env[model].browse(self.env.context.get('active_id'))
        emp_recs = self.env['employee.shift.alloc'].search([('date_from','>=',rec.date_from),('date_to','<=',rec.date_to)])
        return {
            'doc_ids' : docids,
             'data' : data,
            'emp_recs' : emp_recs,
           
        }