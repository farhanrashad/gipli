# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models
from odoo.osv import expression


class ResPartner(models.Model):
    _inherit = 'res.partner'


    def _get_enrol_orders(self, date_from, date_to, states=['open']):
        """
        Returns the enrollment contracts of the student between date_from and date_to
        """
        state_domain = [('enrol_status', 'in', states)]
        return self.env['sale.order'].search(
            expression.AND([[('partner_id', 'in', self.ids)],
            state_domain,
            [('date_enrol_start', '<=', date_to),
                '|',
                    ('date_enrol_end', '=', False),
                    ('date_enrol_end', '>=', date_from)]]))