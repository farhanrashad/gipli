from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PartnerSurveyQualifications(models.Model):
    _name = 'res.partner.survey'
    _description = 'Partner survey'

    partner_id = fields.Many2one('res.partner')
    performed_by_id = fields.Many2one('res.users')
    interviewer_id  = fields.Many2one('res.users')
    survey_id = fields.Many2one('survey.survey')
    response_id = fields.Many2one('survey.user_input', "Response")
    category_id = fields.Many2one('res.partner.category')
    score_total = fields.Float('Total Score', compute='get_score')
    state = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail')
    ], string='Status', index=True, copy=False, track_visibility='onchange')

    def get_score(self):
        for rec in self:
            answer = rec.env['survey.user_input'].search([('id', '=', rec.response_id.id)])
            rec.score_total = answer.scoring_total

    def action_start_survey(self):
        self.ensure_one()
        for rec in self:
            if rec.env.user.id == rec.interviewer_id.id:
                if not rec.response_id:
                    response = rec.survey_id._create_answer(partner=rec.performed_by_id)
                    rec.response_id = response.id
                else:
                    response = rec.response_id
                rec.performed_by_id = rec._uid
                return rec.survey_id.action_start_survey(answer=response)
            else:
                raise UserError('Sorry, this Interview is to be conducted by ' + rec.interviewer_id.name)

    def action_print_answers(self, answer=None):
        """ Open the website page with the survey form """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'name': "View Answers",
            'target': 'new',
            'url': '/survey/print/%s?answer_token=%s' % (self.survey_id.access_token, self.response_id.access_token)
        }
