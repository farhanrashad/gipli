from odoo import fields, models


class BookCategory(models.Model):
    _name = 'os.school.library.book.category'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
