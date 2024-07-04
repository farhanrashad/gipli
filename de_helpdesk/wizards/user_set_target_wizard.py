# -*- coding: utf-8 -*-

from odoo import fields, models, _, api
from odoo.exceptions import UserError, ValidationError

class SetUserTargetWizard(models.TransientModel):
    _name = 'project.helpdesk.user.target.wizard'
    _description = 'Set user Target'

    def _get_default_target_ticket_closed(self):
        target_value = self.env.user.target_ticket_closed
        return target_value

    def _get_default_target_ticket_rating(self):
        target_value = self.env.user.target_ticket_rating
        return target_value

    def _get_default_target_ticket_sla_success_rate(self):
        target_value = self.env.user.target_ticket_sla_success_rate
        return target_value
        
    target_ticket_closed = fields.Integer(string='Target Tickets to Close', 
                                          default=lambda s: s._get_default_target_ticket_closed(),
                                         )
    target_ticket_rating = fields.Float(string='Target Rating',
                                        default=lambda s: s._get_default_target_ticket_rating(),
                                       )
    target_ticket_sla_success_rate = fields.Float(string='Target Success Rate',
                                                  default=lambda s: s._get_default_target_ticket_sla_success_rate(),
                                                 )
        
    def action_set_target(self):
        user_id = self.env.user
        #raise UserError(user_id)
        user_id.write({
            'target_ticket_closed': self.target_ticket_closed,
            'target_ticket_rating': self.target_ticket_rating,
            'target_ticket_sla_success_rate': self.target_ticket_sla_success_rate,
        })
        
    def _prepare_ticket_reopen_values(self):
        return {
            'stage_id': self.stage_id.id,
        }

