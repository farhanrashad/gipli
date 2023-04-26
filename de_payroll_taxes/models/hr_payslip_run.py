# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'
    
    
    def action_payment_request(self):
        work_location_list = [] 
        payslips = self.env['hr.payslip'].search([('payslip_run_id','=',self.id),('state','not in', ('cancel','draft'))])
        for location_slip in payslips:
            work_location_list.append(location_slip.employee_id.work_location_id.id)
        uniq_work_location = set(work_location_list)
        payment_request = self.env['hr.salary.rule'].search([('ora_account_service','=',True)])
        for rule in payment_request:             
            if rule.ora_split_location==True:   
                for uniq_location in uniq_work_location:
                    slip_total_amount = 0
                    parent_rules = self.env['hr.salary.rule'].search([('ora_rule_id','=',rule.id)])
                    for p_rule in parent_rules:                    
                        for slip in payslips:
                            if slip.employee_id.work_location_id.id==uniq_location: 
                                for slip_rule in slip.line_ids:
                                    if p_rule.id == slip_rule.salary_rule_id.id:
                                        slip_total_amount += slip_rule.amount
                    for slip in payslips:
                        if slip.employee_id.work_location_id.id==uniq_location: 
                            for slip_rule in slip.line_ids:
                                if rule.id==slip_rule.salary_rule_id.id:
                                    slip_total_amount += slip_rule.amount

                    if slip_total_amount > 0:    
                        vals = {
                          'name':  rule.ora_account_label ,
                          'rule_id':  rule.id ,
                          'payment_type':  rule.ora_payment_type+' -'+ str(self.env['hr.work.location'].search([('id','=', uniq_location)], limit=1).name ),
                          'account_id': self.env['account.account'].search([('code','=', rule.ora_account_code),('company_id','=',self.company_id.id)]).id ,
                          'amount': slip_total_amount ,
                          'fiscal_month':  self.date_end.month,
                          'year':  self.date_end.year,
                          'company_id': self.company_id.id ,
                        }
                        pay_req = self.env['account.payment.request'].create(vals)
            else:
                slip_total_amount = 0
                for slip in payslips:
                    for slip_rule in slip.line_ids:
                        if rule.id==slip_rule.salary_rule_id.id:
                            slip_total_amount += slip_rule.amount 
                parent_rules = self.env['hr.salary.rule'].search([('ora_rule_id','=',rule.id)])
                for p_rule in parent_rules:                    
                    for slip in payslips:                         
                        for slip_rule in slip.line_ids:
                            if p_rule.id == slip_rule.salary_rule_id.id:
                                slip_total_amount += slip_rule.amount
                if slip_total_amount > 0:   
                    vals = {
                      'name':  rule.ora_account_label ,
                      'payment_type':  rule.ora_payment_type,
                      'rule_id':  rule.id ,
                      'account_id': self.env['account.account'].search([('code','=', rule.ora_account_code),('company_id','=',self.company_id.id)]).id ,
                      'amount': slip_total_amount ,
                      'fiscal_month':  self.date_end.month,
                      'year':  self.date_end.year, 
                      'company_id': self.company_id.id ,
                    }
                    pay_req = self.env['account.payment.request'].create(vals)
    
    
    

