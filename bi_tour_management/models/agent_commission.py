from odoo import models, fields, api, _


class AgentCommissionInvoice(models.Model):
    _name = 'agent.commission.invoice'

    name = fields.Char(string='Registration ID', required=True,
                       readonly=True, default=lambda self: _('New'))
    date = fields.Date(string='Date')
    agent_partner_id = fields.Many2one('res.partner', string='Agent')
    currency_id = fields.Many2one('res.currency', string='Price List')
    state = fields.Selection(
        string='Status',
        selection=[('draft', 'Draft'),
                   ('confirm', 'Confirm'),
                   ('invoiced', 'Invoice'),
                   ('done', 'Done'),
                   ('cancel', 'Cancel'),
                   ],
        required=False, default='draft')
    commission_line_ids = fields.One2many('agent.commission.invoice.line', 'invoice_id', string='Commission Lines')
    total_amount_commission = fields.Float(string='Commission Amount', compute='_compute_total_amount_commission')
    commission_count = fields.Integer(string='Invoice', compute='_compute_commission_count')

    @api.depends('commission_line_ids.total_tour_cost')
    def _compute_total_amount_commission(self):
        for commission in self:
            commission.total_amount_commission = sum(commission.commission_line_ids.mapped('total_tour_cost'))

    def confirm_record(self):
        for record in self:
            record.state = 'confirm'

    def create_commission_invoice(self):
        for order in self:
            invoice_vals = {
                'partner_id': order.agent_partner_id.id,
                'name': order.name,
                'move_type': 'in_invoice',
                'invoice_date': fields.Date.today(),
            }
            invoice = self.env['account.move'].sudo().create(invoice_vals)
            line_vals = {
                'move_id': invoice.id,
                # 'product_id': order.id,
                'name': order.name,
                'quantity': 1,
                'price_unit': order.total_amount_commission,
            }
            self.env['account.move.line'].create(line_vals)
            # Mark the sale order as invoiced
            order.write({'state': 'invoiced'})

    def commission_done(self):
        for rec in self:
            rec.state = 'done'

    def cancel_commission(self):
        for rec in self:
            rec.state = 'cancel'

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'agent.commission') or _('New')
        res = super(AgentCommissionInvoice, self).create(vals)
        return res

        # Code For Smart Button

    def _compute_commission_count(self):
        for record in self:
            journal_total = self.env['account.move'].search_count(
                [('partner_id', '=', record.agent_partner_id.id)])
            record.commission_count = journal_total

    def action_commission_invoice(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'view_mode': 'kanban,tree,form',
            'target': 'current',
            'res_model': 'account.move',
            'domain': ['|', ('partner_id', '=', self.agent_partner_id.id), ],
            'context': "{'create': False}",
            'default_move_type': 'out_invoice',
        }

    # End Code For Smart Button


class AgentCommissionInvoiceLine(models.Model):
    _name = 'agent.commission.invoice.line'

    invoice_id = fields.Many2one('agent.commission.invoice', string='Invoice')
    # tour_package_id = fields.Many2one('tour.package', string='Tour')
    tour_booking_id = fields.Many2one('tour.booking', string='Tour Booking')
    name = fields.Char(string='Description')
    tour_cost = fields.Float(string='Tour Cost')
    customer_partner_id = fields.Many2one('res.partner', string='Customer Name')
    commission_type = fields.Selection([
        ('type1', 'Commission Percentage'),
        ('type2', 'Commission Amount'),
    ], string='Commission Type')
    commission_amount = fields.Float(string='Commission Amount')
    commission_percentage = fields.Float('Commission Percentage', digits=(5, 2))
    total_tour_cost = fields.Float(string='Tour Cost', compute='_compute_total_tour_cost')

    @api.depends('commission_type', 'commission_percentage', 'commission_amount')
    def _compute_total_tour_cost(self):
        self.total_tour_cost = 0
        for tour in self:
            if tour.commission_type == 'type1':
                commission_total = tour.commission_percentage * tour.commission_amount / 100
                tour.total_tour_cost = commission_total
            elif tour.commission_type == 'type2':
                commission_total_am = tour.commission_amount
                tour.total_tour_cost = commission_total_am + tour.tour_cost
