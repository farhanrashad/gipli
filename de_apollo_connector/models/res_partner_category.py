# -*- coding: utf-8 -*-

from odoo import models, fields

class ResPartnerCategory(models.Model):
    _inherit = 'res.partner.category'

    apl_id = fields.Char(
        string='Apollo ID',
        help="The Apollo ID is used for tracking purposes."
    )
    apl_date_sync = fields.Date('Synronization Date', help="he date of the most recent synchronization of tags with Apollo.")

    update_required_for_apollo = fields.Boolean('Update Required for Apollo', help="Set to 'True' when this record requires an update in Apollo.")