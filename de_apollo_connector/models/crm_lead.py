# -*- coding: utf-8 -*-

from odoo import models, fields

class CRMLead(models.Model):
    _inherit = 'crm.lead'

    ap_id = fields.Char(
        string='Apollo ID',
        help="The Apollo ID is used for tracking purposes."
    )
    ap_date_sync = fields.Date('Synronization Date', help="he date of the most recent synchronization of contacts with Apollo.")

    update_required_for_apollo = fields.Boolean('Update Required for Apollo', help="Set to 'True' when this record requires an update in Apollo.")

    def action_send_to_apollo(self):
        pass

    

