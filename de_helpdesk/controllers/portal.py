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
        
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'tickets_count' in counters:
            values['tickets_count'] = request.env['project.task'].search_count([('project_id', '!=', False)]) \
                if request.env['project.task'].check_access_rights('read', raise_exception=False) else 0
        return values

    def _get_ticket_page_view_values(self, task, access_token, **kwargs):
        # Inherit the original method and add custom logic here
        values = super(TicketCustomerPortal, self)._task_get_page_view_values(task, access_token, **kwargs)
        
        # Check if the project is a helpdesk team
        if task.sudo().project_id.is_helpdesk_team:
            # Modify the URL accordingly
            #ticket_url = f"my/desk/ticket/%s?model=project.project&res_id={values['user'].id}&access_token={access_token}"

            history = request.session.get('my_tickets_history', [])
            try:
                current_task_index = history.index(task.id)
            except ValueError:
                return values
    
            total_ticket = len(history)

            values['ticket_link_section'] = []
            
            values['page_name'] = 'ticket'
            task_url = f"/my/desk/ticket/%s?model=project.task&res_id={values['user'].id}&access_token={access_token}"
            #values['prev_record'] = task_url % task.id
            #values['next_record'] = task_url % task.id
            values['ticket'] = task
            values['prev_record'] = current_task_index != 0 and task_url % history[current_task_index - 1]
            values['next_record'] = current_task_index < total_ticket - 1 and task_url % history[current_task_index + 1]
            #values['breadcrumb'] = [{'name': 'Tasks', 'url': '/my/desk/tickets'}, 
            #                        {'name': f'This is testing ticket 011111 (copy) (#TKT/{task.id})', 'url': task_url % task.id}]
            values['detail_page'] = 'ticket'

        return values

        
    def _get_ticket_page_view_values1(self, ticket_id, access_token, **kwargs):
        page_name = 'ticket'
        history = 'my_tickets_history'
        values = {
            'page_name': page_name,
            'ticket': ticket_id,
            'user': request.env.user,
            #'ticket_link_section': [],
            #'preview_object': ticket_id,
            #'object': ticket_id,
            'my_tickets_history': False,
            'page_name': 'ticket'
        }
        history = request.session.get('my_tickets_history', [])
        try:
            current_ticket_index = history.index(ticket_id.id)
        except ValueError:
            return values

        total_ticket = len(history)
        ticket_url = f"my/desk/ticket/%s?model=project.project&res_id={values['user'].id}&access_token={access_token}"

        values['prev_record'] = current_ticket_index != 0 and ticket_url % history[current_ticket_index - 1]
        values['next_record'] = current_ticket_index < total_ticket - 1 and ticket_url % history[current_ticket_index + 1]
        values['url'] = ticket_url
        #return values
        #raise UserError(ticket_url)
        return self._get_page_view_values(ticket_id, access_token, values, 'my_tickets_history', False, **kwargs)

    def _prepare_tickets_domain(self, partner):
        return [
            #('message_partner_ids', 'child_of', [partner.sudo().commercial_partner_id.id]),
            #('is_ticket', '=', True),
            ('partner_id','=',partner.id),
        ]
        

    def _prepare_tickets_values(self, page=1, date_begin=None, date_end=None, sortby=None, filterby='all', search=None, groupby='none', search_in='content'):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        domain = self._prepare_tickets_domain(partner)

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            #'reference': {'label': _('Reference'), 'order': 'id desc'},
            'name': {'label': _('Subject'), 'order': 'name'},
            'user': {'label': _('Assigned to'), 'order': 'user_ids'},
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
                search_domain = OR([search_domain, [('user_ids', 'in', assignees)]])
            if search_in == 'message':
                discussion_subtype_id = request.env.ref('mail.mt_comment').id
                search_domain = OR([search_domain, [('message_ids.body', 'ilike', search), ('message_ids.subtype_id', '=', discussion_subtype_id)]])
            if search_in == 'status':
                search_domain = OR([search_domain, [('stage_id', 'ilike', search)]])
            domain = AND([domain, search_domain])

        # pager
        tickets_count = request.env['project.task'].search_count(domain)
        pager = portal_pager(
            url="/my/desk/tickets",
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
            #'tickets': tickets,
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

    # Clsoe Ticket
    @http.route(['/my/desk/ticket/close/<int:ticket_id>'
                ], type='http', auth="user", website=True)        
    def close_ticket(
        self,
        ticket_id,
        access_token=False,
        **kw
    ):
        ticket_sudo = request.env['project.task'].browse(ticket_id)
        if kw.get('comment'):
            comment = kw.get('comment')
        else:
            comment = ' Ticket is no longer needed'
            
        rating = kw.get('rating')

        
        ticket_sudo.sudo().write({
            'customer_rating' : rating,
            'rating_comment': comment,
            'closed_by': 'customer',
            'stage_id': ticket_sudo.project_id.portal_close_stage_id.id,
        })

        lang = ticket_sudo.partner_id.lang or request.env.user.lang
        message_body = ticket_sudo._get_ticket_reopen_digest(comment, lang=lang)
        ticket_sudo.sudo().message_post(
            body=message_body,
            message_type='comment',
            subtype_id=request.env.ref('mail.mt_comment').id
        )
        
        return request.redirect(f'/my/desk/ticket/{ticket_id}?access_token={access_token}')

    # Reopen Ticket
    @http.route(['/my/desk/ticket/reopen/<int:ticket_id>'
                ], type='http', auth="user", website=True)        
    def reopen_ticket(
        self,
        ticket_id,
        access_token=False,
        **kw
    ):
        ticket_sudo = request.env['project.task'].browse(ticket_id)
        reason = kw.get('reason')

        reopen_reason_id = request.env['project.ticket.reopen']
        reopen_reason_id.create(ticket_sudo._prepare_ticket_reopen_reason_values(ticket_sudo,reason))

        stage_id = request.env['project.task.type'].search([
            ('fold','=',False),('project_ids','in',ticket_sudo.project_id.id)
        ],limit=1,order='sequence')

        ticket_sudo._prepare_ticket_reopen(stage_id)
     
        lang = ticket_sudo.partner_id.lang or request.env.user.lang
        message_body = ticket_sudo._get_ticket_reopen_digest(reason, lang=lang)
        ticket_sudo.sudo().message_post(
            body=message_body,
            message_type='comment',
            subtype_id=request.env.ref('mail.mt_comment').id
        )
        ticket_sudo.sudo().write({
            'stage_id': stage_id.id,
        })
        
        values = self._get_ticket_page_view_values(ticket_sudo, access_token, **kw)
        values['no_breadcrumbs'] = True
        values['op_type'] = 'ticket_reopend'
        return request.redirect(f'/my/desk/ticket/{ticket_id}?access_token={access_token}')
        
    # Submit Rating
    @http.route(['/my/desk/ticket/rating/<int:ticket_id>'
                ], type='http', auth="user", website=True)        
    def customer_rating_form(
        self,
        ticket_id,
        access_token=False,
        **kw
    ):
        ticket_sudo = request.env['project.task'].browse(ticket_id)
        values = self._get_ticket_page_view_values(ticket_sudo, access_token, **kw)
        values['no_breadcrumbs'] = True
        return request.render("de_helpdesk.portal_customer_rating_template", values)

    @http.route(['/my/desk/ticket/rating/submit/<int:ticket_id>'
                ], type='http', auth="user", website=True)        
    def customer_rating_submit(
        self,
        ticket_id,
        access_token=False,
        **kw
    ):
        ticket_sudo = request.env['project.task'].browse(ticket_id)
        comment = kw.get('comment')
        rating = kw.get('rating')
        
        ticket_sudo.write({
            'customer_rating' : rating,
            'rating_comment': comment,
            'closed_by': 'customer',
        })
        values = self._get_ticket_page_view_values(ticket_sudo, access_token, **kw)
        values['no_breadcrumbs'] = True

        html_message = ''
        html_message += '<h3>Thank You for Your Valuable Feedback on ' + ticket_sudo.name + '(##' + ticket.sudo.ticket_no + ')' + '</h3>'
        html_message += '<p>We appreciate your input and value your feedback. Thank you for taking the time to share your thoughts with us.</p>'
        values['html_message'] = html_message
        return request.render("de_helpdesk.portal_thanks_message_template", values)

    