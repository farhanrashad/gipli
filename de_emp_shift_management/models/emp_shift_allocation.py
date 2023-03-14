from odoo import models, fields, api,_

class EmployeeShiftAllocation(models.Model):
    _name = "employee.shift.alloc"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    
    
    name = fields.Char(
        string="Employee Shift Allocation",
        required=True, copy=False, readonly=True,
       
        # states={'draft': [('readonly', False)]},
        default=lambda self: _('New'))
     
     
    shift_id = fields.Many2one("emp.shift", string = "Shift")
    shift_type_id = fields.Many2one("shift.type", string = "Shift type")
    employee_id = fields.Many2one("hr.employee", string = "Employee" ,tracking=True)
    company_id = fields.Many2one("res.company", string = "company")
    date_from = fields.Date(string = "Date from")
    date_to = fields.Date(string = "Date to") 
    state =  fields.Selection(
        selection=[
            ('draft', "Draft"),
            ('done', "Done"),
            ('cancel', "Cancelled"),
            
       ],
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=True,
        default='draft')
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('employee.shift.alloc') or _('New')
        res = super(EmployeeShiftAllocation, self).create(vals_list)
        return res

    
    