from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError

class HostelRoomAllocate(models.Model):
    _name = 'oe.hostel.room.allocate'
    _description = 'Hostel Room Allocation'
    _order = 'date_order desc, id desc'
    _check_company_auto = True

    
            
    name = fields.Char(
        string="Order Reference",
        required=True, copy=False, readonly=False,
        index='trigram',
        default=lambda self: _('New'))

    date_order = fields.Datetime(
        string="Allocation Date",
        required=True, copy=False,
        default=fields.Datetime.now)


    date_start = fields.Date(string='Start Date', required=True, default=fields.Datetime.now)
    date_end = fields.Date(string='End Date', compute='_compute_end_date', store=True)
    
    duration = fields.Integer(string='Duration', required=True, default=1)
    
    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True, index=True,
        default=lambda self: self.env.company)

    @api.model
    def _default_domain_partner_ids(self):
        teacher_ids = self.env['hr.employee'].search([('is_teacher', '=', True)])
        student_ids = self.env['res.partner'].search([('is_student', '=', True)]).ids
        return teacher_ids.mapped('user_id.partner_id.id') + teacher_ids.mapped('address_id.id') + student_ids
        
    partner_id = fields.Many2one('res.partner', string='Resident', required=True,
                                 domain="[('id','in',domain_partner_ids)]"
                                )
    domain_partner_ids = fields.Many2many('res.partner', 
                                default=lambda self: self._default_domain_partner_ids(),
                                #compute='_compute_partners_domain'
                                         )
    building_id = fields.Many2one('oe.hostel.unit', string='Building', required=True,
                                  domain="[('unit_type','=','building')]"
                                 )
    room_id = fields.Many2one('oe.hostel.unit', string='Room', required=True,
                              domain="[('unit_id','child_of',building_id),('unit_type','=','room')]"
                             )
    
    fee = fields.Float(string='Fee')
    deposit = fields.Float(string='Deposit')
    note = fields.Text(string='Note')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('reserve', 'Reserved'),
        ('allocate', 'Allocated'),
        ('cancel', 'Cancelled'),
        ('close', 'Closed'),
    ], string='Status', default='draft', required=True)

    #=== CRUD METHODS ===#

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'company_id' in vals:
                self = self.with_company(vals['company_id'])
            if vals.get('name', _("New")) == _("New"):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'room.allocation.order') or _("New")

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
        self.write({
            'state': 'reserve'
        })
    def action_confirm(self):
        self.write({
            'state': 'allocate'
        })
    