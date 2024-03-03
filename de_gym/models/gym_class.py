# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from datetime import datetime
from datetime import timedelta


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
    

    date_start = fields.Date("Start Date", compute='_compute_datetime', readonly=False, required=True, copy=True)
    date_end = fields.Date("End Date", compute='_compute_datetime', readonly=False, required=True, copy=True)

    time_from = fields.Float(
        'From Time',
        default=0.0,
        required=True,
    )
    time_to = fields.Float(
        'Quantity',
        default=0.0,
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
    @api.onchange('trainer_id')
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
            pass

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

    @api.depends('date')
    def _compute_day_of_week(self):
        for record in self:
            if record.date:
                record.day_of_week = str(record.date.weekday())
            else:
                record.day_of_week = False