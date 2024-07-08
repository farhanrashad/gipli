from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError

class HostelRoomAssign(models.Model):
    _name = 'oe.hostel.room.assign'
    _description = 'Hostel Room Assignment'
    _order = 'date_order desc, id desc'
    _check_company_auto = True

    @api.model
    def _default_domain_partner_ids(self):
        teacher_ids = self.env['hr.employee'].search([('is_teacher', '=', True)])
        student_ids = self.env['res.partner'].search([('is_student', '=', True)]).ids
        return teacher_ids.mapped('user_id.partner_id.id') + teacher_ids.mapped('address_id.id') + student_ids

    
    name = fields.Char(
        string="Order Reference",
        required=True, copy=False, readonly=False,
        index='trigram',
        default=lambda self: _('New'))
    date_order = fields.Datetime(
        string="Assignment Date",
        required=True, copy=False,
        default=fields.Datetime.now)
    date_start = fields.Date(string='Start Date', required=True, default=fields.Datetime.now)
    date_end = fields.Date(string='End Date', compute='_compute_end_date', store=True)
    
    duration = fields.Integer(string='Duration', required=True, default=1)
    
    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True, index=True,
        default=lambda self: self.env.company)
        
    partner_id = fields.Many2one('res.partner', string='Resident', required=True,
                                 domain="[('id','in',domain_partner_ids)]"
                                )
    domain_partner_ids = fields.Many2many('res.partner', 
                                default=lambda self: self._default_domain_partner_ids(),
                                #compute='_compute_partners_domain'
                                         )

    location_id = fields.Many2one('stock.location',string='Dormitory Out', required=True, 
                                  domain = "[('is_hostel','=',True),('unit_usage','=','internal')]",
                                  default=lambda self: self.env.company.hostel_location_id.id
                                 )

    location_dest_id = fields.Many2one('stock.location',string='Dormitory In', required=True, 
                                  domain = "[('is_hostel','=',True),('unit_usage','=','internal')]"
                                 )
    
    product_id = fields.Many2one('product.product', string='Unit', required=True,
                                 domain ="[('is_hostel_unit','=',True)]"
                                )

    product_tracking = fields.Selection(related='product_id.tracking')

    lot_id = fields.Many2one('stock.lot', string='Sub-Unit', required=True,
                                 domain ="[('product_id','=',product_id)]"
                                )
    
    fee = fields.Float(string='Fee')
    deposit = fields.Float(string='Deposit')
    note = fields.Text(string='Note')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('reserve', 'Reserved'),
        ('assign', 'Assigned'),
        ('cancel', 'Cancelled'),
        ('close', 'Closed'),
    ], string='Status', default='draft', required=True)

    entry_type = fields.Selection([
        ('assign', 'Assigned'),
        ('transfer', 'Transfer Room'),
        ('unassign', 'Unassigned'),
    ], string='Entry Type')

    assign_picking_ids = fields.One2many(
        'stock.picking', 'room_assign_id', 'Room Assignments',
        copy=False,
    )
    assign_move_ids = fields.One2many(
        'stock.move', 'room_assign_id', 'Room Assignments',
        copy=False,
    )
    assign_move_line_ids = fields.One2many(
        'stock.move.line', 'room_assign_id', 'Room Assignments',
        copy=False,
    )

    
    #=== CRUD METHODS ===#

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'company_id' in vals:
                self = self.with_company(vals['company_id'])
            if vals.get('name', _("New")) == _("New"):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'room.assignment.order') or _("New")

        return super().create(vals_list)

    
    @api.depends('date_start', 'duration')
    def _compute_end_date(self):
        for allocation in self:
            if allocation.date_start and allocation.duration:
                # Calculate end date based on start date and duration in months
                start_date = fields.Date.from_string(allocation.date_start)
                end_date = start_date + relativedelta(months=allocation.duration)
                allocation.date_end = end_date

    #@api.depends_context('id')
    @api.model
    def _compute_partners_domain(self):
        #raise UserError('helo')
        for record in self:
            teacher_ids = self.env['hr.employee'].search([('is_teacher','=',True)])
            student_ids = self.env['res.partner'].sudo().search([])
            record.write({
                'domain_partner_ids': student_ids.ids
            })
    
    # Actions
    def action_reserve(self):
        self.ensure_one()
        from_location = self.company_id.hostel_location_id

        if not from_location:
            raise UserError(_("Hostel location is not set in the company settings."))

        move_line_ids = self.assign_move_line_ids.filtered(lambda x: x.state != 'cancel')
        if self.lot_id.id in move_line_ids.mapped('lot_id.id'):
            raise UserError(_("Room %s is not available.") % self.lot_id.name)

        move_line_ids = self.assign_move_line_ids.filtered(lambda x: x.state != 'cancel')
        if self.partner_id.id in move_line_ids.mapped('owner_id.id'):
            raise UserError(_("Hostel location is not set in the company settings."))

        
            
        #stock_move = self._create_stock_move(from_location)
        #stock_move_line = self._create_stock_move_line(stock_move, from_location)
        
        picking_id = self.env['stock.picking'].create(self._prepare_picking_values())
        picking_id.sudo().action_confirm()
        for move in picking_id.move_ids:
            self.env['stock.move.line'].create(self._prepare_stock_move_line(move, from_location))

        self.write({'state': 'reserve'})
        

    def _prepare_picking_values(self):
        picking_type_id = self.env.ref('stock.picking_type_internal').id
        location_id = self.company_id.hostel_location_id.id
        location_dest_id = self.location_id.id
        picking_values = {
            'picking_type_id': picking_type_id,
            'location_id': location_id,
            'location_dest_id': location_dest_id,
            'scheduled_date': fields.Datetime.now(),
            'partner_id': self.partner_id.id,
            'state': 'draft',
            'origin': self.name,
            'room_assign_id': self.id,
            'move_ids': [(0, 0, {
                'name': self.name,
                'product_id': self.product_id.id,
                'product_uom': self.product_id.uom_id.id,
                'product_uom_qty': 1.0,
                'location_id': location_id,
                'location_dest_id': location_dest_id,
                'room_assign_id': self.id,
            })],
            # Add more fields as needed
        }
        return picking_values

    def _prepare_stock_move_line(self, move, from_location):
        return {
            'picking_id': move.picking_id.id,
            'move_id': move.id,
            'product_id': move.product_id.id,
            'product_uom_id': move.product_uom.id,
            'quantity': move.product_uom_qty,
            'location_id': from_location.id,
            'location_dest_id': move.location_dest_id.id,
            'lot_id': self.lot_id.id,
            'room_assign_id': self.id,
            'owner_id': self.partner_id.id,
        }

    def action_confirm(self):
        picking_to_confirm = self.assign_picking_ids.filtered(lambda p: p.state not in ('cancel','done'))
        picking_to_confirm.sudo().button_validate()
        self.write({'state': 'assign'})

    def action_draft(self):
        self.assign_move_ids._action_cancel()
        self.write({'state': 'draft'})

    def action_open_all_room_moves(self):
        action = self.env["ir.actions.actions"]._for_xml_id("de_school_hostel.action_dormitory_stock_move_lines")
        action['domain'] = [('room_assign_id', '=', self.id)]
        action['context'] = {
            #'default_room_assign_id': self.id,
            #'default_company_id': (self.company_id or self.env.company).id,
            'create': False,
            'edit': False,
            'delete': False,
        }
        
        return action
    