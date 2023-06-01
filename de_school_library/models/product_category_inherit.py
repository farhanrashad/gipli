from odoo import models, fields


class ProductCategory(models.Model):
    _inherit = 'product.category'
    _description = 'Product Category'

    is_book = fields.Boolean(string='Is Book', default=True)


class LibraryBook(models.Model):
    _inherit = 'product.product'

    author_id = fields.Many2one('res.partner', string='Author')
    publisher_id = fields.Many2one('res.partner', string='Publisher')
    book_type_id = fields.Many2one('oe.school.library.book.type', string='Book Type')
    isbn_no = fields.Char(string='ISBN No.')
    book_tag_ids = fields.Many2many('os.school.library.book.category', string='Book Tags')


class StockProductionLot(models.Model):
    _inherit = 'stock.lot'

    isbn_no = fields.Char(string='Isbn No')
    edition_no = fields.Char(string='Edition No')
