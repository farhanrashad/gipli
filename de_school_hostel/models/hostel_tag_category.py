from odoo import models, fields


class OeSchoolHostelCategory(models.Model):
    _name = 'oe.school.hostel.category'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']

    _description = 'Hostel Category'

    name = fields.Char(string='Name', required=True, store=True)
    code = fields.Char(string='Code', required=True)
