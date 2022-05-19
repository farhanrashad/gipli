import json
from odoo.exceptions import UserError
from datetime import datetime
from odoo import api, fields, models, _

class GenerateXLSXReport(models.Model):
    _name = 'report.de_report_general_ledger.general_ledger_xlsx'
    _description = 'General Ledger Report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, linesmodel="ir.actions.report",output_format="xlsx",report_name="de_report_general_ledger.general_ledger_xlsx"):
#         raise UserError(data['gl_account'])
        
        f_date = data['from_date']
        f_date = datetime.strptime(f_date, '%Y-%m-%d')
        f_date = f_date.strftime("%d/%m/%Y")
        
        t_date = data['to_date']
        t_date = datetime.strptime(t_date, '%Y-%m-%d')
        t_date = t_date.strftime("%d/%m/%Y")
        
        date = str(f_date) + " to " + str(t_date)
        
        format0 = workbook.add_format({'font_size': '10', 'align': 'left', 'bold': True,})
        format00 = workbook.add_format({'font_size': '10', 'align': 'center', 'bold': True, 'border':True, 'bg_color': '#ccffff'})
        
        format1 = workbook.add_format({'font_size': '10', 'align': 'center', 'bold': True, 'border':True, 'bg_color': '#ffffcc'})
        
        format2 = workbook.add_format({'font_size': '10', 'align': 'center', 'border':True,})
        format3 = workbook.add_format({'font_size': '10', 'align': 'right', 'num_format':'#,##0.00', 'border':True})
        
        
        move_lines = opening_lines = self.env['account.move.line']
        counter_entries = self.env['account.move']
        counter_account = ''
        
        curr_amount = i_curr_bal = 0
        
        m_date = ''
        partner = project = employee = department = ccenter = ''
        ibal = bal = comp_bal = 0
        domain = domain_state = ''
        acc = company = ''
        if data['state'] == 'draft':
            domain_state = [('parent_state','=','draft')]
        elif data['state'] == 'posted':
            domain_state = [('parent_state','=','posted')]
        else:
            domain_state = [('parent_state','in',['draft','posted'])]
            
        if data['account_ids']:
            account_ids = self.env['account.account'].search([('id', 'in', data['account_ids'])])
            for account in account_ids:
                acc += account.code + ','
                company = account.company_id.name
        
        sheet = workbook.add_worksheet('General Ledger')
        sheet.merge_range(0, 0, 0, 6, ('GENERAL LEDGER - ' + company), format0)
        #sheet.write(1, 0, 'General Ledger Report', format0)
        #sheet.write(3, 0, 'Date', format0)
        #sheet.write(3, 1, date, format0)

        
        sheet.merge_range(2, 0, 2, 1, ('Chart of Account'), format00)
        sheet.write(2, 2, 'Fiscal Year', format00)
        sheet.merge_range(2, 3, 2, 7, ('Periods Filter'), format00)
        sheet.merge_range(2, 8, 2, 9, ('Accounts Filter'), format00)
        sheet.merge_range(2, 10, 2, 11, ('Target Moves'), format00)
        sheet.merge_range(2, 12, 2, 13, ('Initial Balance'), format00)
        
        sheet.merge_range(3, 0, 3, 1, company, format2)
        #sheet.write(2, 2, (f_date.strftime("%Y")), format00)
        sheet.write(3, 2, date[-4:], format2)
        sheet.merge_range(3, 3, 3, 7, date, format2)
        sheet.merge_range(3, 8, 3, 9, acc[:-1], format2)
        if data['state']:
            sheet.merge_range(3, 10, 3, 11, (data['state'] + ' Entries'), format2)
        
        sheet.write(6, 0, 'Date', format1)
        sheet.write(6, 1, 'Period', format1)
        sheet.write(6, 2, 'Entry', format1)
        sheet.write(6, 3, 'Journal', format1)
        sheet.write(6, 4, 'Account', format1)
        sheet.write(6, 5, 'Site', format1)
        sheet.write(6, 6, 'Cost Center', format1)
        sheet.write(6, 7, 'Partner', format1)
        sheet.write(6, 8, 'Label', format1)
        sheet.write(6, 9, 'Counterpart', format1)
        sheet.write(6, 10, 'Employee', format1)
        sheet.write(6, 11, 'Department', format1)
        sheet.write(6, 12, 'Debit', format1)
        sheet.write(6, 13, 'Credit', format1)
        sheet.write(6, 14, 'Balance', format1)
        sheet.write(6, 15, 'Currency', format1)
        sheet.write(6, 16, 'Curr. Amount', format1)
        sheet.write(6, 17, 'Curr. Balance', format1)
        sheet.write(6, 18, 'Doc. Currency', format1)
        
        
        
        row = 7
        
        
            
        if data['account_ids']:
            account_ids = self.env['account.account'].search([('id', 'in', data['account_ids'])])
            for account in account_ids:
                
                sheet.set_column(row, 0, 15,format2)
                sheet.set_column(row, 1, 15,format2)
                sheet.set_column(row, 2, 25,format2)
                sheet.set_column(row, 3, 15,format2)
                sheet.set_column(row, 4, 15,format2)
                sheet.set_column(row, 5, 20,format2)
                sheet.set_column(row, 6, 20,format2)
                sheet.set_column(row, 7, 30,format2)
                sheet.set_column(row, 8, 35,format2)
                sheet.set_column(row, 9, 25,format2)
                sheet.set_column(row, 10, 20,format2)
                sheet.set_column(row, 11, 20,format2)
                sheet.set_column(row, 12, 15,format2)
                sheet.set_column(row, 13, 15,format2)
                sheet.set_column(row, 14, 15,format2)
                sheet.set_column(row, 15, 15,format2)
                sheet.set_column(row, 16, 15,format2)
                sheet.set_column(row, 17, 15,format2)
                sheet.set_column(row, 18, 15,format2)
        
                ibal = bal = comp_bal = 0
                curr_amount = i_curr_bal = curr_bal = 0
                domain = domain_state + [('account_id','=',account.id),('date','<',data['from_date'])]
                opening_lines = self.env['account.move.line'].search(domain)
                for line in opening_lines:
                    ibal = ibal + (line.debit - line.credit)
                    if line.currency_id.id == line.company_id.currency_id.id:
                        i_curr_bal = 0
                    else:
                        i_curr_bal = i_curr_bal + line.amount_currency
                    
                sheet.merge_range(row, 0, row, 4, (account.code + ' - ' + account.name), format0)
                sheet.write(row, 13, 'Initial Balance', format0)
                sheet.write(row, 14, (float(ibal)), format3)
                sheet.write(row, 17, (float(i_curr_bal)), format3)
                
                row = row + 1
                #move_lines = self.env['account.move.line'].search([('account_id','=',account.id),('date','>=',data['from_date']),('date','<=',data['to_date'])])
                domain = domain_state + [('account_id','=',account.id),('date','>=',data['from_date']),('date','<=',data['to_date'])]
                move_lines = self.env['account.move.line'].search(domain,order="date asc")
                
                bal = ibal
                curr_bal = i_curr_bal
                for line in move_lines:
                    m_date = str(line.date)
                    m_date = datetime.strptime(m_date, '%Y-%m-%d')
                    m_date = m_date.strftime("%d/%m/%Y")
                    bal = bal + (line.debit - line.credit)
                    
                    counter_entries = self.env['account.move.line'].search([('move_id','=',line.move_id.id)])
                    counter_account = ''
                    for cline in counter_entries.filtered(lambda x: x.account_id.id != line.account_id.id):
                        counter_account += cline.account_id.code + ', '
                        
                    if line.currency_id.id == line.company_id.currency_id.id:
                        curr_amount = 0
                    else:
                        curr_amount = line.amount_currency
                        curr_bal = curr_bal + line.amount_currency
                        
                    sheet.write(row, 0, m_date, format2)
                    sheet.write(row, 1, line.account_period, format2)
                    sheet.write(row, 2, line.move_id.name, format2)
                    sheet.write(row, 3, line.journal_id.name, format2)
                    sheet.write(row, 4, line.account_id.code, format2)
                    if line.project_id.id:
                        sheet.write(row, 5, line.project_id.name, format2)
                    if line.analytic_account_id.id:
                        sheet.write(row, 6, line.analytic_account_id.name, format2)
                    if line.partner_id.id:
                        sheet.write(row, 7, line.partner_id.name, format2)
                    sheet.write(row, 8, line.name, format2)
                    sheet.write(row, 9, counter_account[:-2], format2)
                    #if line.ref:
                    #    sheet.write(row, 4, line.ref, format2)
                    
                    if line.employee_id.id:
                        sheet.write(row, 10, line.employee_id.name, format2)
                    if line.department_id.id:
                        sheet.write(row, 11, line.department_id.name, format2)
                    
                    #sheet.write(row, 12, ('{:,}'.format(line.debit)), format2)
                    sheet.write(row, 12, float(line.debit), format3)
                    sheet.write(row, 13, float(line.credit), format3)
                    sheet.write(row, 14, (float(bal)), format3)
                    sheet.write(row, 15, line.company_id.currency_id.name, format2)
                    sheet.write(row, 16, (float(curr_amount)), format3)
                    sheet.write(row, 17, (float(curr_bal)), format3)
                    if line.currency_id.id != line.company_id.currency_id.id:
                        sheet.write(row, 18, line.currency_id.name, format2)
                    row = row + 1
                row = row + 1
            
