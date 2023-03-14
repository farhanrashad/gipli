from odoo import models, fields, api, _


class AllShiftRequest(models.Model):
    _name = 'all.shift.request'
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
        ('approved', 'Approved'), ('reject', 'Reject')
    ], string='Status', default='new', required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.company)

    @api.model
    def create(self, vals):
        if vals.get('number', _('New')) == _('New'):
            vals['number'] = self.env['ir.sequence'].next_by_code(
                'shift.request') or _('New')
        res = super(AllShiftRequest, self).create(vals)
        return res

