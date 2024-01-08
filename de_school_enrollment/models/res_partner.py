# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date
from odoo import api, fields, models
from odoo.osv import expression


class ResPartner(models.Model):
    _inherit = "res.partner"
    
    enrol_order_ids = fields.One2many('sale.order', 'partner_id', string='Enrolment Orders')

    def _get_enrol_orders(self, date_from, date_to, states=['open'], kanban_state=False):
        """
        Returns the enrolment orders of the student between date_from and date_to
        """
        state_domain = [('enrol_status', 'in', states)]
        if kanban_state:
            state_domain = expression.AND([state_domain, [('kanban_state', 'in', kanban_state)]])

        return self.env['sale.order'].search(
            expression.AND([[('partner_id', 'in', self.ids)],
            state_domain,
            [('date_enrol_start', '<=', date_to),
                '|',
                    ('date_enrol_end', '=', False),
                    ('date_enrol_end', '>=', date_from)]]))