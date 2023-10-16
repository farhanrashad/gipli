# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, time
from dateutil.relativedelta import relativedelta


class FeeslipScheduleWizard(models.TransientModel):
    _name = "oe.feeslip.schedule.wizard"
    _description = 'Fee Schedule Wizard'

    batch_id = fields.Many2one('oe.school.course.batch', string='Batch', required=True)
    course_id = fields.Many2one('oe.school.course', string='Course', related='batch_id.course_id')
    date_start = fields.Date(string='Date Start', store=True, readonly=False, required=True, 
                                 compute='_compute_from_batch')
    date_end = fields.Date(string='Date End', store=True, readonly=False, required=True,
                               compute='_compute_from_batch')
    fee_struct_id = fields.Many2one('oe.fee.struct', string='Fee Structure', required=True)
    installment = fields.Integer('Installment', compute='_compute_installments', store=True)
    
    @api.onchange('batch_id')
    @api.depends('batch_id')
    def compute_from_batch(self):
        for record in self:
            #record.course_id = record.batch_id.course_id.id
            record.date_start = record.batch_id.date_start
            record.date_end = record.batch_id.date_end

    @api.depends('date_start', 'date_end', 'fee_struct_id','fee_struct_id.schedule_pay_duration')
    def _compute_installments(self):
        for record in self:
            if record.date_start and record.date_end and record.fee_duration > 0 and record.fee_struct_id:
                start_date = datetime.strptime(record.date_start, "%Y-%m-%d")
                end_date = datetime.strptime(record.date_end, "%Y-%m-%d")
                installments = 0
                current_date = start_date

                if record.fee_struct_id.pay_one_time:
                    installments = 1
                else:
                    while current_date <= end_date:
                        installments += 1
                        current_date = current_date + relativedelta(months=fee_struct_id.schedule_pay_duration)

                record.installment = installments
                
                
    def action_schedule(self):
        #batch_ids = self.env['oe.school.course.batch'].search([('course_id','=',self.course_id)])
        pass