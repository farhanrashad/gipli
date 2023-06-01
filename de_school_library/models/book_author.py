from odoo import models, fields


class BookAuthor(models.Model):
    _name = 'library.book.author'
    _description = 'Book Author'

    # name = fields.Char('Name', required=True)
    # biography = fields.Text('Biography')
    # book_ids = fields.One2many('oe.school.library.book.type', 'author_id', 'Books')
