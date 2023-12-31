# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta, date
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import float_compare, format_datetime, format_time
from pytz import timezone, UTC


class EnrollmentContract(models.Model):
    _inherit = 'sale.order'

    is_enrol_order = fields.Boolean("Enrol Order")
    state = fields.Selection(selection_add=[('enrol', 'Enrol in Progress')])
    enrol_status = fields.Selection([
        ('draft', 'Draft'),
        ('process','In Process'), #submitted and is awaiting review by the school or admission office.
        #('review','Under Review'), #reviewing the agreement and may request additional information or clarification.
        #('approved', 'Approved'), # reviewed and approved by the school, indicating that the student is accepted.
        #('pending', 'Pending Payment'), #accepted, and the agreement is pending payment of any fees or tuition.
        #('done', 'Done'), #The agreement is marked as done once the student has successfully 
        ('open', 'Running'), #The student is officially enrolled and attending classes.
        ('close', 'Close'), #close the contract, student completed the course.
        ('reject', 'Rejected'), #he school has reviewed the agreement and decided not to accept the student.
        ('cancel', 'Cancelled'), #student decides not to enroll after initially submitting the agreement,
        ('expire', 'Expired'), #Some enrollment agreements may have an expiration date, if that date passes without acceptance, the status could be "Expired.
    ], string="Enroll Status", default='draft', 
        readonly=True, copy=False, index=True,
        tracking=3, store=True, 
                                   )
    # enroll_status = next action to do basically, but shown string is action done.
    
    # Academic Fields
    course_id = fields.Many2one('oe.school.course', string='Course')
    batch_id = fields.Many2one('oe.school.course.batch', string='Batch')
    
    #enrol_order_tmpl_id = fields.Many2one('oe.enrol.order.template', 'Template', readonly=True, check_company=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    admission_team_id = fields.Many2one(
        comodel_name='oe.admission.team',
        string="Admission Team",
        compute='_compute_admission_team_id',
        store=True, readonly=False, precompute=True, ondelete="set null",
        change_default=True, check_company=True,  # Unrequired company
        tracking=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    #@api.onchange('enrol_order_tmpl_id')
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

    @api.depends('partner_id', 'user_id')
    def _compute_admission_team_id(self):
        cached_teams = {}
        for order in self:
            default_team_id = self.env.context.get('default_admission_team_id', False) or order.admission_team_id.id or order.partner_id.admission_team_id.id
            user_id = order.user_id.id
            company_id = order.company_id.id
            key = (default_team_id, user_id, company_id)
            if key not in cached_teams:
                cached_teams[key] = self.env['oe.admission.team'].with_context(
                    default_team_id=default_team_id
                )._get_default_team_id(
                    user_id=user_id, domain=[('company_id', 'in', [company_id, False])])
            order.admission_team_id = cached_teams[key]
            
    #=== CRUD METHODS ===#
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'company_id' in vals:
                self = self.with_company(vals['company_id'])

            if vals.get('name', _("New")) == _("New"):
                if vals.get('is_enrol_order', False):
                    # Assign a new sequence for enrol orders
                    date_order = vals.get('date_order')
                    if date_order:
                        date_order = fields.Datetime.to_datetime(date_order)
                        seq_date = fields.Datetime.context_timestamp(self, date_order)
                    else:
                        seq_date = fields.Datetime.now()

                    vals['name'] = self.env['ir.sequence'].next_by_code(
                        'enrol.order', sequence_date=seq_date) or _("New")
                    vals['state'] = 'enrol'  # Set the state to 'enrol'
                else:
                    # Use the default sequence and state for non-enrol orders
                    date_order = vals.get('date_order')
                    if date_order:
                        date_order = fields.Datetime.to_datetime(date_order)
                        seq_date = fields.Datetime.context_timestamp(self, date_order)
                    else:
                        seq_date = fields.Datetime.now()

                    vals['name'] = self.env['ir.sequence'].next_by_code(
                        'sale.order', sequence_date=seq_date) or _("New")
                    vals['state'] = 'draft'  # Set the state to 'draft' (or another appropriate state)

        return super(EnrollmentContract, self).create(vals_list)


    # -----------------------------------------------
    # --------------- Constraints -------------------
    # -----------------------------------------------
    @api.constrains('enrol_status', 'partner_id')
    def _check_open_contract(self):
        for record in self:
            if record.is_enrol_order:
                #raise UserError(record['enrol_status'])
                open_order = self.env['sale.order'].search_count([('enrol_status', 'in', ['open']), ('partner_id', '=', record.partner_id.id), ('id', '!=', record.id)])
                process_order = self.env['sale.order'].search_count([('enrol_status', 'in', ['open']), ('partner_id', '=', record.partner_id.id)])
    
                #raise UserError(process_order)
                if (record.enrol_status == 'open' and process_order > 1) or open_order > 1:
                    raise models.ValidationError("One of student contract is already running.")

    
    # All action Buttons
    def button_submit(self):
        if len(self.order_line) == 0:
            raise UserError(_(
                    "You can not submit an application without line."
                    ))
            
        self.write({
            'enrol_status': 'process'
        })

    def button_start_review(self):
        self.write({
            'enrol_status': 'review'
        })

    def button_end_review(self):
        self.write({
            'enrol_status': 'approved'
        })
        
    def button_confirm(self):
        self.write({
            'enrol_status': 'open'
        })
        self.action_confirm()

    def button_payment(self):
        self.write({
            'enrol_status': 'done'
        })

    def action_draft(self):
        res = super(EnrollmentContract,self).action_draft()
        self.write({
            'enrol_status': 'draft',
            'state': 'enrol'
        })
        return res
        
    def action_cancel(self):
        res = super(EnrollmentContract,self).action_cancel()
        self.write({
            'enrol_status': 'cancel'
        })
        return res
    #def button_open(self):
    #    self.write({
    #        'enrol_status': 'open'
    #    })


class EnrollmentOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_enrol = fields.Boolean(default=False)  # change to compute if pickup_date and return_date set?

   