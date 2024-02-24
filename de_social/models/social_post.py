# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

SOCIAL_STATE = [
    ('draft', 'Draft'), 
    ('scheduled', 'scheduled'),  
    ('posted', 'Posted'),
]

class SocialPost(models.Model):
    _name = 'sm.post'
    _inherit = [
        'mail.thread', 
        'mail.activity.mixin', 
    ]
    _description = 'Social Post'
    _order = 'create_date desc'
    _rec_name = 'message'

    message = fields.Text("Message")
    image_ids = fields.Many2many(
        'ir.attachment', string='Attach Images',
        help="Will attach images to your posts (if the social media supports it).")
    
    state = fields.Selection(
        selection=SOCIAL_STATE,
        string='Status', default='draft', readonly=True, required=True,
    )
    
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company,
                                 domain=lambda self: [('id', 'in', self.env.companies.ids)])
    channel_ids = fields.Many2many('sm.channel',domain="[('id', 'in', channel_allowed_ids)]")
    channel_allowed_ids = fields.Many2many('sm.channel', string='Allowed Accounts', compute='_compute_channels',
                                           help='List of the channels which can be selected for this post.')

    social_media_ids = fields.Many2many('sm.media', compute='_compute_media_ids', store=True,
        help="The social medias linked to the selected social accounts.")

    method_publish = fields.Selection([
        ('now', 'Publish now'),
        ('scheduled', 'Schedule'),
        ('pipeline', 'Pipeline'),
    ], string="When", default='now', required=True,
        help="Publish your post immediately or schedule it at a later time.")
    
    date_scheduled = fields.Datetime('Scheduled Date')
    date_published = fields.Datetime('Published Date', readonly=True,
        help="When the global post was published. The actual sub-posts published dates may be different depending on the media.")

    
    
    @api.depends('company_id')
    def _compute_channels(self):
        for post in self:
            if post.company_id:
                company_domain = ['|', ('company_id', '=', False), ('company_id', '=', post.company_id.id)]
            else:
                company_domain = ['|', ('company_id', '=', False), ('company_id', 'in', self.env.companies.ids)]
            
            all_channel_ids = self.env['sm.channel'].search(company_domain)
            post.channel_allowed_ids = all_channel_ids


    @api.depends('channel_ids.social_media_id')
    def _compute_media_ids(self):
        for post in self:
            post.social_media_ids = post.with_context(active_test=False).channel_ids.mapped('social_media_id')
            
    # Action Buttons
    def unlink(self):
        for post in self:
            if post.state != 'draft':
                raise UserError("You can only delete posts in draft stage.")
    def action_post(self):
        self.write({
            'method_publish': 'now',
            'date_scheduled': False,
            'date_published': fields.datetime.now(),
            'state': 'posted',
        })

    def action_schedule(self):
        self.write({
            'state': 'scheduled'
        })
        
    def action_schedule1(self):
        self.ensure_one()
        return {
            'name': 'Schedule Post',
            'view_mode': 'form',
            'res_model': 'sm.schedule.post.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'post_id': self.id,
            },
        }