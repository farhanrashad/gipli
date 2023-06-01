from odoo import models, fields


class BookPublisher(models.Model):
    _name = 'book.publisher'
    _description = 'Book Publisher'

    # name = fields.Char(string='Name', required=True)
    # address = fields.Char(string='Address')
    # phone = fields.Char(string='Phone')
    # email = fields.Char(string='Email')
    # book_ids = fields.One2many('oe.school.library.book.type', 'publisher_id', 'Books')

