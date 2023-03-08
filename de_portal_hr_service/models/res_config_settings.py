# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    security_group_id = fields.Many2one('res.groups', string='Security Group')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        security_group_id = ICPSudo.get_param('security_group_id')
        res.update(
            security_group_id=int(security_group_id),
        )
        return res

    def set_values(self):
        self.env['ir.config_parameter'].set_param('security_group_id', self.security_group_id.id)
        super(ResConfigSettings, self).set_values()

