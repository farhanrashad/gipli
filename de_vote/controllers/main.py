# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from datetime import datetime


class WebsiteCandidate(http.Controller):
	@http.route(['/candidate/form'],type="http", auth="public", website=True)
	def faq_ans(self, **kw):
		#obj = request.env["website.faq"].search([('is_published','=',True)]);
		return request.render("de_vote.find_candidate_form");

