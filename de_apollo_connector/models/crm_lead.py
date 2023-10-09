# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class CRMTag(models.Model):
    _inherit = 'crm.tag'

    apl_id = fields.Char(
        string='Apollo ID',
        help="The Apollo ID is used for tracking purposes."
    )
    apl_date_update = fields.Date('Last Update Date', help="he date of the most recent update of tags with Apollo.")


class CRMStage(models.Model):
    _inherit = 'crm.stage'

    apl_id = fields.Char(
        string='Apollo ID',
        help="The Apollo ID is used for tracking purposes."
    )
    apl_date_update = fields.Date('Last Update Date', help="he date of the most recent update of stages with Apollo.")

    
class CRMLead(models.Model):
    _inherit = 'crm.lead'

    apl_id = fields.Char(
        string='Apollo ID',
        help="The Apollo ID is used for tracking purposes."
    )
    apl_date_sync = fields.Date('Synronization Date', help="he date of the most recent synchronization of contacts with Apollo.")

    update_required_for_apollo = fields.Boolean('Update Required for Apollo', help="Set to 'True' when this record requires an update in Apollo.")

    def action_send_to_apollo_data(self):
        ''' Open the account.payment.register wizard to pay the selected journal entries.
        :return: An action opening the account.payment.register wizard.
        '''
        return {
            'name': _('Apollo'),
            'res_model': 'apl.send.data.wizard',
            'view_mode': 'form',
            'context': {
                'active_model': 'crm.lead',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    

