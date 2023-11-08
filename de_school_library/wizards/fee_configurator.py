# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
import math

class RentalWizard(models.TransientModel):
    _name = 'oe.library.fee.config.wizard'
    _description = 'Configure the Library Fee'

    def _default_uom_id(self):
        if self.env.context.get('default_uom_id', False):
            return self.env['uom.uom'].browse(self.context.get('default_uom_id'))
        else:
            return self.env['product.product'].browse(self.env.context.get('default_product_id')).uom_id
            
    product_id = fields.Many2one(
        'product.product', "Product", required=True, ondelete='cascade',
        domain=[('is_book', '=', True)], help="Product to rent (has to be rentable)")
    uom_id = fields.Many2one('uom.uom', 'Unit of Measure', readonly=True, default=_default_uom_id)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company.id, store=False)
    currency_id = fields.Many2one('res.currency', string="Currency", compute='_compute_currency_id')

    pricing_id = fields.Many2one(
        'oe.library.product.fees', compute="_compute_pricing",
        string="Pricing", help="Best Pricing Rule based on duration")
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')

    pickup_date = fields.Datetime(
        string="Pickup", required=True,
        default=lambda s: fields.Datetime.now() + relativedelta(minute=0, second=0, hours=1))
    return_date = fields.Datetime(
        string="Return", required=True,
        default=lambda s: fields.Datetime.now() + relativedelta(minute=0, second=0, hours=1, days=1))
    
    duration = fields.Integer(
        string="Duration", compute="_compute_duration",
        help="The duration unit is based on the unit of the rental pricing rule.")
    duration_unit = fields.Selection([("hour", "Hours"), ("day", "Days"), ("week", "Weeks"), ("month", "Months"), ('year', "Years")],
                                     string="Unit", required=True, compute="_compute_duration")

    unit_price = fields.Monetary(
        string="Unit Price", help="This price is based on the rental price rule that gives the cheapest price for requested duration.",
        readonly=False, default=0.0, required=True)

    quantity = fields.Float("Quantity", default=1, required=True, digits='Product Unit of Measure')  # Can be changed on SO line later if needed


    @api.depends('pricelist_id')
    def _compute_currency_id(self):
        for wizard in self:
            wizard.currency_id = wizard.pricelist_id.currency_id or wizard.env.company.currency_id
    

    @api.depends('pricing_id', 'pickup_date', 'return_date')
    def _compute_duration(self):
        for wizard in self:
            values = {
                'duration_unit': 'day',
                'duration': 1.0,
            }
            if wizard.pickup_date and wizard.return_date:
                duration_dict = self.env['oe.library.product.fees']._compute_duration_vals(wizard.pickup_date, wizard.return_date)
                if wizard.pricing_id:
                    values = {
                        'duration_unit': wizard.pricing_id.recurrence_id.unit,
                        'duration': duration_dict[wizard.pricing_id.recurrence_id.unit]
                    }
                else:
                    values = {
                        'duration_unit': 'day',
                        'duration': duration_dict['day']
                    }
            wizard.update(values)

    @api.depends('pickup_date', 'return_date')
    def _compute_pricing(self):
        self.pricing_id = False
        for wizard in self:
            if wizard.product_id:
                company = wizard.company_id or wizard.env.company
                wizard.pricing_id = wizard.product_id._get_best_library_fee_rule(
                    start_date=wizard.pickup_date,
                    end_date=wizard.return_date,
                    pricelist=wizard.pricelist_id,
                    company=company,
                    currency=wizard.currency_id or company.currency_id,
                )
    