from odoo.tools.mimetypes import guess_mimetype
import base64
from itertools import islice
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import config, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat
import datetime

try:
    import xlrd

    try:
        from xlrd import xlsx
    except ImportError:
        xlsx = None
except ImportError:
    xlrd = xlsx = None

try:
    from . import odf_ods_reader
except ImportError:
    odf_ods_reader = None

FILE_TYPE_DICT = {
    'text/csv': ('csv', True, None),
    'application/vnd.ms-excel': ('xls', xlrd, 'xlrd'),
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ('xlsx', xlsx, 'xlrd >= 1.0.0'),
    'application/vnd.oasis.opendocument.spreadsheet': ('ods', odf_ods_reader, 'odfpy')
}
EXTENSIONS = {
    '.' + ext: handler
    for mime, (ext, handler, req) in FILE_TYPE_DICT.items()
}


class Import(models.TransientModel):
    _name = 'units.import'
    _inherit = ["base_import.import", 'mail.thread', 'mail.activity.mixin']
    supported_formats = ['xlsx', 'xls']
    data = {"dates": []}
    file = fields.Binary(string='select %s file' % supported_formats)
    file_name = fields.Char('File Name')
    file_type = fields.Char('File Type')

    @api.model
    def import_units(self):
        action = self.env.ref('factors_import.import_units_template_action').read()[0]
        return action

    def import_excel(self):
        self.ensure_one()
        self.data['sheet'] = []
        if self.file:
            file_content = base64.b64decode(self.file)
            mimetype = guess_mimetype(file_content)
            (file_extension, handler, req) = FILE_TYPE_DICT.get(
                mimetype, (None, None, None))
            if not file_extension in self.supported_formats:
                raise UserError(_("Unsupported format, please upload file in '{0}'".format(
                    self.supported_formats)))
            book = xlrd.open_workbook(file_contents=file_content)

            header_list = []
            i = 0
            for sheet in book.sheets():
                for rownum in range(sheet.nrows):
                    if rownum == 0:
                        header_list = sheet.row_values(rownum)
                values = self._read_xls_book2(book, i)
                self.mapping_data(values, header_list)
                i += 1

    def _read_xls_book2(self, book, sheet_index):
        sheet = book.sheet_by_index(sheet_index)
        # emulate Sheet.get_rows for pre-0.9.4
        for rowx, row in enumerate(map(sheet.row, range(sheet.nrows)), 1):
            values = []
            for colx, cell in enumerate(row, 1):
                if cell.ctype is xlrd.XL_CELL_NUMBER:
                    is_float = cell.value % 1 != 0.0
                    values.append(
                        str(cell.value)
                        if is_float
                        else str(int(cell.value))
                    )
                elif cell.ctype is xlrd.XL_CELL_DATE:
                    is_datetime = cell.value % 1 != 0.0
                    # emulate xldate_as_datetime for pre-0.9.3
                    dt = datetime.datetime(*xlrd.xldate.xldate_as_tuple(cell.value, book.datemode))
                    values.append(
                        dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                        if is_datetime
                        else dt.strftime(DEFAULT_SERVER_DATE_FORMAT)
                    )
                elif cell.ctype is xlrd.XL_CELL_BOOLEAN:
                    values.append(u'True' if cell.value else u'False')
                elif cell.ctype is xlrd.XL_CELL_ERROR:
                    raise ValueError(
                        _("Invalid cell value at row %(row)s, column %(col)s: %(cell_value)s") % {
                            'row': rowx,
                            'col': colx,
                            'cell_value': xlrd.error_text_from_code.get(cell.value,
                                                                        _("unknown error code %s") % cell.value)
                        }
                    )
                else:
                    values.append(cell.value)
            if any(x for x in values if x.strip()):
                yield values

    def mapping_data(self, content, header_list):
        if content:
            rows = enumerate(islice(content, 1, None))
            lines = []
            factors = []
            for header in header_list:
                if 'factor' in header and 'area' not in header and 'price' not in header and 'print' not in header:
                    factors.append(header)
            vals = {}
            for index, row in rows:
                factors_lines = []
                unit_id = row[header_list.index('Unit ID')]
                type = row[header_list.index('Property Type')]
                type_id = self.env['property.type'].search([('name', '=', type)], limit=1)
                project_name = row[header_list.index('Project')]
                project_id = self.env['project.project'].search([('name', '=', project_name)], limit=1)

                categ_name = row[header_list.index('Category')]
                categ_id = self.env['property.category'].search([('name', '=', categ_name)], limit=1)
                company_name = row[header_list.index('Company')]
                company_id = self.env['res.company'].search([('name', '=', company_name)], limit=1)
                phase_name = row[header_list.index('Phase')]
                phase_id = self.env['project.phase'].search([('name', '=', phase_name)], limit=1)
                name = row[header_list.index('Unit Name')]
                finish_of_property = row[header_list.index('Finishing Type')]
                state = row[header_list.index('Status')]
                if unit_id:
                    unit = self.env['product.product'].sudo().browse(int(unit_id))
                    print("D>D>D>D>",state)
                    unit.write(
                        {
                         'project_id': project_id.id,
                         'phase_id': phase_id.id,
                         'cate_id': categ_id.id,
                         'company_id': company_id.id,
                         'type_of_property_id': type_id.id,
                         'is_factor_price_unit': True,
                         'is_property': True,
                         'finish_of_property': finish_of_property if finish_of_property in ['Finish',
                                                                                            'Core&Shell'] else '',
                         'state': state,
                         })
                else:
                    unit = self.env['product.product'].create(
                        {'name': name, 'property_code': name,
                         'project_id': project_id.id,
                         'phase_id': phase_id.id,
                         'type_of_property_id': type_id.id,
                         'is_factor_price_unit': True,
                         'is_property': True,
                         'finish_of_property': finish_of_property if finish_of_property in ['Finish','Core&Shell'] else '',
                         'state': state,
                         })
                for factor in factors:
                    factor_name = row[header_list.index(factor)]
                    factor_area = row[header_list.index(factor + " area")]
                    factor_price = row[header_list.index(factor + " price")]
                    factor_print = row[header_list.index(factor + " print")]
                    factor_id = self.env['unit.price.factor'].sudo().search([('name', '=', factor_name)], limit=1)
                    print(">D>>",factor_id)
                    if not factor_id and factor_name:
                        factor_id = self.env['unit.price.factor'].sudo().create({'name': factor_name})

                    factors_lines.append({
                        'factor_id': factor_id.id,
                        'space': factor_area,
                        'price': factor_price,
                        'is_print': factor_print,
                    })
                vals.update({
                    unit.id: factors_lines})
            self.update_lines(vals)

    def update_lines(self, vals):
        for key, val in vals.items():
            for line in val:
                unit = self.env['product.product'].sudo().browse(int(key))
                unit_price_lines = unit.unit_price_lines.filtered(
                    lambda line_price: line_price.factor_id.id == line.get('factor_id'))
                if unit_price_lines:
                    unit_price_lines.write({'space': float(line.get('space')), 'price': float(line.get('price')),
                                            'is_print': int(line.get('is_print'))})
                else:
                    if line.get('factor_id'):
                        self.env['unit.price.lines'].create(
                            {'space': float(line.get('space')), 'price': float(line.get('price')),
                             'is_print': int(line.get('is_print')),
                             'unit_id': unit.id,
                             'factor_id': line.get('factor_id')
                             }
                        )
                print("D>D>",unit.id)
