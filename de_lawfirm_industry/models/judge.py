from odoo import models, fields


class CourtJudge(models.Model):
    _name = 'court.judge'
    _description = 'Court Judge'

    name = fields.Char(required=True)
    contact = fields.Char()
    court_id = fields.Many2one('court.court', required=True)
