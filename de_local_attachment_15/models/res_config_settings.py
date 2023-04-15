# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    attachment_folder = fields.Char(
        string='Local attachment Folder',
        help='Local attachment Folder where all the attachments will be stored and retrive when required',
        required=True,
        default='D:/attachments/',
        config_parameter='de_local_attachment.attachment_folder',
    )


    @api.model
    def get_values(self):
        return super(ResConfigSettings, self).get_values()


    def set_values(self):
        super(ResConfigSettings, self).set_values()
