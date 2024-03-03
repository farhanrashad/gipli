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

CLASS_STATUS = [
    ('upcoming', 'Upcoming'),
    ('session', 'In session'),
    ('completed', 'Completed'),
    ('cancel', 'Cancel')
]

class WorkoutPlanning(models.Model):
    _name = 'gym.workout.planning'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Wrokout Planning'
    _order = 'member_id, date_start desc'
    _rec_name = 'member_id'
    _check_company_auto = True

    member_id = fields.Many2one('res.partner', 'Member', store=True, required=True)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)
    
    date_start = fields.Date("Start Date", compute='_compute_datetime', 
                             readonly=False, store=True, required=True, copy=True)
    date_end = fields.Date("End Date", compute='_compute_datetime', 
                           readonly=False, store=True, required=True, copy=True)
    
    day_mon = fields.Boolean('Monday')
    day_tue = fields.Boolean('Tuesday')
    day_wed = fields.Boolean('Wednesday')
    day_thu = fields.Boolean('Thursday')
    day_fri = fields.Boolean('Friday')
    day_sat = fields.Boolean('Saturday')
    day_sun = fields.Boolean('Sunday')

    wo_activity_type_id = fields.Many2one('gym.activity.type', string='Activity Type')
    workout_sets = fields.Integer('Sets', default=1)
    workout_reps = fields.Integer('Reps', default=1)
    workout_weight = fields.Integer('Weight (kg)', default=1)
    workout_rest = fields.Float('Rest Time')
    
    workout_planning_line = fields.One2many('gym.workout.planning.line', 'workout_planning_id', string='Workout Planning Line')

    state = fields.Selection(
        string='Status',
        selection=STATES,
        default='draft',
        store=True, index='btree_not_null', tracking=True,
    )
    
    # Constrains
    @api.constrains('day_mon', 'day_tue', 'day_wed', 'day_thu', 'day_fri', 'day_sat', 'day_sun')
    def _check_at_least_one_selected(self):
        if not any([self.day_mon, self.day_tue, self.day_wed, self.day_thu, self.day_fri, self.day_sat, self.day_sun]):
            raise ValidationError("At least one day must be selected.")

    @api.constrains('date_start', 'date_end', 'day_mon', 'day_tue', 'day_wed', 'day_thu', 'day_fri', 'day_sat', 'day_sun')
    def _check_no_overlapping_records(self):
        for record in self:
            overlapping_records = self.env['gym.workout.planning'].search([
                ('id', '!=', record.id),
                ('company_id', '=', record.company_id.id),
                ('date_start', '<=', record.date_end),
                ('date_end', '>=', record.date_start),
                '|', '|', '|',
                ('day_mon', '=', record.day_mon),
                ('day_tue', '=', record.day_tue),
                ('day_wed', '=', record.day_wed),
                ('day_thu', '=', record.day_thu),
                ('day_fri', '=', record.day_fri),
                ('day_sat', '=', record.day_sat),
                ('day_sun', '=', record.day_sun),
            ])
            if overlapping_records:
                raise ValidationError("The '%s' workout already planned on the same day(s) between %s and %s." % ('test', record.date_start, record.date_end))


    # Compute Methods
    @api.depends('member_id')
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
            
            schedule_data = []
            if plan.date_start and plan.date_end:
                current_date = plan.date_start

                while current_date <= plan.date_end:
                    if current_date.weekday() == 0 and plan.day_mon:
                        schedule_data.append(self._prepare_schedule_values(current_date,current_date.weekday()))
                    if current_date.weekday() == 1 and plan.day_tue:
                        schedule_data.append(self._prepare_schedule_values(current_date,current_date.weekday()))
                    if current_date.weekday() == 2 and plan.day_wed:
                        schedule_data.append(self._prepare_schedule_values(current_date,current_date.weekday()))
                    if current_date.weekday() == 3 and plan.day_thu:
                        schedule_data.append(self._prepare_schedule_values(current_date,current_date.weekday()))
                    if current_date.weekday() == 4 and plan.day_fri:
                        schedule_data.append(self._prepare_schedule_values(current_date,current_date.weekday()))
                    if current_date.weekday() == 5 and plan.day_sat:
                        schedule_data.append(self._prepare_schedule_values(current_date,current_date.weekday()))
                    if current_date.weekday() == 6 and plan.day_sun:
                        schedule_data.append(self._prepare_schedule_values(current_date,current_date.weekday()))
                    
                    current_date += timedelta(days=1)

                try:
                    self.env['gym.workout.planning.line'].create(schedule_data)
                    plan.write({
                        'state': 'review',
                    })
                except:
                    pass
                
                
    def button_draft(self):
        for plan in self:
            plan.class_line.unlink()
            plan.write({
                'state': 'draft',
            })

    def button_confirm(self):
        for plan in self:
            plan.write({
                'state': 'progress',
            })
    def button_cancel(self):
        for plan in self:
            plan.write({
                'state': 'cancel',
            })
    def _prepare_schedule_values(self, date, weekday):
        return {
            'date': date,
            'day_of_week': str(date.weekday()),
            'member_id': self.member_id.id,
            'workout_planning_id': self.id,
            'wo_activity_type_id': self.wo_activity_type_id.id,
        }

    def open_schedule_lines(self):
        return {
            'name': 'Schedule Lines',
            'view_mode': 'tree,calendar',
            'res_model': 'gym.class.planning.line',
            'type': 'ir.actions.act_window',
            'domain': [('workout_planning_id','=',self.id)],
            'action_id': self.env.ref('de_gym.action_class_planning_line').id,
        }

    def open_member_booking(self):
        action = self.env.ref('de_gym.action_class_booking').read()[0]
        action.update({
            'name': 'Booking',
            'view_mode': 'tree,form',
            'res_model': 'gym.class.booking',
            'type': 'ir.actions.act_window',
            'domain': [('workout_planning_id', '=', self.id)],
            'context': {
                'default_workout_planning_id': self.id,
            },
        })
        return action
        
class WorkoutPlanningLine(models.Model):
    _name = 'gym.workout.planning.line'
    _description = 'Workout Planning Line'

    workout_planning_id = fields.Many2one('gym.workout.planning', string='Workout Planning', 
                                   required=True, ondelete='cascade')

    member_id = fields.Many2one('res.partner',
                                 compute='_compute_all_from_planning', 
                                 store=True,
                                )
    
    date = fields.Date('Date', required=True)
    day_of_week = fields.Selection(
        string='Day of Week',
        selection=DAY_SELECTION,
        compute='_compute_day_of_week', store=True, 
    )
    wo_activity_type_id = fields.Many2one('gym.activity.type', string='Activity Type')
    status = fields.Selection(
        string='Status',
        selection=CLASS_STATUS,
        compute='_compute_status',
        search='_search_status',
        group_expand='_group_expand_states',
    )
    
    @api.depends('date')
    def _compute_day_of_week(self):
        for record in self:
            if record.date:
                record.day_of_week = str(record.date.weekday())
            else:
                record.day_of_week = False

    @api.depends('date')
    def _compute_status(self):
        current_datetime = fields.Datetime.now()
        for record in self:
            if record.date > current_datetime.date():
                record.status = 'upcoming'
            elif record.date == current_datetime.date():
                record.status = 'session'
            else:
                record.status = 'completed'
                
    @api.depends(
        'workout_planning_id',
        'workout_planning_id.member_id',
    )
    def _compute_all_from_planning(self):
        for line in self:
            line.member_id = line.workout_planning_id.member_id.id

    @api.model
    def _search_status(self, operator, value):
        if operator == '=':
            return [('status', '=', value)]
        else:
            return []

    def _group_expand_states(self, states, domain, order):
        return ['upcoming', 'session','completed']