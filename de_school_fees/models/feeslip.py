# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import logging

from collections import defaultdict
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, Command, fields, models, _
from odoo.addons.de_school_fees.models.browsable_object import BrowsableObject, InputFees, OrderFeeLines, Feeslips, ResultRules
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round, date_utils, convert_file, html2plaintext
from odoo.tools.float_utils import float_compare
from odoo.tools.misc import format_date
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class FeeSlip(models.Model):
    _name = 'oe.feeslip'
    _description = 'Fee Slip'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    _order = 'date_to desc'

    fee_struct_id = fields.Many2one(
        'oe.fee.struct', string='Fee Structure',
        compute='_compute_struct_id', store=True, readonly=False,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)], 'paid': [('readonly', True)]},
        help='Defines the rules that have to be applied to this feeslip, according '
             'to the contract chosen. If the contract is empty, this field isn\'t '
             'mandatory anymore and all the valid rules of the structures '
             'of the employee\'s contracts will be applied.')
    #struct_type_id = fields.Many2one('hr.payroll.structure.type', related='struct_id.type_id')
    #wage_type = fields.Selection(related='struct_type_id.wage_type')
    name = fields.Char(
        string='Feeslip Name', required=True,
        compute='_compute_name', store=True, readonly=False,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)], 'paid': [('readonly', True)]})
    number = fields.Char(
        string='Reference', readonly=True, copy=False,
        states={'draft': [('readonly', False)], 'verify': [('readonly', False)]})
    student_id = fields.Many2one(
        'res.partner', string='Student', required=True, readonly=True,
        states={'draft': [('readonly', False)], 'verify': [('readonly', False)]},
        domain="[('is_student', '=', True), ('active', '=', True)]")
    course_id = fields.Many2one('oe.school.course',related='student_id.course_id')
    batch_id = fields.Many2one('oe.school.course.batch',related='student_id.batch_id')
    enrol_order_id = fields.Many2one(
        'sale.order', string='Enrol Contract',
        #domain=lambda self: self._compute_enrol_order_domain(),
        domain="[('partner_id', '=', student_id), ('enrol_status', '=', 'open'), ('is_enrol_order', '=', True)]",
        store=True, readonly=False,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)], 'paid': [('readonly', True)]})
    
    date_from = fields.Date(
        string='From', readonly=True, required=True,
        states={'draft': [('readonly', False)], 'verify': [('readonly', False)]})
    date_to = fields.Date(
        string='To', readonly=True, required=True,
        states={'draft': [('readonly', False)], 'verify': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'Draft'),
        ('verify', 'Waiting'),
        ('done', 'Done'),
        ('paid', 'Paid'),
        ('cancel', 'Rejected')],
        string='Status', index=True, readonly=True, copy=False,
        default='draft', tracking=True,
        help="""* When the feeslip is created the status is \'Draft\'
                \n* If the feeslip is under verification, the status is \'Waiting\'.
                \n* If the feeslip is confirmed then status is set to \'Done\'.
                \n* When user cancel feeslip the status is \'Rejected\'.""")
    line_ids = fields.One2many(
        'oe.feeslip.line', 'feeslip_id', string='Feeslip Lines',
        compute='_compute_line_ids', store=True, readonly=True, copy=True,
        states={'draft': [('readonly', False)], 'verify': [('readonly', False)]})
    company_id = fields.Many2one(
        'res.company', string='Company', copy=False, required=False,
        compute='_compute_company_id', store=True, readonly=False,
        default=lambda self: self.env.company,
        states={'draft': [('readonly', False)], 'verify': [('readonly', False)]})
    country_id = fields.Many2one(
        'res.country', string='Country',
        related='company_id.country_id', readonly=True
    )
    country_code = fields.Char(related='country_id.code', readonly=True)
    enrol_order_line_ids = fields.One2many(
        'oe.feeslip.enrol.order.line', 'feeslip_id', string='feeslip Contract Lines', copy=True,
        compute='_compute_enrol_order_line_ids', store=True, readonly=False,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)], 'paid': [('readonly', True)]})
    input_line_ids = fields.One2many(
        'oe.feeslip.input.line', 'feeslip_id', string='Feeslip Inputs', store=True,
        compute='_compute_input_line_ids', 
        readonly=False, states={'done': [('readonly', True)], 'cancel': [('readonly', True)], 'paid': [('readonly', True)]})
    paid = fields.Boolean(
        string='Made Payment Order ? ', readonly=True, copy=False,
        states={'draft': [('readonly', False)], 'verify': [('readonly', False)]})
    note = fields.Text(string='Internal Note', readonly=True, states={'draft': [('readonly', False)], 'verify': [('readonly', False)]})
   
    credit_note = fields.Boolean(
        string='Credit Note', readonly=True,
        states={'draft': [('readonly', False)], 'verify': [('readonly', False)]},
        help="Indicates this feeslip has a refund of another")
    has_refund_slip = fields.Boolean(compute='_compute_has_refund_slip')
    feeslip_run_id = fields.Many2one('oe.feeslip.run', string='Batch Name', readonly=True,
    copy=False, states={'draft': [('readonly', False)], 'verify': [('readonly', False)]}, ondelete='cascade',
    domain="[('company_id', '=', company_id)]")
    compute_date = fields.Date('Computed On')
    currency_id = fields.Many2one(related='company_id.currency_id')
    amount_total = fields.Monetary(string="Total", store=True, compute="_compute_amount_total")
    is_superuser = fields.Boolean(compute="_compute_is_superuser")
    edited = fields.Boolean()
    queued_for_pdf = fields.Boolean(default=False)

    #salary_attachment_ids = fields.Many2many(
    #    'hr.salary.attachment',
    #    relation='hr_feeslip_hr_salary_attachment_rel',
    #    string='Salary Attachments',
    #    compute='_compute_salary_attachment_ids',
    #    store=True,
    #    readonly=False,
    #)
    #salary_attachment_count = fields.Integer('Salary Attachment count', compute='_compute_salary_attachment_count')

    @api.depends('course_id','batch_id','fee_struct_id')
    @api.onchange('course_id','batch_id','fee_struct_id')
    # Method to retrieve oe.feeslip.schedule records without generated oe.feeslip
    def _find_fee_dates(self):
        # Check if this is an existing record
        domain = [('student_id', '=', self.student_id.id)]
        if self._origin and self._origin.id:
            domain.append(('id', '!=', self._origin.id))
        
        slip_id = self.env['oe.feeslip'].search(domain, limit=1, order="date_from desc")

        #raise UserError(slip_id.name)
        # Ensure that there is a current slip
        if slip_id:
            for record in self:
                date_from = record.date_from
                date_to = record.date_to
                fee_schedule_id = record.env['oe.feeslip.schedule'].search([
                        ('batch_id', '=', record.batch_id.id),
                        ('course_id', '=', record.course_id.id),
                        ('fee_struct_id', '=', record.fee_struct_id.id),
                        ('date_from', '>', slip_id.date_to),
                ], limit=1)
                #raise UserError(fee_schedule_id.date_from)
                if not fee_schedule_id:
                    fee_schedule_id = record.env['oe.feeslip.schedule'].search([
                            ('batch_id', '=', record.batch_id.id),
                            ('course_id', '=', record.course_id.id),
                            ('fee_struct_id', '=', record.fee_struct_id.id)
                    ], limit=1)
    
                record.write({
                        'date_from': fee_schedule_id.date_from,
                        'date_to': fee_schedule_id.date_to
                })
        else:
            # Handle the case where there is no current slip
            pass

            
    @api.depends('line_ids','line_ids.total')
    def _compute_amount_total(self):
        for record in self:
            record.amount_total = sum(record.line_ids.mapped('total'))
            
    @api.depends('company_id', 'student_id')
    def _compute_enrol_order_domain(self):
        # Define the domain criteria here
        for feeslip in self:
        # Define the domain criteria here
            domain = [
                ('partner_id', '=', feeslip.student_id.id),
                ('enrol_status', '=', 'open'),
                ('is_enrol_order', '=', True),
            ]
            enrol_order_ids = self.env['sale.order'].search(domain)
            feeslip.enrol_order_id = enrol_order_ids
            

    def _is_invalid(self):
        self.ensure_one()
        if self.state not in ['done', 'paid']:
            return _("This feeslip is not validated. This is not a legal document.")
        return False

    @api.depends('enrol_order_line_ids', 'input_line_ids')
    def _compute_line_ids(self):
        if not self.env.context.get("feeslip_no_recompute"):
            return
        for feeslip in self.filtered(lambda p: p.line_ids and p.state in ['draft', 'verify']):
            feeslip.line_ids = [(5, 0, 0)] + [(0, 0, line_vals) for line_vals in feeslip._get_feeslip_lines()]

    def _compute_is_superuser(self):
        self.update({'is_superuser': self.env.user._is_superuser() and self.user_has_groups("base.group_no_one")})

    def _compute_has_refund_slip(self):
        #This field is only used to know whether we need a confirm on refund or not
        #It doesn't have to work in batch and we try not to search if not necessary
        for feeslip in self:
            if not feeslip.credit_note and feeslip.state in ('done', 'paid') and self.search_count([
                ('student_id', '=', feeslip.student_id.id),
                ('date_from', '=', feeslip.date_from),
                ('date_to', '=', feeslip.date_to),
                #('enrol_order_id', '=', feeslip.enrol_order_id.id),
                ('fee_struct_id', '=', feeslip.struct_id.id),
                ('credit_note', '=', True),
                ('state', '!=', 'cancel'),
                ]):
                feeslip.has_refund_slip = True
            else:
                feeslip.has_refund_slip = False

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        if any(feeslip.date_from > feeslip.date_to for feeslip in self):
            raise ValidationError(_("Feeslip 'Date From' must be earlier 'Date To'."))

    def write(self, vals):
        res = super().write(vals)

        if 'state' in vals and vals['state'] == 'paid':
            # Register payment in Salary Attachments
            # NOTE: Since we combine multiple attachments on one input line, it's not possible to compute
            #  how much per attachment needs to be taken record_payment will consume monthly payments (child_support) before other attachments
            attachment_types = self._get_attachment_types()
            for slip in self.filtered(lambda r: r.salary_attachment_ids):
                for deduction_type, input_type_id in attachment_types.items():
                    attachments = slip.salary_attachment_ids.filtered(lambda r: r.deduction_type == deduction_type)
                    input_lines = slip.input_line_ids.filtered(lambda r: r.input_type_id.id == input_type_id.id)
                    # Use the amount from the computed value in the feeslip lines not the input
                    salary_lines = slip.line_ids.filtered(lambda r: r.code in input_lines.mapped('code'))
                    if not attachments or not salary_lines:
                        continue
                    attachments.record_payment(abs(salary_lines.total))
        return res

    def action_feeslip_draft(self):
        return self.write({'state': 'draft'})

    def _get_pdf_reports(self):
        classic_report = self.env.ref('hr_payroll.action_report_feeslip')
        result = defaultdict(lambda: self.env['oe.feeslip'])
        for feeslip in self:
            if not feeslip.fee_struct_id or not feeslip.fee_struct_id.report_id:
                result[classic_report] |= feeslip
            else:
                result[feeslip.fee_struct_id.report_id] |= feeslip
        return result

    def _generate_pdf(self):
        mapped_reports = self._get_pdf_reports()
        attachments_vals_list = []
        generic_name = _("feeslip")
        template = self.env.ref('hr_payroll.mail_template_new_feeslip', raise_if_not_found=False)
        for report, feeslips in mapped_reports.items():
            for feeslip in feeslips:
                pdf_content, dummy = report.sudo()._render_qweb_pdf(feeslip.id)
                if report.print_report_name:
                    pdf_name = safe_eval(report.print_report_name, {'object': feeslip})
                else:
                    pdf_name = generic_name
                attachments_vals_list.append({
                    'name': pdf_name,
                    'type': 'binary',
                    'raw': pdf_content,
                    'res_model': feeslip._name,
                    'res_id': feeslip.id
                })
                # Send email to employees
                if template:
                    template.send_mail(feeslip.id, notif_layout='mail.mail_notification_light')
        self.env['ir.attachment'].sudo().create(attachments_vals_list)

    def action_feeslip_done(self):
        invalid_feeslips = self.filtered(lambda p: p.enrol_order_id and (p.enrol_order_id.date_start > p.date_to or (p.enrol_order_id.date_end and p.enrol_order_id.date_end < p.date_from)))
        if invalid_feeslips:
            raise ValidationError(_('The following employees have a enrol order outside of the feeslip period:\n%s', '\n'.join(invalid_feeslips.mapped('student_id.name'))))
        if any(slip.enrol_order_id.state == 'cancel' for slip in self):
            raise ValidationError(_('You cannot valide a feeslip on which the contract is cancelled'))
        if any(slip.state == 'cancel' for slip in self):
            raise ValidationError(_("You can't validate a cancelled feeslip."))
        self.write({'state' : 'done'})

        line_values = self._get_line_values(['NET'])

        self.filtered(lambda p: not p.credit_note and line_values['NET'][p.id]['total'] < 0).write({'has_negative_net_to_report': True})
        self.mapped('feeslip_run_id').action_close()
        # Validate work entries for regular feeslips (exclude end of year bonus, ...)
        regular_feeslips = self.filtered(lambda p: p.fee_struct_id.type_id.default_struct_id == p.fee_struct_id)
        work_entries = self.env['hr.work.entry']
        for regular_feeslip in regular_feeslips:
            work_entries |= self.env['hr.work.entry'].search([
                ('date_start', '<=', regular_feeslip.date_to),
                ('date_stop', '>=', regular_feeslip.date_from),
                ('student_id', '=', regular_feeslip.student_id.id),
            ])
        if work_entries:
            work_entries.action_validate()

        if self.env.context.get('feeslip_generate_pdf'):
            if self.env.context.get('feeslip_generate_pdf_direct'):
                self._generate_pdf()
            else:
                self.write({'queued_for_pdf': True})
                feeslip_cron = self.env.ref('hr_payroll.ir_cron_generate_feeslip_pdfs', raise_if_not_found=False)
                if feeslip_cron:
                    feeslip_cron._trigger()

    def action_feeslip_cancel(self):
        if not self.env.user._is_system() and self.filtered(lambda slip: slip.state == 'done'):
            raise UserError(_("Cannot cancel a feeslip that is done."))
        self.write({'state': 'cancel'})
        self.mapped('feeslip_run_id').action_close()

    def action_feeslip_paid(self):
        if any(slip.state != 'done' for slip in self):
            raise UserError(_('Cannot mark feeslip as paid if not confirmed.'))
        self.write({'state': 'paid'})

    def action_open_work_entries(self):
        self.ensure_one()
        return self.student_id.action_open_work_entries()

    def action_open_salary_attachments(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Salary Attachments'),
            'res_model': 'hr.salary.attachment',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.salary_attachment_ids.ids)],
        }

    def refund_sheet(self):
        copied_feeslips = self.env['oe.feeslip']
        for feeslip in self:
            copied_feeslip = feeslip.copy({
                'credit_note': True,
                'name': _('Refund: %(feeslip)s', feeslip=feeslip.name),
                'edited': True,
                'state': 'verify',
            })
            for wd in copied_feeslip.worked_days_line_ids:
                wd.number_of_hours = -wd.number_of_hours
                wd.number_of_days = -wd.number_of_days
                wd.amount = -wd.amount
            for line in copied_feeslip.line_ids:
                line.amount = -line.amount
            copied_feeslips |= copied_feeslip
        formview_ref = self.env.ref('hr_payroll.view_hr_feeslip_form', False)
        treeview_ref = self.env.ref('hr_payroll.view_hr_feeslip_tree', False)
        return {
            'name': ("Refund feeslip"),
            'view_mode': 'tree, form',
            'view_id': False,
            'res_model': 'oe.feeslip',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('id', 'in', copied_feeslips.ids)],
            'views': [(treeview_ref and treeview_ref.id or False, 'tree'), (formview_ref and formview_ref.id or False, 'form')],
            'context': {}
        }

    @api.ondelete(at_uninstall=False)
    def _unlink_if_draft_or_cancel(self):
        if any(feeslip.state not in ('draft', 'cancel') for feeslip in self):
            raise UserError(_('You cannot delete a feeslip which is not draft or cancelled!'))

    def compute_sheet(self):
        feeslips = self.filtered(lambda slip: slip.state in ['draft', 'verify'])
        # delete old feeslip lines
        feeslips.line_ids.unlink()
        for feeslip in feeslips:
            number = feeslip.number or self.env['ir.sequence'].next_by_code('fee.slip')
            lines = [(0, 0, line) for line in feeslip._get_feeslip_lines()]
            feeslip.write({'line_ids': lines, 'number': number, 'state': 'verify', 'compute_date': fields.Date.today()})
        return True

    def action_refresh_from_work_entries(self):
        # Refresh the whole feeslip in case the HR has modified some work entries
        # after the feeslip generation
        if any(p.state not in ['draft', 'verify'] for p in self):
            raise UserError(_('The feeslips should be in Draft or Waiting state.'))
        self.mapped('worked_days_line_ids').unlink()
        self.mapped('line_ids').unlink()
        self._compute_worked_days_line_ids()
        self.compute_sheet()

    def _round_days(self, work_entry_type, days):
        if work_entry_type.round_days != 'NO':
            precision_rounding = 0.5 if work_entry_type.round_days == "HALF" else 1
            day_rounded = float_round(days, precision_rounding=precision_rounding, rounding_method=work_entry_type.round_days_type)
            return day_rounded
        return days

    @api.model
    def _get_attachment_types(self):
        return {
            'attachment': self.env.ref('hr_payroll.input_attachment_salary'),
            'assignment': self.env.ref('hr_payroll.input_assignment_salary'),
            'child_support': self.env.ref('hr_payroll.input_child_support'),
        }

    def _get_worked_day_lines_hours_per_day(self):
        self.ensure_one()
        return self.enrol_order_id.resource_calendar_id.hours_per_day

    def _get_out_of_enrol_order_calendar(self):
        self.ensure_one()
        return self.enrol_order_id.resource_calendar_id

    def _get_worked_day_lines_values(self, domain=None):
        self.ensure_one()
        res = []
        hours_per_day = self._get_worked_day_lines_hours_per_day()
        work_hours = self.enrol_order_id._get_work_hours(self.date_from, self.date_to, domain=domain)
        work_hours_ordered = sorted(work_hours.items(), key=lambda x: x[1])
        biggest_work = work_hours_ordered[-1][0] if work_hours_ordered else 0
        add_days_rounding = 0
        for work_entry_type_id, hours in work_hours_ordered:
            work_entry_type = self.env['hr.work.entry.type'].browse(work_entry_type_id)
            days = round(hours / hours_per_day, 5) if hours_per_day else 0
            if work_entry_type_id == biggest_work:
                days += add_days_rounding
            day_rounded = self._round_days(work_entry_type, days)
            add_days_rounding += (days - day_rounded)
            attendance_line = {
                'sequence': work_entry_type.sequence,
                'work_entry_type_id': work_entry_type_id,
                'number_of_days': day_rounded,
                'number_of_hours': hours,
            }
            res.append(attendance_line)
        return res

    def _get_worked_day_lines(self, domain=None, check_out_of_enrol_order=True):
        """
        :returns: a list of dict containing the worked days values that should be applied for the given feeslip
        """
        res = []
        # fill only if the Enrol Order as a working schedule linked
        self.ensure_one()
        if self:
            enrol_order = self.enrol_order_id
        #if enrol_order.resource_calendar_id:
        #    res = self._get_worked_day_lines_values(domain=domain)
        #    if not check_out_of_enrol_order:
        #        return res

            # If the Enrol Order doesn't cover the whole month, create
            # worked_days lines to adapt the wage accordingly
            out_days, out_hours = 0, 0
            reference_calendar = self._get_out_of_enrol_order_calendar()
            if self.date_from < enrol_order.date_start:
                start = fields.Datetime.to_datetime(self.date_from)
                stop = fields.Datetime.to_datetime(enrol_order.date_start) + relativedelta(days=-1, hour=23, minute=59)
                out_time = reference_lm96y6y8b ;calendar.get_work_duration_data(start, stop, compute_leaves=False, domain=['|', ('work_entry_type_id', '=', False), ('work_entry_type_id.is_leave', '=', False)])
                out_days += out_time['days']
                out_hours += out_time['hours']
            if enrol_order.date_end and enrol_order.date_end < self.date_to:
                start = fields.Datetime.to_datetime(enrol_order.date_end) + relativedelta(days=1)
                stop = fields.Datetime.to_datetime(self.date_to) + relativedelta(hour=23, minute=59)
                out_time = reference_calendar.get_work_duration_data(start, stop, compute_leaves=False, domain=['|', ('work_entry_type_id', '=', False), ('work_entry_type_id.is_leave', '=', False)])
                out_days += out_time['days']
                out_hours += out_time['hours']

            if out_days or out_hours:
                work_entry_type = self.env.ref('hr_payroll.hr_work_entry_type_out_of_enrol_order')
                res.append({
                    'sequence': work_entry_type.sequence,
                    'work_entry_type_id': work_entry_type.id,
                    'number_of_days': out_days,
                    'number_of_hours': out_hours,
                })
        return res

    def _get_base_local_dict(self):
        return {
            'float_round': float_round,
            'float_compare': float_compare,
        }

    def _get_localdict(self):
        self.ensure_one()
        order_fee_lines_dict = {line.code: line for line in self.enrol_order_line_ids if line.code}
        inputs_dict = {line.code: line for line in self.input_line_ids if line.code}

        student = self.student_id
        enrol_order = self.enrol_order_id

        localdict = {
            **self._get_base_local_dict(),
            **{
                'categories': BrowsableObject(student.id, {}, self.env),
                'rules': BrowsableObject(student.id, {}, self.env),
                'feeslip': Feeslips(student.id, self, self.env),
                'order_fee': OrderFeeLines(student.id, order_fee_lines_dict, self.env),
                'inputfee': InputFees(student.id, inputs_dict, self.env),
                'student': student,
                'enrol_order': enrol_order,
                'result_rules': ResultRules(student.id, {}, self.env)
            }
        }
        return localdict

    def _get_feeslip_lines(self):
        self.ensure_one()

        localdict = self.env.context.get('force_feeslip_localdict', None)
        if localdict is None:
            localdict = self._get_localdict()

        rules_dict = localdict['rules'].dict
        result_rules_dict = localdict['result_rules'].dict

        blacklisted_rule_ids = self.env.context.get('prevent_feeslip_computation_line_ids', [])

        result = {}

        for rule in sorted(self.fee_struct_id.rule_ids, key=lambda x: x.sequence):
            if rule.id in blacklisted_rule_ids:
                continue
            localdict.update({
                'result': None,
                'result_qty': 1.0,
                'result_rate': 100,
                'result_name': False
            })
            if rule._satisfy_condition(localdict):
                amount, qty, rate = rule._compute_rule(localdict)
                #check if there is already a rule computed with that code
                previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
                #set/overwrite the amount computed for this rule in the localdict
                tot_rule = amount * qty * rate / 100.0
                localdict[rule.code] = tot_rule
                result_rules_dict[rule.code] = {'total': tot_rule, 'amount': amount, 'quantity': qty}
                rules_dict[rule.code] = rule
                # sum the amount for its salary category
                localdict = rule.category_id._sum_fee_category(localdict, tot_rule - previous_amount)
                # Retrieve the line name in the employee's lang
                employee_lang = self.student_id.sudo().lang
                # This actually has an impact, don't remove this line
                context = {'lang': employee_lang}
                if localdict['result_name']:
                    rule_name = localdict['result_name']
                elif rule.code in ['BASIC', 'GROSS', 'NET', 'DEDUCTION', 'REIMBURSEMENT']:  # Generated by default_get (no xmlid)
                    if rule.code == 'BASIC':  # Note: Crappy way to code this, but _(foo) is forbidden. Make a method in master to be overridden, using the structure code
                        if rule.name == "Double Holiday Pay":
                            rule_name = _("Double Holiday Pay")
                        if rule.fee_struct_id.name == "CP200: Employees 13th Month":
                            rule_name = _("Prorated end-of-year bonus")
                        else:
                            rule_name = _('Basic Salary')
                    elif rule.code == "GROSS":
                        rule_name = _('Gross')
                    elif rule.code == "DEDUCTION":
                        rule_name = _('Deduction')
                    elif rule.code == "REIMBURSEMENT":
                        rule_name = _('Reimbursement')
                    elif rule.code == 'NET':
                        rule_name = _('Net Salary')
                else:
                    rule_name = rule.with_context(lang=employee_lang).name
                # create/overwrite the rule in the temporary results
                result[rule.code] = {
                    'sequence': rule.sequence,
                    'code': rule.code,
                    'name': rule_name,
                    'note': html2plaintext(rule.note),
                    'fee_rule_id': rule.id,
                    #'enrol_order_id': localdict['enrol_order'].id,
                    'student_id': localdict['student'].id,
                    'amount': amount,
                    'quantity': qty,
                    'rate': rate,
                    'feeslip_id': self.id,
                }
        return result.values()

    @api.depends('student_id')
    def _compute_company_id(self):
        for slip in self.filtered(lambda p: p.student_id):
            slip.company_id = slip.student_id.company_id

    @api.depends('student_id', 'date_from', 'date_to')
    def _compute_enrol_order_id(self):
        for slip in self:
            if not slip.student_id or not slip.date_from or not slip.date_to:
                slip.enrol_order_id = False
                continue
            # Add a default enrol_order if not already defined or invalid
            if slip.enrol_order_id and slip.student_id == slip.enrol_order_id.student_id:
                continue
            enrol_orders = False #slip.student_id._get_enrol_orders(slip.date_from, slip.date_to)
            slip.enrol_order_id = enrol_orders[0] if enrol_orders else False

    @api.depends('enrol_order_id','student_id')
    def _compute_struct_id(self):
        for slip in self.filtered(lambda p: not p.fee_struct_id):
            slip.fee_struct_id = False #slip.enrol_order_id.structure_type_id.default_struct_id

    @api.depends('student_id', 'fee_struct_id', 'date_from','date_to')
    def _compute_name(self):
        for slip in self.filtered(lambda p: p.student_id and p.date_from):
            lang = slip.student_id.sudo().lang or self.env.user.lang
            context = {'lang': lang}
            feeslip_name = slip.fee_struct_id.feeslip_name or _('Fee Slip')
            del context

            slip.name = '%(feeslip_name)s - %(employee_name)s (%(date_from)s - %(date_to)s)' % {
                'feeslip_name': feeslip_name,
                'employee_name': slip.student_id.name,
                'date_from': format_date(self.env, slip.date_from, date_format="MMMM y", lang_code=lang),
                'date_to': format_date(self.env, slip.date_to, date_format="MMMM y", lang_code=lang)
            }

    @api.depends('student_id', 'enrol_order_id')
    def _compute_enrol_order_line_ids(self):
        valid_slips = self.filtered(lambda p: p.student_id)
        if not valid_slips:
            return
        # Make sure to reset invalid payslip's worked days line
        self.update({'enrol_order_line_ids': [(5, 0, 0)]})
        if not valid_slips:
            return

        for slip in valid_slips:
            #if not slip.struct_id.use_worked_day_lines:
            #    continue
            # YTI Note: We can't use a batched create here as the payslip may not exist
            slip.update({'enrol_order_line_ids': slip._get_new_enrol_order_lines()})


    def _get_new_enrol_order_lines(self):
        # Retrieve the related sale.order
        sale_order = self.enrol_order_id
        if sale_order:
            # Get the sale.order lines related to the sale.order
            sale_order_lines = sale_order.order_line

            # You may want to filter or modify the sale_order_lines based on your specific criteria
            # In this example, we're including all lines.
            
            # Create a list of tuples for updating the enrol_order_line_ids field
            enrol_order_line_data = [(0, 0, {
                'name': line.name,
                'sequence': 10,
                'product_id': line.product_id.id,
                'code': line.product_id.default_code,
                'amount': line.price_total,
                'quantity': line.product_uom_qty,
                'price_unit': line.price_unit,
                'qty_invoiced': line.qty_invoiced,
                'qty_to_invoice': line.qty_to_invoice,
                'order_line_id': line.id,
            }) for line in sale_order_lines]

            return enrol_order_line_data
        return []

        
    @api.depends('student_id', 'fee_struct_id')
    def _compute_input_line_ids(self):
        valid_slips = self.filtered(lambda p: p.student_id and p.fee_struct_id)
        if not valid_slips:
            return
        # Make sure to reset invalid payslip's worked days line
        self.update({'input_line_ids': [(5, 0, 0)]})
        if not valid_slips:
            return

        for slip in valid_slips:
            #if not slip.struct_id.use_worked_day_lines:
            #    continue
            # YTI Note: We can't use a batched create here as the payslip may not exist
            slip.update({'input_line_ids': slip._get_new_input_lines()})

    def _get_new_input_lines(self):
        # Retrieve the related sale.order
        struct_id = self.fee_struct_id
        if struct_id:
            # Get the sale.order lines related to the sale.order
            other_lines = struct_id.input_line_type_ids

            # You may want to filter or modify the sale_order_lines based on your specific criteria
            # In this example, we're including all lines.
            
            # Create a list of tuples for updating the enrol_order_line_ids field
            other_line_data = [(0, 0, {
                'name': line.name,
                'sequence': 10,
                'input_type_id': line.id,
                'code': line.code,
               
            }) for line in other_lines]

            return other_line_data
        return []


    def _get_salary_line_total(self, code):
        _logger.warning('The method _get_salary_line_total is deprecated in favor of _get_line_values')
        lines = self.line_ids.filtered(lambda line: line.code == code)
        return sum([line.total for line in lines])

    def _get_salary_line_quantity(self, code):
        _logger.warning('The method _get_salary_line_quantity is deprecated in favor of _get_line_values')
        lines = self.line_ids.filtered(lambda line: line.code == code)
        return sum([line.quantity for line in lines])

    def _get_line_values(self, code_list, vals_list=None, compute_sum=False):
        if vals_list is None:
            vals_list = ['total']
        valid_values = {'quantity', 'amount', 'total'}
        if set(vals_list) - valid_values:
            raise UserError(_('The following values are not valid:\n%s', '\n'.join(list(set(vals_list) - valid_values))))
        result = defaultdict(lambda: defaultdict(lambda: dict.fromkeys(vals_list, 0)))
        if not self:
            return result
        self.flush()
        selected_fields = ','.join('SUM(%s) AS %s' % (vals, vals) for vals in vals_list)
        self.env.cr.execute("""
            SELECT
                p.id,
                pl.code,
                %s
            FROM oe_feeslip_line pl
            JOIN oe_feeslip p
            ON p.id IN %s
            AND pl.feeslip_id = p.id
            AND pl.code IN %s
            GROUP BY p.id, pl.code
        """ % (selected_fields, '%s', '%s'), (tuple(self.ids), tuple(code_list)))
        # self = hr.feeslip(1, 2)
        # request_rows = [
        #     {'id': 1, 'code': 'IP', 'total': 100, 'quantity': 1},
        #     {'id': 1, 'code': 'IP.DED', 'total': 200, 'quantity': 1},
        #     {'id': 2, 'code': 'IP', 'total': -2, 'quantity': 1},
        #     {'id': 2, 'code': 'IP.DED', 'total': -3, 'quantity': 1}
        # ]
        request_rows = self.env.cr.dictfetchall()
        # result = {
        #     'IP': {
        #         'sum': {'quantity': 2, 'total': 300},
        #         1: {'quantity': 1, 'total': 100},
        #         2: {'quantity': 1, 'total': 200},
        #     },
        #     'IP.DED': {
        #         'sum': {'quantity': 2, 'total': -5},
        #         1: {'quantity': 1, 'total': -2},
        #         2: {'quantity': 1, 'total': -3},
        #     },
        # }
        for row in request_rows:
            code = row['code']
            feeslip_id = row['id']
            for vals in vals_list:
                if compute_sum:
                    result[code]['sum'][vals] += row[vals]
                result[code][feeslip_id][vals] += row[vals]
        return result

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super().fields_view_get(view_id, view_type, toolbar, submenu)
        if toolbar and 'print' in res['toolbar']:
            res['toolbar'].pop('print')
        return res

    def action_print_feeslip(self):
        return {
            'name': 'Feeslip',
            'type': 'ir.actions.act_url',
            'url': '/print/feeslips?list_ids=%(list_ids)s' % {'list_ids': ','.join(str(x) for x in self.ids)},
        }

    def action_export_feeslip(self):
        self.ensure_one()
        return {
            "name": "Debug Feeslip",
            "type": "ir.actions.act_url",
            "url": "/debug/feeslip/%s" % self.id,
        }

    def _is_outside_enrol_order_dates(self):
        self.ensure_one()
        feeslip = self
        #enrol_order = self.enrol_order_id
        return enrol_order.date_start > feeslip.date_to or (enrol_order.date_end and enrol_order.date_end < feeslip.date_from)

    def _get_data_files_to_update(self):
        # Note: Use lists as modules/files order should be maintained
        return []

    def _update_payroll_data(self):
        data_to_update = self._get_data_files_to_update()
        _logger.info("Update payroll static data")
        idref = {}
        for module_name, files_to_update in data_to_update:
            for file_to_update in files_to_update:
                convert_file(self.env.cr, module_name, file_to_update, idref)

    def action_edit_feeslip_lines(self):
        self.ensure_one()
        if not self.user_has_groups('de_school_fees.group_hr_payroll_manager'):
            raise UserError(_('This action is restricted to payroll managers only.'))
        if self.state == 'done':
            raise UserError(_('This action is forbidden on validated feeslips.'))
        wizard = self.env['hr.payroll.edit.feeslip.lines.wizard'].create({
            'feeslip_id': self.id,
            'line_ids': [(0, 0, {
                'sequence': line.sequence,
                'code': line.code,
                'name': line.name,
                'note': line.note,
                'salary_rule_id': line.salary_rule_id.id,
                'enrol_order_id': line.enrol_order_id.id,
                'student_id': line.student_id.id,
                'amount': line.amount,
                'quantity': line.quantity,
                'rate': line.rate,
                'feeslip_id': self.id}) for line in self.line_ids],
            'worked_days_line_ids': [(0, 0, {
                'name': line.name,
                'sequence': line.sequence,
                'code': line.code,
                'work_entry_type_id': line.work_entry_type_id.id,
                'number_of_days': line.number_of_days,
                'number_of_hours': line.number_of_hours,
                'amount': line.amount,
                'feeslip_id': self.id}) for line in self.worked_days_line_ids]
        })

        return {
            'type': 'ir.actions.act_window',
            'name': _('Edit Feeslip Lines'),
            'res_model': 'hr.payroll.edit.feeslip.lines.wizard',
            'view_mode': 'form',
            'target': 'new',
            'binding_model_id': self.env['ir.model.data']._xmlid_to_res_id('hr_payroll.model_hr_feeslip'),
            'binding_view_types': 'form',
            'res_id': wizard.id
        }

    @api.model
    def _cron_generate_pdf(self):
        feeslips = self.search([
            ('state', 'in', ['done', 'paid']),
            ('queued_for_pdf', '=', True),
        ])
        if not feeslips:
            return
        BATCH_SIZE = 50
        feeslips_batch = feeslips[:BATCH_SIZE]
        feeslips_batch._generate_pdf()
        feeslips_batch.write({'queued_for_pdf': False})
        # if necessary, retrigger the cron to generate more pdfs
        if len(feeslips) > BATCH_SIZE:
            self.env.ref('hr_payroll.ir_cron_generate_feeslip_pdfs')._trigger()

