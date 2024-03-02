# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

DAY_SELECTION = [
    ('0', 'Monday'),
    ('1', 'Tuesday'),
    ('2', 'Wednesday'),
    ('3', 'Thursday'),
    ('4', 'Friday'),
    ('5', 'Saturday'),
    ('6', 'Sunday'),
]

class ScheduleNuitrition(models.Model):
    _name = 'gym.schedule.nutr'
    _description = 'Nutrition Schedule'
    _order = 'member_id, date'
    _rec_name = 'member_id'
    _check_company_auto = True

    member_id = fields.Many2one('res.partner', 'Member', store=True, required=True)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)
    nutr_schedule_line = fields.One2many('gym.schedule.nutr.line', 'nutr_schedule_id', string='Nuitrition Schedule Line')
    date = fields.Date('Date', required=True)

    day_of_week = fields.Selection(
        string='Day of Week',
        selection=DAY_SELECTION,
        compute='_compute_day_of_week', store=True, 
    )
    
    @api.depends('date')
    def _compute_day_of_week(self):
        for record in self:
            if record.date:
                record.day_of_week = str(record.date.weekday())
            else:
                record.day_of_week = False

    
            
class ScheduleNuitritionLine(models.Model):
    _name = 'gym.schedule.nutr.line'
    _description = 'Nutrition Schedule Line'

    nutr_schedule_id = fields.Many2one('gym.schedule.nutr', string='Nuitrition Schedule', 
                                   required=True, ondelete='cascade')

    nutr_meal_type_id = fields.Many2one("gym.nutr.meal.type", string="Meal Type", required=True,
                            )
    nutr_meal_note = fields.Text("Note", required=True)


