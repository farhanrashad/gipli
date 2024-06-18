# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjecTask(models.Model):
    _inherit = "project.task"

    is_service_project_template = fields.Boolean(related='project_id.is_service_project_template')
    days_completion = fields.Integer(string='Days Completion')

    service_product_id = fields.Many2one(
        'product.product', 
        string='Service Product', 
        domain=[('type', '=', 'service')]
    )
    

