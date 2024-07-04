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


    date_start = fields.Date(string='Start Date', required=True)
    date_end = fields.Date(string='End Date', compute='_compute_end_date', store=True)
    
    duration = fields.Integer(string='Duration', required=True, default=1)
    
    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True, index=True,
        default=lambda self: self.env.company)
    
    partner_id = fields.Many2one('res.partner', string='Resident', required=True,
                                 domain="[('id','in',domain_partners)]"
                                )
    domain_partners = fields.Many2many('res.partner', compute='_compute_partners_domain')
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

    @api.depends('date_start', 'duration')
    def _compute_end_date(self):
        for allocation in self:
            if allocation.date_start and allocation.duration:
                # Calculate end date based on start date and duration in months
                start_date = fields.Date.from_string(allocation.date_start)
                end_date = start_date + relativedelta(months=allocation.duration)
                allocation.date_end = end_date

    def _compute_partners_domain(self):
        for record in self:
            teacher_ids = self.env['hr.employee'].search([('is_teacher','=',True)])
            student_ids = self.env['res.partner'].sudo().search([('is_student','=',True)])
            record.domain_partners = 1
            raise UserError('hello')
            
    