# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools, _
import os
from odoo.exceptions import ValidationError
import xlsxwriter
import base64
import os
from io import BytesIO



class DownloadWiz(models.TransientModel):
    _name = 'units.download'
    file_data = fields.Binary('Download report Excel')
    filename = fields.Char('Excel File', size=64)






    def export_data(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        output = BytesIO()
        # file_name = path + '/temp'
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        bold = workbook.add_format({'bold': True,'bold': True, 'align': 'center', 'valign': 'vcenter', 'font_size': 14,})
        bold_green = workbook.add_format({'bold': True, 'bg_color': 'green', 'color': 'white','bold': True, 'align': 'center', 'valign': 'vcenter', 'font_size': 14,})
        bold_orang = workbook.add_format({'bold': True, 'bg_color': '#FFA500', 'color': 'white','bold': True, 'align': 'center', 'valign': 'vcenter', 'font_size': 14,})
        bold_gray = workbook.add_format({'bold': True, 'bg_color': 'gray', 'color': 'white','bold': True, 'align': 'center', 'valign': 'vcenter', 'font_size': 14,})
        report_name = "units"
        sheet = workbook.add_worksheet(report_name[:31])
        units = self.env['product.product'].browse(self._context.get('active_ids'))

        # factors=self.env['unit.price.factor'].sudo().search([])


        sheet.write(0, 0, _('Unit ID'), bold_green)
        sheet.set_column(0, 0, 20)

        sheet.write(0, 1, _('Unit Name'), bold_green)
        sheet.set_column(0, 1, 20)
        sheet.write(0, 2, _('Property Type'), bold_green)
        sheet.set_column(0, 2, 20)
        sheet.write(0, 3, _('Project'), bold_green)
        sheet.set_column(0, 4, 20)
        sheet.write(0,4, _('Category'), bold_green)
        sheet.set_column(0, 5, 20)
        sheet.write(0, 5, _('Company'), bold_green)
        sheet.set_column(0, 5, 20)
        sheet.write(0, 6, _('Phase'), bold_green)
        sheet.set_column(0, 6, 20)
        sheet.write(0, 7, _('Finishing Type'), bold_green)
        sheet.set_column(0, 7, 20)
        sheet.write(0, 8, _('Status'), bold_green)
        sheet.set_column(0, 8, 20)
        factors=[]
        for unit in units:
            for line in unit.unit_price_lines:
                if line.factor_id not in factors:
                    factors.append(line.factor_id)



        col=9
        i=1
        for factor in factors:
            sheet.write(0, col, "factor"+str(i), bold_green)
            sheet.set_column(0, col, 20)
            col+=1
            sheet.write(0, col, "factor"+str(i)+" area", bold_green)
            sheet.set_column(0, col, 20)
            col += 1
            sheet.write(0, col, "factor"+str(i)+" price", bold_green)
            sheet.set_column(0, col, 20)
            col += 1
            sheet.write(0, col, "factor"+str(i)+" print", bold_green)
            sheet.set_column(0, col, 20)
            col += 1
            i += 1
        col = 0
        row=1
        for unit in units:
            sheet.write(row, col, unit.id, bold)
            col+=1
            sheet.write(row, col, str(unit.name), bold)
            col += 1
            sheet.write(row, col, str(unit.type_of_property_id.name if unit.type_of_property_id else "" ), bold)
            col += 1
            sheet.write(row, col, str(unit.project_id.name) if unit.project_id else "", bold)
            col += 1
            sheet.write(row, col, str(unit.cate_id.name) if unit.cate_id else "", bold)
            col += 1
            sheet.write(row, col, str(unit.company_id.name) if unit.company_id else "", bold)
            col += 1
            sheet.write(row, col, str(unit.phase_id.name) if unit.phase_id else "", bold)
            col += 1
            sheet.write(row, col, str(unit.finish_of_property) if unit.finish_of_property else "", bold)
            col += 1
            sheet.write(row, col, str(unit.state) if unit.state else "", bold)
            col += 1
            for factor in factors:
                area = sum(unit.unit_price_lines.filtered(lambda line: line.factor_id.id == factor.id).mapped('space'))
                price = sum(unit.unit_price_lines.filtered(lambda line: line.factor_id.id == factor.id).mapped('price'))
                is_print = any(unit.unit_price_lines.filtered(lambda line: line.factor_id.id == factor.id).mapped('is_print'))
                sheet.write(row, col, str(factor.name), bold)
                col += 1
                sheet.write(row, col, area, bold)
                col += 1
                sheet.write(row, col, price, bold)
                col += 1
                sheet.write(row, col, 1 if is_print else 0, bold)
                col += 1
            col = 0
            row += 1


        workbook.close()
        output.seek(0)
        # with open(file_name, "rb") as file:
        #     file_base64 = base64.b64encode(file.read())
        self.file_data = base64.b64encode(output.read())
        self.filename="units.xlsx"

        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self._name,
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
     


    def excel_col(self, col):
        """Covert 1-relative column number to excel-style column label."""
        quot, rem = divmod(col - 1, 26)
        return self.excel_col(quot) + chr(rem + ord('A')) if col != 0 else ''



