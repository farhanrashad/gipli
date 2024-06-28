# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from datetime import datetime, date, time
from dateutil.relativedelta import relativedelta
import pytz

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools import format_date

from odoo.osv import expression

class FeeslipStudents(models.TransientModel):
    _name = 'oe.feeslip.students'
    _description = 'Generate feeslips for all selected students'

    def _get_available_student_domain(self):
        return [('is_student', '=', True)]

    def _get_students(self):
        active_student_ids = self.env.context.get('active_student_ids', False)
        if active_student_ids:
            return self.env['res.partner'].browse(active_student_ids)
        # YTI check dates too
        return self.env['res.partner'].search(self._get_available_student_domain())

    
    feeslip_run_id = fields.Many2one('oe.feeslip.run', string='Batch Name', readonly=True,
        default=lambda self: self.env.context.get('active_id')
    )

    student_ids_domain = fields.Many2many('res.partner', compute='_compute_student_ids_domain')
    student_ids = fields.Many2many('res.partner', 'oe_student_group_rel', 'feeslip_id', 'student_id', 'Students',
                               store=True, readonly=False,
                               )

    
    fee_struct_id = fields.Many2one('oe.fee.struct', string='Fee Structure')
    #department_id = fields.Many2one('hr.department')

    @api.model
    def default_get(self, fields):
        res = super(FeeslipStudents, self).default_get(fields)
        if 'fee_struct_id' in self._context:
            res['fee_struct_id'] = self._context.get('fee_struct_id')
        return res

    @api.onchange('feeslip_run_id')
    def _onchange_feeslip_run_id(self):
        for record in self:
            record.fee_struct_id = record.feeslip_run_id.fee_struct_id.id
            
            domain = [('course_id', '=', record.feeslip_run_id.fee_struct_id.course_id.id)]
        
            if record.feeslip_run_id.fee_struct_id.batch_ids:
                batch_domain = [('batch_id', 'in', record.feeslip_run_id.fee_struct_id.batch_ids.ids)]
                domain = expression.AND([domain, batch_domain])
    
            record.student_ids = self.env['res.partner'].search(domain)

    @api.depends('feeslip_run_id')
    def _compute_student_ids_domain(self):
        for record in self:
            domain = record._get_student_domain()
            students = self.env['res.partner'].search(domain)
            record.student_ids_domain = [(6, 0, students.ids)]

    def _get_student_domain(self):
        self.ensure_one()
        domain = [('course_id', '=', self.feeslip_run_id.fee_struct_id.course_id.id)]
        if self.feeslip_run_id.fee_struct_id.batch_ids:
            batch_domain = [('batch_id', 'in', self.feeslip_run_id.fee_struct_id.batch_ids.ids)]
            domain = expression.AND([domain, batch_domain])
        return domain

    def compute_sheet(self):
        feeslips = self.env['oe.feeslip']
        Feeslip = self.env['oe.feeslip']
        
        if not self.student_ids:
            raise UserError(_("No students selected. Please select students to generate feeslips."))

        default_values = Feeslip.default_get(Feeslip.fields_get())
        feeslips_vals = []

        
        success_result = {
            'type': 'ir.actions.act_window',
            'res_model': 'oe.feeslip.run',
            'views': [[False, 'form']],
            'res_id': self.feeslip_run_id.id,
        }
        if not self.student_ids:
            return success_result
            
        for student in self.student_ids:
            values = dict(default_values, **{
                'name': _('New Feeslip'),
                'student_id': student.id,
                'feeslip_run_id': self.feeslip_run_id.id,
                'date_from': self.feeslip_run_id.date_start,
                'date_to': self.feeslip_run_id.date_end,
                'fee_struct_id': self.feeslip_run_id.fee_struct_id.id,
            })
            feeslips_vals.append(values)
        feeslips = Feeslip.with_context(tracking_disable=True).create(feeslips_vals)
        feeslips._compute_name()
        feeslips.compute_sheet()
        self.feeslip_run_id.state = 'verify'

        return success_result

    def compute_sheet_backup(self):
        feeslip_obj = self.env['oe.feeslip']
        for student in self.student_ids:
            vals = {
                #'name': student.name,
                'student_id': student.id,
                'feeslip_run_id': self.feeslip_run_id.id,
                'date_from': self.feeslip_run_id.date_start,
                'date_to': self.feeslip_run_id.date_end,
                'fee_struct_id': self.feeslip_run_id.fee_struct_id.id,
                # Add other relevant fields based on your requirements
            }
            payslips = Payslip.with_context(tracking_disable=True).create(payslips_vals)
        payslips._compute_name()
        payslips.compute_sheet()
        
        feeslip_obj.create(vals)
        try:
            feeslip_obj.compute_sheet()
        except Exception as e:
            # Log or print the exception for debugging purposes
            raise UserError(f"Error computing feeslip for student {student.name}: {e}")
            
            #feeslip_obj.sudo().compute_sheet()
        
        #return {
        #    'type': 'ir.actions.client',
        #    'tag': 'reload',  # Reload the current view after creating feeslips
        #}
        
