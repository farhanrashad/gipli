from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PartnerCategory(models.Model):
    _inherit = 'res.partner.category'

    interview_count = fields.Integer('No of Interviews')

    survey_id_1 = fields.Many2one('survey.survey')
    survey_id_2 = fields.Many2one('survey.survey')
    survey_id_3 = fields.Many2one('survey.survey')
    survey_id_4 = fields.Many2one('survey.survey')
    survey_id_5 = fields.Many2one('survey.survey')

    partner_id_a = fields.Many2one('res.users')
    partner_id_b = fields.Many2one('res.users')
    partner_id_c = fields.Many2one('res.users')
    partner_id_d = fields.Many2one('res.users')
    partner_id_e = fields.Many2one('res.users')

    survey_bool_a = fields.Boolean(default=False)
    survey_bool_b = fields.Boolean(default=False)
    survey_bool_c = fields.Boolean(default=False)
    survey_bool_d = fields.Boolean(default=False)
    survey_bool_e = fields.Boolean(default=False)

    @api.onchange('interview_count')
    def check_inetrview_count(self):
        if self.interview_count > 5:
            raise UserError('Number of interviews should be between 1-5')

    @api.onchange('interview_count')
    def compute_survey_bools(self):
        if self.interview_count == 0:
            self.survey_bool_a = False
            self.survey_bool_b = False
            self.survey_bool_c = False
            self.survey_bool_d = False
            self.survey_bool_e = False
        elif self.interview_count == 1:
            self.survey_bool_a = True
            self.survey_bool_b = False
            self.survey_bool_c = False
            self.survey_bool_d = False
            self.survey_bool_e = False
        elif self.interview_count == 2:
            self.survey_bool_a = True
            self.survey_bool_b = True
            self.survey_bool_c = False
            self.survey_bool_d = False
            self.survey_bool_e = False
        elif self.interview_count == 3:
            self.survey_bool_a = True
            self.survey_bool_b = True
            self.survey_bool_c = True
            self.survey_bool_d = False
            self.survey_bool_e = False
        elif self.interview_count == 4:
            self.survey_bool_a = True
            self.survey_bool_b = True
            self.survey_bool_c = True
            self.survey_bool_d = True
            self.survey_bool_e = False
        elif self.interview_count == 5:
            self.survey_bool_a = True
            self.survey_bool_b = True
            self.survey_bool_c = True
            self.survey_bool_d = True
            self.survey_bool_e = True
        else:
            pass
