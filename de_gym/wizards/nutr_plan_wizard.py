# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from datetime import datetime
from datetime import timedelta

from odoo.exceptions import UserError, ValidationError

class NutrPlanWizard(models.TransientModel):
    _name = "gym.nutr.plan.wizard"
    _description = 'Nuitrition Schedule Wizard'

    nutr_planning_id = fields.Many2one('gym.nutr.planning', string='Nuitrition Plan', copy=False, readonly=True)
    plan_mode = fields.Selection([
        ('day', 'Daily'),  
        ('week', 'Weekly'), 
    ], 
        string='Mode', required=True, default="week",
    )
    
    day_mon = fields.Boolean('Monday')
    day_tue = fields.Boolean('Tuesday')
    day_wed = fields.Boolean('Wednesday')
    day_thu = fields.Boolean('Thursday')
    day_fri = fields.Boolean('Friday')
    day_sat = fields.Boolean('Saturday')
    day_sun = fields.Boolean('Sunday')

    nutr_planning_wizard_line = fields.One2many('gym.nutr.plan.wizard.line', 'nutr_wizard_id', string='Nuitrition Wizard Line')

    
    @api.model
    def default_get(self, fields):
        res = super(NutrPlanWizard, self).default_get(fields)
        if 'nutr_planning_id' in self._context:
            res['nutr_planning_id'] = self._context.get('nutr_planning_id')
        return res

    def action_create_schedule(self):
        for schedule in self:
            schedule_data = []
            if schedule.plan_mode == 'day':
                for current_date in self._get_selected_dates(schedule):
                    for line in schedule.nutr_planning_wizard_line:
                        schedule_data.append(schedule._prepare_schedule_values(current_date, current_date.weekday(), line))
            else:
                selected_days = self._get_selected_days(schedule)
                for line in schedule.nutr_planning_wizard_line:
                    for day in selected_days:
                        schedule_data.append(schedule._prepare_schedule_values(False, day, line))
                    
            self.env['gym.nutr.planning.line'].create(schedule_data)
        
    
    def _prepare_schedule_values(self, date, weekday,line):
            return {
                'date': date,
                'day_of_week': str(weekday),
                'member_id': self.nutr_planning_id.member_id.id,
                'nutr_meal_type_id': line.nutr_meal_type_id.id,
                'nutr_meal_note': line.nutr_meal_note,
                'plan_mode': self.plan_mode,
                'nutr_planning_id': self.nutr_planning_id.id,
                #'nutr_planning_line': nutr_plan_lines,
            }

    def _get_selected_dates(self, schedule):
        selected_dates = []
        current_date = schedule.nutr_planning_id.date_start
        while current_date <= schedule.nutr_planning_id.date_end:
            if current_date.weekday() == 0 and schedule.day_mon:
                selected_dates.append(current_date)
            if current_date.weekday() == 1 and schedule.day_tue:
                selected_dates.append(current_date)
            if current_date.weekday() == 2 and schedule.day_wed:
                selected_dates.append(current_date)
            if current_date.weekday() == 3 and schedule.day_thu:
                selected_dates.append(current_date)
            if current_date.weekday() == 4 and schedule.day_fri:
                selected_dates.append(current_date)
            if current_date.weekday() == 5 and schedule.day_sat:
                selected_dates.append(current_date)
            if current_date.weekday() == 6 and schedule.day_sun:
                selected_dates.append(current_date)
            current_date += timedelta(days=1)
        return selected_dates

    def _get_selected_days(self, schedule):
        selected_days = []
        if schedule.day_mon:
            selected_days.append(0)
        if schedule.day_tue:
            selected_days.append(1)
        if schedule.day_wed:
            selected_days.append(2)
        if schedule.day_thu:
            selected_days.append(3)
        if schedule.day_fri:
            selected_days.append(4)
        if schedule.day_sat:
            selected_days.append(5)
        if schedule.day_sun:
            selected_days.append(6)
        return selected_days

class NutrPlanningLine(models.TransientModel):
    _name = 'gym.nutr.plan.wizard.line'
    _description = 'Nutrition Planning Wizard Line'

    nutr_wizard_id = fields.Many2one('gym.nutr.plan.wizard', string='Nuitrition Wizard', 
                                   required=True)

    nutr_meal_type_id = fields.Many2one("gym.nutr.meal.type", string="Meal Type", required=True,
                            )
    nutr_meal_note = fields.Text("Note", required=True)