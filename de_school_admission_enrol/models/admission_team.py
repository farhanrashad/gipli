# -*- coding: utf-8 -*-


from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.exceptions import UserError, AccessError

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
        self.ensure_one()
        active_id = self.env.context.get('team_id')
        context = {
            'default_team_id': active_id,
        }
        if active_id:
            context['search_default_team_id'] = [active_id]
            context['search_default_inprogress_orders'] = True
        return {
            'name': 'Open Contracts',
            'view_type': 'form',
            'view_mode': 'tree,kanban,form,calendar,pivot,graph,activity',
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'context': context,
            'domain': [('team_id','=',self.id),('is_enrol_order','=','True')],
            'action_id': self.env.ref('de_school_enrollment.enrollment_order_action').id,
            'search_view_id': self.env.ref('de_school_enrollment.enrol_order_view_search').id,
        }