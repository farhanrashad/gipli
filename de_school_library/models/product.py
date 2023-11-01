# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    is_book = fields.Boolean("Is Book")
    isbn_no = fields.Char('ISBN')
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
    