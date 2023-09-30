# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools


class ReportLoan(models.Model):
    _name = "report.hr.loan"
    _description = "Loan Analysis Report"
    _auto = False
    _rec_name = 'date'
    _order = 'date desc'

    @api.model
    def _get_done_states(self):
        return ['sale', 'done']

    nbr = fields.Integer('# of Lines', readonly=True)
    name = fields.Char('Loan Reference', readonly=True)
    date = fields.Datetime('Loan Date', readonly=True)
    loan_type_id = fields.Many2one('hr.loan.type', 'Loan Type', readonly=True)
    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    employee_id = fields.Many2one('hr.employee', 'Employee', readonly=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True)
    amount_loan = fields.Float('Amount', readonly=True)
    amount_paid = fields.Float('Paid', readonly=True)
    amount_disbursed = fields.Float('Disbursed', readonly=True)
    amount_balance = fields.Float('Balance', readonly=True)
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('verify', 'Verified'),
        ('confirm', 'To Approve'),
        ('validate1', 'Second Approval'),
        ('validate', 'Approved'),
        ('post', 'Posted'),
        ('paid', 'Paid'),
        ('partial', 'Partially Reconciled'),
        ('close', 'Reconciled'),
        ('refuse', 'Refused'),
        ], string='Status', readonly=True)
    date_due = fields.Datetime('Order Date', readonly=True)
    amount_inst = fields.Float('Installment', readonly=True)


    @property
    def _table_query(self):
        ''' Report needs to be dynamic to take into account multi-company selected + multi-currency rates '''
        return '%s %s %s %s' % (self._select(), self._from(), self._where(), self._group_by())

    def _select(self):
        select_str = """
                SELECT
                    min(ln.id) as id, 
                    ln.name, ln.date, 
                    ln.loan_type_id, 
                    tp.product_id, 
                    ln.employee_id, 
                    ln.company_id,
                    sum(ln.amount) as amount_loan, 
                    sum(ln.amount_paid) as amount_paid, 
                    sum(ln.amount_disbursed) as amount_disbursed, 
                    sum(ln.amount_balance) as amount_balance,
                    ln.state,
                    l.date as date_due,
                    sum(l.amount) as amount_inst
        """
        return select_str
        
    def _from(self):
        from_str = """
            FROM
            hr_loan ln
            join hr_loan_type tp on ln.loan_type_id = tp.id
            join hr_loan_line l on l.loan_id = ln.id
        """
        return from_str
    
    def _where(self):
        return """
            WHERE
                ln.name is not null
        """

    def _group_by(self):
        group_by_str = """
            GROUP BY
                ln.name, 
            ln.date, 
            ln.loan_type_id, 
            tp.product_id, 
            ln.employee_id, 
            ln.company_id,
            ln.amount, 
            ln.amount_paid, 
            ln.amount_disbursed, 
            ln.amount_balance,
            ln.state,
            l.date,
            l.amount
        """
        return group_by_str
    