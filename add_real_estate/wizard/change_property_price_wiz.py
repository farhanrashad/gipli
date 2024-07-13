# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class Change(models.TransientModel):
    _name = 'change.property.price.wiz'
    property_id = fields.Many2one('product.product', _('Property'), readonly=True)
    plot_area = fields.Float(string="Plot Area m²", required=False, )
    sellable = fields.Float(string="Sellable BUA m²", required=False, )
    price_m_a = fields.Float(string="Area Price m²", required=False, )
    total_garden_area = fields.Float(string="Total Garden Area m²", required=False, )
    back_yard = fields.Float(string="Back Yard m²", required=False, )
    front_yard = fields.Float(string="Front Yard m²", required=False, )
    price_m = fields.Float(string="BUA Price m²", required=False, )
    price_garden_new = fields.Float(string="Garden Price m²", )
    is_garage = fields.Boolean(string="Is Garage ?", )
    price_garage_for_one = fields.Float(string="Price Per Garage", required=False, )
    is_finish = fields.Boolean(string="Are you going to finish?", )
    finish_of_property_id = fields.Many2one('property.finished.type', _('Finishing Type'))
    price_finishing_for_m = fields.Float(string="Price Finish For m²", required=False, )
    is_pool = fields.Boolean(string="Is Pool ?", )
    price_pool_for_one = fields.Float(string="Price Per Pool", required=False, )
    number_of_pool = fields.Integer(string="Number Of Pool", required=False, default=1)
    number_of_garage = fields.Integer(string="Number Of Garage", required=False, default=1)
    unit_price_lines = fields.One2many(comodel_name="unit.price.lines.wiz", inverse_name="wiz_id", string="Unit Price Factors", required=False)
    is_factor_price_unit = fields.Boolean(string="Calculate Price With Lines")



    @api.model
    def default_get(self, fields):
        property_id=self.env['res.reservation'].browse(self._context.get('active_ids')).property_id
        if property_id.is_factor_price_unit:
            unit_price_lines=[]
            result = super(Change, self).default_get(fields)
            result['is_factor_price_unit'] = property_id.is_factor_price_unit
            for line in property_id.unit_price_lines:
                unit_price_lines.append((0,0,{
                    'factor_id':line.factor_id.id,
                    'line_id':line.id,
                    'space':line.space,
                    'price':line.price,
                    'total':line.total,
                }))
            result['unit_price_lines'] = unit_price_lines

        else:
            result = super(Change, self).default_get(fields)
            result['plot_area']=property_id.plot_area
            result['sellable']=property_id.sellable
            result['price_m_a']=property_id.price_m_a
            result['total_garden_area']=property_id.total_garden_area
            result['back_yard']=property_id.back_yard
            result['front_yard']=property_id.front_yard
            result['price_m']=property_id.price_m
            result['price_garden_new']=property_id.price_garden_new
            result['is_garage']=property_id.is_garage
            result['price_garage_for_one']=property_id.price_garage_for_one
            result['is_finish']=property_id.is_finish
            result['finish_of_property_id']=property_id.finish_of_property_id.id
            result['is_pool']=property_id.is_pool
            result['price_pool_for_one']=property_id.price_pool_for_one
            result['number_of_pool']=property_id.number_of_pool
            result['number_of_garage']=self.property_id.number_of_garage
        return result

    def change(self):
        if self.is_factor_price_unit:
            for factor in self.unit_price_lines:
                factor.line_id.write({
                    'factor_id': factor.factor_id.id,
                    'space': factor.space,
                    'price': factor.price,
                })
            reservation = self.env['res.reservation'].browse(self._context.get('active_ids'))
            for res in reservation:
                res.recompute_payments()


        else:
            vals = {}
            vals['plot_area'] = self.plot_area
            vals['sellable'] = self.sellable
            vals['price_m_a'] = self.price_m_a
            vals['total_garden_area'] = self.total_garden_area
            vals['back_yard'] = self.back_yard
            vals['front_yard'] = self.front_yard
            vals['price_m'] = self.price_m
            vals['price_garden_new'] = self.price_garden_new
            vals['is_garage'] = self.is_garage
            vals['price_garage_for_one'] = self.price_garage_for_one
            vals['is_finish'] = self.is_finish
            vals['finish_of_property_id'] = self.finish_of_property_id.id
            vals['price_finishing_for_m'] = self.price_finishing_for_m
            vals['is_pool'] = self.is_pool
            vals['price_pool_for_one'] = self.price_pool_for_one
            vals['number_of_pool'] = self.number_of_pool
            vals['price_pool_for_one'] = self.price_pool_for_one
            vals['number_of_garage'] = self.number_of_garage
            self.property_id.sudo().write(vals)
            reservation = self.env['res.reservation'].browse(self._context.get('active_ids'))
            for res in reservation:
                res.recompute_payments()

class UnitPriceLine(models.TransientModel):
    _name='unit.price.lines.wiz'
    factor_id = fields.Many2one(comodel_name="unit.price.factor", string="Factor", required=False)
    wiz_id = fields.Many2one(comodel_name="change.property.price.wiz", )
    line_id = fields.Many2one(comodel_name="unit.price.lines", )
    space = fields.Float(string="Space", required=False)
    price = fields.Float(string="Price", required=False)
    total = fields.Float(string="Total",compute='_calc_total',)

    @api.depends('space','price')
    def _calc_total(self):
        for line in self:
            line.total=line.space*line.price


