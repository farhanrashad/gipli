from odoo import models, fields, api,_


class deHrShift(models.Model):
    _name = 'shift.management'
    _description = 'de_hr_shift.de_hr_shift'
    
    
    shift_manage_id=  fields.Char(
        string="Shift",
        required=True, copy=False, readonly=True,
        index='trigram',
       
        default=lambda self: _('New'))

    name = fields.Char(string="Shift")
    
    state =  fields.Selection(
        selection=[
            ('draft', "Quotation"),
            ('submit', "Submitted"),
            ('approve', "Approved"),
            ('reject', "Rejected"),
       
        ],
        string="Status",
        readonly=True, copy=False, index=True,
        
        default='draft')
    employee_id = fields.Many2one('hr.employee', string="Employee")
    department_id = fields.Many2one('hr.department', string= "Department")
    shift_type = fields.Many2one('resource.calendar', string= "Shift Type")
    manager_id =fields.Many2one('hr.employee', string= "Manager")
    start_date = fields.Date(string ="Start Date")
    end_date = fields.Date(string ="End Date")
    company_id = fields.Many2one("res.company", string="Company")
    description= fields.Text(string="Description")
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('shift_manage_id', _('New')) == _('New'):
                vals['shift_manage_id'] = self.env['ir.sequence'].next_by_code('shift.management') or _('New')
        res = super(deHrShift, self).create(vals_list)
        return res



    
    

    
#
class deEmpShift(models.Model):
    _inherit = 'hr.employee'
    
    
    related_shift_count = fields.Integer('Number of related shifts', compute='_compute_related_shift_count')
    
    def _compute_related_shift_count(self):
        for employee in self:
            employee.related_shift_count = len(self.env['shift.management'].search([('employee_id','=', employee.id)]))
            
            
        
    
    
    def action_related_shifts(self):
        self.ensure_one()
        shift_rec = self.env['shift.management'].search([('employee_id','=', self.id)])
        if shift_rec:
            domain = [('id', 'in', shift_rec.ids)]
        else:
            domain = [()]    
        return {
            'name': _("Related Shifts"),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'shift.management',
             'domain': domain
        }
    
        
    
class deEmpWorkingTime(models.Model):
    _inherit = 'resource.calendar'
    
    
    related_emp_count = fields.Integer('Number of related employees', compute='_compute_related_emp_count')
    
    def _compute_related_emp_count(self):
        for rec in self:
            working_rec = self.env['shift.management'].search([('shift_type','=',rec.id)])
            if working_rec:
                working_emp_rec= working_rec.mapped('employee_id')
                rec.related_emp_count = len(working_emp_rec)
            else:
                rec.related_emp_count=0
        
    
    
    def action_related_emp(self):
        self.ensure_one()
        working_rec = self.env['shift.management'].search([('shift_type','=',self.id)])
        # shift_rec = self.env['shift.management'].search([('employee_id','=', self.id)])
        if working_rec:
            working_emp_rec= working_rec.mapped('employee_id')
            
            domain = [('id', 'in', working_emp_rec.ids)]
        else:
            domain = [()]    
        return {
            'name': _("Related Employee"),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'hr.employee',
            'domain': domain
        }
        
    
    
    