# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    admission_team_ids = fields.Many2many(
        'oe.school.team', 'admission_team_member', 'user_id', 'admission_team_id', string='Admission Teams',
        check_company=True, copy=False, readonly=True,
        compute='_compute_admission_team_ids', search='_search_admission_team_ids')
    
    admission_team_member_ids = fields.One2many('oe.admission.team.member', 'user_id', string='Admission Team Members')
    admission_team_id = fields.Many2one(
        'oe.school.team', string='Admission Team', compute='_compute_admission_team_id',
        readonly=True, store=True,
        help="Main user admissions team. Used notably for pipeline, or to set admission team in admission or enrollment")


    @api.depends('admission_team_member_ids.active')
    def _compute_admission_team_ids(self):
        for user in self:
            user.admission_team_ids = user.admission_team_member_ids.admission_team_id

    def _search_admission_team_ids(self, operator, value):
        return [('admission_team_member_ids.admission_team_id', operator, value)]

    
    @api.depends('admission_team_member_ids.admission_team_id', 'admission_team_member_ids.create_date', 'admission_team_member_ids.active')
    def _compute_admission_team_id(self):
        for user in self:
            if not user.admission_team_member_ids.ids:
                user.admission_team_id = False
            else:
                sorted_memberships = user.admission_team_member_ids  # sorted by create date
                user.admission_team_id = sorted_memberships[0].admission_team_id if sorted_memberships else False
