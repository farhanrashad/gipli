# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

class Company(models.Model):
    _inherit = 'res.company'

    hunter_instance_id = fields.Many2one('hunter.instance', string="Instance", compute='_compute_instance')

    def _compute_instance(self):
        hunter_instance_id = self.env['hunter.instance'].search([], limit=1)
        self.hunter_instance_id = hunter_instance_id.id

    