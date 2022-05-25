# -*- coding: utf-8 -*-
from odoo import models, fields
from datetime import datetime
from datetime import date, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from dateutil.relativedelta import relativedelta
import pytz


class PartnerBalanceXlS(models.AbstractModel):
    _name = 'report.de_report_partner_bal.partner_bal_report_xlsx'
    _description = 'Partner Balence Xlsx report'
    _inherit = 'report.report_xlsx.abstract'
    
  
    def generate_xlsx_report(self, workbook, data, lines):
        data = self.env["partner.wizard"].browse(self.env.context.get('active_ids'))
        format1 = workbook.add_format({'font_size': '12', 'align': 'center', 'bold': False})
        sheet = workbook.add_worksheet('Employee Attendance Report')
        bold = workbook.add_format({'bold': True, 'align': 'center', 'border': True})
        
       
        sheet.write('C1:C1', data.date.strftime('%d-%m-%Y'), bold)
        
        
        format0 = workbook.add_format({'font_size': '12', 'align': 'vcenter', 'bold': True,})
        format1 = workbook.add_format({'font_size': '12', 'align': 'vcenter', 'bold': True, 'bg_color': 'yellow'})       
        label =workbook.add_format({'font_size': '10', 'align': 'center', 'bold': True, 'border':True, 'bg_color': 
                                    '#CCFFFF'})
        format_txt = workbook.add_format({'font_size': '10', 'align': 'center', 'border':True,})
        format_num = workbook.add_format({'font_size': '10', 'align': 'right', 'num_format':'#,##0.00', 'border':True})
                                                                                                                                                      
        
        sheet.set_column(0, 0, 20)
        sheet.set_column(1, 1, 50)
        sheet.set_column(2, 2, 40)
        sheet.set_column(3, 3, 20)
        sheet.set_column(4, 4, 20)
        sheet.set_column(5, 5, 20)
        sheet.set_column(6, 6, 20)
        row = 3
        col = 0
        
       
        
        sheet.write(2,0,'Code', bold)
        sheet.write(2,1 , 'Name',bold)
        sheet.write(2,2 , 'Email',bold)
        sheet.write(2,3 , 'City',bold)
        sheet.write(2,4 , 'CNIC',bold)
        sheet.write(2,5 , 'NTN',bold)
        sheet.write(2,6 , 'STRN',bold)
        sheet.write(2,7 , 'Balance',bold)

       
#         entery_type = ''
#         if data['state'] == 'draft':
#             entery_type == "and parent_state = " + data['draft']
#         elif data['state'] == 'draft':
#             entery_type == "and parent_state = " + data['']
#             raise UserError("test")
           
            
        company_id = ''  
        if data['date']:
            date_param = " to_char(date) <= " + data['date'].strftime("%Y-%m-%d")
        company_id = data.company_id.id            
        dated = data['date'].strftime("%Y-%m-%d")
#         current_date=str((data.date))
#         sssssssss = datetime.strptime(current_date, "%Y-%m-%d").strftime("%d/%m/%Y")
        # -------------------------------------------------------------------------
        # Query for lease agreement
        # -------------------------------------------------------------------------
        
        if data.account_type == 'payable':
            self._cr.execute("""
                select p.ref, p.name, p.vat as strn, p.ntn, p.email, p.nic, p.city, sum(l.debit) - sum(l.credit) as bal
                from account_move_line l
                join account_account a on l.account_id = a.id
                join account_move m on l.move_id = m.id
                join res_partner p on l.partner_id = p.id
                where  a.internal_type = '""" + str(data.account_type) +  """' and l.date <= '""" + str(dated) +  """' and l.company_id='"""+ str(company_id)  + """'
                and m.state in ('draft', 'posted')
                group by p.ref, p.name, p.vat, p.email, p.ntn, p.nic, p.city
                """)
        if data.account_type == 'receivable':
             self._cr.execute("""
                select p.ref, p.name, p.vat as strn, p.ntn, p.email, p.nic, p.city, sum(l.debit) - sum(l.credit) as bal
                from account_move_line l
                join account_account a on l.account_id = a.id
                join account_move m on l.move_id = m.id
                join res_partner p on l.partner_id = p.id
                where a.internal_type = '""" + str(data.account_type) +  """' and l.date <= '""" + str(dated) +  """' and l.company_id='"""+ str(company_id)  + """'
                and m.state in ('draft', 'posted')
                group by p.ref, p.name, p.vat, p.email, p.ntn, p.nic, p.city
                """)
            
        
        
                         
        rs_move = self._cr.dictfetchall()
        
        for move in rs_move:
            sheet.write(row,0, move['ref'], format_txt)
            sheet.write(row,1, move['name'], format_txt)
            sheet.write(row,2, move['email'], format_txt)
            sheet.write(row,3, move['city'], format_txt)
            sheet.write(row,4, move['nic'], format_txt)
            sheet.write(row,5, move['ntn'], format_txt)
            sheet.write(row,6, move['strn'], format_txt)
            sheet.write(row,7, move['bal'], format_num)
            

             
                
            row += 1
        