from collections import OrderedDict
from operator import itemgetter
from markupsafe import Markup

from odoo import conf, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
#from odoo.tools import groupby as groupbyelem

from odoo.osv.expression import OR, AND


class TicketCustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'tickets_count' in counters:
            values['tickets_count'] = request.env['project.task'].search_count([('project_id', '!=', False)]) \
                if request.env['project.task'].check_access_rights('read', raise_exception=False) else 0
        return values
        
    def _ticket_get_page_view_values(self, ticket, access_token, **kwargs):
        project = kwargs.get('project')
        if project:
            project_accessible = True
            page_name = 'project_ticket'
            history = 'my_project_tickets_history'
        else:
            page_name = 'ticket'
            history = 'my_tickets_history'
            try:
                project_accessible = bool(ticket.project_id.id and self._document_check_access('project.project', ticket.project_id.id))
            except (AccessError, MissingError):
                project_accessible = False
        values = {
            'page_name': page_name,
            'ticket': ticket,
            'user': request.env.user,
            'project_accessible': project_accessible,
            'ticket_link_section': [],
            'preview_object': ticket,
        }

    def _ticket_get_searchbar_sortings(self, project=False):
        values = {
            'date': {'label': _('Newest'), 'order': 'create_date desc', 'sequence': 1},
            'name': {'label': _('Title'), 'order': 'name', 'sequence': 2},
            'users': {'label': _('Assignees'), 'order': 'user_ids', 'sequence': 4},
            'stage': {'label': _('Stage'), 'order': 'stage_id, project_id', 'sequence': 5},
            'status': {'label': _('Status'), 'order': 'state', 'sequence': 6},
            'priority': {'label': _('Priority'), 'order': 'priority desc', 'sequence': 8},
            'date_deadline': {'label': _('Deadline'), 'order': 'date_deadline asc', 'sequence': 9},
            'update': {'label': _('Last Stage Update'), 'order': 'date_last_stage_update desc', 'sequence': 11},
        }
        
        return values

    def _ticket_get_searchbar_groupby(self, project=False):
        values = {
            'none': {'input': 'none', 'label': _('None'), 'order': 1},
            'stage': {'input': 'stage', 'label': _('Stage'), 'order': 4},
            'status': {'input': 'status', 'label': _('Status'), 'order': 5},
            'priority': {'input': 'priority', 'label': _('Priority'), 'order': 7},
            'customer': {'input': 'customer', 'label': _('Customer'), 'order': 10},
        }
        
        return dict(sorted(values.items(), key=lambda item: item[1]["order"]))

    def _ticket_get_groupby_mapping(self):
        return {
            'stage': 'stage_id',
            'customer': 'partner_id',
            'priority': 'priority',
            'status': 'state',
        }

    def _ticket_get_order(self, order, groupby):
        #groupby_mapping = self._ticket_get_groupby_mapping()
        #field_name = groupby_mapping.get(groupby, '')
        if not field_name:
            return order
        return '%s, %s' % (field_name, order)

    def _ticket_get_searchbar_inputs(self, project=False):
        values = {
            'all': {'input': 'all', 'label': _('Search in All'), 'order': 1},
            'content': {'input': 'content', 'label': Markup(_('Search <span class="nolabel"> (in Content)</span>')), 'order': 1},
            'ref': {'input': 'ref', 'label': _('Search in Ref'), 'order': 1},
            'users': {'input': 'users', 'label': _('Search in Assignees'), 'order': 3},
            'stage': {'input': 'stage', 'label': _('Search in Stages'), 'order': 4},
            'status': {'input': 'status', 'label': _('Search in Status'), 'order': 5},
            'priority': {'input': 'priority', 'label': _('Search in Priority'), 'order': 7},
            'customer': {'input': 'customer', 'label': _('Search in Customer'), 'order': 10},
            'message': {'input': 'message', 'label': _('Search in Messages'), 'order': 11},
        }
        return dict(sorted(values.items(), key=lambda item: item[1]["order"]))

    def _ticket_get_search_domain(self, search_in, search):
        search_domain = []
        if search_in in ('content', 'all'):
            search_domain.append([('name', 'ilike', search)])
            search_domain.append([('description', 'ilike', search)])
        if search_in in ('customer', 'all'):
            search_domain.append([('partner_id', 'ilike', search)])
        if search_in in ('message', 'all'):
            search_domain.append([('message_ids.body', 'ilike', search)])
        if search_in in ('stage', 'all'):
            search_domain.append([('stage_id', 'ilike', search)])
        if search_in in ('project', 'all'):
            search_domain.append([('project_id', 'ilike', search)])
        if search_in in ('ref', 'all'):
            search_domain.append([('id', 'ilike', search)])
        if search_in in ('milestone', 'all'):
            search_domain.append([('milestone_id', 'ilike', search)])
        if search_in in ('users', 'all'):
            user_ids = request.env['res.users'].sudo().search([('name', 'ilike', search)])
            search_domain.append([('user_ids', 'in', user_ids.ids)])
        if search_in in ('priority', 'all'):
            search_domain.append([('priority', 'ilike', search == 'normal' and '0' or '1')])
        if search_in in ('status', 'all'):
            state_dict = dict(map(reversed, request.env['project.task']._fields['state']._description_selection(request.env)))
            search_domain.append([('state', 'ilike', state_dict.get(search, search))])
        return OR(search_domain)

    def _prepare_tickets_values(self, page, date_begin, date_end, sortby, search, search_in, groupby, url="/my/desk/tickets", domain=None, su=False, project=False):
        values = self._prepare_portal_layout_values()

        Ticket = request.env['project.task']
        searchbar_sortings = dict(sorted(self._ticket_get_searchbar_sortings(project).items(),
                                         key=lambda item: item[1]["sequence"]))
        searchbar_inputs = self._ticket_get_searchbar_inputs(project)
        #searchbar_groupby = self._ticket_get_searchbar_groupby(project)

        if not domain:
            domain = []
        if not su and Ticket.check_access_rights('read'):
            domain = AND([domain, request.env['ir.rule']._compute_domain(Ticket._name, 'read')])
        Ticket_sudo = Ticket.sudo()

        # default sort by value
        if not sortby or (sortby == 'milestone' and not milestones_allowed):
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        
        # default group by value
        if not groupby or (groupby == 'milestone' and not milestones_allowed):
            groupby = 'project'

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        
        # search
        if search and search_in:
            domain += self._ticket_get_search_domain(search_in, search)

        # content according to pager and archive selected
        #order = self._ticket_get_order(order, groupby)

        def get_grouped_tickets(pager_offset):
            tickets = Ticket_sudo.search(domain, order=order, limit=self._items_per_page, offset=pager_offset)
            request.session['my_project_tickets_history' if url.startswith('/my/projects') else 'my_tickets_history'] = tickets.ids[:100]

            

            groupby_mapping = self._ticket_get_groupby_mapping()
            group = groupby_mapping.get(groupby)
            if group:
                if group == 'milestone_id':
                    grouped_tickets = [Ticket_sudo.concat(*g) for k, g in groupbyelem(tickets_project_allow_milestone, itemgetter(group))]

                    if not grouped_tickets:
                        if tickets_no_milestone:
                            grouped_tickets = [tickets_no_milestone]
                    else:
                        if grouped_tickets[len(grouped_tickets) - 1][0].milestone_id and tickets_no_milestone:
                            grouped_tickets.append(tickets_no_milestone)
                        else:
                            grouped_tickets[len(grouped_tickets) - 1] |= tickets_no_milestone

                else:
                    grouped_tickets = [Ticket_sudo.concat(*g) for k, g in groupbyelem(tickets, itemgetter(group))]
            else:
                grouped_tickets = [tickets] if tickets else []


            ticket_states = dict(Ticket_sudo._fields['state']._description_selection(request.env))
            if sortby == 'status':
                if groupby == 'none' and grouped_tickets:
                    grouped_tickets[0] = grouped_tickets[0].sorted(lambda tickets: tickets_states.get(tickets.state))
                else:
                    grouped_tickets.sort(key=lambda tickets: ticket_states.get(tickets[0].state))
            return grouped_tickets

        values.update({
            'date': date_begin,
            'date_end': date_end,
            #'grouped_tickets': get_grouped_tickets,
            'page_name': 'tickets',
            'default_url': url,
            'ticket_url': 'tickets',
            'pager': {
                "url": url,
                "url_args": {'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'groupby': groupby, 'search_in': search_in, 'search': search},
                "total": Ticket_sudo.search_count(domain),
                "page": page,
                "step": self._items_per_page
            },
            'searchbar_sortings': searchbar_sortings,
            #'searchbar_groupby': searchbar_groupby,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'groupby': groupby,
        })
        return values

    def _get_my_tickets_searchbar_filters(self):
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': [('prj_ticket_type_id', '!=', False)]},
        }
        ticket_types = request.env['project.ticket.type'].search([])
        for type in ticket_types:
            searchbar_filters.update({
                str(type.id): {'label': type.name, 'domain': [('prj_ticket_type_id', '=', type.id)]}
            })

        return searchbar_filters
    
    def _get_my_tickets_searchbar_filters1(self, project_domain=None, ticket_domain=None):
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': [('project_id', '!=', False)]},
        }

        # extends filterby criteria with project the customer has access to
        projects = request.env['project.project'].search(project_domain or [])
        for project in projects:
            searchbar_filters.update({
                str(project.id): {'label': project.name, 'domain': [('project_id', '=', project.id)]}
            })

        # extends filterby criteria with project (criteria name is the project id)
        # Note: portal users can't view projects they don't follow
        #project_groups = request.env['project.task']._read_group(AND([[('project_id', 'not in', projects.ids)], ticket_domain or []]),
        #                                                        ['project_id'])
        #for [project] in project_groups:
        #    proj_name = project.sudo().display_name if project else _('Others')
        #    searchbar_filters.update({
        #        str(project.id): {'label': proj_name, 'domain': [('project_id', '=', project.id)]}
        #    })
        return searchbar_filters

    
    @http.route([
        '/my/desk/tickets', 
        '/my/desk/tickets/page/<int:page>'
    ], type='http', auth="user", website=True)
    def portal_my_tickets(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='content', groupby=None, **kw):
        searchbar_filters = self._get_my_tickets_searchbar_filters()

        if not filterby:
            filterby = 'all'
        domain = searchbar_filters.get(filterby, searchbar_filters.get('all'))['domain']

        values = self._prepare_tickets_values(page, date_begin, date_end, sortby, search, search_in, groupby, domain=domain)

        # pager
        pager_vals = values['pager']
        pager_vals['url_args'].update(filterby=filterby)
        pager = portal_pager(**pager_vals)

        values.update({
            #'grouped_tickets': values['grouped_tickets'](pager['offset']),
            'pager': pager,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return request.render("de_helpdesk.portal_my_tickets", values)

    