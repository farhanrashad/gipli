# -*- coding: utf-8 -*-


from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.exceptions import UserError, AccessError
from odoo.osv import expression


class AdmissionTeam(models.Model):
    _inherit = "oe.admission.team"

    enrol_orders_count = fields.Integer(
        string='# Enrol Orders', compute='_compute_enrol_orders_data')
    enrol_orders_amount = fields.Monetary(
        string='Enrol Orders Revenues', compute='_compute_enrol_orders_data')

    def _compute_enrol_orders_data(self):
        for record in self:
            order_ids = self.env['sale.order'].search([('admission_team_id','=',record.id),('is_enrol_order','=',True)])
            record.enrol_orders_count = len(order_ids)
            record.enrol_orders_amount = sum(order_ids.mapped('amount_total'))

    def action_open_enrol_orders(self):
        action = self.env["ir.actions.actions"]._for_xml_id("de_school_enrollment.enrollment_order_action")
        action['context'] = self._prepare_enrol_order_context()
        action['domain'] = expression.AND([[('is_enrol_order', '=', True)], self._get_enrol_order_domain()])
        #context = {
        #    'default_admission_team_id': self.id,
        #    'search_default_inprogress_orders': True,
        #}
        #action['context']['search_default_admission_team_id'] = self.id
        #action['context']['active_test'] = True
        return action

    def _get_enrol_order_domain(self):
        return [('admission_team_id', '=', self.id)]
         
    def _prepare_enrol_order_context(self):
        """ Prepares the context for a new quotation (sale.order) by sharing the values of common fields """
        self.ensure_one()
        order_context = {
            'default_admission_team_id': self.id,
            'search_default_admission_team_id': self.id,
            'search_default_inprogress_orders': 1,
            'create':False,
        }
        order_context['default_admission_team_id'] = self.id
        if self.user_id:
            order_context['default_user_id'] = self.user_id.id
        return order_context
         
    def action_open_enrol_orders11(self):
        self.ensure_one()
        active_id = self.env.context.get('team_id')
        context = {
            'default_admission_team_id': self.id,
            'search_default_inprogress_orders': True,
        }
        if active_id:
            context['search_default_admission_team_id'] = [active_id]
            context['search_default_inprogress_orders'] = True
            context['search_default_team_id'] = [active_id]
            context['default_team_id'] = active_id
        #raise UserError(active_id)
        return {
            'name': 'Open Contracts',
            'view_type': 'form',
            'view_mode': 'tree,kanban,form,calendar,pivot,graph,activity',
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'context': context,
            'domain': [('admission_team_id','=',self.id),('is_enrol_order','=','True')],
            'search_view_id': self.env.ref('de_school_enrollment.enrol_order_view_search').id,
            'action_id': self.env.ref('de_school_admission_enrol.action_team_enrol_orders').id,
            'view_ids': [(5, 0, 0),
                (0, 0, {'view_mode': 'tree', 'view_id': self.env.ref('de_school_enrollment.enrollment_order_view_tree').id}),
                (0, 0, {'view_mode': 'form', 'view_id': self.env.ref('de_school_enrollment.enrol_contract_primary_form_view').id}),
            ],
        }