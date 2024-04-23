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
            ('like','Contains'),
        ], string='Operator', required=True, default='=',
    )
    field_id = fields.Many2one('ir.model.fields', string='Field', ondelete="cascade", required=True,
                               domain="[('model_id','=',rc_header_model_id),('store','=',True)]"
                              )
    report_param_field_id = fields.Many2one('ir.model.fields', string='Param Field', readonly=True)
    


