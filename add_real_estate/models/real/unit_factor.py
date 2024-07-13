 # -*- coding: utf-8 -*-
from odoo import models, fields, api, _, exceptions
import datetime
from odoo.exceptions import ValidationError

class Unit(models.Model):
    _name='unit.price.factor'
    name = fields.Char(string="Name", required=True)
    is_print = fields.Boolean(string="Print")
    is_finish = fields.Boolean(string="Is Finished")
    finish_of_property_id = fields.Many2one('property.finished.type', _('Finishing Type'))




class UnitPriceLine(models.Model):
    _name='unit.price.lines'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name='factor_id'
    factor_id = fields.Many2one(comodel_name="unit.price.factor", string="Factor", required=False,track_visibility = 'always')
    unit_id = fields.Many2one(comodel_name="product.product",track_visibility = 'always')
    project_id = fields.Many2one(comodel_name="project.project", track_visibility = 'always')
    space = fields.Float(string="Space", required=False,track_visibility = 'always')
    price = fields.Float(string="Price", required=False,track_visibility = 'always')
    total = fields.Float(string="Total",compute='_calc_total',store=True,track_visibility = 'always')


    @api.depends('space','price')
    def _calc_total(self):
        for line in self:
            line.total=line.space*line.price


    is_print = fields.Boolean(string="Print",related='factor_id.is_print',store=True,readonly=False,track_visibility = 'always')

    def write(self, values):
        old_price=self.unit_id.final_unit_price
        res=super(UnitPriceLine, self).write(values)
        if values:
            if 'space' in values.keys() or 'price'in values.keys():
                for rec in self:
                    self.env['unit.price.changes'].create({
                        'date':datetime.datetime.now().date(),
                        'old_price':old_price,
                        'new_price':self.get_new_price(rec.unit_id),
                        'unit_id':rec.unit_id.id,
                    })
        return res

    def get_new_price(self,unit_id):
        summ = 0
        final_unit_price = 0
        for line in unit_id.unit_price_lines:
            summ += line.total
        if unit_id.unit_price_lines:
            final_unit_price = summ
        if unit_id.discount_type == 'amount':
            final_unit_price = final_unit_price - unit_id.discount_value
        if unit_id.discount_type == 'percentage':
            final_unit_price = final_unit_price - ((unit_id.discount_value / 100) * final_unit_price)
        print("final_unit_price",final_unit_price)

        return final_unit_price



