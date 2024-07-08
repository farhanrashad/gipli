# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    hostel_location_id = fields.Many2one('stock.location')

    @api.model
    def _create_missing_hostel_location(self):
        company_without_hostel_loc = self.env['res.company'].with_context(active_test=False).search(
            [('hostel_location_id', '=', False)])
        company_without_hostel_loc._create_hostel_location()

    def _create_per_company_locations(self):
        super(ResCompany, self)._create_per_company_locations()
        self._create_hostel_location()

    def _create_hostel_location(self):
        parent_location = self.env.ref('de_school_hostel.hostel_location_locations', raise_if_not_found=False)
        for company in self:
            hostel_location = self.env['stock.location'].create({
                'name': _('Reservation Pool'),
                'usage': 'transit',
                #'location_id': parent_location.id,
                'company_id': company.id,
                'is_hostel': True,
            })
            
            company.hostel_location_id = hostel_location