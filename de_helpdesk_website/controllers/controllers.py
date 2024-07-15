# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.http import request
from odoo.exceptions import UserError, ValidationError


class WebsiteHelpdesk(http.Controller):


    @http.route(['/support/<string:url>'], type="http", auth="public", website=True)
    def website_helpdesk(self, url, **kw):
        
        project = request.env["project.project"].sudo()._get_project_by_website_url('/support/'+url)

        user_name = user_email = ''
        
        if not project:
            return request.not_found()

        if request.env.user.id == request.env.ref('base.public_user').id:
            user_name = ''
            user_email = ''
        else:
            user_name = request.env.user.name
            user_email = request.env.user.email

        vals = {
            'project': project,
            'user_name': user_name,
            'user_email': user_email
        }
        
        return request.render("de_helpdesk_website.website_helpdesk_form", vals)


    @http.route('/support/ticket/submit', type="http", website=True, auth='public', csrf=False)
    def ticket_submit(self, **kw):

        partner_id = request.env['res.partner']
        
        if request.env.user.id == request.env.ref('base.public_user').id:
            partner_id = request.env['res.partner'].sudo().create({
                'name': kw.get('contact_name'),
                'email': kw.get('email_from'),
                'company_type': 'person',
            })
        else:
            partner_id = request.env.user.partner_id
        
        vals = {
            'project_id' : int(kw.get('project_id')),
            'partner_id': partner_id.id,
            'name' : kw.get('name'),
            'email_from': kw.get('email_from'),
            'contact_name': kw.get('contact_name'),
            'description': kw.get('description'),
            'attachment_files': request.httprequest.files.getlist('attachments')
        }
        #raise UserError(kw.get('project_id'))
        ticket = request.env['project.project'].sudo()._create_ticket(vals)

        #ticket = request.env['project.task'].browse(1)
        return request.render("de_helpdesk_website.support_ticket_submited", {"ticket": ticket})
        
