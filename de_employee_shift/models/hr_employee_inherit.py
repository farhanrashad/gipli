from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    shift_request_count = fields.Integer(string='Shift Request', compute='_compute_shift_request_count')

    def _compute_shift_request_count(self):
        for record in self:
            shift_request_total = self.env['shift.request'].search_count([('employee_id', '=', record.id)])
            record.shift_request_count = shift_request_total
            print(shift_request_total)

    def action_shift_request(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Shift Request',
            'view_mode': 'tree,form',
            'target': 'current',
            'res_model': 'shift.request',
            'domain': [('employee_id', '=', self.id)],
            'context': "{'create': False}"
        }
