from odoo import models, fields, api


class CloseMatterWizard(models.TransientModel):
    _name = 'close.matter.wizard'
    _description = 'Close Matter'

    close_reason = fields.Selection([
        ('won', 'Won'),
        ('loss', 'Loss'),
        ('settled', 'Settled'),
        ('drop', 'Dropped'),
    ], string='Close Reason', required=True)

    def close_matter(self):
        active_id = self.env.context.get('active_id')
        project = self.env['project.project'].browse(active_id)
        for rec in self:
            if rec.close_reason == 'won':
                project.state = 'won'
            elif rec.close_reason == 'loss':
                project.state = 'loss'
            elif rec.close_reason == 'drop':
                project.state = 'dropped'
            elif rec.close_reason == 'settled':
                project.state = 'settled'
            else:
                project.state = 'draft'
