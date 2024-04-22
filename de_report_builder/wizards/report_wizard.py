# -*- coding: utf-8 -*-

from odoo import fields, models, _, api
from odoo.exceptions import UserError, ValidationError

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
            field_ids = report_id.rc_header_field_ids.mapped('field_id')
            model_id = report_id.rc_header_model_id

        output += """
            <table class="table table-sm">
        """
        output += """
                <thead>
                    <tr>
        """
        
        output += self._generate_heading_ouput(field_ids)
        output += """
                    </tr>
                </thead>
        """
        # line item records
        output += """
                <tbody>
        """
        
        output += self._generate_lineitems_output(model_id, field_ids)
        output += """
                </tbody>
        """
        
        output += """
            </table>
        """
        return output

    def _generate_heading_ouput(self,field_ids):
        output = ''
        for field in field_ids:
            output += """
            <th class="text-start">""" + str(field.field_description) + """</th>
            """
        return output
    def _generate_lineitems_output(self, model_id, field_ids):
        output = ''
        records = self.env[model_id.model].search([
            
        ])
        for record in records:
            output += """<tr>"""
            for field in field_ids:
                output += """<td class="text-start">""" + str(record[field.name]) + """</td>"""
            output += """</tr>"""
        return output
            
    def _generate_header_data(self, report_id):
        output = ''
        records = self.env[report_id.rc_header_model_id.model].search([
        ])
        field_ids = report_id.rc_header_field_ids.mapped('field_id')
        for record in records:
            for field in field_ids:
                output += record[field.name]
        return output
        #raise UserError(len(records))

    
        