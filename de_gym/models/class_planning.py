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

class GYMClassPlanning(models.Model):
    _name = 'gym.class.planning'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'GYM Class'
    _order = 'trainer_id, date_start desc'
    #_rec_name = 'class_type_id'
    _check_company_auto = True

    name = fields.Char(string='Reference', compute='_compute_name')
    
    class_type_id = fields.Many2one('gym.class.type', 'Class Type', store=True, required=True)
    trainer_id = fields.Many2one('hr.employee', 'Trainer', store=True, required=True)
    sub_trainer_id = fields.Many2one('hr.employee', 'Sub Trainer', store=True)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)
    
    location = fields.Char(string='Location')
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

    day_plan_count = fields.Integer(string='Daily Plan', compute='_compute_daily_plan_count')
    week_plan_count = fields.Integer(string='Daily Plan', compute='_compute_weekly_plan_count')
    
    class_planning_line = fields.One2many('gym.class.planning.line', 'class_planning_id', string='Class Line')

    state = fields.Selection(
        string='Status',
        selection=STATES,
        default='draft',
        store=True, index='btree_not_null', tracking=True,
    )
    limit_seat = fields.Integer('Seat Limit', default=10, required=True)
    class_booking_line = fields.One2many('gym.class.booking', 'class_planning_id', string='Class booking Line')
    booking_count = fields.Integer(string="Booking Count", compute='_compute_booking_count')
    
    # Constrains
    @api.constrains('day_mon', 'day_tue', 'day_wed', 'day_thu', 'day_fri', 'day_sat', 'day_sun')
    def _check_at_least_one_selected(self):
        if not any([self.day_mon, self.day_tue, self.day_wed, self.day_thu, self.day_fri, self.day_sat, self.day_sun]):
            raise ValidationError("At least one day must be selected.")

    @api.constrains('date_start', 'date_end', 'day_mon', 'day_tue', 'day_wed', 'day_thu', 'day_fri', 'day_sat', 'day_sun')
    def _check_no_overlapping_records(self):
        for record in self:
            overlapping_records = self.env['gym.class.planning'].search([
                ('id', '!=', record.id),
                ('company_id', '=', record.company_id.id),
                ('class_type_id', '=', record.class_type_id.id),
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
                raise ValidationError("The '%s' class already planned on the same day(s) between %s and %s." % (record.class_type_id.name, record.date_start, record.date_end))


    # Compute Methods
    def _compute_name(self):
        for record in self:
            record.name = record.class_type_id.name + '/' + record.trainer_id.name + ' (' + str(record.date_start) + ' to ' + str(record.date_end) + ')'

    def _compute_daily_plan_count(self):
        for plan in self:
            plan.day_plan_count = len(self.class_planning_line.filtered(lambda x: x.plan_mode == 'day'))

    def _compute_weekly_plan_count(self):
        for plan in self:
            plan.week_plan_count = len(self.class_planning_line.filtered(lambda x: x.plan_mode == 'week'))
            
    @api.depends('class_type_id')
    def _compute_datetime(self):
        for record in self:
            record.date_start = fields.Date.today()
            date_start_str = record.date_start.strftime("%Y-%m-%d")  # Convert date to string
            date_start = datetime.strptime(date_start_str, "%Y-%m-%d")
            end_of_month = date_start.replace(day=1) + relativedelta(months=1, days=-1)
            record.date_end = end_of_month.strftime('%Y-%m-%d')

    def _compute_booking_count(self):
        for plan in self:
            plan.booking_count = len(plan.class_booking_line)
    # Actions
    def button_plan(self):
        action = self.env.ref('de_gym.action_class_plan_wizard').read()[0]
        action.update({
            'name': 'Class Planning',
            'view_mode': 'form',
            'res_model': 'gym.class.plan.wizard',
            'type': 'ir.actions.act_window',
            'context': {
                'default_class_planning_id': self.id,
            },
        })
        return action
        
    def button_plan1(self):
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
            plan.class_planning_line.unlink()
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
    def _prepare_schedule_values(self, date, weekday, time_from, time_to):
        return {
            'date': date,
            'day_of_week': str(date.weekday()),
            'time_from': time_from,
            'time_to': time_to,
            'trainer_id': self.trainer_id.id,
            'class_type_id': self.class_type_id.id,
            'class_planning_id': self.id,
        }

    def open_weekly_plan(self):
        action = self.env.ref('de_gym.action_class_planning_line_weekly').read()[0]
        action.update({
            'name': 'Weekly Class Plan',
            'view_mode': 'tree,form',
            'res_model': 'gym.class.planning.line',
            'type': 'ir.actions.act_window',
            'domain': [('class_planning_id', '=', self.id),('plan_mode', '=', 'week')],
            'context': {
                'create': 0,
                'edit': 1,
                'default_class_planning_id': self.id,
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
            'domain': [('class_planning_id', '=', self.id),('plan_mode', '=', 'day')],
            'context': {
                'create': 0,
                'edit': 1,
                'default_class_planning_id': self.id,
            },
        })
        return action

    def open_member_booking(self):
        action = self.env.ref('de_gym.action_class_booking').read()[0]
        action.update({
            'name': 'Booking',
            'view_mode': 'tree,form',
            'res_model': 'gym.class.booking',
            'type': 'ir.actions.act_window',
            'domain': [('class_planning_id', '=', self.id)],
            'context': {
                'default_class_type_id': self.class_type_id.id,
                'default_class_planning_id': self.id,
            },
        })
        return action
        
class GYMClassPlanningLine(models.Model):
    _name = 'gym.class.planning.line'
    _description = 'Schedule Class'
    _rec_name = 'class_type_id'

    class_planning_id = fields.Many2one('gym.class.planning', string='Class', 
                                   required=True, ondelete='cascade')

    trainer_id = fields.Many2one('hr.employee',
                                 compute='_compute_all_from_planning', 
                                 store=True,
                                )

    class_type_id = fields.Many2one('gym.class.type',
                                 compute='_compute_all_from_planning', 
                                 store=True,
                                )
    
    date = fields.Date('Date')
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

    plan_mode = fields.Selection([
        ('day', 'Daily'),  
        ('week', 'Weekly'), 
    ], 
        string='Mode', required=True, default="week",
    )
    
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

    @api.depends('date', 'time_from', 'time_to')
    def _compute_status(self):
        current_datetime = fields.Datetime.now()
        for record in self:
            if record.date:
                if record.date > current_datetime.date():
                    record.status = 'upcoming'
                elif record.date == current_datetime.date() and record.time_from <= current_datetime.hour and record.time_to > current_datetime.hour:
                    record.status = 'session'
                else:
                    record.status = 'completed'
            else:
                record.status = False
                
    @api.depends(
        'class_planning_id',
        'class_planning_id.trainer_id',
        'class_planning_id.class_type_id',
    )
    def _compute_all_from_planning(self):
        for line in self:
            line.trainer_id = line.class_planning_id.trainer_id.id
            line.class_type_id = line.class_planning_id.class_type_id.id

    @api.model
    def _search_status(self, operator, value):
        if operator == '=':
            return [('status', '=', value)]
        else:
            return []

    def _group_expand_states(self, states, domain, order):
        return ['upcoming', 'session','completed']


class GYMClassbooking(models.Model):
    _name = 'gym.class.booking'
    _description = 'Class Class'
    _rec_name = 'class_type_id'

    class_planning_id = fields.Many2one('gym.class.planning', string='Class', 
                                   ondelete='cascade')
    class_type_id = fields.Many2one('gym.class.type',related='class_planning_id.class_type_id')
    member_id = fields.Many2one('res.partner',
                                 required=True,
                                domain="[('is_gym_member','=',True)]"
                                )