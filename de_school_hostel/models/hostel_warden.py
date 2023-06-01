from odoo import models, fields


class HostelWarden(models.Model):
    _name = "oe.school.hostel.warden"
    _description = 'School Hostel Warden'
    _rec_name = 'hostel_id'

    hostel_id = fields.Many2one('oe.school.hostel', string='Hostel')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    department_id = fields.Many2one('hr.department', string='Department')
    room_count = fields.Integer(string='Room Count', compute='_compute_room_count')

    def _compute_room_count(self):
        for record in self:
            room_total = self.env['oe.school.hostel.room'].search_count([])
            record.room_count = room_total

    def action_room_entry(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Rooms',
            'view_mode': 'tree,form',
            'target': 'current',
            'res_model': 'oe.school.hostel.room',
            # 'domain': [('employee_id', '=', self.employee_id.id)],
            'context': "{'create': False}"
        }
