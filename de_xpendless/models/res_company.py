# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = 'res.company'

    xpl_api_key = fields.Char(string='API Key', help='API Key')
    xpl_api_secret = fields.Char(string='Secret', help=' API Secret')
    xpl_access_token = fields.Char(string='Token')
    xpl_url = fields.Char(string='URL', )


    def _get_instance(self):
        instance_id = self.env['xpl.instance'].search([],limit=1)
        return instance_id
