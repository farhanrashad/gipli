from odoo import models, fields


class LawTaskList(models.Model):
    _name = 'law.task.list'
    _description = 'List of tasks related to law cases'

    name = fields.Char(string='Name')
    task_ids = fields.Many2many('law.task', string='Tasks')


class InheritHrEmployee(models.Model):
    _inherit = 'hr.employee'
    _description = 'Inherit Hr Employee'


class InheritResPartner(models.Model):
    _inherit = 'res.partner'
    _description = 'Inherit Res Partner'
