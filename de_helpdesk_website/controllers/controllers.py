# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.http import request
from odoo.exceptions import UserError, ValidationError


class WebsiteHelpdesk(http.Controller):

    
    #@http.route(['/support/'], type="http", auth="public", website=True, sitemap=True)
    #def faq_ans(self, **kw):
    #    obj = request.env["project.project"].search([('is_published', '=', True)])
    #    return request.render("de_helpdesk_website.web_faq", {"object": obj, })

    @http.route(['/support/<string:url>'], type="http", auth="public", website=True)
    def website_helpdesk(self, url, **kw):
        # Search for the project with the given URL
        #raise UserError('/support/'+url)
        project = request.env["project.project"].sudo()._get_project_by_website_url('/support/'+url)
        #search([('website_url', '=', 'support/'+url)], limit=1)
        
        if not project:
            return request.not_found()

        vals = {
            'project': project,
        }
        
        return request.render("de_helpdesk_website.website_helpdesk_form", vals)


    @http.route('/support/ticket/submit', type="http", website=True, auth='public', csrf=False)
    def ticket_submit(self, **kw):
        ticket = request.env['project.task'].browse(1)
        return request.render("de_helpdesk_website.support_ticket_submited", {"ticket": ticket})
        
