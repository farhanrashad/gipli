# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    def _get_available_contracts_domain(self):
        return [('contract_ids.state', 'in', ('open', 'close')), ('company_id', '=', self.env.company.id)]

    def _get_employees(self):
        active_employee_ids = self.env.context.get('active_employee_ids', False)
        exist_payslips = self.env['hr.payslip'].search([('fiscal_month','=',fields.date.today().month)])
        if active_employee_ids:
            return self.env['hr.employee'].search([('id', 'not in', exist_payslips.employee_id.ids), ('bank_account_id','!=',False),('active', '=', True),('stop_salary','=',False),('contract_ids.state', '=', 'open'), ('company_id', '=', self.env.company.id)])
        # YTI check dates too
        return self.env['hr.employee'].search([('id', 'not in', exist_payslips.employee_id.ids),('bank_account_id','!=',False), ('contract_ids.state', '=', 'open'),('active', '=', True),('stop_salary','=',False),('company_id', '=', self.env.company.id)])
    

    # code commented due to error generate in batch processing
    def compute_sheet111(self):
        self.ensure_one()
        if not self.env.context.get('active_id'):
            from_date = fields.Date.to_date(self.env.context.get('default_date_start'))
            end_date = fields.Date.to_date(self.env.context.get('default_date_end'))
            payslip_run = self.env['hr.payslip.run'].create({
                'name': from_date.strftime('%B %Y'),
                'date_start': from_date,
                'date_end': end_date,
            })
        else:
            payslip_run = self.env['hr.payslip.run'].browse(self.env.context.get('active_id'))
        employees = self.with_context(active_test=False).employee_ids
        if not employees:
            raise UserError(_("You must select employee(s) to generate payslip(s)."))
        payslips = self.env['hr.payslip']
        Payslip = self.env['hr.payslip']
        contracts = employees._get_contracts(
            payslip_run.date_start, payslip_run.date_end, states=['open', 'close']
        ).filtered(lambda c: c.active)
        contracts._generate_work_entries(payslip_run.date_start, payslip_run.date_end)
        work_entries = self.env['hr.work.entry'].search([
            ('date_start', '<=', payslip_run.date_end),
            ('date_stop', '>=', payslip_run.date_start),
            ('employee_id', 'in', employees.ids),
        ])
        
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


        default_values = Payslip.default_get(Payslip.fields_get())
        payslip_values = [dict(default_values, **{
            'name': 'Payslip - %s' % (contract.employee_id.name),
            'employee_id': contract.employee_id.id,
            'credit_note': payslip_run.credit_note,
            'payslip_run_id': payslip_run.id,
            'date_from': payslip_run.date_start,
            'date_to': payslip_run.date_end,
            'contract_id': contract.id,
            'struct_id': self.structure_id.id or contract.structure_type_id.default_struct_id.id,
        }) for contract in contracts]

        payslips = Payslip.with_context(tracking_disable=True).create(payslip_values)
        for payslip in payslips:
            payslip._onchange_employee()

        payslips.compute_sheet()
        payslip_run.state = 'verify'

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.payslip.run',
            'views': [[False, 'form']],
            'res_id': payslip_run.id,
        }


class HrTaxCreditWizard(models.TransientModel):
    _name = 'hr.tax.credit.wizard'
    _description='Tax Credit Wizard'
    
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    date = fields.Date(string='Start Date', required=True, default=fields.date.today() )
    credit_amount = fields.Float(string='Credit Amount')
    number_of_month = fields.Integer(string='Number Of Month', default=1)
    remarks = fields.Char(string='Remarks')
    credit_type_id = fields.Many2one('tax.credit.type', string='Tax Credit Type', required=True)

    
    def action_create_tax_credit(self):
        for line in self:
            period=line.date
            count = 0
            for ext_rang in range(self.number_of_month):
                count +=1
                if count > 1:
                    period=period+timedelta(31)
                vals={
                    'name': line.employee_id.name +' ('+str(line.employee_id.emp_number)+')',
                    'employee_id': line.employee_id.id,
                    'date': period,
                    'fiscal_month': period.month,
                    'tax_year': period.year,
                    'tax_amount': (line.credit_amount/line.number_of_month),
                    'company_id': line.employee_id.company_id.id,
                    'remarks': line.remarks,
                    'dist_month': line.number_of_month,
                    'post': 'N',
                    'credit_type_id': line.credit_type_id.id,
                }
                tax_credit=self.env['hr.tax.credit'].create(vals)
    
    
    
    
    
    
 
    
    
    

