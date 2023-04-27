from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PayslipReport(models.AbstractModel):
    _name = 'report.de_payslip_batches_comparison.batch_wise_payroll'

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_('Form content is missing, this report cannot be printed.'))
            
        from_batch_id = self.env['hr.payslip.run'].browse(data['form']['from_batch_id'])
        to_batch_id = self.env['hr.payslip.run'].browse(data['form']['to_batch_id'])
        
        
        # Compensation Query
        query = '''
        select a.rule_id, a.rule_name, sum(batch1_total) as batch1_total, sum(batch2_total) as batch2_total,
            sum(batch1_total-batch2_total) as batch_diff
        FROM (
            select r.id as rule_id, r.compansation_summary_label as rule_name, l.total as batch1_total, 0 as batch2_total
            from hr_payslip_run b
            join hr_payslip p on p.payslip_run_id = b.id
            join hr_payslip_line l on l.slip_id = p.id 
            join hr_salary_rule r on l.salary_rule_id = r.id 
            where b.company_id = %(company_id)s and b.id = %(from_batch_id)s
            and reconcile_compansation = True
            union all 
            select r.id as rule_id, r.compansation_summary_label as rule_name, 0 as batch1_total, l.total as batch2_total
            from hr_payslip_run b
            join hr_payslip p on p.payslip_run_id = b.id
            join hr_payslip_line l on l.slip_id = p.id 
            join hr_salary_rule r on l.salary_rule_id = r.id 
            where b.company_id = %(company_id)s and b.id = %(to_batch_id)s
            and reconcile_compansation = True
        ) a 
        group by a.rule_id, a.rule_name
        '''
        args = {
            'company_id': data['form']['company_id'],
            'from_batch_id': data['form']['from_batch_id'],
            'to_batch_id': data['form']['to_batch_id'],
        }
        self.env.cr.execute(query, args)
        rs_rules = self._cr.dictfetchall()
        
        # Deductions Query
        query = '''
        select a.rule_id, a.rule_name, sum(batch1_total) as batch1_total, sum(batch2_total) as batch2_total,
            sum(batch1_total-batch2_total) as batch_diff
        FROM (
            select r.id as rule_id, r.deduction_summary_label as rule_name, l.total as batch1_total, 0 as batch2_total 
            from hr_payslip_run b
            join hr_payslip p on p.payslip_run_id = b.id
            join hr_payslip_line l on l.slip_id = p.id 
            join hr_salary_rule r on l.salary_rule_id = r.id 
            where b.company_id = %(company_id)s and b.id = %(from_batch_id)s
            and r.reconcile_deduction = True
            union all 
            select r.id as rule_id, r.deduction_summary_label as rule_name, 0 as batch1_total, l.total as batch2_total
            from hr_payslip_run b
            join hr_payslip p on p.payslip_run_id = b.id
            join hr_payslip_line l on l.slip_id = p.id 
            join hr_salary_rule r on l.salary_rule_id = r.id 
            where b.company_id = %(company_id)s and b.id = %(to_batch_id)s
            and r.reconcile_deduction = True
        ) a 
        group by a.rule_id, a.rule_name
        '''
        args = {
            'company_id': data['form']['company_id'],
            'from_batch_id': data['form']['from_batch_id'],
            'to_batch_id': data['form']['to_batch_id'],
        }
        self.env.cr.execute(query, args)
        rs_ded_rules = self._cr.dictfetchall()
        
        
        # Employees Data
        query = '''
        select ROW_NUMBER() OVER( ORDER BY 1) as sr_no, 
            a.emp_id, a.emp_number, a.emp_name, a.rule_id, max(a.doj) as doj, sum(batch1_total) as batch1_total, sum(batch2_total) as batch2_total,
            sum(batch1_total - batch2_total) as batch_diff
            from (
                select e.id as emp_id, e.emp_number, e.date as doj, e.name as emp_name, r.id as rule_id, 
                l.total as batch1_total, 0 as batch2_total 
                from hr_payslip_run b
                join hr_payslip p on p.payslip_run_id = b.id
                join hr_payslip_line l on l.slip_id = p.id 
                join hr_salary_rule r on l.salary_rule_id = r.id
                join hr_employee e on p.employee_id = e.id
                where b.company_id = %(company_id)s and b.id = %(from_batch_id)s
                union all 
                select e.id as emp_id, e.emp_number, e.date as doj, e.name as emp_name, r.id as rule_id,
                0 as batch1_total, l.total as batch2_total 
                from hr_payslip_run b
                join hr_payslip p on p.payslip_run_id = b.id
                join hr_payslip_line l on l.slip_id = p.id 
                join hr_salary_rule r on l.salary_rule_id = r.id
                join hr_employee e on p.employee_id = e.id
                where b.company_id = %(company_id)s and b.id = %(to_batch_id)s
            ) a
            group by a.rule_id, a.emp_id, a.emp_number, a.emp_name
            having sum(batch1_total - batch2_total) != 0
        '''
        args = {
            'company_id': data['form']['company_id'],
            'from_batch_id': data['form']['from_batch_id'],
            'to_batch_id': data['form']['to_batch_id'],
        }
        self.env.cr.execute(query, args)
        rs_employees = self._cr.dictfetchall()
        
        
        
        batch_1 = self.env['hr.payslip.run'].browse(data['form']['from_batch_id'])
        batch_2 = self.env['hr.payslip.run'].browse(data['form']['to_batch_id'])
        employees_batch_1 = self.env['hr.employee'].search([('id', 'in', batch_1.slip_ids.employee_id.ids)])
        employees_batch_2 = self.env['hr.employee'].search([('id', 'in', batch_2.slip_ids.employee_id.ids)])

        report = self.env['ir.actions.report']._get_report_from_name('de_payslip_batches_comparison.batch_wise_payroll')
        net_salary_diff = sum(batch_1.slip_ids.mapped('net_wage')) - sum(
            batch_2.slip_ids.mapped('net_wage'))

        # For Basic Salary Batch 1
        payslips_batch_1 = self.env['hr.payslip'].search([('payslip_run_id', '=', batch_1.id)])
        payslip_lines = self.env['hr.payslip.line'].search([('slip_id', 'in', payslips_batch_1.ids)])
        total_basic_salary = sum(line.total for line in payslip_lines if line.code == 'BASIC')
        # ********************************************* Allowance in Batch 1 ****************************************
        allowances = self.env['hr.payslip.line'].search(
            [('slip_id', 'in', payslips_batch_1.ids), ('category_id.code', '=', 'ALW')])
        # ********************************************* Deduction in Batch 1 ****************************************
        deduction = self.env['hr.payslip.line'].search(
            [('slip_id', 'in', payslips_batch_1.ids), ('category_id.code', '=', 'DED')])
        # ********************************************* Sum All Allowances ****************************************
        batch_dict = {}
        for allo in allowances:
            name = allo.name
            amount = allo.amount
            if name in batch_dict:
                batch_dict[name] += allo.amount
            else:
                batch_dict[allo.name] = allo.amount
        # ********************************************* For sum Of each deduction ***************************
        batch_ded_dict = {}
        for da in deduction:
            name = da.name
            amount = da.amount
            if name in batch_ded_dict:
                batch_ded_dict[name] += da.amount
            else:
                batch_ded_dict[name] = da.amount
        # ***************************************** For Basic Salary Batch 2 ********************************
        payslips_batch_2 = self.env['hr.payslip'].search([('payslip_run_id', '=', batch_2.id)])
        payslip_lines_1 = self.env['hr.payslip.line'].search([('slip_id', 'in', payslips_batch_2.ids)])
        total_basic_salary_1 = sum(line.total for line in payslip_lines_1 if line.code == 'BASIC')
        basic_salary_diff = total_basic_salary - total_basic_salary_1
        allowances_1 = self.env['hr.payslip.line'].search(
            [('slip_id', 'in', payslips_batch_2.ids), ('category_id.code', '=', 'ALW')])
        # ********************************************* For Sum of Allowance Batch 1 and Batch 2 *******
        allowance_total = sum(line.amount for line in payslip_lines if line.category_id.code == 'ALW')
        allowance_total_1 = sum(line.amount for line in payslip_lines_1 if line.category_id.code == 'ALW')
        # ***************************************** For Sum Deduction in Batch 1 and Batch 2 *****************
        deduction_total = sum(line.amount for line in payslip_lines if line.category_id.code == 'DED')
        deduction_total_1 = sum(line.amount for line in payslip_lines_1 if line.category_id.code == 'DED')
        # ***************************************** Difference in Deduction in Batch 1 and Batch 2 *****************
        total_ded_difference = deduction_total - deduction_total_1
        total_allow_difference = allowance_total - allowance_total_1
        allow_dedud = total_allow_difference - total_ded_difference
        deduction_1 = self.env['hr.payslip.line'].search(
            [('slip_id', 'in', payslips_batch_2.ids), ('category_id.code', '=', 'DED')])
        # ***************************************** For Batch 2 Allowance *****************
        allowance_dict = {}
        for batch_allowance in allowances_1:
            name = batch_allowance.name
            amount = batch_allowance.amount
            if name in allowance_dict:
                allowance_dict[name] += batch_allowance.amount
            else:
                allowance_dict[name] = batch_allowance.amount
        # ***************************************** For Batch 2 Deduction *****************
        deduction_dict = {}
        for batch_deduction in deduction_1:
            name = batch_deduction.name
            amount = batch_deduction.amount
            if name in deduction_dict:
                deduction_dict[name] += batch_deduction.amount
            else:
                deduction_dict[name] = batch_deduction.amount

        # ***************************************** Difference Between Allowance *****************
        diff_dict = {}
        for name in batch_dict:
            if name in allowance_dict:
                diff = batch_dict[name] - allowance_dict[name]
                diff_dict[name] = diff

        # ***************************************** Difference Between Deduction *****************
        diff_deduction_total = {}
        for name in batch_ded_dict:
            if name in deduction_dict:
                diff_ded = batch_ded_dict[name] - deduction_dict[name]
                diff_deduction_total[name] = diff_ded
        # ******* For Getting Employee if has Net Salary Not Match between Batch 1 and Batch 2 ********
        data = {}
        data1 = {}
        data2 = {}
        for payslip in payslips_batch_1:
            for payslip1 in payslips_batch_2:
                if payslip.employee_id.id == payslip1.employee_id.id:
                    if payslip.net_wage != payslip1.net_wage:
                        diff_net_wage = payslip.net_wage - payslip1.net_wage
                        data[payslip] = payslip
                        data1[payslip1] = payslip1
                        data2[diff_net_wage] = diff_net_wage
                        
        

        report_data = {
            'from_batch_id': from_batch_id,
            'to_batch_id': to_batch_id,
            'rs_rules': rs_rules,
            'rs_ded_rules': rs_ded_rules,
            'rs_employees': rs_employees,
            'currency': self.env.company.currency_id.name,
        }
        return report_data
