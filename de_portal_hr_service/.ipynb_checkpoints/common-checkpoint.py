from odoo import fields, models, api, _
from odoo.exceptions import UserError
import csv
import base64
import xlrd
from odoo.tools import ustr
import logging

_logger = logging.getLogger(__name__)
def import_data(self_ref =None,model = None,record_sudo=None,import_type = 'excel',file=None,line_item = None,service_id=None):
    service_items = line_item.hr_service_record_line_items
    counter = 0
    headers= []
    row_values= []
    objs = None
    # skipped_line_no = {}
    # row_field_dic = {}
    # row_field_error_dic = {}
    try:
        if import_type == 'excel':
            wb = None
            try:
                wb = xlrd.open_workbook(
                file_contents=base64.decodebytes(file))
            except Exception as e:
                raise UserError(_('Unable to decode this format file'))
           
            sheet = wb.sheet_by_index(0)
            for row in range(sheet.nrows):
                for i in range(0, sheet.ncols):
                    if row==0:
                        headers.append(sheet.cell(row, i).value)
            for row in range(0,sheet.nrows):
                if row >0:
                    values = []
                    for i in range(0, sheet.ncols):
                        values.append(sheet.cell(row, i).value)
                    row_values.append(values)
    
            objs = [{field: value for field, value in zip(headers, values)} for values in row_values]
        if import_type == 'csv':
            file = None
            try:
                file = str(base64.decodebytes(file).decode('utf-8'))
            except Exception as e:
                raise UserError(_('Unable to decode this format file'))
            myreader = csv.reader(file.splitlines())
            csv_header_counter = 0
            for row in myreader:
                csv_header_counter = csv_header_counter + 1
                values = []
                for i in range(0, len(row)):
                    if csv_header_counter == 1:
                        headers=row
                        break
                if csv_header_counter != 1:
                    for i in range(1, len(row)):
                        values = row
                        break
                    row_values.append(values)

            objs = [{field: value for field, value in zip(headers, values)} for values in row_values]
        vals = {}
        for obj in objs:
            for field in service_items:
                field_val = None

                if obj.get(field.field_label):
                    field_val = obj.get(field.field_label)
                if field.field_type == 'many2one':
                    m2o_id = self_ref.env[field.field_model].sudo().search([('name','=',field_val)],limit=1)
                    # m2o_id = self_ref.env[field.field_model].sudo().search([('id','=',int(field_val))],limit=1)
                    vals.update({
                            field.field_name: m2o_id.id,
                        })
                elif field.field_type == 'float':
                    vals.update({
                        field.field_name: float(obj.get(field.field_label))
                    })
                else:
                    vals.update({
                        field.field_name: obj.get(field.field_label) 
                    })
                    
            if line_item.line_model_id.id == int(model.id):
                parent_record_sudo = self_ref.env[service_id.header_model_id.model].sudo().search([('id','=',int(record_sudo))],limit=1)
                vals.update({
                        line_item.sudo().parent_relational_field_id.name: int(record_sudo.id), #parent_record_sudo.id
                        # line_item.sudo().parent_relational_field_id.name: int(record_id), #parent_record_sudo.id
                    })
                # line_item.sudo().parent_relational_field_id.name = sheet_id
                record_result = self_ref.env[line_item.line_model_id.model].sudo().create(vals)
                if record_result:
                    counter = counter + 1
    except Exception as e:
        raise UserError(_(e.args[0]))
        
    return counter

