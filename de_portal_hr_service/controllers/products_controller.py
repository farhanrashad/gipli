import json
from odoo import http, _
from odoo.http import request
from odoo.http import content_disposition, Controller, request, route


class products_service(http.Controller):
 
    @http.route(['/get/target/items'], type='http', auth="public", method=['POST'],csrf=False)
    def find_uoms(self, **kw):
        data_list = []
        try:
            # product_id
            # name of the field which is changed
            field_name = kw.get('field_name')
            model_field = kw.get('model_field')
            response_field = kw.get('response_field')
            # option id  selected product
            selected_option_id = int(kw.get('selected_option_id'))
            service_id = int(kw.get('service_id'))
            # service = request.env['hr.service'].sudo().search([('id', '=', service_id)])
            line_items = request.env['hr.service.record.line.items'].sudo().search([('hr_service_id', '=', service_id)])
            line_item = None
            line_item_model = None
            for line in line_items:
                if line.field_name == field_name:
                    line_item = line
                    line_item_model = line.field_model
                    break
            # python_code =  line_item.python_code
            # ref_populate_field =  line_item.ref_populate_field
            # python_code = "product_id.uom_id,product_uom_id"
            # parts = ref_populate_field.split(",", 1)
            # line_item_record_next_referance = parts[0] # Output: "product_id.uom_id"
            # line_item_record_to_update = parts[1]  # Output: "product_uom_id"

            # # product_id.uom_id
            # line_item_record_next_referance_fields = line_item_record_next_referance.split(".", 1)
            # main_field = line_item_record_next_referance_fields[0]
            # referance = line_item_record_next_referance_fields[1]

            line_item_record_to_update = response_field
            referance = model_field

            # product_seelcted_record
            line_item_record = request.env[line_item_model].sudo().search([('id', '=', selected_option_id)])

            # uoms_list
            referanced_items = line_item_record.mapped(referance)

            
            if line_item_record and referanced_items:
                obj = None
                for item in referanced_items:
                    obj = {
                    'value':item.id,
                    'text':item.name,
                    'responce_field':line_item_record_to_update}
                    data_list.append(obj)
                    obj = None
                data = json.dumps(data_list)
                return data
        except Exception as e:
            obj = {
                'error_message': e or False
            }
            data_list.append(obj)
        data = json.dumps(data_list)
        return data
  