from odoo import models, fields, api


class OeSchoolHostel(models.Model):
    _name = 'oe.school.hostel'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']
    _description = 'School Hostel'

    name = fields.Char(string='Name', required=True)
    hostel_category_ids = fields.Many2many('oe.school.hostel.category', string='Tag')
    hostel_type_id = fields.Many2one('hostel.type', string='Hostel Type')
    location = fields.Char(string='Location', required=True)
    description = fields.Text(string='Description')
    hostel_room_ids = fields.One2many('oe.school.hostel.room', 'hostel_id', string='Hostel Rooms')
