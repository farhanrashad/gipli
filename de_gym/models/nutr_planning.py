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

NUTR_STATUS = [
    ('upcoming', 'Upcoming'),
    ('session', 'In session'),
    ('completed', 'Completed'),
    ('cancel', 'Cancel')
]

class NutrPlanning(models.Model):
    _name = 'gym.nutr.planning'
    _description = 'Nutrition Planning'
    _order = 'member_id, date'
    _rec_name = 'member_id'
    _check_company_auto = True

    member_id = fields.Many2one('res.partner', 'Member', store=True, required=True)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)
    nutr_planning_line = fields.One2many('gym.nutr.planning.line', 'nutr_planning_id', string='Nuitrition Plan Line')
    date = fields.Date('Date', required=True)    
    date_start = fields.Date("Start Date", compute='_compute_datetime', 
                             readonly=False, store=True, required=True, copy=True)
    date_end = fields.Date("End Date", compute='_compute_datetime', 
                           readonly=False, store=True, required=True, copy=True)
    

    state = fields.Selection(
        string='Status',
        selection=STATES,
        default='draft',
        store=True, index='btree_not_null', tracking=True,
    )

    day_plan_count = fields.Integer(string='Daily Plan', compute='_compute_daily_plan_count')
    week_plan_count = fields.Integer(string='Daily Plan', compute='_compute_weekly_plan_count')
    
    # Compute Methods
    def _compute_daily_plan_count(self):
        for plan in self:
            plan.day_plan_count = len(self.nutr_planning_line.filtered(lambda x: x.plan_mode == 'day'))

    def _compute_weekly_plan_count(self):
        for plan in self:
            plan.week_plan_count = len(self.nutr_planning_line.filtered(lambda x: x.plan_mode == 'week'))
            
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
        action = self.env.ref('de_gym.action_nutr_plan_wizard').read()[0]
        action.update({
            'name': 'Nuitrition Plan',
            'view_mode': 'form',
            'res_model': 'gym.nutr.plan.wizard',
            'type': 'ir.actions.act_window',
            'context': {
                'default_nutr_planning_id': self.id,
            },
        })
        return action
        
    def button_draft(self):
        for plan in self:
            plan.nutr_planning_line.unlink()
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
    

    def open_weekly_plan(self):
        action = self.env.ref('de_gym.action_workout_planning_line_weekly').read()[0]
        action.update({
            'name': 'Weekly Nuitrition Plan',
            'view_mode': 'tree,form',
            'res_model': 'gym.nutr.planning.line',
            'type': 'ir.actions.act_window',
            'domain': [('nutr_planning_id', '=', self.id),('plan_mode', '=', 'week')],
            'context': {
                'create': 0,
                'edit': 1,
            },
        })
        return action

    def open_daily_plan(self):
        action = self.env.ref('de_gym.action_workout_planning_line_daily').read()[0]
        action.update({
            'name': 'Weekly Nuitrition Plan',
            'view_mode': 'tree,form',
            'res_model': 'gym.nutr.planning.line',
            'type': 'ir.actions.act_window',
            'domain': [('nutr_planning_id', '=', self.id),('plan_mode', '=', 'day')],
            'context': {
                'create': 0,
                'edit': 1,
            },
        })
        return action
            
class NutrPlanningLine(models.Model):
    _name = 'gym.nutr.planning.line'
    _description = 'Nutrition Planning Line'

    nutr_planning_id = fields.Many2one('gym.nutr.planning', string='Nuitrition Plan', 
                                   required=True, ondelete='cascade')

    nutr_meal_type_id = fields.Many2one("gym.nutr.meal.type", string="Meal Type", required=True,
                            )
    nutr_meal_note = fields.Text("Note", required=True)
    
    date = fields.Date('Date', readonly=True)
    day_of_week = fields.Selection(
        string='Day of Week',
        selection=DAY_SELECTION,
        store=True, readonly=True,
        compute='_compute_day_of_week',
    )
    
    plan_mode = fields.Selection([
        ('day', 'Daily'),  
        ('week', 'Weekly'), 
    ], 
        string='Mode', required=True, default="week",
    )
    status = fields.Selection(
        string='Status',
        selection=NUTR_STATUS,
        compute='_compute_status',
        search='_search_status',
        group_expand='_group_expand_states',
    )

    @api.depends('date')
    def _compute_day_of_week(self):
        for record in self:
            if record.date:
                record.day_of_week = str(record.date.weekday())

    @api.depends('date')
    def _compute_status(self):
        current_datetime = fields.Datetime.now()
        for record in self:
            if record.date:
                if record.date > current_datetime.date():
                    record.status = 'upcoming'
                elif record.date == current_datetime.date():
                    record.status = 'session'
                else:
                    record.status = 'completed'
            else:
                record.status = False


