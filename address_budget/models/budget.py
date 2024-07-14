from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit='account.move.line'
    budget_company_id= fields.Many2one(comodel_name='res.company',string='Company',required=True)
    branch_id= fields.Many2one(comodel_name='address.branch',string='Branch')
    project_id= fields.Many2one(comodel_name='project.project',string='Project')
    franchise_id= fields.Many2one(comodel_name='franchise.type',string='Franchise')
    department_id = fields.Many2one('hr.department', string="Department")
    conconcatenate_cost_code = fields.Char(string='Conconcatenate Cost Code',compute='_calc_conconcatenate_cost_code',store=False)

    @api.depends('budget_company_id','branch_id','project_id','franchise_id','department_id')
    def _calc_conconcatenate_cost_code(self):
        for rec in self:
            st=''
            if rec.budget_company_id and rec.budget_company_id.cost_code:
                st+=rec.budget_company_id.cost_code
            else:
                st+='00'
            if rec.branch_id and rec.branch_id.cost_code:
                st+=rec.branch_id.cost_code
            else:
                st+='00'
            if rec.project_id and rec.project_id.cost_code:
                st+=rec.project_id.cost_code
            else:
                st+='00'
            if rec.department_id and rec.department_id.cost_code:
                st+=rec.department_id.cost_code
            else:
                st+='000'
            if rec.franchise_id and rec.franchise_id.cost_code:
                st+=rec.franchise_id.cost_code
            else:
                st+='0000'
            rec.conconcatenate_cost_code=st





class AddressBranch(models.Model):
    _name='address.branch'
    name = fields.Char(string='Name',required=True)
    code = fields.Char(string='Code',required=True)
    cost_code = fields.Char(string='Cost Code',size=2)
    area = fields.Char(string='Accepted Area')
    company_id= fields.Many2one(comodel_name='res.company',string='Company',required=True, default=lambda self: self.env.company,)
    state= fields.Selection(
        string='Status',
        selection=[('active', 'Active'),
                   ('not_active', 'Not Active'), ],
        required=False, )
class Comapny(models.Model):
    _inherit='res.company'
    cost_code = fields.Char(string='Cost Code',size=2)
class Franchise(models.Model):
    _inherit='franchise.type'
    cost_code = fields.Char(string='Cost Code',size=4)
class Department(models.Model):
    _inherit='hr.department'
    cost_code = fields.Char(string='Cost Code',size=3)
class Project(models.Model):
    _inherit='project.project'
    cost_code = fields.Char(string='Cost Code',size=2)




