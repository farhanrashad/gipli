from odoo import models, fields


class TrustAccount(models.Model):
    _name = 'trust.account'
    _description = 'Trust Account'

    name = fields.Char(string='Name', required=True)
    partner_id = fields.Many2one('res.partner', string='Customer')
    case_id = fields.Many2one('project.project', string='Case')
    matter_id = fields.Many2one('project.project', string='Matter')
    amount = fields.Float(string='Amount')
    amount_due = fields.Float(string='Amount Due')
    attachment = fields.Binary(string='Attachment')
