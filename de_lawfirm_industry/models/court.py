from odoo import models, fields


class Court(models.Model):
    _name = 'court.court'
    _description = 'Court'

    name = fields.Char(string='Name', required=True)
    address = fields.Char(string='Address')
    judge_ids = fields.One2many('court.judge', 'court_id', string='Judges')
