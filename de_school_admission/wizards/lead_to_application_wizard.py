# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Lead2OpportunityMassConvert(models.TransientModel):
    _name = 'oe.admission.lead2op.wizard'
    _description = 'Convert Enquiry to Application (in mass)'

    # Academic Fields
    admission_register_id = fields.Many2one('oe.admission.register',string="Admission Register", required=True)
    
    course_id = fields.Many2one('oe.school.course', string='Course', compute='_compute_from_admission_register')
    course_code = fields.Char(related='course_id.code')
    batch_id = fields.Many2one('oe.school.course.batch', string='Batch', domain="[('course_id','=',course_id)]")

    def action_mass_convert(self):
        pass
    