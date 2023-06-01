from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_hostel_room = fields.Boolean(string='Is Hostel Room', default=True, required=True, store=True)

    @api.model
    def default_get(self, fields):
        res = super(ProductTemplate, self).default_get(fields)
        if self._context.get('default_type') == 'service':
            res.update({'is_hostel_room': False})
        else:
            res.update({'is_hostel_room': True})
        return res
