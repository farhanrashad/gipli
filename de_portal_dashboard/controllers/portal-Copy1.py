# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

class CustomerPortal(CustomerPortal):

    @http.route('/my/services/dashboard', type='http', auth='public', website=True, csrf=False)
    def my_services_dashboard(self, **kwargs):
        dash_item_ids = request.env['base.dashboard.item'].search([])

        output_html = '''
            <div class="container">
                <h1>Services Dashboard</h1>
                <div class="row">
        '''
        
        for item in dash_item_ids:
            records = request.env[item.model_id.model].search([])
            output_html += '''
                <div class="col-lg-6">
                    <div class="card mb-3">
                        <div class="card-body">
                            <h5 class="card-title">{item_name}</h5>
                            <table id="table-{item_id}" class="display">
                                <thead>
                                    <tr>
            '''.format(item_name=item.name, item_id=item.id)

            # Adding table headers
            for field in item.field_ids:
                output_html += '<th>{}</th>'.format(field.name.capitalize())
                
            output_html += '''
                                    </tr>
                                </thead>
                                <tbody>
            '''
            
            # Adding table rows with links to record details
            for record in records:
                output_html += '<tr>'
                for field in item.field_ids:
                    record_value = getattr(record, field.name, '')
                    output_html += '<td><a href="/my/services/record/{model_id}/{record_id}">{record_value}</a></td>'.format(
                        model_id=item.model_id.id,
                        record_id=record.id,
                        record_value=record_value
                    )
                output_html += '</tr>'

            output_html += '''
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            '''

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

    @http.route('/my/services/record/<int:model_id>/<int:record_id>', type='http', auth='public', website=True, csrf=False)
    def record_detail(self, model_id, record_id, **kwargs):
        model = request.env['ir.model'].browse(model_id)
        model_name = model.model
        record = request.env[model_name].browse(record_id)
    
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
    
        # Adding record fields dynamically
        fields = [field for field in record._fields if field != 'id']  # Exclude ID field if not needed
    
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
