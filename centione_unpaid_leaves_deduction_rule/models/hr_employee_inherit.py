# -*- coding: utf-8 -*-

from odoo import models, fields, api

class hrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    def get_unpaid_leaves_deduction(self,payslip):
        unpaid_leaves=self.env['hr.leave'].search([ ('employee_id','=',payslip.employee_id) ,
                                                    ('state','=','validate')
                                                     ,('request_date_to','<=', payslip.date_to) ,
                                                    ('request_date_from','>=',  payslip.date_from)])

        wage_per_day=payslip.contract_id.wage/30
        unpaid_days_to_deduct=0
        for leave in unpaid_leaves:
            unpaid_days_to_deduct+=1

        return  unpaid_days_to_deduct*wage_per_day




