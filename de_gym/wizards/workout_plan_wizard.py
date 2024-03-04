# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from datetime import datetime
from datetime import timedelta

from odoo.exceptions import UserError, ValidationError

class WrokoutPlanWizard(models.TransientModel):
    _name = "gym.workout.plan.wizard"
    _description = 'Workout Plan Wizard'

    workout_planning_id = fields.Many2one('gym.workout.planning', string='Workout Plan', copy=False, readonly=True)
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

    wo_activity_type_id = fields.Many2one('gym.activity.type', string='Activity Type', required=True)
    workout_activity_id = fields.Many2one('gym.workout.activity', 
                                          string='Activity', required=True,
                                          domain="[('wo_activity_type_id','=',wo_activity_type_id)]"
                                         )
    
    workout_sets = fields.Integer('Sets', default=1)
    workout_reps = fields.Integer('Reps', default=1)
    workout_weight = fields.Integer('Weight (kg)', default=1)
    workout_rest = fields.Float('Rest Time')

    


    @api.model
    def default_get(self, fields):
        res = super(WrokoutPlanWizard, self).default_get(fields)
        if 'workout_planning_id' in self._context:
            res['workout_planning_id'] = self._context.get('workout_planning_id')
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
            self.env['gym.workout.planning.line'].create(schedule_data)
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