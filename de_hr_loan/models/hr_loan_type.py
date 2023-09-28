# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource


class LoanType(models.Model):
    _name = 'hr.loan.type'
    _description = 'Loan Category'
    _order = 'sequence, id'

    _check_company_auto = True

    def _get_default_image(self):
        default_image_path = get_module_resource('de_hr_loan', 'static/src/img', 'loan.svg')
        return base64.b64encode(open(default_image_path, 'rb').read())

    name = fields.Char(string="Name", translate=True, required=True)
    company_id = fields.Many2one(
        'res.company', 'Company', copy=False,
        required=True, index=True, default=lambda s: s.env.company)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(string="Sequence")
    description = fields.Char(string="Description", translate=True)
    image = fields.Binary(string='Image', default=_get_default_image)
    automated_sequence = fields.Boolean('Automated Sequence?',
        help="If checked, the Approval Requests will have an automated generated name based on the given code.")
    sequence_code = fields.Char(string="Code")
    sequence_id = fields.Many2one('ir.sequence', 'Reference Sequence',
        copy=False, check_company=True)
    product_id = fields.Many2one('product.product', string="Product", required=True, domain="[('type','=','service')]")



    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('automated_sequence'):
                sequence = self.env['ir.sequence'].create({
                    'name': _('Sequence') + ' ' + vals['sequence_code'],
                    'padding': 5,
                    'prefix': vals['sequence_code'],
                    'company_id': vals.get('company_id'),
                })
                vals['sequence_id'] = sequence.id
        return super().create(vals_list)

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