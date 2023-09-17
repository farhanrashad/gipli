from odoo import api, models

class HrContract(models.Model):
    _inherit = 'hr.contract'

    @api.model
    def get_current_user_employee_id(self):
        # Retrieve the current user's related employee's user ID
        employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        if employee:
            return employee.id
        return False
