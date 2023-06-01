from odoo import models, fields, api


class ServiceType(models.Model):
    _name = 'service.type'
    _description = 'Service Type'
    _rec_name = 'service_id'

    service_id = fields.Many2one('product.product', string='Product')
    description = fields.Text(string='Description')
