# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
from random import randint


#class CourseGradingType(models.Model):
#    _name = 'oe.school.course.grading.type'
#    _description = 'Course Grading Type'
#    name = fields.Char(string='Type', required=True, index=True, translate=True) 

    
class VoteLocation(models.Model):
    _name = 'vote.location'
    _description = 'Location'
    _order = 'name'
    
    def _default_color(self):
        return randint(1, 11)
    
    name = fields.Char(string='Location', required=True, index=True, translate=True) 
    code = fields.Char(string='Code', required=True, size=10)
    complete_name = fields.Char('Complete Name', compute='_compute_complete_name', recursive=True, store=True)
    parent_id = fields.Many2one('vote.location', string='Parent Location', index=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    active = fields.Boolean('Active', default=True)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)

    color = fields.Integer(default=_default_color)    
    
    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for course in self:
            if course.parent_id:
                course.complete_name = '%s / %s' % (course.parent_id.complete_name, course.name)
            else:
                course.complete_name = course.name
    