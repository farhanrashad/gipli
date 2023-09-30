from odoo.exceptions import AccessError, UserError, ValidationError
from odoo import fields, models, api, _



class BaseModel(models.AbstractModel):
    _inherit = 'base'

    def write(self, vals):
        # Check if the 'state' field is being updated
        if 'state' in vals:
            new_state = vals['state']

            if self._name == 'account.move' or self._name == 'sale.order':
                if new_state == 'draft':
                    # Create a record in the 'target.model'
                    self.env['audit.log'].create({
                        'record_id': self.id,
                        'model_name': self._name,
                    })

        # Call the parent's write method to perform the standard write operation
        return super(BaseModel, self).write(vals)


class AuditLog(models.Model):
    _name = 'audit.log'
    _description = 'Audit Log'

    # Fields for audit log
    record_id = fields.Integer('Record ID')
    model_name = fields.Char('Model Name')
 
