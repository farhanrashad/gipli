from odoo import models, fields


class LawTask(models.Model):
    _name = 'law.task'
    _description = 'Law Task'

    name = fields.Char(string='Name', required=True)
    law_task_type = fields.Selection(
        [('consultation', 'Consultation'), ('submission', 'Submission'), ('trial', 'Trial'),
         ('meeting', 'Meeting'), ('other', 'Other')], string='Law Task Type',
        required=True)
    description = fields.Text(string='Description')
