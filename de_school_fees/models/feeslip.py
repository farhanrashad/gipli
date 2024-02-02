# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import logging

from collections import defaultdict
from markupsafe import Markup

from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, Command, fields, models, _
from odoo.addons.de_school_fees.models.browsable_object import BrowsableObject, InputFees, OrderFeeLines, Feeslips, ResultRules
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round, date_utils, convert_file, html2plaintext
from odoo.tools import float_compare, float_is_zero, plaintext2html

from odoo.tools.float_utils import float_compare
from odoo.tools.misc import format_date
from odoo.tools.safe_eval import safe_eval

from odoo.osv import expression

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
        domain="[('id', 'in', enrol_order_domain_ids)]",
        compute='_compute_enrol_order',
        store=True, readonly=False,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)], 'paid': [('readonly', True)]})
    enrol_order_domain_ids = fields.Many2many('sale.order', compute='_compute_enrol_order_domain_ids')
    
    date_from = fields.Date(
        string='From', readonly=True, required=True,
        default=lambda self: fields.Date.to_string(date.today().replace(day=1)),
        states={'draft': [('readonly', False)], 'verify': [('readonly', False)]})
    date_to = fields.Date(
        string='To', readonly=False, required=True,
        precompute=True, compute="_compute_date_to", store=True,
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
        'res.company', string='Company', copy=False, required=True,
       store=True, readonly=False,
        default=lambda self: self.env.company,
        states={'draft': [('readonly', False)], 'verify': [('readonly', False)]})
    country_id = fields.Many2one(
        'res.country', string='Country',
        related='company_id.country_id', readonly=True
    )
    country_code = fields.Char(related='country_id.code', readonly=True)
    enrol_order_line_ids = fields.One2many(
        'oe.feeslip.enrol.order.line', 'feeslip_id', string='feeslip Contract Lines', copy=True,
        compute='_compute_enrol_order_line_ids', store=True, readonly=True,
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
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    amount_total = fields.Monetary(string="Total", store=True, compute="_compute_amount_total")
    
    is_superuser = fields.Boolean(compute="_compute_is_superuser")
    edited = fields.Boolean()
    queued_for_pdf = fields.Boolean(default=False)

    account_move_id = fields.Many2one('account.move', 'Accounting Entry', readonly=True, copy=False)
    date = fields.Date('Date Account', states={'draft': [('readonly', False)], 'verify': [('readonly', False)]}, readonly=True, help="Keep empty to use the period of the validation(Feeslip) date.")

    
    # ================================================================
    # ====================== Computed Methods ========================
    # ================================================================

    @api.depends('date_from','fee_struct_id')
    def _compute_date_to(self):
        for feeslip in self:
            mons = feeslip.fee_struct_id.schedule_pay_duration or 1
            next_month = relativedelta(months=+mons, day=1, days=-1)
            feeslip.date_to = feeslip.date_from and feeslip.date_from + next_month

    @api.depends('company_id', 'student_id', 'date_from', 'date_to')
    def _compute_enrol_order_domain_ids(self):
        for feeslip in self:
            feeslip.enrol_order_domain_ids = self.env['sale.order'].search([
                ('company_id', '=', feeslip.company_id.id),
                ('partner_id', '=', feeslip.student_id.id),
                ('state', '!=', 'cancel'),
                ('date_enrol_start', '<=', feeslip.date_to),
                '|',
                ('date_enrol_end', '>=', feeslip.date_from),
                ('date_enrol_end', '=', False)])

    @api.depends('student_id', 'date_from', 'date_to')
    def _compute_enrol_order(self):
        for slip in self:
            if not slip.student_id or not slip.date_from or not slip.date_to:
                slip.enrol_order_id = False
                continue
            # Add a default contract if not already defined or invalid
            if slip.enrol_order_id: #and slip.student_id == slip.contract_id.employee_id:
                continue
            enrol_orders = slip.student_id._get_enrol_orders(slip.date_from, slip.date_to)
            slip.enrol_order_id = enrol_orders[0] if enrol_orders else False
    
            
    @api.depends('line_ids','line_ids.total')
    def _compute_amount_total(self):
        for record in self:
            record.amount_total = sum(record.line_ids.mapped('total'))
            

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
                ('fee_struct_id', '=', feeslip.fee_struct_id.id),
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
        invalid_feeslips = self.filtered(lambda p: not p.enrol_order_id)
        if invalid_feeslips:
            raise ValidationError(_('The following students have a enrol order outside of the feeslip period:\n%s', '\n'.join(invalid_feeslips.mapped('student_id.name'))))
        if any(slip.enrol_order_id.state == 'cancel' for slip in self):
            raise ValidationError(_('You cannot valide a feeslip on which the contract is cancelled'))
        if any(slip.state == 'cancel' for slip in self):
            raise ValidationError(_("You can't validate a cancelled feeslip."))
        self.write({'state' : 'done'})
        
        if self.env.context.get('feeslip_generate_pdf'):
            if self.env.context.get('feeslip_generate_pdf_direct'):
                self._generate_pdf()
            else:
                self.write({'queued_for_pdf': True})
                feeslip_cron = self.env.ref('de_school_fees.ir_cron_generate_feeslip_pdfs', raise_if_not_found=False)
                if feeslip_cron:
                    feeslip_cron._trigger()

        #self._create_so_line()
        # Create Fee Depiost section if necessary
        if not any(line.display_type and line.is_downpayment for line in self.enrol_order_id.order_line):
            self.env['sale.order.line'].create(
                self._prepare_feeslip_payment_section_values(self.enrol_order_id)
            )
        # Create Fee Depiost line
        fee_payment_so_line = self.env['sale.order.line'].create(
            self._prepare_so_line_values(self.enrol_order_id)
        )
        
        self._action_create_fee_invoice(fee_payment_so_line)

    def _prepare_feeslip_payment_section_values(self, order):
        context = {'lang': order.partner_id.lang}
        so_values = {
            'name': _('Feeslips Payments'),
            'product_uom_qty': 0.0,
            'order_id': order.id,
            'display_type': 'line_section',
            'is_downpayment': True,
            'sequence': order.order_line and order.order_line[-1].sequence + 1 or 10,
            'feeslip_id': self.id,
        }

        del context
        return so_values

    def _prepare_so_line_values(self, order):
        self.ensure_one()
        analytic_distribution = {}
        amount_total = sum(order.order_line.mapped("price_total"))
        if not float_is_zero(amount_total, precision_rounding=self.currency_id.rounding):
            for line in order.order_line:
                distrib_dict = line.analytic_distribution or {}
                for account, distribution in distrib_dict.items():
                    analytic_distribution[account] = distribution * line.price_total + analytic_distribution.get(account, 0)
            for account, distribution_amount in analytic_distribution.items():
                analytic_distribution[account] = distribution_amount/amount_total
        context = {'lang': order.partner_id.lang}
        so_values = {
            'name': self.name,
            'price_unit': self.amount_total,
            'price_subtotal': self.amount_total * -1,
            'price_total': self.amount_total * -1,
            'product_uom_qty': 0.0,
            'order_id': order.id,
            'discount': 0.0,
            'qty_invoiced': 1,
            'product_id': self.fee_struct_id.deposit_product_id.id,
            'analytic_distribution': analytic_distribution,
            'is_downpayment': True,
            'sequence': order.order_line and order.order_line[-1].sequence + 1 or 10,
            'feeslip_id': self.id,
        }
        del context
        return so_values
        
    def _action_create_fee_invoice(self,sale_line_id):
        precision = self.env['decimal.precision'].precision_get('Fee')
    
        # Add feeslip without run
        feeslips_to_post = self.filtered(lambda slip: not slip.feeslip_run_id)
    
        # Adding fee slips from a batch and deleting fee slips with a batch that is not ready for validation.
        feeslip_runs = (self - feeslips_to_post).mapped('feeslip_run_id')
        for run in feeslip_runs:
            if run._are_feeslips_ready():
                feeslips_to_post |= run.slip_ids
    
        # A feeslip needs to have a done state and not an accounting move.
        feeslips_to_post = feeslips_to_post.filtered(lambda slip: slip.state == 'done' and not slip.account_move_id)
    
        # Check that a journal exists on all the structures
        if any(not feeslip.fee_struct_id for feeslip in feeslips_to_post):
            raise ValidationError(_('One of the contract for these feeslips has no structure type.'))
        if any(not structure.journal_id for structure in feeslips_to_post.mapped('fee_struct_id')):
            raise ValidationError(_('One of the feeslips structures has no account journal defined on it.'))
    
        # Map all feeslips by structure journal
        # {'journal_id': [slip_ids]}
        #slip_mapped_data = defaultdict(list)
        slip_mapped_data = defaultdict(lambda: defaultdict(lambda: self.env['oe.feeslip']))
        for slip in feeslips_to_post:
            # Append slip to the list for the specific journal_id.
            #slip_mapped_data[slip.fee_struct_id.journal_id.id].append(slip)
            slip_mapped_data[slip.fee_struct_id.journal_id.id][slip.date or fields.Date().end_of(slip.date_to, 'month')] |= slip
    
        for journal_id in slip_mapped_data:
            for slip_date in slip_mapped_data[journal_id]:
                line_ids = []
                debit_sum = 0.0
                credit_sum = 0.0
                date = fields.Date().end_of(slip.date_to, 'month')
                move_dict = {
                    'narration': '',
                    'ref': date.strftime('%B %Y'),
                    'journal_id': journal_id,
                    'date': slip_date,
                }
            
                for slip in slip_mapped_data[journal_id][slip_date]:
                    move_dict['narration'] += plaintext2html(slip.number or '' + ' - ' + slip.student_id.name or '')
                    move_dict['narration'] += Markup('<br/>')
                    slip_lines = slip._prepare_slip_lines(date, line_ids, sale_line_id)
                    line_ids.extend(slip_lines)
    
                for line_id in line_ids:
                    debit_sum += line_id['debit']
                    credit_sum += line_id['credit']
    
                # The code below is called if there is an error in the balance between credit and debit sum.
                if float_compare(credit_sum, debit_sum, precision_digits=precision) == -1:
                    slip._prepare_adjust_line(line_ids, 'credit', debit_sum, credit_sum, date)
                elif float_compare(debit_sum, credit_sum, precision_digits=precision) == -1:
                    slip._prepare_adjust_line(line_ids, 'debit', debit_sum, credit_sum, date)

                # for testing purpose
                move_dict['line_ids'] = [(0, 0, line_vals) for line_vals in line_ids]
                move_dict_str = '\n'.join([f"{key}: {value}" for key, value in move_dict.items()])
                #raise UserError(move_dict_str)
            
                # Add accounting lines in the move
                move_dict['line_ids'] = [(0, 0, line_vals) for line_vals in line_ids]
                move = self._create_account_move(move_dict)
                for slip in slip_mapped_data[journal_id][slip_date]:
                    slip.write({'account_move_id': move.id, 'date': date})
        return True


    def _prepare_line_values(self, line, account_id, date, debit, credit,sale_line_id):
        return {
            'name': line.name,
            'partner_id': line.partner_id.id or self.student_id.id,
            'account_id': account_id,
            'journal_id': line.feeslip_id.fee_struct_id.journal_id.id,
            'date': date,
            'debit': debit,
            'credit': credit,
            'sale_line_ids': [(6, 0, [sale_line_id.id])],
            'analytic_distribution': (line.fee_rule_id.analytic_account_id and {line.fee_rule_id.analytic_account_id.id: 100}) or
                                     (line.feeslip_id.enrol_order_id.analytic_account_id.id and {line.feeslip_id.enrol_order_id.analytic_account_id.id: 100})
        }
        
    def _prepare_slip_lines(self, date, line_ids, sale_line_id):
        self.ensure_one()
        precision = self.env['decimal.precision'].precision_get('FEE')
        new_lines = []
        for line in self.line_ids.filtered(lambda line: line.category_id):
            amount = line.total
            if line.code == 'NET': # Check if the line is the 'Net Salary'.
                for tmp_line in self.line_ids.filtered(lambda line: line.category_id):
                    if tmp_line.fee_rule_id.not_computed_in_net: # Check if the rule must be computed in the 'Net Salary' or not.
                        if amount > 0:
                            amount -= abs(tmp_line.total)
                        elif amount < 0:
                            amount += abs(tmp_line.total)
            if float_is_zero(amount, precision_digits=precision):
                continue
            debit_account_id = line.fee_rule_id.account_debit.id
            credit_account_id = line.fee_rule_id.account_credit.id
            if debit_account_id: # If the rule has a debit account.
                debit = amount if amount > 0.0 else 0.0
                credit = -amount if amount < 0.0 else 0.0

                debit_line = self._get_existing_lines(
                    line_ids + new_lines, line, debit_account_id, debit, credit)

                if not debit_line:
                    debit_line = self._prepare_line_values(line, debit_account_id, date, debit, credit, sale_line_id)
                    debit_line['tax_ids'] = [(4, tax_id) for tax_id in line.fee_rule_id.account_debit.tax_ids.ids]
                    new_lines.append(debit_line)
                else:
                    debit_line['debit'] += debit
                    debit_line['credit'] += credit

            if credit_account_id: # If the rule has a credit account.
                debit = -amount if amount < 0.0 else 0.0
                credit = amount if amount > 0.0 else 0.0
                credit_line = self._get_existing_lines(
                    line_ids + new_lines, line, credit_account_id, debit, credit)

                if not credit_line:
                    credit_line = self._prepare_line_values(line, credit_account_id, date, debit, credit, sale_line_id)
                    credit_line['tax_ids'] = [(4, tax_id) for tax_id in line.fee_rule_id.account_credit.tax_ids.ids]
                    new_lines.append(credit_line)
                else:
                    credit_line['debit'] += debit
                    credit_line['credit'] += credit
        return new_lines

    def _get_existing_lines(self, line_ids, line, account_id, debit, credit):
        existing_lines = (
            line_id for line_id in line_ids if
            line_id['name'] == line.name
            and line_id['account_id'] == account_id
            and ((line_id['debit'] > 0 and credit <= 0) or (line_id['credit'] > 0 and debit <= 0))
            and (
                    (
                        not line_id['analytic_distribution'] and
                        not line.fee_rule_id.analytic_account_id.id and
                        not line.feeslip_id.contract_id.analytic_account_id.id
                    )
                    or line_id['analytic_distribution'] and line.fee_rule_id.analytic_account_id.id in line_id['analytic_distribution']
                    or line_id['analytic_distribution'] and line.feeslip_id.contract_id.analytic_account_id.id in line_id['analytic_distribution']

                )
        )
        return next(existing_lines, False)
    def _create_account_move(self, values):
        return self.env['account.move'].sudo().create(values)
        
    # ==============================================================
    # ====================== Action Methods ========================
    # ==============================================================
    
    def action_feeslip_cancel(self):
        if not self.env.user._is_system() and self.filtered(lambda slip: slip.state == 'done'):
            raise UserError(_("Cannot cancel a feeslip that is done."))
        self.write({'state': 'cancel'})
        self.account_move_id.unlink()
        self.enrol_order_id.order_line.filtered(lambda x: x.is_downpayment and x.feeslip_id.id == self.id).unlink()
        #raise UserError(self.enrol_order_id.order_line.filtered(lambda x: x.feeslip_id.id == self.id))
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

    @api.depends('course_id')
    def _compute_struct_id(self):
        for slip in self:
            struct_id = self.env['oe.fee.struct'].search([
                ('active','=',True),
                '|',
                ('course_id','=',slip.course_id.id),
                ('course_id','=',False),
            ],limit=1)
            slip.fee_struct_id = struct_id.id

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
        so = self.enrol_order_id
        move_ids = self.env['account.move.line'].search([
            ('sale_line_ids','in',so.order_line.ids),
            ('account_id.account_type','=', 'asset_receivable'),
        ])
        enrol_order_data = []
        #raise UserError(move_ids)
        if so:
            enrol_order_data.append(
                (0, 0, {
                    'name': so.name,
                    'code': 'ENRL',
                    'sequence': 10,
                    'amount': so.amount_total,
                })
            )
            sale_order_lines = so.order_line
    
        if len(move_ids):
            enrol_order_data.append(
                (0, 0, {
                    'name': so.name,
                    'code': 'INV',
                    'sequence': 20,
                    'amount': sum(move_ids.mapped('debit')),
                    'amount_residual': sum(move_ids.mapped('amount_residual')),
                })
            )
    
        return enrol_order_data

        
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

