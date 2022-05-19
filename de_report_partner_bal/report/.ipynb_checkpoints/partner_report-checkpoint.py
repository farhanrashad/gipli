import json
from odoo import api, models, _ , fields 
from odoo.exceptions import UserError
from datetime import datetime


class PartnerBalanceXlS(models.AbstractModel):
    _name = 'report.de_report_partner_bal.partner_bal_report_xlsx'
    _description = 'Partner Balance Xlsx Report'
    _inherit = 'report.report_xlsx.abstract'

    
    def generate_xlsx_report(self, workbook, data, lines):
        data = self.env['partner.wizard'].browse(self.env.context.get('active_ids'))
    

        
        sheet = workbook.add_worksheet('Partner Balance Xlsx Report')
        bold = workbook. add_format({'bold': True, 'align': 'center','bg_color': '#8CBDD6','border': True})
        title = workbook.add_format({'bold': True, 'align': 'center', 'font_size': 14, 'border': True})
        header_row_style = workbook.add_format({'bold': True, 'align': 'center', 'border':True})
        format2 = workbook.add_format({'align': 'center'})
        format3 = workbook.add_format({'align': 'center','bold': True,'border': True,})   
        
        
        format0 = workbook.add_format({'font_size': '12', 'align': 'vcenter', 'bold': True,})
        format1 = workbook.add_format({'font_size': '12', 'align': 'vcenter', 'bold': True, 'bg_color': 'yellow'})       
        label =workbook.add_format({'font_size': '10', 'align': 'center', 'bold': True, 'border':True, 'bg_color': 
                                    '#CCFFFF'})
        format_txt = workbook.add_format({'font_size': '10', 'align': 'center', 'border':True,})
        format_num = workbook.add_format({'font_size': '10', 'align': 'right', 'num_format':'#,##0.00', 'border':True})
                                                                                                                                                      
        
        sheet.set_column(0, 0, 20)
        sheet.set_column(1, 1, 50)
        sheet.set_column(2, 2, 20)
        sheet.set_column(3, 3, 20)
        sheet.set_column(4, 4, 20)
        sheet.set_column(5, 5, 20)
        sheet.set_column(6, 6, 20)
        row = 3
        col = 0
        
       
        
        sheet.write(1,0,'Code', bold)
        sheet.write(1,1 , 'Name',bold)
        sheet.write(1,2 , 'City',bold)
        sheet.write(1,3 , 'CNIC',bold)
        sheet.write(1,4 , 'NTN',bold)
        sheet.write(1,5 , 'STRN',bold)
        sheet.write(1,6 , 'Balance',bold)

        sheet.write('A0:A0', data.state, format1)
        entery_type = ''
        if not data['state'] == 'all':
            entery_type == " and parent_state = " + data['state']
#             raise UserError("test")
           
            
            
            
        to_char = data['date']                                                                                                                              
        # -------------------------------------------------------------------------
        # Query for lease agreement
        # -------------------------------------------------------------------------
        self._cr.execute("""
            select p.ref, p.name, p.vat as strn, p.ntn, p.nic,p.city, sum(a.debit) - sum(a.credit) as bal
            from account_move_line a
            join res_partner p on a.partner_id = p.id
            where a.date <= '""" + str(to_char) + entery_type + """' 
            group by p.ref, p.name, p.vat, p.ntn, p.nic, p.city
            """)
        
                         
        rs_move = self._cr.dictfetchall()
        
        for move in rs_move:
            sheet.write(row,0, move['ref'], format_txt)
            sheet.write(row,1, move['name'], format_txt)
            sheet.write(row,2, move['city'], format_txt)
            sheet.write(row,3, move['nic'], format_txt)
            sheet.write(row,4, move['ntn'], format_txt)
            sheet.write(row,5, move['strn'], format_txt)
            sheet.write(row,6, move['bal'], format_num)
            

             
                
            row += 1
        