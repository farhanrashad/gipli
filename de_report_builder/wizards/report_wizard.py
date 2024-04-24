# -*- coding: utf-8 -*-

from odoo import fields, models, _, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools import safe_eval
from odoo.osv import expression
import json
from odoo.tools import date_utils
import io

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter
    
class ReportWizard(models.TransientModel):
    _name = 'rc.report.wizard'
    _description = 'Custom Report Wizard'

    # ==================================================================
    # =============== Generate Report in excel =========================
    # ==================================================================
    def action_report_excel(self):
        report_id = self.env['report.config'].browse(self.env.context.get('report_id'))
        
        data = {
            'report_id': self.env.context.get('report_id'),
        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'rc.report.wizard',
                     'options': json.dumps(data,
                                           default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': report_id.name.replace(' ', '_').lower(),
                     },
            'report_type': 'report_excel'
        }

    def get_xlsx_report(self, data, response):
        rid = data['report_id']
        #raise UserError(report_id)
        
        #raise UserError(data['report_id'])
        report_id = self.env['report.config'].browse(rid)
        
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet(str(report_id.name))

        # Report Formats
        format_heading = workbook.add_format({
            'font_size': 17,
            'align': 'center', 
            'bg_color': '#D3D3D3', 
            'bold': True,
            'border': True,
        })
        format_label = workbook.add_format({
            'font_size': 13, 
            'align': 'center', 
            'bg_color': '#D3D3D3', 
            'bold': True,
            'border': True,
        })

        # Heading
        #num_main_columns = len(field_ids)
        #num_line_item_columns = sum(len(line_model.rc_line_model_field_ids) for line_model in report_id.rc_line_model_ids)

        if num_main_columns > 0 or num_line_item_columns > 0:
            start_cell = 'A1'
            end_cell = chr(ord('A') + num_main_columns + num_line_item_columns - 1) + '1'
            heading_text = report_id.name

        sheet.merge_range(start_cell + ':' + end_cell, heading_text, format_heading)
        #sheet.merge_range('A1:G1', report_id.name, format_heading)
        sheet.set_row(0, 25)
        
        records = self.env[report_id.rc_header_model_id.model].search(self._get_records_domain(report_id))
        field_ids = report_id.rc_header_field_ids

        col_widths = []
        
        col = 0
        row = 2
        line_row = 0
        for record in records:
            col = 0
            line_row = row
            for field in field_ids:
                sheet.write(1, col, field.field_id.field_description, format_label)

                if field.field_id.ttype in ['integer', 'float']:
                    cell_format = workbook.add_format({'align': 'right'})
                elif field.field_id.ttype == 'monetary':
                    cell_format = workbook.add_format({'num_format': '#,##0.00'})
                else:
                    cell_format = workbook.add_format({'align': 'left'})
                            
                if record[field.field_id.name]:
                    cell_value, col_width = self.get_cell_value_and_width(record, field)
                    sheet.write(row, col, cell_value, cell_format)
                    sheet.set_column(col, col, col_width)
                col += 1

            
            for line_model in report_id.rc_line_model_ids:
                line_row = (row - 1)
                lines_fields = line_model.rc_line_model_field_ids

                field_name = line_model.rc_header_rel_field_id.name
                lines = self.env[line_model.rc_line_model_id.model].search([(field_name, '=', record.id)])
                for line in lines:
                    line_row += 1
                    line_col = col
                    for line_field in lines_fields:

                        if line_field.field_id.ttype in ['integer', 'float']:
                            cell_format = workbook.add_format({'align': 'right'})
                        elif line_field.field_id.ttype == 'monetary':
                            cell_format = workbook.add_format({'num_format': '#,##0.00'})
                        else:
                            cell_format = workbook.add_format({'align': 'left'})
    
                        sheet.write(1, line_col, line_field.field_id.field_description, format_label)
                        if line[line_field.field_id.name]:
                            cell_value, col_width = self.get_cell_value_and_width(line, line_field)
                            sheet.write(line_row, line_col, cell_value, cell_format)
                            col_width = max(col_width, 10)
                            sheet.set_column(line_col, line_col, col_width)
                        line_col += 1
                    
                    
            row = line_row + 1


        # Set the column widths based on the maximum content length in each column
        #for i, width in enumerate(col_widths):
        #    sheet.set_column(i, i, width + 2)  # Add some padding to the width

        num_visible_columns = 30  # You can adjust this value based on your layout and page size
        if num_main_columns + num_line_item_columns > num_visible_columns:
            sheet.set_h_pagebreaks([num_visible_columns])
    
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()


    def get_cell_value_and_width(self, record, field):
        if field.field_id.ttype == 'many2one':
            related_record = record[field.field_id.name]
            if related_record and hasattr(related_record, field.link_field_id.name):
                link_field_value = getattr(related_record, field.link_field_id.name)
                cell_value = str(link_field_value)
            else:
                cell_value = ''
        elif field.field_id.ttype == 'many2many':
            related_records = record[field.field_id.name]
            if related_records:
                display_names = ", ".join(str(r[field.link_field_id.name]) for r in related_records)
                cell_value = display_names
            else:
                cell_value = ''
        else:
            cell_value = str(record[field.field_id.name])
    
        col_width = len(cell_value) + 2  # Add some padding to the width
        return cell_value, col_width

    
    # ============================================================
    # PDF Generation Code
    # ============================================================
    def generate_report(self):
        #raise UserError(self.env.context.get('report_id'))
        report_id = self.env['report.config'].browse(self.env.context.get('report_id'))
        #self._generate_output(report_id)
        #raise UserError(self._generate_output(report_id))
        html_data = """
            <div class="page">
        """ + self._generate_output(report_id) + """</div>"""
        data = {
            'date_start': False, 
            'date_stop': False, 
            'html_data': html_data,
        }
        return self.env.ref('de_report_builder.action_custom_report').report_action([], data=data)

    def _generate_output(self, report_id):
        output = ''
        records = self.env[report_id.rc_header_model_id.model].search(self._get_records_domain(report_id))
        if report_id.rc_line_model_ids:
            for record in records:
                output += """<div class="text-center" style="break-inside: avoid;">"""
                output += """<h2>""" + report_id.name + """</h2></div>"""
                output += self._generate_header_output(record, report_id.rc_header_field_ids)
                for line_model in report_id.rc_line_model_ids:
                    field_name = line_model.rc_header_rel_field_id.name
                    lines = self.env[line_model.rc_line_model_id.model].search([(field_name, '=', record.id)])
                    lines_fields = line_model.rc_line_model_field_ids
                    output += self._generate_table_output(lines, lines_fields)
                output += """<div style="page-break-after: always;"/>"""
        else:
            lines = records
            lines_fields = report_id.rc_header_field_ids
            output += self._generate_table_output(lines, lines_fields)
    
        return output

    def _get_records_domain(self, report_id):
        param_lines = report_id.rc_param_line
        domain = []
        record = self
        value = self.id
        for param in param_lines:
            if record[param.report_param_field_id.name]:
                if param.report_param_field_id.ttype == 'many2one':
                    value = record[param.report_param_field_id.name].id
                else:
                    value = record[param.report_param_field_id.name]
                param_domain = [(param.field_id.name, param.field_operator, value)]
                domain = expression.AND([param_domain, domain])
        #raise UserError(domain)
        return domain

    
    def _generate_header_output(self, record, fields):
        output = """<div id="header" class="row mt-4 mb32">"""
        for field in fields:
            if record[field.field_id.name]:
                output += """<div class="col-3 bm-2">"""
                output += """<strong>""" + field.field_id.field_description + """</strong>"""
                output += """<p>""" 
                if field.field_id.ttype == 'many2one':
                    related_record = record[field.field_id.name]
                    if related_record and hasattr(related_record, field.link_field_id.name):
                        link_field_value = getattr(related_record, field.link_field_id.name)
                        output += str(link_field_value)
                elif field.field_id.ttype == 'many2many':
                    related_records = record[field.field_id.name]
                    if related_records:
                        display_names = ", ".join(str(r[field.link_field_id.name]) for r in related_records)
                        output += display_names
                else:
                    output += str(record[field.field_id.name]) 
                output += """</p>"""
                output += """</div>"""
        output += """</div>"""
        return output
            
    def _generate_table_output(self, records, fields):
        output = ''
        output += """<table class="table table-sm">"""
        output += """<thead>"""
        output += """<tr>"""
        for field in fields:
            output += """<th class="text-start">""" + str(field.field_id.field_description) + """</th>"""
        output += """</tr>"""
        output += """</thead>"""
        output += """<tbody>"""
        output += self._generate_table_lines_output(records, fields)
        output += """</tbody>"""
        output += """</table>"""
        
        return output
    
    def _generate_table_lines_output(self, records, fields):
        output = ''
        for record in records:
            output += """<tr>"""
            for field in fields:
                if record[field.field_id.name]:
                    if field.field_id.ttype == 'many2one':
                        related_record = record[field.field_id.name]
                        if related_record and hasattr(related_record, field.link_field_id.name):
                            link_field_value = getattr(related_record, field.link_field_id.name)
                            output += """<td class="text-start">""" + str(link_field_value) + """</td>"""
                    elif field.field_id.ttype == 'many2many':
                        related_records = record[field.field_id.name]
                        if related_records:
                            display_names = ", ".join(str(r[field.link_field_id.name]) for r in related_records)
                            output += """<td class="text-start">""" + display_names + """</td>"""
                    else:
                        output += """<td class="text-start">""" + str(record[field.field_id.name]) + """</td>"""
                else:
                    output += """<td class="text-start"/>"""
            output += """</tr>"""
        return output