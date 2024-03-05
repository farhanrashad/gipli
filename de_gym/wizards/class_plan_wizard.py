# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from datetime import datetime
from datetime import timedelta

from odoo.exceptions import UserError, ValidationError

class ClassPlanWizard(models.TransientModel):
    _name = "gym.class.plan.wizard"
    _description = 'Class Plan Wizard'

    class_planning_id = fields.Many2one('gym.class.planning', string='Class Plan', copy=False, readonly=True)
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

    time_from = fields.Float(
        'From Time',
        default=9.0,
        required=True,
    )
    time_to = fields.Float(
        'To Time',
        default=10.0,
        required=True,
    )

    @api.model
    def default_get(self, fields):
        res = super(ClassPlanWizard, self).default_get(fields)
        if 'class_planning_id' in self._context:
            res['class_planning_id'] = self._context.get('class_planning_id')
        return res
        
    

    def action_create_schedule(self):
        for schedule in self:
            
            schedule_data = []
            current_date = schedule.class_planning_id.date_start
                
            if schedule.plan_mode == 'day':
                if schedule.class_planning_id.date_start and schedule.class_planning_id.date_end:
                    while current_date <= schedule.class_planning_id.date_end:
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
            self.env['gym.class.planning.line'].create(schedule_data)
            if self.plan_mode == 'week':
                self.open_weekly_plan()
            else:
                self.open_daily_plan
                
            #except:
            #    pass

    def _prepare_schedule_values(self, date, weekday):
        return {
            'date': date,
            'day_of_week': str(weekday),
            'trainer_id': self.class_planning_id.trainer_id.id,
            'plan_mode': self.plan_mode,
            'class_planning_id': self.class_planning_id.id,
            'time_from': self.time_from,
            'time_to': self.time_to,
        }

    def open_weekly_plan(self):
        action = self.env.ref('de_gym.action_class_planning_line_weekly').read()[0]
        action.update({
            'name': 'Weekly Class Plan',
            'view_mode': 'tree,form',
            'res_model': 'gym.class.planning.line',
            'type': 'ir.actions.act_window',
            'domain': [('class_planning_id', '=', self.class_planning_id.id),('plan_mode', '=', 'week')],
            'context': {
                'create': 0,
                'edit': 1,
                'default_class_planning_id': self.class_planning_id.id,
            },
        })
        return action
        
    def open_daily_plan(self):
        action = self.env.ref('de_gym.action_class_planning_line_daily').read()[0]
        action.update({
            'name': 'Weekly Class Plan',
            'view_mode': 'tree,form',
            'res_model': 'gym.class.planning.line',
            'type': 'ir.actions.act_window',
            'domain': [('class_planning_id', '=', self.class_planning_id.id),('plan_mode', '=', 'day')],
            'context': {
                'create': 0,
                'edit': 1,
                'default_class_planning_id': self.class_planning_id.id,
            },
        })
        return action