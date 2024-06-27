# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from datetime import datetime, date, time
from dateutil.relativedelta import relativedelta
import pytz

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools import format_date


class FeeslipStudents(models.TransientModel):
    _name = 'oe.feeslip.students'
    _description = 'Generate feeslips for all selected students'

    def _get_available_student_domain(self):
        return [('is_student', '=', True)]

    def _get_students(self):
        active_student_ids = self.env.context.get('active_student_ids', False)
        if active_student_ids:
            return self.env['res.partner'].browse(active_student_ids)
        # YTI check dates too
        return self.env['res.partner'].search(self._get_available_student_domain())

    student_ids = fields.Many2many('res.partner', 'oe_student_group_rel', 'feeslip_id', 'student_id', 'Students',
                                    default=lambda self: self._get_students(), required=True,
                                    #compute='_compute_student_ids', 
                                   store=True, readonly=False)
    fee_struct_id = fields.Many2one('oe.fee.struct', string='Fee Structure')
    #department_id = fields.Many2one('hr.department')

    #@api.depends('department_id')
    def _compute_employee_ids(self):
        for wizard in self:
            domain = wizard._get_available_contracts_domain()
            if wizard.department_id:
                domain = expression.AND([
                    domain,
                    [('department_id', 'child_of', self.department_id.id)]
                ])
            wizard.employee_ids = self.env['hr.employee'].search(domain)

    def _check_undefined_slots(self, work_entries, feeslip_run):
        """
        Check if a time slot in the contract's calendar is not covered by a work entry
        """
        work_entries_by_contract = defaultdict(lambda: self.env['hr.work.entry'])
        for work_entry in work_entries:
            work_entries_by_contract[work_entry.contract_id] |= work_entry

        for contract, work_entries in work_entries_by_contract.items():
            if contract.work_entry_source != 'calendar':
                continue
            calendar_start = pytz.utc.localize(datetime.combine(max(contract.date_start, feeslip_run.date_start), time.min))
            calendar_end = pytz.utc.localize(datetime.combine(min(contract.date_end or date.max, feeslip_run.date_end), time.max))
            outside = contract.resource_calendar_id._attendance_intervals_batch(calendar_start, calendar_end)[False] - work_entries._to_intervals()
            if outside:
                time_intervals_str = "\n - ".join(['', *["%s -> %s" % (s[0], s[1]) for s in outside._items]])
                raise UserError(_("Some part of %s's calendar is not covered by any work entry. Please complete the schedule. Time intervals to look for:%s") % (contract.employee_id.name, time_intervals_str))

    def _filter_contracts(self, contracts):
        # Could be overriden to avoid having 2 'end of the year bonus' feeslips, etc.
        return contracts

    def compute_sheet(self):
        self.ensure_one()
        if not self.env.context.get('active_id'):
            from_date = fields.Date.to_date(self.env.context.get('default_date_start'))
            end_date = fields.Date.to_date(self.env.context.get('default_date_end'))
            today = fields.date.today()
            first_day = today + relativedelta(day=1)
            last_day = today + relativedelta(day=31)
            if from_date == first_day and end_date == last_day:
                batch_name = from_date.strftime('%B %Y')
            else:
                batch_name = _('From %s to %s', format_date(self.env, from_date), format_date(self.env, end_date))
            feeslip_run = self.env['oe.feeslip.run'].create({
                'name': batch_name,
                'date_start': from_date,
                'date_end': end_date,
            })
        else:
            feeslip_run = self.env['oe.feeslip.run'].browse(self.env.context.get('active_id'))

        employees = self.with_context(active_test=False).employee_ids
        if not employees:
            raise UserError(_("You must select employee(s) to generate feeslip(s)."))

        #Prevent a feeslip_run from having multiple feeslips for the same employee
        employees -= feeslip_run.slip_ids.employee_id
        success_result = {
            'type': 'ir.actions.act_window',
            'res_model': 'oe.feeslip.run',
            'views': [[False, 'form']],
            'res_id': feeslip_run.id,
        }
        if not employees:
            return success_result

        feeslips = self.env['oe.feeslip']
        Feeslip = self.env['oe.feeslip']

        #contracts = employees._get_contracts(
        #    payslip_run.date_start, payslip_run.date_end, states=['open', 'close']
        #).filtered(lambda c: c.active)
        #contracts._generate_work_entries(payslip_run.date_start, payslip_run.date_end)
        #work_entries = self.env['hr.work.entry'].search([
        #    ('date_start', '<=', payslip_run.date_end),
        #    ('date_stop', '>=', payslip_run.date_start),
        #    ('employee_id', 'in', employees.ids),
        #])
        #self._check_undefined_slots(work_entries, payslip_run)

        if(self.structure_id.type_id.default_struct_id == self.structure_id):
            work_entries = work_entries.filtered(lambda work_entry: work_entry.state != 'validated')
            if work_entries._check_if_error():
                work_entries_by_contract = defaultdict(lambda: self.env['hr.work.entry'])

                for work_entry in work_entries.filtered(lambda w: w.state == 'conflict'):
                    work_entries_by_contract[work_entry.contract_id] |= work_entry

                for contract, work_entries in work_entries_by_contract.items():
                    conflicts = work_entries._to_intervals()
                    time_intervals_str = "\n - ".join(['', *["%s -> %s" % (s[0], s[1]) for s in conflicts._items]])
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Some work entries could not be validated.'),
                        'message': _('Time intervals to look for:%s', time_intervals_str),
                        'sticky': False,
                    }
                }


        default_values = Feeslip.default_get(Feeslip.fields_get())
        feeslips_vals = []
        for contract in self._filter_contracts(contracts):
            values = dict(default_values, **{
                'name': _('New Feeslip'),
                'employee_id': contract.employee_id.id,
                'feeslip_run_id': feeslip_run.id,
                'date_from': feeslip_run.date_start,
                'date_to': feeslip_run.date_end,
                'contract_id': contract.id,
                'struct_id': self.structure_id.id or contract.structure_type_id.default_struct_id.id,
            })
            feeslips_vals.append(values)
        feeslips = Feeslip.with_context(tracking_disable=True).create(feeslips_vals)
        feeslips._compute_name()
        feeslips.compute_sheet()
        feeslip_run.state = 'verify'

        return success_result
