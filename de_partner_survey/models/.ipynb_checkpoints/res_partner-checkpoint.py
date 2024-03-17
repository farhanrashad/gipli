from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime

class PartnerQualifications(models.Model):
    _inherit = 'res.partner'

    partner_survey_count = fields.Integer('Count', compute='survey_count')

    def survey_count(self):
        record = self.env['res.partner.survey'].search_count([('partner_id', '=', self.id)])
        self.partner_survey_count = record

    def action_partner_interview(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Recruitment Survey',
            'view_id': self.env.ref('de_partner_survey.view_partner_interview_tree', False).id,
            'target': 'current',
            'domain': [('partner_id', '=', self.id)],
            'res_model': 'res.partner.survey',
            'views': [[False, 'tree']],
        }

    def write(self, vals):
        record = super(models.Model, self).write(vals)
        # if self.is_survey_setting:
        tags = self.category_id

        record = self.env['res.partner.survey'].search([('partner_id', '=', self.id)])
        survey_list = []
        for survey in record:
            survey_list.append(survey.id)

        for tag in tags:
            # if tag.name not in category_list:
            record = self.env['res.partner.category'].search([('name', '=', tag.name)])
            self.create_interviews(record)

    def create_interviews(self, tag):
        for rec in self:
            if tag.interview_count == 1:
                rec.env['res.partner.survey'].create({
                    'interviewer_id': tag.partner_id_a.id,
                    'survey_id': tag.survey_id_1.id,
                    'partner_id': rec.id,
                    'category_id': tag.id,
                })
            elif tag.interview_count == 2:
                rec.env['res.partner.survey'].create({
                    'interviewer_id': tag.partner_id_a.id,
                    'survey_id': tag.survey_id_1.id,
                    'partner_id': rec.id,
                    'category_id': tag.id,
                })
                rec.env['res.partner.survey'].create({
                    'interviewer_id': tag.partner_id_b.id,
                    'survey_id': tag.survey_id_2.id,
                    'partner_id': rec.id,
                    'category_id': tag.id,
                })
            elif tag.interview_count == 3:
                rec.env['res.partner.survey'].create({
                    'interviewer_id': tag.partner_id_a.id,
                    'survey_id': tag.survey_id_1.id,
                    'partner_id': rec.id,
                    'category_id': tag.id,
                })
                rec.env['res.partner.survey'].create({
                    'interviewer_id': tag.partner_id_b.id,
                    'survey_id': tag.survey_id_2.id,
                    'partner_id': rec.id,
                    'category_id': tag.id,
                })
                rec.env['res.partner.survey'].create({
                    'interviewer_id': tag.partner_id_c.id,
                    'survey_id': tag.survey_id_3.id,
                    'partner_id': rec.id,
                    'category_id': tag.id,
                })
            elif tag.interview_count == 4:
                rec.env['res.partner.survey'].create({
                    'interviewer_id': tag.partner_id_a.id,
                    'survey_id': tag.survey_id_1.id,
                    'partner_id': rec.id,
                    'category_id': tag.id,
                })
                rec.env['res.partner.survey'].create({
                    'interviewer_id': tag.partner_id_b.id,
                    'survey_id': tag.survey_id_2.id,
                    'partner_id': rec.id,
                    'category_id': tag.id,
                })
                rec.env['res.partner.survey'].create({
                    'interviewer_id': tag.partner_id_c.id,
                    'survey_id': tag.survey_id_3.id,
                    'partner_id': rec.id,
                    'category_id': tag.id,
                })
                rec.env['res.partner.survey'].create({
                    'interviewer_id': tag.partner_id_d.id,
                    'survey_id': tag.survey_id_4.id,
                    'partner_id': rec.id,
                    'category_id': tag.id,
                })
            elif tag.interview_count == 5:
                rec.env['res.partner.survey'].create({
                    'interviewer_id': tag.partner_id_a.id,
                    'survey_id': tag.survey_id_1.id,
                    'partner_id': rec.id,
                    'category_id': tag.id,
                })
                rec.env['res.partner.survey'].create({
                    'assessment_date': datetime.datetime.today(),
                    'interviewer_id': tag.partner_id_b.id,
                    'survey_id': tag.survey_id_2.id,
                    'partner_id': rec.id,
                    'category_id': tag.id,
                })
                rec.env['res.partner.survey'].create({
                    'survey_id': tag.survey_id_3.id,
                    'interviewer_id': tag.partner_id_c.id,
                    'partner_id': rec.id,
                    'category_id': tag.id,
                })
                rec.env['res.partner.survey'].create({
                    'interviewer_id': tag.partner_id_d.id,
                    'survey_id': tag.survey_id_4.id,
                    'partner_id': rec.id,
                    'category_id': tag.id,
                })
                rec.env['res.partner.survey'].create({
                    'interviewer_id': tag.partner_id_e.id,
                    'survey_id': tag.survey_id_5.id,
                    'partner_id': rec.id,
                    'category_id': tag.id,
                })


