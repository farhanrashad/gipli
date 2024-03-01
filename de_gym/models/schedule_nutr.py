# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ScheduleNuitrition(models.Model):
    _name = 'gym.schedule.nutr'
    _description = 'Nutrition Schedule'
    _order = 'date,id desc'
    _rec_name = 'name'
    _check_company_auto = True

    name = fields.Text('Note', compute='_compute_name', store=True, required=True)
    member_id = fields.Many2one('res.partner', 'Member', store=True, required=True)
    nutr_schedule_line = fields.One2many('gym.schedule.nutr.line', 'food_item_id', string='Food Item Line')
    
    @api.depends('course_id','batch_id','subject_id','company_id')
    def _compute_name(self):
        for record in self:
            record.name = record.member_id.name


class ScheduleNuitritionLine(models.Model):
    _name = 'gym.schedule.nutr.line'
    _description = 'Nutrition Schedule Line'

    nutr_schedule_id = fields.Many2one('gym.schedule.nutr', string='Nuitrition Schedule', 
                                   required=True, ondelete='cascade')

    nutr_meal_type = fields.Many2one("gym.nutr.meal.type", string="Meal Type", required=True,
                            )


