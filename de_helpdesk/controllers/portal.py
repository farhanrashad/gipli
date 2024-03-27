from collections import OrderedDict
from operator import itemgetter
from markupsafe import Markup

from odoo import conf, http, _
from odoo.exceptions import AccessError, MissingError, UserError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.tools import groupby as groupbyelem

from odoo.osv.expression import OR, AND


class TicketCustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(TicketCustomerPortal, self)._prepare_portal_layout_values()
        return values
        
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'tickets_count' in counters:
            values['tickets_count'] = request.env['project.task'].search_count([('project_id', '!=', False)]) \
                if request.env['project.task'].check_access_rights('read', raise_exception=False) else 0
        return values
        
    def _get_ticket_page_view_values(self, ticket_id, access_token, **kwargs):
        page_name = 'ticket'
        history = 'my_tickets_history'
        values = {
            'page_name': page_name,
            'ticket': ticket_id,
            'user': request.env.user,
            'ticket_link_section': [],
            'preview_object': ticket_id,
            'object': ticket_id,
        }
        return self._get_page_view_values(ticket_id, access_token, values, 'my_tickets_history', False, **kwargs)

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

    def _ticket_get_searchbar_inputs(self):
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

    def _prepare_tickets_domain(self):
        return []
        
    def _prepare_tickets_values(self, page, date_begin, date_end, sortby, search, search_in, groupby, url="/my/desk/tickets", domain=None, su=False, project=False):
        values = self._prepare_portal_layout_values()

        Ticket = request.env['project.task'].search([])
        searchbar_sortings = dict(sorted(self._ticket_get_searchbar_sortings(project).items(),
                                         key=lambda item: item[1]["sequence"]))
        searchbar_inputs = self._ticket_get_searchbar_inputs()
        #searchbar_groupby = self._ticket_get_searchbar_groupby(project)

        if not domain:
            domain = []
        #if not su and Ticket.check_access_rights('read'):
        #    domain = AND([domain, request.env['ir.rule']._compute_domain(Ticket._name, 'read')])
        Ticket_sudo = Ticket.sudo()

        # default sort by value
       
        order = searchbar_sortings[sortby]['order']
        
        # default group by value
        

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        
        # search
        if search and search_in:
            domain += self._ticket_get_search_domain(search_in, search)

        # content according to pager and archive selected
        # order = self._ticket_get_order(order, groupby)
        #raise UserError(len(Ticket_sudo))

        values.update({
            'date': date_begin,
            'date_end': date_end,
            #'grouped_tickets': get_grouped_tickets,
            'page_name': 'ticket',
            'default_url': url,
            'ticket_url': 'tickets',
            'tickets': Ticket_sudo,
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

    def _prepare_tickets_values(self, page=1, date_begin=None, date_end=None, sortby=None, filterby='all', search=None, groupby='none', search_in='content'):
        values = self._prepare_portal_layout_values()
        domain = self._prepare_tickets_domain()

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            #'reference': {'label': _('Reference'), 'order': 'id desc'},
            'name': {'label': _('Subject'), 'order': 'name'},
            #'user': {'label': _('Assigned to'), 'order': 'user_id'},
            'stage': {'label': _('Stage'), 'order': 'stage_id'},
            #'update': {'label': _('Last Stage Update'), 'order': 'date_last_stage_update desc'},
        }
        searchbar_filters = {
            #'all': {'label': _('All'), 'domain': []},
            'assigned': {'label': _('Assigned'), 'domain': [('user_ids', '!=', False)]},
            'unassigned': {'label': _('Unassigned'), 'domain': [('user_ids', '=', False)]},
            #'open': {'label': _('Open'), 'domain': [('close_date', '=', False)]},
            #'closed': {'label': _('Closed'), 'domain': [('close_date', '!=', False)]},
        }
        searchbar_inputs = {
            'content': {'input': 'content', 'label': Markup(_('Search <span class="nolabel"> (in Content)</span>'))},
            #'ticket_ref': {'input': 'ticket_ref', 'label': _('Search in Reference')},
            'message': {'input': 'message', 'label': _('Search in Messages')},
            'user': {'input': 'user', 'label': _('Search in Assigned to')},
            'status': {'input': 'status', 'label': _('Search in Stage')},
        }
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'stage': {'input': 'stage_id', 'label': _('Stage')},
            'user': {'input': 'user_ids', 'label': _('Assigned to')},
        }

        if not groupby:
            groupby = 'none'
        
        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        if groupby in searchbar_groupby and groupby != 'none':
            order = f'{searchbar_groupby[groupby]["input"]}, {order}'

        
        #else:
        #    domain = AND([domain, searchbar_filters[filterby]['domain']])

        if date_begin and date_end:
            domain = AND([domain, [('create_date', '>', date_begin), ('create_date', '<=', date_end)]])

        # search
        if search and search_in:
            search_domain = []
            if search_in == 'ticket_ref':
                search_domain = OR([search_domain, [('ticket_ref', 'ilike', search)]])
            if search_in == 'content':
                search_domain = OR([search_domain, ['|', ('name', 'ilike', search), ('description', 'ilike', search)]])
            if search_in == 'user':
                assignees = request.env['res.users'].sudo()._search([('name', 'ilike', search)])
                search_domain = OR([search_domain, [('user_id', 'in', assignees)]])
            if search_in == 'message':
                discussion_subtype_id = request.env.ref('mail.mt_comment').id
                search_domain = OR([search_domain, [('message_ids.body', 'ilike', search), ('message_ids.subtype_id', '=', discussion_subtype_id)]])
            if search_in == 'status':
                search_domain = OR([search_domain, [('stage_id', 'ilike', search)]])
            domain = AND([domain, search_domain])

        # pager
        tickets_count = request.env['project.task'].search_count(domain)
        pager = portal_pager(
            url="/my/tickets",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'search_in': search_in, 'search': search, 'groupby': groupby, 'filterby': filterby},
            total=tickets_count,
            page=page,
            step=self._items_per_page
        )

        tickets = request.env['project.task'].search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_tickets_history'] = tickets.ids[:100]

        if not tickets:
            grouped_tickets = []
        elif groupby != 'none':
            grouped_tickets = [request.env['project.task'].concat(*g) for k, g in groupbyelem(tickets, itemgetter(searchbar_groupby[groupby]['input']))]
        else:
            grouped_tickets = [tickets]

        tickets = request.env['project.task'].search([])
        #raise UserError(tickets)
        values.update({
            'date': date_begin,
            'grouped_tickets': grouped_tickets,
            'tickets': tickets,
            'page_name': 'ticket',
            'default_url': '/my/desk/tickets',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            #'searchbar_filters': searchbar_filters,
            'searchbar_inputs': searchbar_inputs,
            'searchbar_groupby': searchbar_groupby,
            'sortby': sortby,
            'groupby': groupby,
            'search_in': search_in,
            'search': search,
            'filterby': filterby,
        })
        return values
    
    @http.route([
        '/my/desk/tickets', 
        '/my/desk/tickets/page/<int:page>'
    ], type='http', auth="user", website=True)
    def portal_my_tickets(self, page=1, date_begin=None, date_end=None, sortby='date', filterby=None, search=None, search_in='content', groupby=None, **kw):
        values = self._prepare_tickets_values(page, date_begin, date_end, sortby, filterby, search, groupby, search_in)
        return request.render("de_helpdesk.portal_my_tickets", values)

    @http.route([
        "/my/desk/ticket/<int:ticket_id>",
        "/my/desk/ticket/<int:ticket_id>/<access_token>",
        '/my/desk/ticket/<int:ticket_id>',
        '/my/desk/ticket/<int:ticket_id>/<access_token>'
    ], type='http', auth="public", website=True)
    def portal_my_ticket(self, ticket_id, report_type=None, access_token=None, project_sharing=False, **kw):
        try:
            ticket_sudo = self._document_check_access('project.task', ticket_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
    
        if report_type in ('pdf', 'html', 'text'):
            return self._show_ticket_report(ticket_sudo, report_type, download=kw.get('download'))
    
        # ensure attachment are accessible with access token inside template
        for attachment in ticket_sudo.attachment_ids:
            attachment.generate_access_token()
        
        # Add 'ticket' to the values dictionary
        values = self._get_ticket_page_view_values(ticket_sudo, access_token, **kw)
        
        #request.session['my_tickets_history'] = ticket_sudo.ids
        return request.render("de_helpdesk.portal_my_ticket", values)

    