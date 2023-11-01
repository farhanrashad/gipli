# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    is_book = fields.Boolean('Is Book')
    isbn_no = fields.Char('ISBN',
        help='(International Standard Book Number): A unique identifier for the book.',
                         )
    edition_book = fields.Char('Book Edition')
    genre_id = fields.Many2one(
        comodel_name='oe.library.genre',
        string="Genre",
        ondelete='restrict')
    book_lang_id = fields.Many2one('res.lang', string='Language')
    book_pages = fields.Integer(string='Page Count', default=1)
    
    publisher_id = fields.Many2one(
        comodel_name='res.partner',
        domain="[('is_publisher','=',True)]",
        string="Publisher",
        change_default=True, ondelete='restrict')
    author_id = fields.Many2one(
        comodel_name='res.partner',
        domain="[('is_author','=',True)]",
        string="Author",
        change_default=True, ondelete='restrict')
    date_publish = fields.Date('Publication Date')

    
    
    