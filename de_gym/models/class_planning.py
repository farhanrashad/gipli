# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from datetime import datetime
from datetime import timedelta
from odoo.exceptions import UserError, ValidationError


DAY_SELECTION = [
    ('0', 'Monday'),
    ('1', 'Tuesday'),
    ('2', 'Wednesday'),
    ('3', 'Thursday'),
    ('4', 'Friday'),
    ('5', 'Saturday'),
    ('6', 'Sunday'),
]

STATES = [
    ('draft', 'New'),  
    ('review', 'Review'),
    ('progress', 'Running'),
    ('paused', 'Paused'),
    ('close', 'Close'),
    ('cancel', 'Cancel'),
]

class GYMClassPlanning(models.Model):
    _name = 'gym.class.planning'
    _description = 'GYM Class'
    _order = 'trainer_id, date_start desc'
    _rec_name = 'trainer_id'
    _check_company_auto = True

    class_type_id = fields.Many2one('gym.class.type', 'Class Type', store=True, required=True)
    trainer_id = fields.Many2one('hr.employee', 'Trainer', store=True, required=True)
    sub_trainer_id = fields.Many2one('hr.employee', 'Sub Trainer', store=True)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)
    
    location = fields.Char(string='Location')
    date_start = fields.Date("Start Date", compute='_compute_datetime', 
                             readonly=False, store=True, required=True, copy=True)
    date_end = fields.Date("End Date", compute='_compute_datetime', 
                           readonly=False, store=True, required=True, copy=True)

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
    
    day_mon = fields.Boolean('Monday')
    day_tue = fields.Boolean('Tuesday')
    day_wed = fields.Boolean('Wednesday')
    day_thu = fields.Boolean('Thursday')
    day_fri = fields.Boolean('Friday')
    day_sat = fields.Boolean('Saturday')
    day_sun = fields.Boolean('Sunday')
    
    class_line = fields.One2many('gym.class.planning.line', 'class_planning_id', string='Class Line')

    state = fields.Selection(
        string='Status',
        selection=STATES,
        default='draft',
        store=True, index='btree_not_null', tracking=True,
    )


    # Compute Methods
    @api.depends('class_type_id')
    def _compute_datetime(self):
        for record in self:
            record.date_start = fields.Date.today()
            date_start_str = record.date_start.strftime("%Y-%m-%d")  # Convert date to string
            date_start = datetime.strptime(date_start_str, "%Y-%m-%d")
            end_of_month = date_start.replace(day=1) + relativedelta(months=1, days=-1)
            record.date_end = end_of_month.strftime('%Y-%m-%d')

    # Actions
    def button_plan(self):
        for plan in self:
            #raise UserError(plan.time_from)
            if plan.time_from <= 0 or plan.time_to <=0 :
                raise UserError('Please define the correct class time.')

            schedule_data = []
            if plan.date_start and plan.date_end:
                current_date = plan.date_start

                while current_date <= plan.date_end:
                    if current_date.weekday() == 0 and plan.day_mon:
                        schedule_data.append(self._prepare_schedule_values(current_date,current_date.weekday(), plan.time_from, plan.time_to))
                    if current_date.weekday() == 1 and plan.day_tue:
                        schedule_data.append(self._prepare_schedule_values(current_date,current_date.weekday(), plan.time_from, plan.time_to))
                    if current_date.weekday() == 2 and plan.day_wed:
                        schedule_data.append(self._prepare_schedule_values(current_date,current_date.weekday(), plan.time_from, plan.time_to))
                    if current_date.weekday() == 3 and plan.day_thu:
                        schedule_data.append(self._prepare_schedule_values(current_date,current_date.weekday(), plan.time_from, plan.time_to))
                    if current_date.weekday() == 4 and plan.day_fri:
                        schedule_data.append(self._prepare_schedule_values(current_date,current_date.weekday(), plan.time_from, plan.time_to))
                    if current_date.weekday() == 5 and plan.day_sat:
                        schedule_data.append(self._prepare_schedule_values(current_date,current_date.weekday(), plan.time_from, plan.time_to))
                    if current_date.weekday() == 6 and plan.day_sun:
                        schedule_data.append(self._prepare_schedule_values(current_date,current_date.weekday(), plan.time_from, plan.time_to))
                    
                    current_date += timedelta(days=1)

                try:
                    self.env['gym.class.planning.line'].create(schedule_data)
                    plan.write({
                        'state': 'review',
                    })
                except:
                    pass
                
                
    def button_draft(self):
        for plan in self:
            plan.write({
                'state': 'draft',
            })

    def _prepare_schedule_values(self, date, weekday, time_from, time_to):
        return {
            'date': date,
            'day_of_week': str(date.weekday()),
            'time_from': time_from,
            'time_to': time_to,
            'class_planning_id': self.id,
        }
class GYMClassPlanningLine(models.Model):
    _name = 'gym.class.planning.line'
    _description = 'Schedule Class'

    class_planning_id = fields.Many2one('gym.class.planning', string='Class', 
                                   required=True, ondelete='cascade')

    date = fields.Date('Date', required=True)
    day_of_week = fields.Selection(
        string='Day of Week',
        selection=DAY_SELECTION,
        compute='_compute_day_of_week', store=True, 
    )
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

    _sql_constraints = [
        ('unique_member_date', 'UNIQUE(class_planning_id, date, time_from)', 'Class timing cannot overlapped.')
    ]


    @api.depends('date')
    def _compute_day_of_week(self):
        for record in self:
            if record.date:
                record.day_of_week = str(record.date.weekday())
            else:
                record.day_of_week = False