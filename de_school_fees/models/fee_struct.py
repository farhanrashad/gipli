#-*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class FeeStructure(models.Model):
    _name = 'oe.fee.struct'
    _description = 'Fee Structure'

    @api.model
    def _get_default_report_id(self):
        return self.env.ref('hr_payroll.action_report_feeslip', False)

    
    @api.model
    def _get_default_rule_ids(self):
        return False

    name = fields.Char(required=True)
    code = fields.Char()
    active = fields.Boolean(default=True)
    #type_id = fields.Many2one('hr.payroll.structure.type', required=True)
    country_id = fields.Many2one('res.country', string='Country', default=lambda self: self.env.company.country_id)
    note = fields.Html(string='Description')
    rule_ids = fields.One2many(
        'oe.fee.rule', 'fee_struct_id',
        string='Fee Rules', default=_get_default_rule_ids)
    #report_id = fields.Many2one('ir.actions.report', string="Report", domain="[('model','=','hr.feeslip'),('report_type','=','qweb-pdf')]", default=_get_default_report_id)
    feeslip_name = fields.Char(string="Feeslip Name", translate=True,
        help="Name to be set on a feeslip. Example: 'End of the year bonus'. If not set, the default value is 'Fee Slip'")
    use_enrol_contract_lines = fields.Boolean(default=True, help="contract lines won't be computed/displayed in fee slips.")
    schedule_pay_duration = fields.Integer(string='Schedule Pay', default=1, required=True)
    pay_one_time = fields.Boolean('One Time Pay')
    input_line_type_ids = fields.Many2many('oe.feeslip.input.type', string='Other Input Line')
    
    # Academic Fields
    course_id = fields.Many2one('oe.school.course', string='Course')
    batch_ids = fields.Many2many('oe.school.course.batch', string='Course Batches')


    @api.constrains('schedule_pay_duration')
    def _check_schedule_pay_duration(self):
        for record in self:
            if record.schedule_pay_duration <= 0:
                raise exceptions.ValidationError("Schedule Pay Duration must be greater than 0.")
                
