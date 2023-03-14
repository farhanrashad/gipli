from odoo import models, fields, api, _


class ShiftRequest(models.Model):
    _name = 'shift.request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']
    _rec_name = 'employee_id'
    _description = 'Shift Request'

    number = fields.Char(string='Number', required=True,
                         readonly=True, default=lambda self: _('New'))
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    shift_responsible_id = fields.Many2one('hr.employee', string='Shift Responsible')
    employee_manger_id = fields.Many2one('hr.employee', string='Employee Manager')
    department_id = fields.Many2one('hr.department', string='Department', required=True)
    start_date = fields.Datetime(string='Start Date', required=True)
    end_date = fields.Datetime(string='End Date', required=True)
    description = fields.Text(string='Description')
    internal_note = fields.Text(string='Internal Notes')
    shift_type_id = fields.Many2one('shipt.type', string='Shift Type')
    status = fields.Selection([
        ('new', 'New'),
        ('confirm', 'Confirm'),
        ('approved', 'Approved'), ('cancel', 'Cancel')
    ], string='Status', default='new', required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.company)
    confirm_req = fields.Boolean(default=False)

    @api.model
    def create(self, vals):
        if vals.get('number', _('New')) == _('New'):
            vals['number'] = self.env['ir.sequence'].next_by_code(
                'shift.request') or _('New')
        res = super(ShiftRequest, self).create(vals)
        if res:
            self.env['all.shift.request'].create({
                'number': res.number,
                'employee_id': res.employee_id.id,
                'employee_manger_id': res.employee_manger_id.id,
                'shift_responsible_id': res.shift_responsible_id.id,
                'department_id': res.department_id.id,
                'start_date': res.start_date,
                'end_date': res.end_date,
                'description': res.description,
                'internal_note': res.internal_note,
                'shift_type_id': res.shift_type_id.id,
                'status': res.status,
                'company_id': res.company_id.id,
            })
        return res

    def action_confirm(self):
        self.write({'status': 'confirm'})
        self.confirm_req = True
        request_approve = self.env['shift.request.approve'].search([])
        all_shift_request = self.env['all.shift.request'].search([])
        for rec in self:
            values = {
                'number': rec.number,
                'employee_id': rec.employee_id.id,
                'employee_manger_id': rec.employee_manger_id.id,
                'shift_responsible_id': rec.shift_responsible_id.id,
                'department_id': rec.department_id.id,
                'start_date': rec.start_date,
                'end_date': rec.end_date,
                'description': rec.description,
                'internal_note': rec.internal_note,
                'shift_type_id': rec.shift_type_id.id,
                'status': rec.status,
                'company_id': rec.company_id.id,
            }
            request_approve.create(values)
            all_shift_request.create(values)

    def action_cancel(self):
        self.confirm_req = True
        self.write({'status': 'cancel'})
        all_shift_request = self.env['all.shift.request'].search([])
        for rec in self:
            values = {
                'number': rec.number,
                'employee_id': rec.employee_id.id,
                'employee_manger_id': rec.employee_manger_id.id,
                'shift_responsible_id': rec.shift_responsible_id.id,
                'department_id': rec.department_id.id,
                'start_date': rec.start_date,
                'end_date': rec.end_date,
                'description': rec.description,
                'internal_note': rec.internal_note,
                'shift_type_id': rec.shift_type_id.id,
                'status': rec.status,
                'company_id': rec.company_id.id,
            }
            all_shift_request.create(values)
