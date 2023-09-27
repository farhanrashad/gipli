from odoo import models, fields

class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    allow_leave_encashment = fields.Boolean(string="Allow Leave Encashment")
    product_id = fields.Many2one('product.product', string="Product", domain="[('type','=','service')]")
