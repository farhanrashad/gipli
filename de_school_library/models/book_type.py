from odoo import models, fields


class BookType(models.Model):
    _name = 'oe.school.library.book.type'

    name = fields.Char(string='Book', required=True)
    code = fields.Char(string='Code', required=True)
    price = fields.Float(string='Price')
    book_category_id = fields.Many2one('os.school.library.book.category', string='Book Category')
    # author_id = fields.Many2one('library.book.author', string='Author')
    # publisher_id = fields.Many2one('book.publisher', string='Publisher')
