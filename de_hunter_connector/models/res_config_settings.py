# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
        
    hunter_instance_id = fields.Many2one(comodel_name="hunter.instance", related='company_id.hunter_instance_id')

    def action_hunter_instance_from_settings(self):
        hunter_instance_id = self.env['hunter.instance'].search([], limit=1)
        if hunter_instance_id:
            # If a record exists, open it
            return {
                'name': 'Hunter Connection',
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': hunter_instance_id.id,
                'res_model': 'hunter.instance',
                'type': 'ir.actions.act_window',
                'target': 'new',
            }
        else:
            return {
                'name': 'Hunter Connection',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'hunter.instance',
                'type': 'ir.actions.act_window',
                'target': 'new',
            }