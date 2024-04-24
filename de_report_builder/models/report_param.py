# -*- coding: utf-8 -*-

from odoo import models, fields, exceptions, api, _
from odoo.exceptions import ValidationError, AccessError, UserError

class ReportParams(models.Model):
    _name = 'rc.param.line'
    _description = 'Custom Report Line Models'

    report_config_id = fields.Many2one('report.config', string='Report Config', required=True, ondelete='cascade', index=True, copy=False)
    rc_header_model_id = fields.Many2one(related='report_config_id.rc_header_model_id')
    field_name = fields.Char('Field Name', required=True)
    field_operator = fields.Selection(
        [
            ('=','='),('!=','!='),
            ('>','>'),('>=','>='),
            ('<','<'),('<=','<='),
            ('in','Contains'),('not in','Not Contains'),
            ('like','Like'),('ilike','iLike'),
        ], string='Operator', required=True, default='=',
    )
    field_id = fields.Many2one('ir.model.fields', string='Field', ondelete="cascade", required=True,
                           domain="[('model_id','=',rc_header_model_id),('store','=',True),('ttype','not in',['one2many'])]"
                          )
    field_type = fields.Selection(related='field_id.ttype')
    report_param_field_id = fields.Many2one('ir.model.fields', string='Param Field', readonly=True)
    is_multi_vals = fields.Boolean(string='Multi List')

    @api.onchange('is_multi_vals')
    def _onchange_multi_vals(self):
        for record in self:
            record.field_operator = 'in'

    @api.constrains('is_multi_vals', 'field_operator')
    def _check_multi_vals_operator(self):
        for field in self:
            if field.is_multi_vals and field.field_operator not in ('in', 'not in'):
                raise ValidationError("Multi-list functionality is compatible only with 'Contains' and 'Not Contains' operators.")
    


