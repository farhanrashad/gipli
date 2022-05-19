import json
from odoo.exceptions import UserError
from datetime import datetime
from odoo import api, fields, models, _

class GenerateXLSXReport(models.Model):
    _name = 'report.de_report_partner_ledger.partner_ledger_xlsx'
    _description = 'Partner Ledger Report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, linesmodel="ir.actions.report",output_format="xlsx",report_name="de_report_partner_ledger.partner_ledger_xlsx"):
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
        
        formata = workbook.add_format({'font_size': '14', 'align': 'left', 'bold': True, 'border':True, 'bg_color': '#ffffcc'})
        
        format2 = workbook.add_format({'font_size': '10', 'align': 'center', 'border':True,})
        format3 = workbook.add_format({'font_size': '10', 'align': 'right', 'num_format':'#,##0.00', 'border':True})
        
        formatih = workbook.add_format({'font_size': '10', 'align': 'left', 'border':True, 'italic':True})
        formati = workbook.add_format({'font_size': '10', 'align': 'right', 'num_format':'#,##0.00', 'border':True, 'italic':True})
        
        formatf1 = workbook.add_format({'font_size': '12', 'align': 'center', 'bold': True, 'border':True, 'bg_color': '#ffffcc'})
        formatf2 = workbook.add_format({'font_size': '12', 'align': 'right', 'bold': True, 'border':True, 'bg_color': '#ffffcc','num_format':'#,##0.00'})
        
        move_lines = opening_lines = self.env['account.move.line']
        
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
            
        if data['partner_ids']:
            partner_ids = self.env['res.partner'].search([('id', 'in', data['partner_ids'])])
            for partner in partner_ids:
                acc += str(partner.ref) + ','
                company = '' #account.company_id.name
        
        sheet = workbook.add_worksheet('Partner Ledger')
        sheet.merge_range(0, 0, 0, 6, ('Partner LEDGER - ' + company), format0)
        

        
        sheet.merge_range(2, 0, 2, 1, ('Chart of Account'), format00)
        sheet.write(2, 2, 'Fiscal Year', format00)
        sheet.merge_range(2, 3, 2, 5, ('Periods Filter'), format00)
        sheet.merge_range(2, 6, 2, 7, ('Accounts Filter'), format00)
        sheet.merge_range(2, 8, 2, 9, ('Target Moves'), format00)
        sheet.merge_range(2, 10, 2, 11, ('Initial Balance'), format00)
        
        sheet.merge_range(3, 0, 3, 1, company, format2)
        #sheet.write(2, 2, (f_date.strftime("%Y")), format00)
        sheet.write(3, 2, date[-4:], format2)
        sheet.merge_range(3, 3, 3, 7, date, format2)
        sheet.merge_range(3, 8, 3, 9, acc[:-1], format2)
        if data['state']:
            sheet.merge_range(3, 10, 3, 11, (data['state'] + ' Entries'), format2)
        
        row = 5
        
        account_ids = self.env['account.account'].search([('internal_type','in',['receivable','payable'])])
        
        for account in account_ids:
            sheet.merge_range(row, 0, row, 11, (str(account.code) + ' - ' + account.name), formata)
            row = row + 1
            
            ibal = idebitbal = icreditbal = bal = comp_bal = 0
            curr_amount = i_curr_bal = curr_bal = 0
            acml_bal = acml_debit = acml_credit = 0
            
            if data['partner_ids']:
                partner_ids = self.env['res.partner'].search([('id', 'in', data['partner_ids'])])
                for partner in partner_ids:
                    sheet.merge_range(row, 0, row, 4, (str(partner.ref) + ' - ' + partner.name), format0)
                    row = row + 1
                    
                    sheet.write(row, 0, 'Date', format1)
                    sheet.write(row, 1, 'Period', format1)
                    sheet.write(row, 2, 'Entry', format1)
                    sheet.write(row, 3, 'Journal', format1)
                    sheet.write(row, 4, 'Partner', format1)
                    sheet.write(row, 5, 'Label', format1)
                    sheet.write(row, 6, 'Rec.', format1)
                    sheet.write(row, 7, 'Debit', format1)
                    sheet.write(row, 8, 'Credit', format1)
                    sheet.write(row, 9, 'Accum. Bal.', format1)
                    sheet.write(row, 10, 'Currency Bal.', format1)
                    sheet.write(row, 11, 'Currency', format1)
        
                    sheet.set_column(row, 0, 15,format2)
                    sheet.set_column(row, 1, 15,format2)
                    sheet.set_column(row, 2, 25,format2)
                    sheet.set_column(row, 3, 20,format2)
                    sheet.set_column(row, 4, 25,format2)
                    sheet.set_column(row, 5, 35,format2)
                    sheet.set_column(row, 6, 15,format2)
                    sheet.set_column(row, 7, 15,format2)
                    sheet.set_column(row, 8, 15,format2)
                    sheet.set_column(row, 9, 15,format2)
                    sheet.set_column(row, 10, 15,format2)
                    sheet.set_column(row, 11, 15,format2)
                    
                    row = row + 1                 
                    
                    domain = domain_state + [('partner_id','=',partner.id),('account_id','=',account.id),('date','<',data['from_date'])]
                    opening_lines = self.env['account.move.line'].search(domain)
                    for line in opening_lines:
                        ibal = ibal + (line.debit - line.credit)
                        idebitbal = idebitbal + line.debit
                        icreditbal = icreditbal + line.credit
                    
                    sheet.write(row, 5, 'Initial Balance', formatih)
                    sheet.write(row, 7, (float(idebitbal)), formati)
                    sheet.write(row, 8, (float(icreditbal)), formati)
                    sheet.write(row, 9, (float(ibal)), formati)
                    row = row + 1
                    
                    
                    domain = domain_state + [('partner_id','=',partner.id),('account_id','=',account.id),('date','>=',data['from_date']),('date','<=',data['to_date'])]
                    move_lines = self.env['account.move.line'].search(domain,order="date asc")
                
                    bal = ibal
                    curr_bal = i_curr_bal
                    acml_bal = ibal
                    acml_debit = idebitbal
                    acml_credit = icreditbal
                    for line in move_lines:
                        m_date = str(line.date)
                        m_date = datetime.strptime(m_date, '%Y-%m-%d')
                        m_date = m_date.strftime("%d/%m/%Y")
                        bal = bal + (line.debit - line.credit)
                        
                        if line.currency_id.id == line.company_id.currency_id.id:
                            curr_amount = 0
                        else:
                            curr_amount = line.amount_currency
                            curr_bal = curr_bal + line.amount_currency
                        
                        acml_debit += line.debit
                        acml_credit += line.credit
                        acml_bal = acml_bal + (line.debit - line.credit)
                        
                        sheet.write(row, 0, m_date, format2)
                        sheet.write(row, 1, line.account_period, format2)
                        sheet.write(row, 2, line.move_id.name, format2)
                        sheet.write(row, 3, line.journal_id.name, format2)                    
                        if line.partner_id.id:
                            sheet.write(row, 4, line.partner_id.name, format2)
                        sheet.write(row, 5, line.name, format2)
                        if line.full_reconcile_id:
                            sheet.write(row, 6, line.full_reconcile_id.name, format2)
                        sheet.write(row, 7, float(line.debit), format3)
                        sheet.write(row, 8, float(line.credit), format3)
                        sheet.write(row, 9, (float(bal)), format3)
                        #sheet.write(row, 10, (float(curr_amount)), format3)
                        #sheet.write(row, 10, (float(curr_bal)), format3)
                        if line.currency_id.id != line.company_id.currency_id.id:
                            sheet.write(row, 10, (float(line.amount_currency)), format3)
                            sheet.write(row, 11, line.currency_id.name, format2)
                        else:
                            sheet.write(row, 10, 0, format3)
                        row = row + 1
                        
                    sheet.merge_range(row, 0, row, 4, '', formatf1)
                    sheet.merge_range(row, 5, row, 6, 'Accumulated Partner Balance', formatf1)
                    sheet.write(row, 7, (float(acml_debit)), formatf2)
                    sheet.write(row, 8, (float(acml_credit)), formatf2)
                    sheet.write(row, 9, (float(acml_bal)), formatf2)
                    sheet.merge_range(row, 10, row, 11, '', formatf1)
                    row = row + 2
                    
            
