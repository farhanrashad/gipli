# -*- coding: utf-8 -*-
import pandas as pd
import plotly.express as px
from odoo import http
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.exceptions import AccessError, MissingError, UserError, ValidationError

class CustomerPortal(CustomerPortal):

    @http.route('/my/services/dashboard', type='http', auth='public', website=True, csrf=False)
    def my_services_dashboard(self, **kwargs):
        dash_item_ids = request.env['base.dashboard.item'].sudo().search([])

        output_html = '''
            <div class="container">
                <h1>My Dashboard</h1>
                <div class="row">
        '''
        
        for item in dash_item_ids:
            if item.view_type == 'list':
                output_html += self.render_list_view(item)
            elif item.view_type == 'graph':
                output_html += self.render_graph_view(item)
        
        output_html += '''
                </div>
            </div>
            <script src="/web/static/lib/jquery/jquery.js"></script>
            <script src="https://cdn.datatables.net/1.10.21/js/jquery.dataTables.min.js"></script>
            <script src="https://cdn.datatables.net/buttons/1.6.1/js/dataTables.buttons.min.js"></script>
            <script src="https://cdn.datatables.net/buttons/1.6.1/js/buttons.colVis.min.js"></script>
            <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.21/css/jquery.dataTables.min.css"/>
            <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/buttons/1.6.1/css/buttons.dataTables.min.css"/>
            <script type="text/javascript">
                $(document).ready(function() {
                    $('table.display').each(function() {
                        $(this).DataTable({
                            stateSave: true,
                            dom: 'Bfrtip',
                            buttons: [
                                'colvis'
                            ],
                            initComplete: function () {
                                var api = this.api();
                                api.columns().every(function () {
                                    var column = this;
                                    var select = $('<select><option value=""></option></select>')
                                        .appendTo($(column.footer()).empty())
                                        .on('change', function () {
                                            var val = $.fn.dataTable.util.escapeRegex(
                                                $(this).val()
                                            );
                                            column
                                                .search(val ? '^' + val + '$' : '', true, false)
                                                .draw();
                                        });
                                    column.data().unique().sort().each(function (d, j) {
                                        select.append('<option value="' + d + '">' + d + '</option>')
                                    });
                                });
                            }
                        });
                    });
                });
            </script>
        '''

        values = {
            'output_html': output_html,
        }
        return request.render("de_portal_dashboard.portal_services_dashboard", values)
    
    def render_list_view(self, item):
        #records = request.env[item.model_id.model].search([])
        
        records = request.env[item.model_id.model].sudo().browse(item._get_records_filter_by_domain(request.env.user.partner_id.id))

        list_view_html = '''
            <div class="col-lg-6 mb-3">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">{item_name}</h5>
                        <table id="table-{item_id}" class="display">
                            <thead>
                                <tr>
        '''.format(item_name=item.name, item_id=item.id)
        
        # Adding table headers
        for field in item.field_ids:
            list_view_html += '<th>{}</th>'.format(field.field_description.capitalize())
        
        list_view_html += '''
                            </tr>
                        </thead>
                        <tbody>
        '''
        
        # Adding table rows with links to record details
        for record in records:
            list_view_html += '<tr>'
            for field in item.field_ids:
                record_value = getattr(record, field.name, '')
                list_view_html += '<td><a href="/my/dashboard/item/{item_id}/{record_id}">{record_value}</a></td>'.format(
                    item_id=item.id,
                    record_id=record.id,
                    record_value=self._get_field_values(record,field)
                )
            list_view_html += '</tr>'
        
        list_view_html += '''
                        </tbody>
                    </table>
                </div>
            </div>
            </div>
        '''
        
        return list_view_html

    def _get_field_values(self, record, field):
        record_value = ''
        if record[field.name]:
            if field.ttype == 'many2one':
                record_value = record[field.name].name
            else:
                record_value = record[field.name]
        return record_value
        
    def render_graph_view(self, item):
        # Fetch data from the model
        #records = request.env[item.model_id.model].search([])

        records = request.env[item.model_id.model].sudo().browse(item._get_records_filter_by_domain(request.env.user.partner_id.id))

    
        # Prepare data using pandas
        data = []
        for record in records:
            label = getattr(record, item.graph_label_field_id.name, 'No Label')
            value = getattr(record, item.graph_data_field_id.name, 0)
            data.append({'label': label, 'value': value})
    
        # Create a DataFrame
        df = pd.DataFrame(data)
    
        # Create the Plotly figure
        fig = px.bar(df, x='label', y='value', title=item.name, color='label')
    
        # Convert Plotly figure to HTML
        graph_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
    
        # Wrap the Plotly HTML into a div container
        graph_view_html = (
            '<div class="col-lg-6 mb-3">'
            '    <div class="card">'
            '        <div class="card-body">'
            '            <h5 class="card-title">' + item.name + '</h5>'
            '            <div>' + graph_html + '</div>'
            '        </div>'
            '    </div>'
            '</div>'
        )
    
        return graph_view_html

    @http.route('/my/dashboard/item/<int:item_id>/<int:record_id>', type='http', auth='public', website=True, csrf=False)
    def record_detail(self, item_id, record_id, **kwargs):
        item = request.env['base.dashboard.item'].sudo().browse(item_id)
        model = item.model_id
        model_name = model.model
        record = request.env[model_name].sudo().browse(record_id)
    
        if not record.exists():
            return request.not_found()
    
        output_html = '''
            <div class="container">
                <h1>Record Details</h1>
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Details for {record_name}</h5>
                        <table class="table">
                            <tbody>
        '''.format(record_name=record.name)
    
        # Correcting fields extraction
        fields = [field.name for field in item.field_ids]  # Ensure field names are strings
    
        for i in range(0, len(fields), 4):
            output_html += '<tr>'
            for j in range(i, min(i + 4, len(fields))):
                field = fields[j]
                field_value = getattr(record, field, '')
                if j % 2 == 0:
                    # Even index - label
                    output_html += '<th>{}</th>'.format(field.capitalize())
                else:
                    # Odd index - value
                    output_html += '<td>{}</td>'.format(field_value)
            output_html += '</tr>'
    
        output_html += '''
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        '''
    
        values = {
            'output_html': output_html,
            'record': record,  # Pass the record object to the template
        }
        return request.render("de_portal_dashboard.portal_record_detail", values)