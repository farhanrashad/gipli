from odoo import models, fields, api, exceptions

class HRLeave(models.Model):
    _inherit = 'hr.leave'

    leave_encash_id = fields.Many2one('hr.leave.encash', string='Leave Encashment')

    @api.constrains('date_from', 'date_to', 'employee_id')
    def _check_date(self):
        if self.leave_encash_id:
            pass
        else:
            # Call the original _check_date method
            super(HRLeave, self)._check_date()
