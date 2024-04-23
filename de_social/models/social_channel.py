# -*- coding: utf-8 -*-

from odoo import models, fields, api
from random import randint

class SocialChannel(models.Model):
    _name = 'sm.channel'
    _description = 'Social Channel'
    _inherit = ['mail.thread']

    def _default_color(self):
        return randint(1, 11)
        
    name = fields.Char('Name', required=True, translate=True)
    name_handle = fields.Char('Handle', required=True, translate=True,
                              help="Social media channel or handle name"
                             )
    image = fields.Binary('Image')
    active = fields.Boolean(default=True)

    social_media_id = fields.Many2one('sm.media', string="Social Media", required=True, readonly=False,
        help="Related Social Media (Facebook, Twitter, ...).", ondelete='cascade')

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company,
                                 domain=lambda self: [('id', 'in', self.env.companies.ids)],
                                 help="Link an account to a company to restrict its usage or keep empty to let all companies use it.")
    color = fields.Integer(default=_default_color, 
                           compute='_compute_color', store=True,
                          )
    def _compute_color(self):
        for record in self:
            record.color = randint(1, 11)
    