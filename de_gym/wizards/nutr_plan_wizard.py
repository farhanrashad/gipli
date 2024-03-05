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
    
    day_mon = fields.Boolean('Monday')
    day_tue = fields.Boolean('Tuesday')
    day_wed = fields.Boolean('Wednesday')
    day_thu = fields.Boolean('Thursday')
    day_fri = fields.Boolean('Friday')
    day_sat = fields.Boolean('Saturday')
    day_sun = fields.Boolean('Sunday')

    @api.model
    def default_get(self, fields):
        res = super(NutrPlanWizard, self).default_get(fields)
        if 'nutr_planning_id' in self._context:
            res['nutr_planning_id'] = self._context.get('nutr_planning_id')
        return res
        
    def action_create_schedule(self):
        for schedule in self:
            
            schedule_data = []
            current_date = schedule.workout_planning_id.date_start
                
            if schedule.plan_mode == 'day':
                if schedule.workout_planning_id.date_start and schedule.workout_planning_id.date_end:
                    while current_date <= schedule.workout_planning_id.date_end:
                        if current_date.weekday() == 0 and schedule.day_mon:
                            schedule_data.append(self._prepare_schedule_values(current_date,current_date.weekday()))
                        if current_date.weekday() == 1 and schedule.day_tue:
                            schedule_data.append(self._prepare_schedule_values(current_date,current_date.weekday()))
                        if current_date.weekday() == 2 and schedule.day_wed:
                            schedule_data.append(self._prepare_schedule_values(current_date,current_date.weekday()))
                        if current_date.weekday() == 3 and schedule.day_thu:
                            schedule_data.append(self._prepare_schedule_values(current_date,current_date.weekday()))
                        if current_date.weekday() == 4 and schedule.day_fri:
                            schedule_data.append(self._prepare_schedule_values(current_date,current_date.weekday()))
                        if current_date.weekday() == 5 and schedule.day_sat:
                            schedule_data.append(self._prepare_schedule_values(current_date,current_date.weekday()))
                        if current_date.weekday() == 6 and schedule.day_sun:
                            schedule_data.append(self._prepare_schedule_values(current_date,current_date.weekday()))
                        
                        current_date += timedelta(days=1)
            else:
                
                if schedule.day_mon:
                    schedule_data.append(self._prepare_schedule_values(False,0))
                if schedule.day_tue:
                    schedule_data.append(self._prepare_schedule_values(False,1))
                if schedule.day_wed:
                    schedule_data.append(self._prepare_schedule_values(False,2))
                if schedule.day_thu:
                    schedule_data.append(self._prepare_schedule_values(False,3))
                if schedule.day_fri:
                    schedule_data.append(self._prepare_schedule_values(False,4))
                if schedule.day_sat:
                    schedule_data.append(self._prepare_schedule_values(False,5))
                if schedule.day_sun:
                    schedule_data.append(self._prepare_schedule_values(False,6))

            #raise UserError(schedule_data)
            #try:
            self.env['gym.nutr.planning.line'].create(schedule_data)
            #except:
            #    pass

    def _prepare_schedule_values(self, date, weekday):
        return {
            'date': date,
            'day_of_week': str(weekday),
            'member_id': self.workout_planning_id.member_id.id,
            'wo_activity_type_id': self.wo_activity_type_id.id,
            'workout_activity_id': self.workout_activity_id.id,
            'plan_mode': self.plan_mode,
            'workout_planning_id': self.workout_planning_id.id,
        }

