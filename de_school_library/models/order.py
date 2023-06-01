from odoo import fields, models, _, api


class Order(models.Model):
    _name = 'library.order'
    _description = 'Order'

    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: self.env['ir.sequence'].next_by_code('library.order'))
    order_lines = fields.One2many('library.order.line', 'order_id', string='Order Lines')
    customer_id = fields.Many2one('res.partner', string='Customer', required=True)
    date_order = fields.Datetime(string='Order Date', required=True, default=fields.Datetime.now)
    state = fields.Selection(
        [('draft', 'Draft'), ('confirmed', 'Confirmed'), ('done', 'Done'), ('cancel', 'Cancelled')], string='Status',
        readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
    amount_total = fields.Float(string='Total Amount', compute='_compute_amount_total')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'library.order') or _('New')
        res = super(Order, self).create(vals)
        return res

    def _compute_amount_total(self):
        for order in self:
            amount_total = 0.0
            for line in order.order_lines:
                amount_total += line.subtotal
            order.amount_total = amount_total


class OrderLine(models.Model):
    _name = 'library.order.line'
    _description = 'Order Line'

    order_id = fields.Many2one('library.order', string='Order', ondelete='cascade')
    book_id = fields.Many2one('oe.school.library.book.type', string='Book', required=True)
    # author = fields.Char(string='Author', related='book_id.author_id.name', required=True)
    # publisher = fields.Char(string='Publisher', related='book_id.publisher_id.name', required=True)
    quantity = fields.Float(string='Quantity', required=True, default=1.0)
    price = fields.Float(string='Price', related='book_id.price', readonly=True)
    book_category_id = fields.Char(string='Book Category', related='book_id.book_category_id.name', readonly=True)
    subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal')

    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.price * line.quantity
