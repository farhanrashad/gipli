# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import random

from babel.dates import format_date
from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.release import version


class AdmissionRegister(models.Model):
    _name = "oe.admission.register"
    _description = "Admission Register"
    _order = "name asc"

    READONLY_STATES = {
        'progress': [('readonly', True)],
        'close': [('readonly', True)],
        'cancel': [('readonly', True)],
    }


    active = fields.Boolean(default=True)
    name = fields.Char(string='Name', required=True, index='trigram', translate=True,  states=READONLY_STATES,)
    color = fields.Integer(string='Color Index', help="The color of the channel")
    school_year_id = fields.Many2one('oe.school.year',string='Academic Year',  
                        required=True, readonly=False, store=True, 
                        default=lambda self: self.env['oe.school.year'].search([('active','=',True)], limit=1),
                        compute='_compute_year', states=READONLY_STATES,)
    date_start = fields.Date(string='Start Date',  compute='_compute_all_dates', store=True, readonly=False, required=True, states=READONLY_STATES,)
    date_end = fields.Date(string='End Date',  compute='_compute_all_dates', store=True, readonly=False, required=True, states=READONLY_STATES,)
    max_students = fields.Integer(string='Maximum Admissions', store=True, states=READONLY_STATES,
                                        help='Expected number of students for this course after new admission.')
    min_students = fields.Integer(string="Minimum Admission", store=True,  states=READONLY_STATES,
                                  help='Number of minimum students expected for this course.')
    no_of_applicants = fields.Integer(string='Total Applicants', help='Number of new applications you expect to enroll.', compute='_compute_all_admission')
    no_of_enrolled = fields.Integer(string='Total Enrolled', help='Number of new admission you expect to enroll.', compute='_compute_all_admission')
        
    description = fields.Html(string='Description')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        "res.currency", string="Currency",
        related='company_id.currency_id', readonly=True)
    course_id = fields.Many2one('oe.school.course', string='Course', required=True, readonly=False, states=READONLY_STATES,)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('progress', 'Open'),
        ('close', 'Closed'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    opportunities_count = fields.Integer(
        string='# Opportunities', compute='_compute_opportunities_data')
    opportunities_amount = fields.Monetary(
        string='Opportunities Revenues', compute='_compute_opportunities_data')

    dashboard_graph_data = fields.Text(compute='_compute_dashboard_graph')

    
    def _compute_opportunities_data(self):
        opportunity_data = self.env['oe.admission']._read_group([
            ('team_id', 'in', self.ids),
            ('type', '=', 'opportunity'),
        ], ['expected_revenue:sum', 'team_id'], ['team_id'])
        counts = {datum['team_id'][0]: datum['team_id_count'] for datum in opportunity_data}
        amounts = {datum['team_id'][0]: datum['expected_revenue'] for datum in opportunity_data}
        for team in self:
            team.opportunities_count = counts.get(team.id, 0)
            team.opportunities_amount = amounts.get(team.id, 0)
    
    def _compute_all_admission(self):
        admission_ids = self.env['oe.admission']
        for ar in self:
            admission_ids = self.env['oe.admission'].search([('admission_register_id','=',ar.id),('active','=',True)])
            ar.write({
                'no_of_applicants': len(admission_ids), 
                'no_of_enrolled': len(admission_ids.filtered(lambda x:x.stage_id.is_close)),
            })

    def _compute_year(self):
        year_id = self.env['oe.school.year'].search([('active','=',True)],limit=1)
        for record in self:
            record.school_year_id = year_id.id

    @api.onchange('school_year_id')
    def _onchange_school_year(self):
        if self.school_year_id:
            self.date_start = self.school_year_id.date_start
            self.date_end = self.school_year_id.date_end

    @api.depends('school_year_id')
    def _compute_all_dates(self):
        for record in self:
            record.date_start = record.school_year_id.date_start
            record.date_end = record.school_year_id.date_end

    def unlink(self):
        for record in self:
            if record.state != 'draft' and record.no_of_applicants > 0:
                raise exceptions.UserError("You cannot delete a record with applicants when the status is not 'Draft'.")
        return super(YourModel, self).unlink()

    def button_draft(self):
        self.write({'state': 'draft'})
        return {}

    def button_open(self):
        self.write({'state': 'progress'})
        return {}

    def button_close(self):
        self.write({'state': 'close'})
        return {}
        
    def button_cancel(self):
        self.write({'state': 'draft'})
        return {}


    # -----------------------------------------------------------------
    # ----------------------- graph -----------------------------------
    # -----------------------------------------------------------------
    def _compute_dashboard_graph(self):
        for team in self:
            team.dashboard_graph_data = json.dumps(team._get_dashboard_graph_data())
            
    def _graph_get_model(self):
        return 'oe.admission'

    

    def _graph_get_dates(self, today):
        """ return a coherent start and end date for the dashboard graph covering a month period grouped by week.
        """
        start_date = today - relativedelta(months=1)
        # we take the start of the following week if we group by week
        # (to avoid having twice the same week from different month)
        start_date += relativedelta(days=8 - start_date.isocalendar()[2])
        return [start_date, today]

    def _graph_date_column(self):
        return 'create_date'

    def _graph_x_query(self):
        return 'EXTRACT(WEEK FROM %s)' % self._graph_date_column()

    def _graph_y_query(self):
        return 'count(*)'
        #return super(AdmissionTeam,self)._graph_y_query()

    def _extra_sql_conditions(self):
        return ''

    def _graph_title_and_key(self):
        """ Returns an array containing the appropriate graph title and key respectively.

            The key is for lineCharts, to have the on-hover label.
        """
        return ['', '']

    def _graph_data(self, start_date, end_date):
        """ return format should be an iterable of dicts that contain {'x_value': ..., 'y_value': ...}
            x_values should be weeks.
            y_values are floats.
        """
        query = """SELECT %(x_query)s as x_value, %(y_query)s as y_value
                     FROM %(table)s
                    WHERE team_id = %(team_id)s
                      AND DATE(%(date_column)s) >= %(start_date)s
                      AND DATE(%(date_column)s) <= %(end_date)s
                      %(extra_conditions)s
                    GROUP BY x_value;"""

        # apply rules
        dashboard_graph_model = self._graph_get_model()
        GraphModel = self.env[dashboard_graph_model]
        graph_table = GraphModel._table
        extra_conditions = self._extra_sql_conditions()
        where_query = GraphModel._where_calc([])
        GraphModel._apply_ir_rules(where_query, 'read')
        from_clause, where_clause, where_clause_params = where_query.get_sql()
        if where_clause:
            extra_conditions += " AND " + where_clause

        query = query % {
            'x_query': self._graph_x_query(),
            'y_query': self._graph_y_query(),
            'table': graph_table,
            'team_id': "%s",
            'date_column': self._graph_date_column(),
            'start_date': "%s",
            'end_date': "%s",
            'extra_conditions': extra_conditions
        }

        self._cr.execute(query, [self.id, start_date, end_date] + where_clause_params)
        return self.env.cr.dictfetchall()

    def _get_dashboard_graph_data(self):
        def get_week_name(start_date, locale):
            """ Generates a week name (string) from a datetime according to the locale:
                E.g.: locale    start_date (datetime)      return string
                      "en_US"      November 16th           "16-22 Nov"
                      "en_US"      December 28th           "28 Dec-3 Jan"
            """
            if (start_date + relativedelta(days=6)).month == start_date.month:
                short_name_from = format_date(start_date, 'd', locale=locale)
            else:
                short_name_from = format_date(start_date, 'd MMM', locale=locale)
            short_name_to = format_date(start_date + relativedelta(days=6), 'd MMM', locale=locale)
            return short_name_from + '-' + short_name_to

        self.ensure_one()
        values = []
        today = fields.Date.from_string(fields.Date.context_today(self))
        start_date, end_date = self._graph_get_dates(today)
        graph_data = self._graph_data(start_date, end_date)
        x_field = 'label'
        y_field = 'value'

        # generate all required x_fields and update the y_values where we have data for them
        locale = self._context.get('lang') or 'en_US'

        weeks_in_start_year = int(date(start_date.year, 12, 28).isocalendar()[1]) # This date is always in the last week of ISO years
        week_count = (end_date.isocalendar()[1] - start_date.isocalendar()[1]) % weeks_in_start_year + 1
        for week in range(week_count):
            short_name = get_week_name(start_date + relativedelta(days=7 * week), locale)
            values.append({x_field: short_name, y_field: 0, 'type': 'future' if week + 1 == week_count else 'past'})

        for data_item in graph_data:
            index = int((data_item.get('x_value') - start_date.isocalendar()[1]) % weeks_in_start_year)
            values[index][y_field] = data_item.get('y_value')

        [graph_title, graph_key] = self._graph_title_and_key()
        color = '#875A7B' if '+e' in version else '#7c7bad'

        # If no actual data available, show some sample data
        if not graph_data:
            graph_key = _('Sample data')
            for value in values:
                value['type'] = 'o_sample_data'
                # we use unrealistic values for the sample data
                value['value'] = random.randint(0, 20)
        return [{'values': values, 'area': True, 'title': graph_title, 'key': graph_key, 'color': color}]

    
    # -----------------------------------------------------------------
    # ----------------------- Action buttons- --------------------------
    # ------------------------------------------------------------------
    def action_open_admission_register(self):
        self.ensure_one()
        return {
            'name': 'Admission',
            'view_type': 'form',
            'view_mode': 'kanban',
            'res_model': 'oe.admission',
            'type': 'ir.actions.act_window',
        }
    def action_open_team_admissions_pending(self):
        self.ensure_one()
        return {
            'name': 'Admission',
            'view_type': 'form',
            'view_mode': 'kanban',
            'res_model': 'oe.admission',
            'type': 'ir.actions.act_window',
        }
    def action_open_team_admissions_confirm(self):
        self.ensure_one()
        return {
            'name': 'Admission',
            'view_type': 'form',
            'view_mode': 'kanban',
            'res_model': 'oe.admission',
            'type': 'ir.actions.act_window',
        }

    def action_open_new_admissions(self):
        self.ensure_one()
        return {
            'name': 'Admission',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'oe.admission',
            'type': 'ir.actions.act_window',
        }

    def admission_activity_report_action_team(self):
        self.ensure_one()
        return {
            'name': 'Admission Activities',
            'view_mode': 'graph,pivot,tree',
            'res_model': 'oe.admission.activity.report',
            'type': 'ir.actions.act_window',
        }
        
    def action_admin_config(self):
        self.ensure_one()
        return {
            'name': self.name,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'views': [[False, "form"]],
            'res_model': 'oe.admission.team',
            'res_id': self.id,
        }

    def action_edit_admissions_team(self):
        return {
           'name': 'Admission Team',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.id,
            'res_model': 'oe.admission.team',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    
            
