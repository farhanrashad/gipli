# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime, time

from dateutil.relativedelta import relativedelta
from datetime import date

from itertools import groupby
from pytz import timezone, UTC
from werkzeug.urls import url_encode

from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_is_zero
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang, format_amount



class HREOSContract(models.Model):
    """
        Here are the rights associated with the expense flow

        Action       Group                   Restriction
        =================================================================================
        Submit      Employee                Only his own
                    Officer                 If he is expense manager of the employee, manager of the employee
                                             or the employee is in the department managed by the officer
                    Manager                 Always
        Approve     Officer                 Not his own and he is expense manager of the employee, manager of the employee
                                             or the employee is in the department managed by the officer
                    Manager                 Always
        Post        Anybody                 State = approve and journal_id defined
        Done        Anybody                 State = approve and journal_id defined
        Cancel      Officer                 Not his own and he is expense manager of the employee, manager of the employee
                                             or the employee is in the department managed by the officer
                    Manager                 Always
        =================================================================================
    """
    _name = "hr.eos.contract"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "End of Service Contract"
    _order = "date desc, id desc"
    _check_company_auto = True
    
    
    @api.model
    def _default_employee_id(self):
        return self.env.user.employee_id
    
    READONLY_STATES = {
        'submit': [('readonly', True)],
        'approval1': [('readonly', True)],
        'approval2': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }
    
    @api.model
    def _get_employee_id_domain(self):
        res = [('id', '=', 0)] # Nothing accepted by domain, by default
        if self.user_has_groups('hr.group_hr_user'):
            res = "['|', ('company_id', '=', False), ('company_id', '=', company_id)]"  # Then, domain accepts everything
        elif self.user_has_groups('de_emp_books_end_services.group_hr_eos_team_approver') and self.env.user.employee_ids:
            user = self.env.user
            employee = self.env.user.employee_id
            res = [
                '|', '|', '|',
                ('department_id.manager_id', '=', employee.id),
                ('parent_id', '=', employee.id),
                ('id', '=', employee.id),
                ('expense_manager_id', '=', user.id),
                '|', ('company_id', '=', False), ('company_id', '=', employee.company_id.id),
            ]
        elif self.env.user.employee_id:
            employee = self.env.user.employee_id
            res = [('id', '=', employee.id), '|', ('company_id', '=', False), ('company_id', '=', employee.company_id.id)]
        return res
    
    name = fields.Char(string='Name', required=True, translate=True, default=lambda self: _('New'))
    contract_type_id = fields.Many2one('hr.eos.type', string="Contract Type", required=True, states=READONLY_STATES)

    date = fields.Date(states=READONLY_STATES, default=fields.Date.context_today, string="Date", required=True)
    employee_id = fields.Many2one('hr.employee', compute='_compute_employee_id', string="Employee",
        store=True, required=True, readonly=False, tracking=True,
        states=READONLY_STATES,
        default=_default_employee_id, domain=lambda self: self._get_employee_id_domain(), check_company=True)

    user_id = fields.Many2one('res.users', 'Manager', compute='_compute_from_employee_id', store=True, readonly=True, copy=False, states=READONLY_STATES, tracking=True, domain=lambda self: [('groups_id', 'in', self.env.ref('de_emp_books_end_services.group_hr_eos_team_approver').id)])

    department_id = fields.Many2one('hr.department', compute='_compute_from_employee_id', store=True, readonly=False, copy=False, string='Department', states=READONLY_STATES)
    job_title = fields.Char(related='employee_id.job_title' )
    first_contract_date = fields.Date(related='employee_id.first_contract_date')
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True, default=lambda self: self.env.company)

    state = fields.Selection([
        ('draft', 'New'),
        ('submit', 'Submitted'),
        ('approval1', 'Manager Approved'),
        ('approval2', 'HR Approved'),
        ('done', 'Paid'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    
    date_notice_start = fields.Date(states=READONLY_STATES, default=fields.Date.context_today, string="Start Date", required=True)
    date_notice_end = fields.Date(states=READONLY_STATES, default=fields.Date.context_today, string="End Date", required=True)
    
    notice_duration = fields.Char(string='Total Notice', compute='_compute_notice_duration')
    job_duration = fields.Char(string='Service Duration', compute='_compute_job_duration')
    
    description = fields.Html(string='Description')
    
    contract_checklist_ids = fields.Many2many('hr.eos.checklist', string='Checklist')
    checklist_progress = fields.Float(compute='_compute_eos_checklist_progress', string='Progress', store=True,
                                      default=0.0)
    max_rate = fields.Integer(string='Maximum rate', default=100)
    
    # ---------------------------------------------------
    # ------------------ overide methods ----------------
    # ---------------------------------------------------
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('hr.eos.contract') or ' '
        res = super(HREOSContract, self).create(vals)
        return res
    
    def unlink(self):
        for eos in self:
            if contract.state not in ['draft']:
                raise UserError(_('You cannot delete a posted or approved contract.'))
        return super(HREOSContract, self).unlink()
    
    # ---------------------------------------------------
    # ------------------ Computation --------------------
    # ---------------------------------------------------
    @api.depends('company_id')
    def _compute_employee_id(self):
        if not self.env.context.get('default_employee_id'):
            for contract in self:
                contract.employee_id = self.env.user.with_company(contract.company_id).employee_id
    
    @api.depends('employee_id')
    def _compute_from_employee_id(self):
        for contract in self:
            #contract.address_id = contract.employee_id.sudo().address_home_id
            contract.department_id = contract.employee_id.department_id
            contract.user_id = contract.employee_id.parent_id.user_id
            
    @api.depends('date_notice_start','date_notice_end')
    def _compute_notice_duration(self):
        days = months = years = ''
        for contract in self:
            d1 = datetime.strptime(str(contract.date_notice_start), "%Y-%m-%d").date()
            d2 = datetime.strptime(str(contract.date_notice_end), "%Y-%m-%d").date()
            #d2 = date.today()
            rd = relativedelta(d2, d1)
            if rd.days == 1:
                days = str(rd.days) + ' Day'
            if rd.days > 1:
                days = str(rd.days) + ' Days'
                
            if rd.months == 1:
                months = str(rd.months) + ' Month'
            elif rd.months > 0:
                months = str(rd.months) + ' Months'
            
            if rd.years == 1:
                years = str(rd.years) + ' Year' 
            elif rd.years > 1:
                years = str(rd.years) + ' Years' 
            contract.notice_duration = years + ' ' + months + ' ' + days
    
    @api.depends('first_contract_date','date_notice_end')
    def _compute_job_duration(self):
        days = months = years = ''
        for contract in self:
            d1 = datetime.strptime(str(contract.first_contract_date), "%Y-%m-%d").date()
            d2 = datetime.strptime(str(contract.date_notice_end), "%Y-%m-%d").date()
            #d2 = date.today()
            rd = relativedelta(d2, d1)
            if rd.days == 1:
                days = str(rd.days) + ' Day'
            if rd.days > 1:
                days = str(rd.days) + ' Days'
                
            if rd.months == 1:
                months = str(rd.months) + ' Month'
            elif rd.months > 0:
                months = str(rd.months) + ' Months'
            
            if rd.years == 1:
                years = str(rd.years) + ' Year' 
            elif rd.years > 1:
                years = str(rd.years) + ' Years' 
            contract.job_duration = years + ' ' + months + ' ' + days


    @api.depends('contract_checklist_ids')
    def _compute_eos_checklist_progress(self):
        total_len = self.env['hr.eos.checklist'].search_count([])
        for rec in self:
            if total_len != 0:
                check_list_len = len(rec.contract_checklist_ids)
                rec.checklist_progress = (check_list_len * 100) / total_len
            else:
                rec.checklist_progress = 0
    
    
    # --------------------------------------------
    # Mail Thread
    # --------------------------------------------

    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'state' in init_values and self.state in ['approval1','approval2']:
            return self.env.ref('de_emp_books_end_services.mt_eos_contract_approved')
        elif 'state' in init_values and self.state == 'cancel':
            return self.env.ref('de_emp_books_end_services.mt_eos_contract_refused')
        elif 'state' in init_values and self.state == 'done':
            return self.env.ref('de_emp_books_end_services.mt_eos_contract_done')
        return super(HREOSContract, self)._track_subtype(init_values)

    def _message_auto_subscribe_followers(self, updated_values, subtype_ids):
        res = super(HREOSContract, self)._message_auto_subscribe_followers(updated_values, subtype_ids)
        if updated_values.get('employee_id'):
            employee = self.env['hr.employee'].browse(updated_values['employee_id'])
            if employee.user_id:
                res.append((employee.user_id.partner_id.id, subtype_ids, False))
        return res

    # ---------------------------------------------------
    # ------------------ Action Buttons -----------------
    # ---------------------------------------------------
    
    def action_submit_contract(self):
        self.write({'state': 'submit'})
        self.activity_update()
        
    def action_contract_manager_approval(self):        
        if not self.user_has_groups('de_emp_books_end_services.group_hr_eos_team_approver'):
            raise UserError(_("Only Managers and HR Officers can approve contracts"))
        elif not self.user_has_groups('hr.group_hr_manager'):
            current_managers = self.employee_id.parent_id.user_id | self.employee_id.department_id.manager_id.user_id

            if self.employee_id.user_id == self.env.user:
                raise UserError(_("You cannot approve your own contract"))

            if not self.env.user in current_managers and not self.user_has_groups('hr.group_hr_user') and self.employee_id.expense_manager_id != self.env.user:
                raise UserError(_("You can only approve your department contracts"))
        
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('There are no contracts to approve.'),
                'type': 'warning',
                'sticky': False,  #True/False will display for few seconds if false
            },
        }
        filtered_contract = self.filtered(lambda s: s.state in ['submit', 'draft'])
        if not filtered_contract:
            return notification
        for contract in filtered_contract:
            contract.write({'state': 'approval1', 'user_id': contract.user_id.id or self.env.user.id})
        notification['params'].update({
            'title': _('The contract were successfully approved.'),
            'type': 'success',
            'next': {'type': 'ir.actions.act_window_close'},
        })
            
        self.activity_update()
        return notification
    
    def action_hr_approval(self):        
        if not self.user_has_groups('hr.group_hr_user'):
            raise UserError(_("Only Managers and HR Officers can approve contracts"))
        elif not self.user_has_groups('hr.group_hr_manager'):
            if self.employee_id.user_id == self.env.user:
                raise UserError(_("You cannot approve your own contract"))
        
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('There are no contracts to approve.'),
                'type': 'warning',
                'sticky': False,  #True/False will display for few seconds if false
            },
        }
        filtered_contract = self.filtered(lambda s: s.state in ['approval1'])
        if not filtered_contract:
            return notification
        for contract in filtered_contract:
            contract.write({'state': 'approval2', 'user_id': contract.user_id.id or self.env.user.id})
        notification['params'].update({
            'title': _('The contract were successfully approved.'),
            'type': 'success',
            'next': {'type': 'ir.actions.act_window_close'},
        })
            
        self.activity_update()
        return notification
    
    def action_done(self):
        self.write({'state': 'done'})
        self.employee_id.write({
            'active': False,
        })
        self.activity_update()
        
    def action_cancel(self):
        self.write({'state': 'cancel'})
        
    def _get_responsible_for_approval(self):
        if self.user_id:
            return self.user_id
        elif self.employee_id.parent_id.user_id:
            return self.employee_id.parent_id.user_id
        elif self.employee_id.department_id.manager_id.user_id:
            return self.employee_id.department_id.manager_id.user_id
        return self.env['res.users']
        
    def activity_update(self):
        for contract in self.filtered(lambda hol: hol.state == 'submit'):
            self.activity_schedule(
                'de_emp_books_end_services.mail_act_eos_contract_approval',
                user_id=contract.sudo()._get_responsible_for_approval().id or self.env.user.id)
        self.filtered(lambda hol: hol.state in ['approval1','approval2','approval3']).activity_feedback(['de_emp_books_end_services.mail_act_eos_contract_approval'])
        self.filtered(lambda hol: hol.state in ('draft', 'cancel')).activity_unlink(['de_emp_books_end_services.mail_act_eos_contract_approval'])

    