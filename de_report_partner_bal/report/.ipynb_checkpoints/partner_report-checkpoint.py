import json
from odoo import models
from odoo.exceptions import UserError


class PartnerBalanceXlS(models.AbstractModel):
    _name = 'report.de_report_partner_bal.partner_bal_report_xlsx'
    _description = 'Partner Balance Xlsx report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        data = self.env['partner.wizard'].browse(self.env.context.get('active_ids'))
        
        sheet = workbook.add_worksheet('Partner Balance Xlsx report')
        bold = workbook. add_format({'bold': True, 'align': 'center','bg_color': '#8CBDD6','border': True})
        title = workbook.add_format({'bold': True, 'align': 'center', 'font_size': 14, 'border': True})
        header_row_style = workbook.add_format({'bold': True, 'align': 'center', 'border':True})
        format2 = workbook.add_format({'align': 'center'})
        format3 = workbook.add_format({'align': 'center','bold': True,'border': True,})   
        
        sheet.set_column(0, 0, 20)
        sheet.set_column(1, 1, 20)
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

        
        