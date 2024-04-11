# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError

class ClassroomBuilding(models.Model):
    _name = 'oe.school.subject.allocation'
    _description = 'Subject Allocation'
    _order = 'subject_id'

    employee_id = fields.Many2one('hr.employee', 
                                  string='Employee', required=True, 
                                  domain="[('is_teacher','=',True)]"
                                 )
    subject_id = fields.Many2one('oe.school.subject', string='Subject', required=True)
