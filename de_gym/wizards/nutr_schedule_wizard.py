# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from datetime import datetime
from datetime import timedelta

from odoo.exceptions import UserError, ValidationError

class NutrScheduleWizard(models.TransientModel):
    _name = "gym.nutr.schedule.wizard"
    _description = 'Nuitrition Schedule Wizard'

    date_start = fields.Date("Start Date", compute='_compute_datetime', readonly=False, required=True, copy=True)
    date_end = fields.Date("End Date", compute='_compute_datetime', readonly=False, required=True, copy=True)
    member_id = fields.Many2one('res.partner', 'Member', store=True, required=True)
    
    day_mon = fields.Boolean('Monday')
    day_tue = fields.Boolean('Tuesday')
    day_wed = fields.Boolean('Wednesday')
    day_thu = fields.Boolean('Thursday')
    day_fri = fields.Boolean('Friday')
    day_sat = fields.Boolean('Saturday')
    day_sun = fields.Boolean('Sunday')

    schedule_wizard_line = fields.One2many('gym.nutr.schedule.wizard.line', 'schedule_wizard_id', string='Schedule Wizard Line')

    @api.onchange('member_id')
    def _compute_datetime(self):
        for record in self:
            record.date_start = fields.Date.today()
            date_start_str = record.date_start.strftime("%Y-%m-%d")  # Convert date to string
            date_start = datetime.strptime(date_start_str, "%Y-%m-%d")
            end_of_month = date_start.replace(day=1) + relativedelta(months=1, days=-1)
            record.date_end = end_of_month.strftime('%Y-%m-%d')

    def action_create_schedule(self):
        for schedule in self:
            if schedule.date_start and schedule.date_end:
                schedule_data = []
                schedule_line = []
                current_date = schedule.date_start
                for line in schedule.schedule_wizard_line:
                    schedule_line = [(0, 0, {
                        'nutr_meal_type_id': line.nutr_meal_type_id.id,
                        'nutr_meal_note': line.nutr_meal_note,
                    })]
                while current_date <= schedule.date_end:
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

                try:
                    self.env['gym.schedule.nutr'].create(schedule_data)
                except:
                    pass

    def _prepare_schedule_values(self, date, weekday):
        schedule_line = []
        for line in self.schedule_wizard_line:
            schedule_line.append((0, 0, {
                'nutr_meal_type_id': line.nutr_meal_type_id.id,
                'nutr_meal_note': line.nutr_meal_note,
            }))
        return {
            'date': date,
            'day_of_week': str(date.weekday()),
            'member_id': self.member_id.id,
            'nutr_schedule_line': schedule_line ,
        }
                    


class NutrScheduleWizardLine(models.TransientModel):
    _name = "gym.nutr.schedule.wizard.line"
    _description = 'Nuitrition Schedule Wizard Line'

    schedule_wizard_id = fields.Many2one('gym.nutr.schedule.wizard', string='Schedule Wizard', 
                                   required=True, )
    nutr_meal_type_id = fields.Many2one("gym.nutr.meal.type", string="Meal Type", required=True,
                            )
    nutr_meal_note = fields.Text("Note", required=True)