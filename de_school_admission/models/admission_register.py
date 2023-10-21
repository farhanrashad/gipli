# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, SUPERUSER_ID, _

from odoo import exceptions

class AdmissionRegister(models.Model):
    _name = "oe.admission.register"
    _description = "Admission Register"
    _order = "name asc"

    READONLY_STATES = {
        'progress': [('readonly', True)],
        'close': [('readonly', True)],
        'cancel': [('readonly', True)],
    }


    active = fields.Boolean(default=True)
    name = fields.Char(string='Name', required=True, index='trigram', translate=True,  states=READONLY_STATES,)
    school_year_id = fields.Many2one('oe.school.year',string='Academic Year',  
                        required=True, readonly=False, store=True, 
                        default=lambda self: self.env['oe.school.year'].search([('active','=',True)], limit=1),
                        compute='_compute_year', states=READONLY_STATES,)
    date_start = fields.Date(string='Start Date',  compute='_compute_all_dates', store=True, readonly=False, required=True, states=READONLY_STATES,)
    date_end = fields.Date(string='End Date',  compute='_compute_all_dates', store=True, readonly=False, required=True, states=READONLY_STATES,)
    max_students = fields.Integer(string='Maximum Admissions', store=True, states=READONLY_STATES,
                                        help='Expected number of students for this course after new admission.')
    min_students = fields.Integer(string="Minimum Admission", store=True,  states=READONLY_STATES,
                                  help='Number of minimum students expected for this course.')
    no_of_applicants = fields.Integer(string='Total Applicants', help='Number of new applications you expect to enroll.', compute='_compute_all_admission')
    no_of_enrolled = fields.Integer(string='Total Enrolled', help='Number of new admission you expect to enroll.', compute='_compute_all_admission')
        
    description = fields.Html(string='Description')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    
    course_id = fields.Many2one('oe.school.course', string='Course', required=True, readonly=False, states=READONLY_STATES,)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('progress', 'Open'),
        ('close', 'Closed'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    def _compute_all_admission(self):
        admission_ids = self.env['oe.admission']
        for ar in self:
            admission_ids = self.env['oe.admission'].search([('admission_register_id','=',ar.id),('active','=',True)])
            ar.write({
                'no_of_applicants': len(admission_ids), 
                'no_of_enrolled': len(admission_ids.filtered(lambda x:x.stage_id.is_close)),
            })

    def _compute_year(self):
        year_id = self.env['oe.school.year'].search([('active','=',True)],limit=1)
        for record in self:
            record.school_year_id = year_id.id

    @api.onchange('school_year_id')
    def _onchange_school_year(self):
        if self.school_year_id:
            self.date_start = self.school_year_id.date_start
            self.date_end = self.school_year_id.date_end

    @api.depends('school_year_id')
    def _compute_all_dates(self):
        for record in self:
            record.date_start = record.school_year_id.date_start
            record.date_end = record.school_year_id.date_end

    def unlink(self):
        for record in self:
            if record.state != 'draft' and record.no_of_applicants > 0:
                raise exceptions.UserError("You cannot delete a record with applicants when the status is not 'Draft'.")
        return super(YourModel, self).unlink()

    def button_draft(self):
        self.write({'state': 'draft'})
        return {}

    def button_open(self):
        self.write({'state': 'progress'})
        return {}

    def button_close(self):
        self.write({'state': 'close'})
        return {}
        
    def button_cancel(self):
        self.write({'state': 'draft'})
        return {}

    
            
