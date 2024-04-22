# -*- coding: utf-8 -*-

from odoo import fields, models, _, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools import safe_eval

class ReportWizard(models.TransientModel):
    _name = 'rc.report.wizard'
    _description = 'Custom Report Wizard'

    def generate_report(self):
        #raise UserError(self.env.context.get('report_id'))
        report_id = self.env['report.config'].browse(self.env.context.get('report_id'))
        #self._generate_output(report_id)
        #raise UserError(self._generate_output(report_id))
        html_data = """
            <div class="text-center" style="break-inside: avoid;">
                <h2>""" + report_id.name + """</h2>
            </div>
        """ + self._generate_output(report_id)
        data = {
            'date_start': False, 
            'date_stop': False, 
            'html_data': html_data,
        }
        return self.env.ref('de_report_builder.action_custom_report').report_action([], data=data)

    def _generate_output(self,report_id):
        output = ''
        
        if report_id.rc_line_model_ids:
            pass
        else:
            field_lines = report_id.rc_header_field_ids
            model_id = report_id.rc_header_model_id

        output += """
            <table class="table table-sm">
        """
        output += """
                <thead>
                    <tr>
        """
        
        output += self._generate_heading_ouput(field_lines)
        output += """
                    </tr>
                </thead>
        """
        # line item records
        output += """
                <tbody>
        """
        
        output += self._generate_lineitems_output(model_id, field_lines)
        output += """
                </tbody>
        """
        
        output += """
            </table>
        """
        return output

    def _generate_heading_ouput(self,field_lines):
        output = ''
        for line in field_lines:
            output += """
            <th class="text-start">""" + str(line.field_id.field_description) + """</th>
            """
        return output
    def _generate_lineitems_output(self, model_id, field_lines):
        output = ''
        records = self.env[model_id.model].search([
            
        ])
        for record in records:
            output += """<tr>"""
            for line in field_lines:
                if record[line.field_id.name]:
                    if line.field_id.ttype == 'many2one':
                        related_record = record[line.field_id.name]
                        if related_record and hasattr(related_record, line.link_field_id.name):
                            link_field_value = getattr(related_record, line.link_field_id.name)
                            output += """<td class="text-start">""" + str(link_field_value) + """</td>"""
                    elif line.field_id.ttype == 'many2many':
                        related_records = record[line.field_id.name]
                        if related_records:
                            display_names = ", ".join(str(r[line.link_field_id.name]) for r in related_records)
                            output += """<td class="text-start">""" + display_names + """</td>"""
                    else:
                        output += """<td class="text-start">""" + record[line.field_id.name] + """</td>"""
                else:
                    output += """<td class="text-start"/>"""
            output += """</tr>"""
        return output
            
        #raise UserError(len(records))

    
        