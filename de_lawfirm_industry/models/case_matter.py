from odoo import models, fields, api


class Matter(models.Model):
    _inherit = 'project.project'

    court_id = fields.Many2one('court.court', string='Court')
    judge_id = fields.Many2one('court.judge', string='Judge')
    crime_type_id = fields.Many2one('crime.type', string='Crime Type')
    task_template_id = fields.Many2one('law.task.list', string='Task Template')
    partner_id = fields.Many2one('res.partner', string='Client')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('won', 'Won'),
        ('loss', 'Loss'),
        ('settled', 'Settled'),
        ('dropped', 'Dropped'),
    ], string='Status', default='draft', required=True)

    trust_account = fields.Integer(string='Shift Request', compute='_compute_shift_request_count')

    def _compute_shift_request_count(self):
        for record in self:
            shift_request_total = self.env['trust.account'].search_count([('partner_id', '=', record.partner_id.id)])
            record.trust_account = shift_request_total

    def action_shift_request(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Trust Account',
            'view_mode': 'tree,form',
            'target': 'current',
            'res_model': 'trust.account',
            'domain': [('partner_id', '=', self.partner_id.id)],
            'context': "{'create': False}"
        }


class MyPartner(models.Model):
    _inherit = 'res.partner'

    trust_account = fields.Integer(string='Shift Request', compute='_compute_shift_request_count')
    cases_count = fields.Integer(string='Cases', compute='_compute_cases_count')

    def _compute_cases_count(self):
        for record in self:
            cases_total = self.env['project.project'].search_count([('partner_id', '=', record.id)])
            record.cases_count = cases_total

    def _compute_shift_request_count(self):
        for record in self:
            shift_request_total = self.env['trust.account'].search_count([('partner_id', '=', record.id)])
            record.trust_account = shift_request_total

    def action_cases_count(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cases',
            'view_mode': 'tree,form',
            'target': 'current',
            'res_model': 'project.project',
            'domain': [('partner_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def action_shift_request(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Trust Account',
            'view_mode': 'tree,form',
            'target': 'current',
            'res_model': 'trust.account',
            'domain': [('partner_id', '=', self.id)],
            'context': "{'create': False}"
        }

