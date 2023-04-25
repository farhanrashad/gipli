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
        
        
        #Comparison
        query = '''
        select a.rule_id, a.rule_name, sum(batch1_total) as batch1_total, sum(batch2_total) as batch2_total from 
        (
            select r.id as rule_id, r.name as rule_name, l.total as batch1_total, 0 as batch2_total 
            from hr_payslip_run b
            join hr_payslip p on p.payslip_run_id = b.id
            join hr_payslip_line l on l.slip_id = p.id 
            join hr_salary_rule r on l.salary_rule_id = r.id 
            where b.company_id= %(company_id)s and b.id = %(from_batch_id)s
            union all 
            select r.id as rule_id, r.name as rule_name, 0 as batch1_total, l.total as batch2_total
            from hr_payslip_run b
            join hr_payslip p on p.payslip_run_id = b.id
            join hr_payslip_line l on l.slip_id = p.id 
            join hr_salary_rule r on l.salary_rule_id = r.id 
            where b.company_id= %(company_id)s and b.id = %(to_batch_id)s
        ) a 
        group by a.rule_id, a.rule_name
        '''
        args = {
            'company_id': data['company_id'],
            'from_batch_id': data['from_batch_id'],
            'to_batch_id': data['to_batch_id'],
        }
        self.env.cr.execute(query)
        rs_rules = self._cr.dictfetchall()
        
        
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
            'batch_name': batch_1.name,
            'batch_name_2': batch_2.name,
            'employee_count': len(employees_batch_1),
            'employee_count_2': len(employees_batch_2),
            'total_net_salary': sum(batch_1.slip_ids.mapped('net_wage')),
            'total_net_salary_2': sum(batch_2.slip_ids.mapped('net_wage')),
            'net_salary_diff': net_salary_diff,
            'total_basic_salary': total_basic_salary,
            'total_basic_salary_1': total_basic_salary_1,
            'basic_salary_diff': basic_salary_diff,
            'allowance_dict': allowance_dict,
            'batch_dict': batch_dict,
            'batch_ded_dict': batch_ded_dict,
            'deduction_dict': deduction_dict,
            'diff_dict': diff_dict,
            'diff_deduction_total': diff_deduction_total,
            'deduction_1': deduction_1,
            'allow_dedud': allow_dedud,
            'data': data,
            'data1': data1,
            'data2': data2,
            'employees': employees_batch_1,
        }
        return report_data
