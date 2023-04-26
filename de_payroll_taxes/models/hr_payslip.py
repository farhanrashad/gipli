# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from datetime import date, datetime, timedelta

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    
    employee_number = fields.Char(related='employee_id.emp_number')
    work_location_id = fields.Many2one('hr.work.location', string='FWork Location', compute='_compute_work_location')  
    fwork_location_id = fields.Many2one('hr.work.location', string='Work Location')   
    is_salary_Stop = fields.Boolean(string='Stop Salary')
    current_month_tax_amount = fields.Float(string='Tax Amount')
    arrears_amount = fields.Float(string='Arrears Amount')
    current_pfund = fields.Float(string='Pfund Amount')
    absent_amount = fields.Float(string='Absent Amount')
    ot_hours = fields.Float(string='OT Hours')
    fiscal_month = fields.Many2one('fiscal.year.month', string='Month')
    tax_year = fields.Char(string='Year')
    next_fiscal_month = fields.Date(string='Next Month')
    net_work_days = fields.Float(string='Net Days', compute='_compute_net_workdays')
    date_of_joining = fields.Date(string='Date of Joining')
    fiscal_year_date = fields.Date(string='Last Date')
    current_taxable_amount = fields.Float(string='Taxable Amount')
 

    @api.depends('work_location_id','employee_id','fwork_location_id')
    def _compute_work_location(self):
        for slip in self:
            slip.update({
               'work_location_id': slip.employee_id.work_location_id.id,
               'date_of_joining': slip.employee_id.date,
               'fwork_location_id': slip.employee_id.work_location_id.id, 
               
            })

    @api.depends('worked_days_line_ids', 'worked_days_line_ids.number_of_days')
    def _compute_net_workdays(self):
        for slip in self:
            net_days = 0
            absent_days = 0
            for workday in slip.worked_days_line_ids:
                if workday.work_entry_type_id.code == "ABSENT100":
                    absent_days += workday.number_of_days
            net_days = slip.fiscal_month.days - absent_days
            if net_days < 0:
                net_days = 0   
            slip.update({
                'net_work_days': net_days,
                'fiscal_year_date': '2022-06-30' ,
            })
            
    def action_update_income_tax(self):   
        taxable_amount_list = []
        fiscal_y_amount_credit= 0
        previous_year_vals = 0
        previous_tax_ded_amount = 0
        previous_taxable_amount = 0
        previous_pf_amount = 0
        current_year_vals=int(self.date_to.year)
        if self.fiscal_month.id in (1,2,3,4,5,6):
            previous_year_vals=int(self.date_to.year) - 1
            previous_year_tax_credits = self.env['hr.tax.credit'].search([('employee_id','=',self.employee_id.id),('tax_year','=',previous_year_vals), ('fiscal_month',  'in', (7,8,9,10,11,12) )])
            for  prv_y_credit in previous_year_tax_credits:
                fiscal_y_amount_credit += prv_y_credit.tax_amount                 
            previous_year_tax_data = self.env['hr.tax.ded'].search([('employee_id','=',self.employee_id.id),('period_num','in',(7,8,9,10,11,12)),('tax_year','=', previous_year_vals )]) 
            for prv_year_tax in previous_year_tax_data:
                previous_tax_ded_amount += prv_year_tax.tax_ded_amount
                previous_taxable_amount += prv_year_tax.taxable_amount
                previous_pf_amount += prv_year_tax.pf_amount
                         
        current_year_tax_data = self.env['hr.tax.ded'].search([('employee_id','=',self.employee_id.id),('period_num','in', (1,2,3,4,5,6)),('tax_year','=', current_year_vals),('fiscal_month','<', self.fiscal_month.id) ], order='period_num asc')
        curr_year_month_fiscal_month = self.date_to.month
        month_passed = 0
        if curr_year_month_fiscal_month==8:
            month_passed = 1
        elif curr_year_month_fiscal_month==9:
            month_passed = 2
        elif curr_year_month_fiscal_month==10:
            month_passed = 3
        elif curr_year_month_fiscal_month==11:
            month_passed = 4
        elif curr_year_month_fiscal_month==12:
            month_passed = 5
        elif curr_year_month_fiscal_month==1:
            month_passed = 6
        elif curr_year_month_fiscal_month==2:
            month_passed = 7
        elif curr_year_month_fiscal_month==3:
            month_passed = 8
        elif curr_year_month_fiscal_month==4:
            month_passed = 9
        elif curr_year_month_fiscal_month==5:
            month_passed = 10
        elif curr_year_month_fiscal_month==6:
            month_passed = 11         
        
        for curr_year_tax in current_year_tax_data:
            previous_tax_ded_amount += curr_year_tax.tax_ded_amount
            previous_taxable_amount += curr_year_tax.taxable_amount
            previous_pf_amount += curr_year_tax.pf_amount
             
            
        fiscal_month = 12 - (month_passed)
        pf=0
        if self.employee_id.pf_member in ('yes_with', 'yes_without'): 
            pf = previous_pf_amount + ((self.contract_id.wage * self.employee_id.company_id.pf_percent)/100) * fiscal_month   
        current_month_pf_amt = 0    
        current_month_pf_amt = 0
        ext_month_days = self.env['fiscal.year.month'].sudo().search([('id','=',self.date_to.month)], limit=1).days
        fiscal_year_start_date = fields.date.today().replace(month=7,day=1) 
        fiscal_year_end_date = fields.date.today().replace(month=6,day=30) 
        if self.fiscal_month.id in (1,2,3,4,5,6):
            previous_year = (fields.date.today().year - 1)
            fiscal_year_start_date = fields.date.today().replace(month=6, day=1, year=previous_year)
            
        if self.employee_id.pf_effec_date:
            if  self.employee_id.pf_effec_date > fiscal_year_start_date and self.employee_id.pf_effec_date < fiscal_year_end_date:
                month_days = self.env['fiscal.year.month'].sudo().search([('id','=',self.employee_id.pf_effec_date.month)], limit=1).days
                month_start_date = self.employee_id.pf_effec_date.replace(day=1)
                month_end_date = self.employee_id.pf_effec_date.replace(day=month_days)
                remaining_fiscal_month = 0
                tax_fiscal_month = self.employee_id.pf_effec_date.month
                if tax_fiscal_month==7:
                    remaining_fiscal_month = 11
                elif tax_fiscal_month==8:
                    remaining_fiscal_month = 10
                elif tax_fiscal_month==9:
                    remaining_fiscal_month = 9
                elif tax_fiscal_month==10:
                    remaining_fiscal_month = 8
                elif tax_fiscal_month==11:
                    remaining_fiscal_month = 7
                elif tax_fiscal_month==12:
                    remaining_fiscal_month = 6
                elif tax_fiscal_month==1:
                    remaining_fiscal_month = 5
                elif tax_fiscal_month==2:
                    remaining_fiscal_month = 4
                elif tax_fiscal_month==3:
                    remaining_fiscal_month = 3
                elif tax_fiscal_month==4:
                    remaining_fiscal_month = 2
                elif tax_fiscal_month==5:
                    remaining_fiscal_month = 1
                elif tax_fiscal_month==6:
                    remaining_fiscal_month = 0 
                if  self.employee_id.pf_effec_date > month_start_date and self.employee_id.pf_effec_date < month_end_date:
                    pf = ((self.contract_id.wage * self.employee_id.company_id.pf_percent)/100) * remaining_fiscal_month  
                    total_pf_amt = (((self.contract_id.wage * self.employee_id.company_id.pf_percent)/100))/month_days
                    delta_days = (month_end_date - self.employee_id.pf_effec_date).days + 1 
                    current_month_pf_amt = total_pf_amt * delta_days
                    pf = pf + current_month_pf_amt 
        apf = 0
        if pf > self.employee_id.company_id.pf_exceeding_amt:
            apf=pf-self.employee_id.company_id.pf_exceeding_amt    
            
        total_sum_allowance = 0
        taxable_input_types = self.env['hr.payslip.input.type'].search([('is_include_tax', '=', True)])
        for taxable_input_type in taxable_input_types:
            for input_line in self.input_line_ids:
                if input_line.input_type_id.id==taxable_input_type.id:
                    total_sum_allowance += input_line.amount

        if self.contract_id.gme_salary==True:
            for input_line in self.input_line_ids:
                if input_line.input_type_id.code=='UT01':
                    total_sum_allowance = total_sum_allowance - input_line.amount
                 
        current_month_taxable_amount = self.employee_id.contract_id.wage +  total_sum_allowance 
        if self.contract_id.is_split_salary==True:
            current_month_taxable_amount = self.contract_id.basic_salary +  total_sum_allowance 
        
        medical_amount = 0 
        current_month_taxable_amount = current_month_taxable_amount - medical_amount
        
        #=========================================================
        # Absent Deduction
        #=========================================================
        leap_year=False
        leap_year_amount = 1
        if self.fiscal_month.id==2:
            leap_year_amount=((self.date_to.year)/4)
        if leap_year_amount == 0:
            leap_year=True
        days=self.fiscal_month.days
        if leap_year==True:
            days = days + 1
        absent_days = 0    
        for work_days in self.worked_days_line_ids:
            if work_days.work_entry_type_id.code=='ABSENT100':
                absent_days = work_days.number_of_days      
        deduction_amount=(self.contract_id.wage/days) * absent_days
        if self.employee_id.leave_ded==True:
            deduction_amount=0 
        
        current_month_ot_amount = 0 
        current_month_arrear_amount = 0 
        future_month_allowance = 0
        current_month_bonus_amount = 0
        for input_line in self.input_line_ids:
            if input_line.input_type_id.code=='OT100': 
                current_month_ot_amount =  input_line.amount
            if input_line.input_type_id.code=='ARR01': 
                current_month_arrear_amount =  input_line.amount
            if input_line.input_type_id.code=='B01': 
                current_month_bonus_amount =  input_line.amount
          
        total_taxable_adjustment_amt = 0    
        taxable_amount_adj = self.env['taxable.ded.entry'].search([('employee_id','=',self.employee_id.id),('date','>=',fiscal_year_start_date ),('date','<=',fiscal_year_end_date)])
        for tax_adj in taxable_amount_adj:
            total_taxable_adjustment_amt += tax_adj.amount
        self.current_taxable_amount =   (current_month_taxable_amount + current_month_bonus_amount + current_month_arrear_amount  + current_month_ot_amount)  
        yearly_taxable_amount = ((current_month_taxable_amount * fiscal_month) + current_month_arrear_amount  + current_month_ot_amount + previous_taxable_amount + apf - deduction_amount) - total_taxable_adjustment_amt
        
        if self.contract_id.is_medical==True:
            basic_devision = yearly_taxable_amount/2
            medical_amount  = (basic_devision/100) * self.contract_id.medical_percent
        yearly_taxable_amount = yearly_taxable_amount - medical_amount
        taxable_amount_list.append(yearly_taxable_amount)
        bonus_yearly_taxable_amount = yearly_taxable_amount + current_month_bonus_amount 
        taxable_amount_list.append(bonus_yearly_taxable_amount)   
        #=========================================================
        #Tax slabs
        #=========================================================   
        taxable_amount_count=0
        basic_tax_amount=0
        bonus_taxable_amount=0
        result = 0
        tax_slab_loop_count = 0
        for taxable_amount in  taxable_amount_list:
            tax_slab_loop_count += 1 
            taxable_amount_count += 1
            tax_range = self.env['hr.tax.range'].search([('year','=',self.date_to.year)], limit=1)
            if not tax_range:
                previous_year_tax_range_vals = self.env['hr.tax.range'].search([('year','=',self.date_to.year-1)], limit=1)
                if previous_year_tax_range_vals:
                    rng_year_vals = {
                        'date': self.date_to,
                        'name': 'Tax Range For Year '+str(self.date_to.year),
                        'month': self.date_to.month, 
                        'year': self.date_to.year,    
                    }
                    hr_tax_range = self.env['hr.tax.range'].create(rng_year_vals)
                    for line_range_vals in previous_year_tax_range_vals.tax_range_line_ids:
                        line_vals = {
                            'range_id': hr_tax_range.id,
                            'month': self.date_to.month, 
                            'year': self.date_to.year,
                            'start_amount': line_range_vals.start_amount,
                            'end_amount': line_range_vals.end_amount,
                            'addition_amount': line_range_vals.addition_amount,
                            'percentage': line_range_vals.percentage,
                            'deduction_amount': line_range_vals.deduction_amount,
                        }
                        line_tax_range = self.env['hr.tax.range.line'].create(line_vals)                                     
            tax_range = self.env['hr.tax.range'].search([('year','=',self.date_to.year)], limit=1)
            tax_range_lines = self.env['hr.tax.range.line'].search([('range_id','=',tax_range.id)], order='percentage asc')
            for range_vals in tax_range_lines:  
                if taxable_amount >= range_vals.start_amount and taxable_amount <= range_vals.end_amount:
                    result = ((taxable_amount - range_vals.deduction_amount)/100) * range_vals.percentage + range_vals.addition_amount
            if tax_slab_loop_count==1:       
                basic_tax_amount = result
            if tax_slab_loop_count==2:
                bonus_taxable_amount = result     
        
        bonus_tax_amount  = bonus_taxable_amount - basic_tax_amount
        if bonus_tax_amount < 0:
            bonus_tax_amount  = 0         
        fiscal_year_tax_credits = self.env['hr.tax.credit'].search([('employee_id','=',self.employee_id.id),('date','>=', fiscal_year_start_date),('date','<', self.date_to) ])
        for  fiscal_y_credit in fiscal_year_tax_credits:
            fiscal_y_amount_credit += fiscal_y_credit.tax_amount
        current_month_tax = basic_tax_amount - (previous_tax_ded_amount + fiscal_y_amount_credit)
        comulative_tax = (current_month_tax / fiscal_month)
        if comulative_tax < 0:
            comulative_tax=0  
        result=round(comulative_tax+bonus_tax_amount)

        
        #==============================================
        # Tax Credit Adjustment
        #==============================================
        tax_credits = self.env['hr.tax.credit'].search([('employee_id','=',self.employee_id.id),('tax_year','=',self.tax_year),('fiscal_month','=',self.fiscal_month.id)])
        existing_post = 'N'
        for tax_credit in tax_credits:  
            if tax_credit.tax_amount >  result and result > 0:
                existing_post = tax_credit.post
                tax_credit.update({'reconcile_amount':result, 'post':'Y' , 'remaining_amount': (tax_credit.tax_amount - result)}) 
                result=0
            elif result==0:
                tax_credit.update({'reconcile_amount':0, 'post':'Y' , 'remaining_amount': (tax_credit.tax_amount)}) 
            else:
                result=result - tax_credit.tax_amount
                tax_credit.update({'reconcile_amount':tax_credit.tax_amount,  'post':'Y', 'remaining_amount': 0})
        tot_remaining_amount=0.0
        credit_type = 2
        after_tax_credits = self.env['hr.tax.credit'].search([('employee_id','=',self.employee_id.id),('tax_year','in',(previous_year_vals, current_year_vals)), 
          ('fiscal_month','=',self.fiscal_month.id)])
        for atax_credit in after_tax_credits:
            tot_remaining_amount += atax_credit.remaining_amount
            credit_type = atax_credit.credit_type_id.id
        next_payslip_period =1   
        next_year= self.tax_year
        if  self.fiscal_month:
            next_payslip_period= self.fiscal_month.id + 1
            next_year_date=self.next_fiscal_month.month
            next_year= self.next_fiscal_month.strftime('%Y')
        next_tax_credit = self.env['hr.tax.credit'].search([('employee_id','=',self.employee_id.id),('tax_year','=',next_year),('fiscal_month','=',next_payslip_period)], limit=1) 
        if next_tax_credit:   
            next_tax_credit.tax_amount - tot_remaining_amount
            tot_proceded_amount=next_tax_credit.tax_amount + tot_remaining_amount
            if existing_post=='N':
                next_tax_credit.update({
                      'tax_amount':  tot_proceded_amount,
                })  
        if not next_tax_credit and tot_remaining_amount >  0.0:
            employee_credit = self.env['hr.employee'].search([('id','=', self.employee_id.id)], limit=1)
            vals = {
                'name': employee_credit.name +' '+str(employee_credit.emp_number),
               'fiscal_month': next_payslip_period if next_payslip_period<=12  else 1 ,
               'tax_year':  next_year,
               'employee_id':  self.employee_id.id,
               'date' :  self.next_fiscal_month,
               'tax_amount': tot_remaining_amount,
               'post':  'N',
               'credit_type_id':  credit_type,
               'dist_month':  1,
              'company_id': self.company_id.id ,
            } 
            if self.fiscal_month.id!=6:  
                next_tax_credit=self.env['hr.tax.credit'].create(vals)

        if self.employee_id.is_consultant=='yes':
            result=round((self.contract_id.wage/100)*self.employee_id.tax_rate)

        #============================================
        # Tax Concession in Current Month
        #============================================
        tax_rule = self.env['hr.salary.rule'].search([('code','=','INC01')], limit=1)
        salary_adjust = self.env['salary.adjustment.allowance'].search([('rule_id', '=', tax_rule.id),('employee_id','=',self.employee_id.id),('fiscal_month','=',self.fiscal_month.id),('with_effect' , '=' ,  'less' )], limit=1)
        if salary_adjust:
            result = result - salary_adjust.amount
            salary_adjust.update({
              'post': True
            })
        for input_line in self.input_line_ids:
            if input_line.input_type_id.code=='INC01':
                result = input_line.amount         
        result =  round(result)
        self.current_month_tax_amount = result
        #==========================================
        # END Calculations
        #==========================================
    
            

    def compute_sheet(self):
        for pay in self:
            delta_days = 0
            tot_day_unpaid = 0
            salary_rules = self.env['hr.salary.rule'].search([('salary_adjustment','=',True)])
            for sly_rule in salary_rules:
                adjustments=self.env['salary.adjustment.allowance'].search([('rule_id','=',sly_rule.id),('employee_id','=',pay.employee_id.id),('tax_year','=',pay.date_to.year),('fiscal_month','=',pay.fiscal_month.id) ])
                rule_total_adj_amt = 0
                with_effect = ''
                if adjustments:
                    for adj in adjustments:
                        with_effect = adj.with_effect
                        adj.update({'post':True})
                        rule_total_adj_amt += adj.amount
                    if sly_rule.code=='INC01' and with_effect=='add':
                        other_inputs = self.env['hr.payslip.input.type'].search([('code','=',sly_rule.code)], limit=1)
                        inputs_adj = self.env['hr.payslip.input'].search([('payslip_id','=', pay.id),('input_type_id.code','=',sly_rule.code)])
                        if inputs_adj:
                            inputs_adj.update({
                              'amount': rule_total_adj_amt
                            })
                        if not inputs_adj and other_inputs:
                            other_inputs = {
                            'payslip_id': pay.id,
                            'input_type_id': other_inputs.id,
                            'amount': rule_total_adj_amt,
                            }
                            inputs=self.env['hr.payslip.input'].create(other_inputs)
                    elif sly_rule.code!='INC01':      
                        other_inputs = self.env['hr.payslip.input.type'].search([('code','=',sly_rule.code)], limit=1)
                        inputs_adj = self.env['hr.payslip.input'].search([('payslip_id','=', pay.id),('input_type_id.code','=',sly_rule.code)])
                       
                        if inputs_adj:
                            inputs_adj.update({
                              'amount': rule_total_adj_amt
                            })
                        if not inputs_adj and other_inputs:
                            other_inputs = {
                              'payslip_id': pay.id,
                              'input_type_id': other_inputs.id,
                              'amount': rule_total_adj_amt,
                            }
                            inputs=self.env['hr.payslip.input'].create(other_inputs)        
            next_month=pay.date_to +timedelta(31)
            pay.update({
                'fiscal_month':  pay.date_to.month,
                'next_fiscal_month': next_month,
                'tax_year': pay.date_to.year,
            })
            for rule in pay.line_ids:
                if rule.code=='PF01':  
                    pay.update({
                      'current_pfund': rule.amount,
                    })
                if rule.code=='ARR01':  
                    pay.update({
                      'arrears_amount': rule.amount,
                    }) 
                if rule.code=='ABNT':  
                    pay.update({
                      'absent_amount': rule.amount,
                    })
            pay.action_update_income_tax()
            if pay.contract_id.is_split_salary==True:
                house_rent = self.env['hr.payslip.input.type'].search([('code','=','HR01')], limit=1)
                house_rent_inputs_adj = self.env['hr.payslip.input'].search([('payslip_id','=', pay.id),('input_type_id.code','=',house_rent.code)])
                if house_rent_inputs_adj:
                    house_rent_inputs_adj.update({
                      'amount': self.contract_id.house_rent
                    })
                if not house_rent_inputs_adj:
                    house_other_inputs = {
                      'payslip_id': pay.id,
                      'input_type_id': house_rent.id,
                      'amount': self.contract_id.house_rent,
                    }
                    house_rentinputs=self.env['hr.payslip.input'].create(house_other_inputs)
                    
                utility = self.env['hr.payslip.input.type'].search([('code','=','UT01')], limit=1)
                utility_inputs_adj = self.env['hr.payslip.input'].search([('payslip_id','=', pay.id),('input_type_id.code','=',utility.code)])
                if utility_inputs_adj:
                    utility_inputs_adj.update({
                      'amount': self.contract_id.utility,
                    })
                if not utility_inputs_adj:
                    utility_other_inputs = {
                      'payslip_id': pay.id,
                      'input_type_id': utility.id,
                      'amount': self.contract_id.utility,
                    }
                    utility_inputs=self.env['hr.payslip.input'].create(utility_other_inputs)    
                    
        rec = super(HrPayslip, self).compute_sheet()
        
        return rec
    
    
    
        

    
    