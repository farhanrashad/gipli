from odoo import models, fields, api
from datetime import timedelta


class SchoolAcademicYear(models.Model):
    _name = 'oe.school.year'
    _description = 'oe.academic.year'
 
    name = fields.Char('Name',required=True)
    date_start = fields.Date('Date Start', required = True)
    date_end = fields.Date('Date end',required = True)
    active = fields.Boolean('Active', default=True)

    @api.constrains('date_start', 'date_end')
    def _check_date_overlap(self):
        for year in self:
            # Check for overlapping dates in other academic years
            overlapping_years = self.search([
                ('id', '!=', year.id),
                ('date_start', '<=', year.date_end),
                ('date_end', '>=', year.date_start),
            ])
            if overlapping_years:
                raise ValidationError("Academic years cannot overlap with each other.")