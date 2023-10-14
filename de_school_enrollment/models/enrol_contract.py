# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta, date
from odoo import api, fields, models, _
from odoo.tools import float_compare, format_datetime, format_time
from pytz import timezone, UTC


class EnrollmentContract(models.Model):
    _inherit = 'sale.order'

    is_enrol_order = fields.Boolean("Enrol Order")
    enrol_status = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('confirm', 'Enrolled'),
        ('drop', 'Dropped'),
        ('cancel', 'Cancelled'),
    ], string="Enroll Status", default='draft', store=True)
    # enroll_status = next action to do basically, but shown string is action done.
    
    # Academic Fields
    course_id = fields.Many2one('oe.school.course', string='Course')
    batch_id = fields.Many2one('oe.school.course.batch', string='Batch')
    
    enrol_order_tmpl_id = fields.Many2one('oe.enrol.order.template', 'Template', readonly=True, check_company=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    @api.onchange('enrol_order_tmpl_id')
    def _onchange_enrol_order_tmpl_id(self):
        enrol_order_template = self.enrol_order_tmpl_id.with_context(lang=self.partner_id.lang)

        order_lines_data = [fields.Command.clear()]
        order_lines_data += [
            fields.Command.create(line._prepare_order_line_values())
            for line in enrol_order_template.enrol_order_tmpl_line
        ]

        # set first line to sequence -99, so a resequence on first page doesn't cause following page
        # lines (that all have sequence 10 by default) to get mixed in the first page
        if len(order_lines_data) >= 2:
            order_lines_data[1][2]['sequence'] = -99

        self.order_line = order_lines_data
    

class EnrollmentOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_enrol = fields.Boolean(default=False)  # change to compute if pickup_date and return_date set?

   