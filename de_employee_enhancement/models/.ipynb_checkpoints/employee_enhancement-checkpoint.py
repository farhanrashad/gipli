# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from werkzeug.urls import url_encode

from odoo.exceptions import UserError

class HrJob(models.Model):
    _inherit = 'hr.job'

class HrRecruitmentSource(models.Model):
    _inherit = 'hr.recruitment.source'

class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"
    
    @api.depends('department_id')
    def _compute_parent_id(self):
        for employee in self.filtered('department_id.manager_id'):
            employee.parent_id = employee.parent_id



class ResCompany(models.Model):
    _inherit = 'res.company'

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if name:
            # Be sure name_search is symetric to name_get
            name = name.split(' / ')[-1]
            args = ['|','|', ('name',operator, name),('segment1', operator , name),('ora_code', operator , name)] + args
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)



class EmployeeEnhancement(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if name:
            # Be sure name_search is symetric to name_get
            name = name.split(' / ')[-1]
            args = ['|', ('name',operator, name),('emp_number', operator , name)] + args
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)


    emp_number = fields.Char('Employee Number', required=True)
    dept_manager_id = fields.Many2one('hr.employee', string='Dept Manager')
    emp_status = fields.Char('Employee Status')
    emp_type = fields.Selection([
        ('permanent', 'Regular'),
        ('contractor', 'Contractual'),
        ('freelancer', 'Freelancer'),
        ('inter', 'Intern'),
        ('part_time', 'Part Time'),
        ('project_based', 'Project Based Hiring'),
        ('outsource', 'Outsource'),
        ], string='Employee Type', index=True, copy=False, default='permanent', track_visibility='onchange', required=True)
    section = fields.Char('Section')
    father_name = fields.Char("Father's Name", required=False)
    grade_type = fields.Many2one('grade.type', required=True)
    grade_designation = fields.Many2one('grade.designation', required=True)
    date = fields.Date('Date of Joining', required=True)
    probation_period = fields.Selection([
        ('1', '1 Month'),
        ('2', '2 Months'),
        ('3', '3 Months'),
        ('4', '4 Months'),
        ('5', '5 Months'),
        ('6', '6 Months'),
        ('9', '9 Months'),
        ('12', '12 Months'),
        ], string='Probation Period', index=True, copy=False, default='1', track_visibility='onchange')

    confirm_date = fields.Date('Confirmation Date', compute='compute_confirmation_date')
    contract_expiry = fields.Date("Contract Expiry", compute='compute_contract_date')# Need To confirm
    cnic = fields.Char('CNIC', size=13)

    def compute_contract_date(self):
        for record in self:
            rec = self.env['hr.contract'].search([('employee_id', '=', record.id), ('state', '=', 'open')])
            record.contract_expiry = rec.date_end

    employee_number = fields.Char(string="Auto Employee Number", required=True, copy=False, readonly=True, index=True,
                          default=lambda self: _('New'))
    
    permanent_address = fields.Char(string='Permanent Address')
    
    def action_auto_employee_number_sequence(self):
        exist_sequence=self.env['ir.sequence'].sudo().search([('code','=','hr.employee.sequence'),('company_id','=',self.company_id.id)], limit=1)
        if not exist_sequence:
            seq_vals = {
                'name': 'Employee Number Sequence',
                'code': 'hr.employee.sequence',
                'implementation': 'standard',
                'number_next_actual': 1,
                'prefix': '',
            }
            exist_sequence= self.env['ir.sequence'].sudo().create(seq_vals) 
        self.employee_number = self.env['ir.sequence'].sudo().next_by_code('hr.employee.sequence') or _('New')
    
    
    @api.model
    def create(self, vals):
        if vals.get('user_id'):
            user = self.env['res.users'].browse(vals['user_id'])
            vals.update(self._sync_user(user, vals.get('image_1920') == self._default_image()))
            vals['name'] = vals.get('name', user.name)
        employee = super(EmployeeEnhancement, self).create(vals)
        url = '/web#%s' % url_encode({
            'action': 'hr.plan_wizard_action',
            'active_id': employee.id,
            'active_model': 'hr.employee',
            'menu_id': self.env.ref('hr.menu_hr_root').id,
        })
        employee._message_log(body=_('<b>Congratulations!</b> May I recommend you to setup an <a href="%s">onboarding plan?</a>') % (url))
        if employee.department_id:
            self.env['mail.channel'].sudo().search([
                ('subscription_department_ids', 'in', employee.department_id.id)
            ])._subscribe_users()
        #employee.action_auto_employee_number_sequence()    
        return employee

    @api.onchange('name','emp_type')
    def onchange_name(self):
        for line in self:
            line.action_auto_employee_number_sequence()  

            #if line.emp_type=='permanent':
            #    self.emp_number= self.employee_number
            #if  line.emp_type!='permanent' and line.company_id.id not in (2,8,5):
            #    self.emp_number= 'C-'+self.employee_number
            #if  line.emp_type!='permanent' and line.company_id.id==2:
            #    self.emp_number= 'O'+self.employee_number
            #if  line.emp_type!='permanent' and line.company_id.id==8:
            #    self.emp_number= 'DTI-'+self.employee_number
            #if  line.emp_type!='permanent' and line.company_id.id==5:
            #    self.emp_number= 'IN'+self.employee_number    

    @api.constrains('emp_number','cnic')
    def _check_emp_number(self):
    	if self.emp_number:
            number_exist = self.env['hr.employee'].search([('emp_number','=',self.emp_number),('cnic','!=',self.cnic)])
            if number_exist:
                raise UserError('Not Allow to Enter Duplicate Employee Number! Please change Employee Number.')    

    @api.constrains('probation_period','emp_type')
    def _check_probation_period(self):
        for line in self:
            if line.emp_type != 'permanent' and line.probation_period:
                raise UserError(_('Probation Only Allow for Regular Employee!'))
                    
                    
    @api.constrains('pf_member','emp_type','probation_period')
    def _check_pf_member(self):
        for line in self:
            date = fields.date.today()
            if line.date:
                prob_date = line.probation_period
                date = line.date + relativedelta(months=int(prob_date))
            if line.pf_member in ('yes_with','yes_without') and line.emp_type=='permanent' and date > fields.date.today():
                raise UserError(_('PFUND Only Allow for Confirm Employee!'))
            if line.pf_member in ('yes_with','yes_with') and line.emp_type!='permanent':
                raise UserError(_('PFUND Only Allow for Regular Employee!'))     
              
     
    @api.constrains('emp_type','birthday')
    def _check_employee_type(self):
        for line in self:
            if line.emp_type and line.birthday: 
                service_period = (fields.date.today() - line.birthday).days
                if service_period > 21915 and line.emp_type=='permanent':
                    raise UserError(_('Regular Employee Type Only allow for Age less than 60 year!')) 
    
    @api.constrains('eobi_member', 'birthday')
    def _check_eobi_member(self):
        for line in self:
            if line.eobi_member=='yes' and line.birthday:
                service_period = (fields.date.today() - line.birthday).days
                if service_period > 21915:
                    raise UserError(_('EOBI Only Allow for Employee Age less than 60 year!'))  
                 

    
    @api.constrains('cnic','emp_number')
    def _check_cnic(self):
        if self.cnic:
            cnic_exist = self.env['hr.employee'].search([('cnic','=',self.cnic),('emp_number','!=',self.emp_number),('resigned_date','=',False)])
            if cnic_exist:
                raise UserError(_('Not Allow to Enter Duplicate CNIC! Please change CNIC Number.'))   
            if len(self.cnic) < 13:
                raise UserError(('CNIC No is invalid'))
            if not self.cnic.isdigit():
                raise UserError(('CNIC No is invalid'))

                
    blood_group = fields.Selection([
        ('a+', 'A+'),
        ('a-', 'A-'),
        ('b+', 'B+'),
        ('b-', 'B-'),
        ('o+', 'O+'),
        ('o-', 'O-'),
        ('ab+', 'AB+'),
        ('ab-', 'AB-'),
        ], string='Blood Group', index=True, copy=False, default='a+', track_visibility='onchange')
    fac_deduction = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
        ], string='FAC Deduction Applicable', index=True, copy=False, default='no', track_visibility='onchange')
    fac_deduction_percentage = fields.Float('FAC Deduction Percentage(%)')
    is_consultant = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
        ], string='Is Consultant', index=True, copy=False, default='no', track_visibility='onchange')
    tax_rate = fields.Float('Consultant Tax Rate')
    resigned_date = fields.Date("Resigned Date")
    resign_type = fields.Char("Resign Type")
    resigned_remarks = fields.Char("Resigned Remarks")
    resign_reason = fields.Char("Resign Reason")
    religion = fields.Selection([
        ('islam', 'Islam'),
        ('christianity', 'Christianity'),
        ('judism', 'Judism'),
        ('buddhism', 'Buddhism'),
        ('hindu', 'Hinduism'),
        ('other', 'Other'),
        ], string='Religion', index=True, copy=False, default='islam', track_visibility='onchange')
    ntn = fields.Char("NTN", size=8)
    temporary_address = fields.Char('Temporary Address')
    pf_member = fields.Selection([
        ('no', 'No'),
        ('yes_with', 'Yes with Interest'),
        ('yes_without', 'Yes w/o Interest'),
        ], string='PF Member', index=True, copy=False, default='no', track_visibility='onchange')
    pf_trust = fields.Char('PF Trust')
    pf_effec_date = fields.Date('PF Effective Date')
    ss_entitled = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
        ], string='SS Entitled', index=True, copy=False, default='yes', track_visibility='onchange')
    ss_number = fields.Char('SS Number')
    union_fund = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
        ], string='Union Fund Entitled', index=True, copy=False, default='yes', track_visibility='onchange')
    eobi_member = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
        ], string='EOBI member', index=True, copy=False, default='yes', track_visibility='onchange')
    union_fund_amount = fields.Float('Union Fund Amount')
    ot_allowed = fields.Boolean('OT Allowed')
    gratuity = fields.Boolean('Has Gratuity')
    stop_salary = fields.Boolean('Stop Salary')
    eobi_number = fields.Char('EOBI Number')
    eobi_registration_date = fields.Date('EOBI Registration Date')
    wps = fields.Char('WPS')
    ipl_variable = fields.Char('IPL Variable Cost')
    # cost_center_information_line = fields.One2many('cost.information.line', 'employee_id')
    reason_to_leave = fields.Char('Reason To Leave')
    salary = fields.Float('Salary')
    # FIXME: ###############################
    institute = fields.Char('Institute')
    project_lines = fields.One2many('employee.project.line', 'employee_id')
    benefit_lines = fields.One2many('employee.benefit.line', 'employee_id')
    asset_lines = fields.One2many('employee.asset.line', 'employee_id')

    def compute_confirmation_date(self):
        for date_rec in self:
            if date_rec.date:
                prob_date = date_rec.probation_period
                date = date_rec.date + relativedelta(months=int(prob_date))
            else:
                date = ''
            date_rec.confirm_date = date




class EmployeeAssets(models.Model):
    _name = 'employee.asset'

    name = fields.Char('Asset Name')
    life_span = fields.Char('Life Span')
    value = fields.Float('Value')
    code = fields.Char('Asset Code')


class EmployeeAssetsLine(models.Model):
    _name = 'employee.asset.line'

    employee_id = fields.Many2one('hr.employee')
    asset_id = fields.Many2one('employee.asset')
    issue_date = fields.Date('Issue Date')
    description = fields.Text('Description')
    estimated_life_span = fields.Char('Estimated Life Span', related='asset_id.life_span')
    recovery_date = fields.Date('Recovery Date')


class EmployeeProjectLine(models.Model):
    _name = 'employee.project.line'

    employee_id = fields.Many2one('hr.employee')
    name = fields.Char('Project')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    location = fields.Char('Location')
    period = fields.Char('Period', compute='compute_period')  # compute period

    def compute_period(self):
        if self.start_date and self.end_date:
            # date = self.end_date - self.start_date
            rdelta = relativedelta(self.end_date, self.start_date)

        # date = date.strftime("%d/%m/%Y")

            if rdelta.days > 0 and rdelta.months > 0:
                result = str(rdelta.months) + " Months " + str(rdelta.days) + " Days"
            elif rdelta.days == 0:
                result = str(rdelta.months) + " Months"
            elif rdelta.months == 0:
                result = str(rdelta.days) + " Days"
        else:
            result = ''
        self.period = result

class EmployeeBenefitLine(models.Model):
    _name = 'employee.benefit.line'

    employee_id = fields.Many2one('hr.employee')
    name = fields.Char('Description')
    start_date = fields.Date('Start Date')
    benefit_remarks = fields.Char('Remarks')
    benefit_amount = fields.Integer('Amount')
    benefit_description = fields.Selection([
        ('car', 'Car'),
        ('fleet', 'Fleet Card'),
        ('mobile', 'Mobile'),
        ], string='Benefit', index=True, copy=False, default='car', track_visibility='onchange')


class GradeType(models.Model):
    _name = 'grade.type'

    name = fields.Char('Grade Type')


class GradeDesignation(models.Model):
    _name = 'grade.designation'

    name = fields.Char('Grade Designation')
    company_id = fields.Many2one('res.company', string='Company')



class CostCenterInformations(models.Model):
    _inherit = 'hr.contract'
    
    expense_account = fields.Selection([
        ('1', 'Operating Expenses'),
        ('2', 'Factory Overheads'),
        ('3', 'Marketing Expenses'),
        ], string='Expense Head', index=True, copy=False, default='1', track_visibility='onchange')
    cost_center_information_line = fields.One2many('cost.information.line','contract_id',string='Cost Center Lines')
    total_percentage = fields.Float('Total Percentage', compute = 'limit_total_percentage')


#     @api.constrains('total_percentage')
    def limit_total_percentage(self):
        for rec in self:
            count = 0
            for line in rec. cost_center_information_line:
                count = count + line.percentage_charged
            rec.total_percentage = count

#    @api.model
#    def create(self,vals):
#        res = super(CostCenterInformations, self).create(vals)
#        if self.cost_center_information_line.cost_center:
#        	if res.total_percentage != 100:
#        		raise UserError('Total Percentage must be equal 100')
#        return res
    
#    def write(self, vals):
#        res = super(CostCenterInformations, self).write(vals)
#        if self.cost_center_information_line.cost_center:
#        	if self.total_percentage != 100:
#        		raise UserError('Total Percentage must be equal 100')
#        return res


class CostCenterInformation(models.Model):
    _name = 'cost.information.line'

    contract_id = fields.Many2one('hr.contract')
    employee_id = fields.Many2one('hr.employee')
    cost_center = fields.Many2one('account.analytic.account')
    percentage_charged = fields.Float('Percentage Charged')

    @api.onchange('percentage_charged')
    def limit_percentage_charged(self):
        if self.percentage_charged:
            for rec in self:
                if rec.percentage_charged > 100 or rec.percentage_charged <1:
                    raise UserError('Percentage Charged Cannot be greater than 100 or less than 1')