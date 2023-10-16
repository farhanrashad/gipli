# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

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

    #@api.depends('batch_id')
    def compute_from_batch(self):
        for record in self:
            #record.course_id = record.batch_id.course_id.id
            record.date_start = record.batch_id.date_start
            record.date_end = record.batch_id.date_end
            
    def action_schedule(self):
        #batch_ids = self.env['oe.school.course.batch'].search([('course_id','=',self.course_id)])
        pass