# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.http import request


class WebsiteHelpdesk(http.Controller):

    @http.route(['/support'], type="http", auth="public", website=True, sitemap=True)
    def faq_ans(self, **kw):
        obj = request.env["project.project"].search([('is_published', '=', True)])
        return request.render("de_helpdesk_website.web_faq", {"object": obj, })
