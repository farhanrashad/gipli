from odoo import models

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def get_current_user_id(self):
        return self.env.user.id
