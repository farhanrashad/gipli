from odoo import models, fields, api


class DiscountInvoices(models.Model):
    _inherit = 'account.move'

    discount = fields.Float("Discount")

    @api.onchange('discount')
    def discount_invoice(self):
        for order in self:
            # amount_untaxed += line.price_subtotal
            order.update({
                # 'amount_untaxed': order.currency_id.round(amount_untaxed),
                'amount_untaxed': order.amount_untaxed - order.discount,
                # 'total_disc': (order.amount_untaxed) - order.discount
            })

    # total_disc = fields.Float(string='Total', compute='_disount_grand_tot')
    # currency_id = fields.Many2one('res.currency', string='Currency')

    # @api.depends('discount')
    # def _disount_grand_tot(self):
    #     for order in self:
    #         # amount_untaxed += line.price_subtotal
    #         order.update({
    #             # 'amount_untaxed': order.currency_id.round(amount_untaxed),
    #             'amount_total': order.amount_total - order.discount,
    #             'total_disc': (order.amount_untaxed) - order.discount
    #         })

    # @api.depends('order_line.price_total')
    # def _amount_all(self):
    #     for order in self:
    #         amount_untaxed = amount_tax = 0.0
    #         for line in order.order_line:
    #             amount_untaxed += line.price_subtotal
    #             amount_tax += line.price_tax
    #         order.update({
    #             'amount_untaxed': order.currency_id.round(amount_untaxed),
    #             'amount_tax': order.currency_id.round(amount_tax),
    #             'amount_total': amount_untaxed + amount_tax,
    #         })
