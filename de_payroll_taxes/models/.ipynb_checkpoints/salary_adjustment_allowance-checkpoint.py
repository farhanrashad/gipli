# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta

class SalaryAdjustmentAllowance(models.Model):
    _name = 'salary.adjustment.allowance'
    _description = 'Salary Adjustment Allowance'
    
    
    name = fields.Char(string='Name')
    company_id=fields.Many2one('res.company', string='Company', compute='_compute_company')
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    rule_id = fields.Many2one('hr.salary.rule', string='Rule', domain="[('salary_adjustment','=', True)]", required=True)
    date=fields.Date(string='Date', required=True, default=fields.date.today().replace(day=1) )
    amount= fields.Float(string='Amount')
    with_effect=fields.Selection([
        ('less', 'Less'),
        ('add', 'Add'),
        ], string="With Effect",
        default="less")
    reconcile_amount= fields.Float(string='Reconcile Amount')
    remaining_amount= fields.Float(string='Remaining Amount')
    fiscal_month=fields.Many2one('fiscal.year.month', string='Month', ondelete='cascade')
    tax_year = fields.Char(string='Year')
    post = fields.Boolean(string='Post')
    adjustment_line_ids=fields.One2many('salary.adjustment.line', 'adjustment_id', string='Adjustment Lines')
    
    
    @api.depends('employee_id')
    def _compute_company(self):
        for line in self:
            if line.employee_id:
                line.update({
                    'company_id': line.employee_id.company_id.id,
                })
            else:
                line.update({
                    'company_id': self.env.company,
                })
    
    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE
        rslt = super(SalaryAdjustmentAllowance, self).create(vals_list)
        rslt._action_generate_adj()
        return rslt
    
    def _action_generate_adj(self):
        for line in self:
            start_month = line.date.month
            adjustment_start_date = line.date
            fiscal_month = line.company_id.fiscal_month.id
            if line.company_id.fiscalyear_last_day in (30,31,28,29):
                fiscal_month =  fiscal_month + 1   
            month_passed = (line.date.month - fiscal_month)
            remaining_month = (12 - month_passed) - 1
            for adjustment in range(remaining_month):
                start_month = start_month + 1
                adjustment_start_date = adjustment_start_date + timedelta(31)   
                vals={
                    'employee_id': line.employee_id.id,
                    'date':  line.date,
                    'rule_id': line.rule_id.id,
                    'amount':  round((line.amount/remaining_month),2),
                    'with_effect': 'add',
                    'fiscal_month': int(start_month),
                    'tax_year':   adjustment_start_date.year,
                    'adjustment_id': line.id,
                    'company_id': line.employee_id.company_id.id,
                } 
                adjustment=self.env['salary.adjustment.line'].create(vals)
                if start_month == 12:
                    start_month = 0  
    
    def unlink(self):
        for line in self:
            if line.post == True:
                raise UserError(_('You cannot delete an Document which is Reconciled.'))
            return super(SalaryAdjustmentAllowance, self).unlink()  
    
    @api.constrains('date')
    def _check_date(self):
        for line in self:
            if line.date:
                line.update({
                    'fiscal_month': int(line.date.month),
                    'tax_year': line.date.year,
                })
                
    @api.constrains('employee_id')
    def _check_employee_id(self):
        for line in self:
            if line.employee_id:
                line.update({
                    'name': line.employee_id.name+' ('+line.employee_id.emp_number+')',
                    'company_id': line.employee_id.company_id.id,
                })


class AdjustmentLine(models.Model):
    _name = 'salary.adjustment.line'
    _description = 'Salary Adjustment Lines'  
    
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    date=fields.Date(string='Date')
    rule_id = fields.Many2one('hr.salary.rule', string='Rule', domain="[('salary_adjustment','=', True)]", required=True)
    fiscal_month=fields.Many2one('fiscal.year.month', string='Month')
    with_effect=fields.Selection([
        ('less', 'Less'),
        ('add', 'Add'),
        ], string="With Effect",
        default="less")
    amount= fields.Float(string='Amount', digits=(12, 2))
    tax_year = fields.Char(string='Year')
    post = fields.Boolean(string='Post')
    company_id=fields.Many2one('res.company', string='Company')
    adjustment_id = fields.Many2one('salary.adjustment.allowance', string='Adjustment')

    def unlink(self):
        for line in self:
            if line.post == True:
                raise UserError(_('You cannot delete an Document which is Reconciled.'))
            return super(AdjustmentLine, self).unlink()