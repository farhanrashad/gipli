# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource
from ast import literal_eval


class LoanType(models.Model):
    _name = 'hr.loan.type'
    _description = 'Loan Category'
    _order = 'sequence, id'

    _check_company_auto = True

    def _get_default_image(self):
        default_image_path = get_module_resource('de_hr_loan', 'static/src/img', 'loan.svg')
        return base64.b64encode(open(default_image_path, 'rb').read())

    name = fields.Char(string="Name", translate=True, required=True)
    color = fields.Integer('Color')
    company_id = fields.Many2one(
        'res.company', 'Company', copy=False,
        required=True, index=True, default=lambda s: s.env.company)
    currency_id = fields.Many2one(related='company_id.currency_id')
    active = fields.Boolean(default=True)
    sequence = fields.Integer(string="Sequence")
    description = fields.Char(string="Description", translate=True, required=True)
    image = fields.Binary(string='Image', default=_get_default_image)
    sequence_code = fields.Char(string="Code", required=True )
    sequence_id = fields.Many2one('ir.sequence', 'Reference Sequence',
        copy=False, check_company=True)

    repayment_model_id = fields.Many2one('ir.model', readonly=False, string="Repayment Mode",  
                ondelete='cascade', required=True, domain=lambda self: self._compute_model_domain(),
                help="Repayment mode defines the default method employees will use to repay their loans."
    )
    repayment_model = fields.Char(related='repayment_model_id.model')
    prepayment_credit_memo = fields.Boolean(string='Is Prepayment')
    
    payment_product_id = fields.Many2one('product.product', string="Product", required=True, domain="[('type','=','service')]")

    request_to_validate_count = fields.Integer("Number of requests to validate", compute="_compute_request_to_validate_count")

    # Loan Rules
    calculation_type = fields.Selection([
        ('fix', 'Fixed'),
        ('percent', 'Percentage'),
    ], string='Calculation Type', required=True, default='fix')

    fixed_amount = fields.Float(string="Fixed Amount")
    calculation_field_id = fields.Many2one(
        'ir.model.fields',
        string='Calculation Field',
        domain=[
            ('model', 'in', ['hr.contract']),
            ('ttype', 'in', ['float', 'monetary']),
        ],
        ondelete='cascade',
    )
    amount_per = fields.Float(string="Percentage (%)")
    
    loan_frequency = fields.Selection(
        [
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
            ('semi_annual', 'Semi-Annually'),
            ('annual', 'Annually'),
            ('custom', 'Custom')
        ],
        string="Frequency", required=True, default='no_limit',
        help="Loan frequency determines how often an employee can apply for the next loan."
    )
    loan_frequency_interval = fields.Integer(string='Interval', required=True, default=1)

    interval_loan_mode = fields.Selection([
        ('fix', 'Fixed'),
        ('max', 'Maximum'),
    ], string='Interval Mode', required=True, default='fix',
        help="Loan interval specifies the number of months within which an employee must repay the loan, with options for a maximum limit or a fixed number of intervals."
    )
    interval_loan = fields.Integer(string='Interval', required=True, default=1)
    
    # Compute all counts
    count_loan_pending = fields.Integer(compute='_compute_loan_count')
    count_loan_confirm = fields.Integer(compute='_compute_loan_count')
    count_loan_to_pay = fields.Integer(compute='_compute_loan_count')
    
    

    loan_type_document_ids = fields.One2many('hr.loan.type.document', 'loan_type_id', string='Documents')

    @api.constrains('amount_per')
    def _check_percentage_value(self):
        for record in self:
            if record.calculation_type == 'percent' and (record.amount_per < 1 or record.amount_per > 100):
                raise ValidationError("Percentage value must be between 1 and 100.")

    @api.model
    def _compute_model_domain(self):
        allowed_model_ids = self.env['ir.model'].search([('model', 'in', ['hr.payslip', 'account.move'])]).ids
        return [('id', 'in', allowed_model_ids)]


    def _compute_request_to_validate_count(self):
        domain = [('state', '=', 'confirm')]
        requests_data = self.env['hr.loan']._read_group(domain, ['loan_type_id'], ['loan_type_id'])
        requests_mapped_data = dict((data['loan_type_id'][0], data['loan_type_id_count']) for data in requests_data)
        for type in self:
            type.request_to_validate_count = requests_mapped_data.get(type.id, 0)

    def _compute_loan_count(self):
        domains = {
            'count_loan_pending': [('state', 'in', ['partial','validate'])],
            'count_loan_confirm': [('state', 'in', ['confirm'])],
        }
        for type in self:
            loan_ids = self.env['hr.loan'].search([('state', 'not in', ('done', 'cancel')), ('loan_type_id', '=', type.id)])
            type.count_loan_pending = len(loan_ids.filtered(lambda x:x.state in ('validate','partial')))
            type.count_loan_confirm = len(loan_ids.filtered(lambda x:x.state in ('confirm')))
            type.count_loan_to_pay = len(loan_ids.filtered(lambda x:x.state in ('post')))
        #for field in domains:
        #    data = self.env['hr.loan']._read_group(domains[field] +
        #        [('state', 'not in', ('done', 'cancel')), ('loan_type_id', 'in', self.ids)],
        #        ['loan_type_id'], ['loan_type_id'])
        #    count = {
        #        x['loan_type_id'][0]: x['loan_type_id_count']
        #        for x in data if x['loan_type_id']
        #    }
        #    for record in self:
        #        record[field] = count.get(record.id, 0)

                
    # --------------------------------------------
    # -------------- Operations ------------------
    # --------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('sequence_code'):
                sequence = self.env['ir.sequence'].create({
                    'name': _('Sequence') + ' ' + vals['sequence_code'],
                    'padding': 5,
                    'prefix': vals['sequence_code'],
                    'company_id': vals.get('company_id'),
                })
                vals['sequence_id'] = sequence.id
        res = super().create(vals_list)
        res._check_payroll()
        return res

    def write(self, vals):
        if 'sequence_code' in vals:
            for loan_type in self:
                sequence_vals = {
                    'name': _('Sequence') + ' ' + vals['sequence_code'],
                    'padding': 5,
                    'prefix': vals['sequence_code'],
                }
                if loan_type.sequence_id:
                    loan_type.sequence_id.write(sequence_vals)
                else:
                    sequence_vals['company_id'] = vals.get('company_id', loan_type.company_id.id)
                    sequence = self.env['ir.sequence'].create(sequence_vals)
                    loan_type.sequence_id = sequence
        if 'company_id' in vals:
            for loan_type in self:
                if loan_type.sequence_id:
                    loan_type.sequence_id.company_id = vals.get('company_id')
        return super().write(vals)

    def _check_payroll(self):
        # Check if the field 'x_payslip_id' already exists in hr.loan.type model
        payslip_field_exits_in_loan_line = self.env['ir.model.fields'].search([
            ('model_id.model', '=', 'hr.loan.line'),
            ('name', '=', 'x_payslip_id')
        ], limit=1)

        loanline_field_exits_in_payslip = self.env['ir.model.fields'].search([
            ('model_id.model', '=', 'hr.payslip'),
            ('name', '=', 'x_loan_lines')
        ], limit=1)

        hr_loan_line_model = self.env['ir.model'].search([('model', '=', 'hr.loan.line')])
        hr_payslip_model = self.env['ir.model'].search([('model', '=', 'hr.payslip')])

        # compute 
        compute_method = '''
for record in self:
    # Compute the related loan lines based on x_payslip_id
    try:
        loan_lines = self.env['hr.loan.line'].search([('employee_id', '=', record.employee_id.id),('date', '>=', record.date_from),('date', '<=', record.date_to),('state', 'in', ['draft','pending']),('loan_id.repayment_model', '=', 'hr.payslip')])
        record['x_loan_lines'] = loan_lines.filtered(lambda x:x.loan_id.loan_type_id.repayment_model == 'hr.payslip')

    except:
        pass
        '''
        # Create a new record in the hr.salary.rule model
        python_code_for_loan = """
result = employee.compute_loan_from_payslip(payslip.id,'hr.payslip')
        """
        category_id = self.env['hr.salary.rule.category'].search([('code','=','DED')],limit=1)
        struct_id = self.env['hr.payroll.structure'].browse(1)
        rule_exists = self.env['hr.salary.rule'].search([('code', '=', 'LOAN')],limit=1)
        if hr_loan_line_model:
            if not payslip_field_exits_in_loan_line:
                # Create the field 'x_payslip_id' if it doesn't exist
                self.env['ir.model.fields'].create({
                    'name': 'x_payslip_id',
                    'field_description': 'Payslip Reference',
                    'model_id': hr_loan_line_model.id,
                    'ttype': 'many2one',
                    'relation': 'hr.payslip',
                    'store': True,
                    'copied': False,
                    'help': 'Reference to the associated payslip',
                })
            if hr_payslip_model:
                if not loanline_field_exits_in_payslip:
                    hr_payslip_model.write({
                        'field_id': [(0, 0, {
                            'name': 'x_loan_lines',
                            'field_description': 'Loan Lines',
                            'model_id': hr_payslip_model.id,
                            'ttype': 'one2many',
                            'relation': 'hr.loan.line',
                            'relation_field': 'x_payslip_id',
                            'store': True,
                            'copied': False,
                            'depends': 'employee_id,date_from,date_to',
                            'compute': compute_method,
                            'help': 'Reference to associated loan lines',
                        })]
                    })
                if not rule_exists:
                    salary_rule_id = self.env['hr.salary.rule'].create({
                        'name': 'Loan Deduction',
                        'category_id': category_id.id,
                        'code': 'LOAN',
                        'sequence': 1,
                        'struct_id': struct_id.id,
                        'amount_select': 'code',
                        'amount_python_compute': python_code_for_loan,                
                    })
    # ===============================================
    # ================== Actions ====================
    # ===============================================
    def create_request(self):
        self.ensure_one()
        # If category uses sequence, set next sequence as name
        # (if not, set category name as default name).
        return {
            "type": "ir.actions.act_window",
            "res_model": "hr.loan",
            "views": [[False, "form"]],
            "context": {
                'form_view_initial_mode': 'edit',
                'default_name': _('New') if self.sequence_code else self.name,
                'default_loan_type_id': self.id,
                #'default_request_owner_id': self.env.user.id,
                'default_request_status': 'draft'
            },
        }

    def _get_action(self, action_xmlid, domain=[]):
        action = self.env["ir.actions.actions"]._for_xml_id(action_xmlid)
        if self:
            action['display_name'] = self.display_name
            
        context = {
            'search_default_loan_type_id': [self.id],
            'default_loan_type_id': self.id,
            'default_company_id': self.company_id.id,
        }

        action_context = literal_eval(action['context'])
        context = {**action_context, **context}
        action['context'] = context
        if domain:
            action['domain'] = domain  # Add the domain parameter here if it's provided
        return action
        
    def get_action_loan_tree_pending(self):
        domain = [('loan_type_id', '=', self.id),('state', 'in', ['validate','partial'])]
        return self._get_action('de_hr_loan.action_loan_tree',domain=domain)
    def get_action_loan_tree_confirm(self):
        domain = [('loan_type_id', '=', self.id),('state', 'in', ['confirm'])]
        return self._get_action('de_hr_loan.action_loan_tree',domain=domain)
    def get_action_loan_tree_to_pay(self):
        domain = [('loan_type_id', '=', self.id),('state', 'in', ['post'])]
        return self._get_action('de_hr_loan.action_loan_tree',domain=domain)

    def get_action_all_loan_type(self):
        domain = [('loan_type_id', '=', self.id)]
        return self._get_action('de_hr_loan.action_loan_tree',domain=domain)
    def get_action_all_loan_type_paid(self):
        domain = [('loan_type_id', '=', self.id),('state', 'in', ['paid'])]
        return self._get_action('de_hr_loan.action_loan_tree',domain=domain)
    def get_action_all_loan_type_refused(self):
        domain = [('loan_type_id', '=', self.id),('state', 'in', ['refuse'])]
        return self._get_action('de_hr_loan.action_loan_tree',domain=domain)
    def get_action_all_loan_type_closed(self):
        domain = [('loan_type_id', '=', self.id),('state', 'in', ['close'])]
        return self._get_action('de_hr_loan.action_loan_tree',domain=domain)

    def action_open_loan_type(self):
        self.ensure_one()
        return {
            'name': self.name,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'views': [[False, "form"]],
            'res_model': 'hr.loan.type',
            'res_id': self.id,
        }

class LoanTypeDocument(models.Model):
    _name = 'hr.loan.type.document'
    _description = 'Loan Type Document'

    name = fields.Char(string='Name', required=True)
    is_mandatory = fields.Boolean(string='Is Mandatory', default=False)
    loan_type_id = fields.Many2one('hr.loan.type', string='Loan Type', required=True)
    
