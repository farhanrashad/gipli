# -*- coding: utf-8 -*-

from odoo import models, fields, exceptions, api, _
from odoo.exceptions import ValidationError, AccessError, UserError
   

class ReportConfig(models.Model):
    _name = 'report.config'
    _description = 'Custom Report Configuration'

    name = fields.Char(string='Name', required=True, translate=True, )
    active = fields.Boolean(default=True)
    description = fields.Char(string='Description')

    rc_header_model_id = fields.Many2one('ir.model', ondelete='cascade', string='Model', required=True)

    rc_header_field_ids = fields.One2many('rc.header.fields', 'report_config_id', string='Header Fields', copy=True, auto_join=True)
    rc_line_model_ids = fields.One2many('rc.line.models', 'report_config_id', string='Header Fields', copy=True, auto_join=True)

class HeaderFields(models.Model):
    _name = 'rc.header.fields'
    _description = 'Custom Report Header Fields'

    report_config_id = fields.Many2one('report.config', string='Report Config', required=True, ondelete='cascade', index=True, copy=False)
    rc_header_model_id = fields.Many2one(related='report_config_id.rc_header_model_id')
    field_id = fields.Many2one('ir.model.fields', string='Field', ondelete="cascade", required=True,
                               domain="[('model_id','=',rc_header_model_id)]"
                              )
    


class LineModels(models.Model):
    _name = 'rc.line.models'
    _description = 'Custom Report Line Models'

    report_config_id = fields.Many2one('report.config', string='Report Config', required=True, ondelete='cascade', index=True, copy=False)

    rc_header_model_relations = fields.Many2many('ir.model', string='Line Item Model',
                                                compute='_compute_header_model_relation'
                                                )
    rc_line_model_id = fields.Many2one('ir.model', ondelete='cascade', string='Line Item Model', 
                                       store=True,
                                       domain="[('id','in',rc_header_model_relations)]"
                                      )


    @api.depends('report_config_id')
    def _compute_header_model_relation(self):
        model_id = self.env['ir.model']
        for record in self:
            model_ids = self.env['ir.model'].search([
                ('model','in',record.report_config_id.rc_header_model_id.field_id.mapped('relation'))
            ])
            record.rc_header_model_relations = model_ids
    


    


