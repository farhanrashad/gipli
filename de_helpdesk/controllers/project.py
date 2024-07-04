# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import OrderedDict
from operator import itemgetter
from markupsafe import Markup

from odoo import conf, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.tools import groupby as groupbyelem

from odoo.osv.expression import OR, AND


class ProjectCustomerPortal(CustomerPortal):
    def _prepare_project_domain(self):
        domain = super(ProjectCustomerPortal, self)._prepare_project_domain()
        # Add or modify conditions in the domain as needed
        domain += [('is_helpdesk_team', '=', False)]
        return domain

    """
    def _prepare_tasks_values(self, page, date_begin, date_end, sortby, search, search_in, groupby, url="/my/tasks", domain=None, su=False, project=False):
        # Apply your custom domain
        if domain is None:
            domain = []
        ticket_domain = [('is_ticket', '!=', True)]
        domain = AND([domain, ticket_domain])

        # Call the original method with the modified domain
        values = super()._prepare_tasks_values(page, date_begin, date_end, sortby, search, search_in, groupby, url, domain, su, project)

        return values
    """