# -*- coding: utf-8 -*-

from odoo import models, fields, exceptions, api, _
from odoo.exceptions import ValidationError, AccessError, UserError

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
    rc_header_rel_field_ids = fields.Many2many('ir.model.fields', string="Related Fields", 
                                             compute='_compute_all_header_rel_fields'
                                              )
    rc_header_rel_field_id = fields.Many2one('ir.model.fields', string="Related Field", 
                                               store=True, readonly=False,
                                             domain="[('id','in',rc_header_rel_field_ids)]",
                                             compute='_compute_header_rel_field'
                                             )

    rc_line_model_field_ids = fields.One2many('rc.line.models.fields', 'line_model_id', string='Line Model Fields', copy=True, auto_join=True)

    @api.depends('rc_line_model_id')
    @api.onchange('rc_line_model_id')
    def _compute_all_header_rel_fields(self):
        model_ids = self.env['ir.model.fields'].search([
            ('model_id','=',self.rc_line_model_id.id),
            ('relation','=',self.report_config_id.rc_header_model_id.model)
        ])
        self.rc_header_rel_field_ids = model_ids
        
    @api.depends('rc_header_rel_field_ids')
    def _compute_header_rel_field(self):
        for record in self:
            if record.rc_header_rel_field_ids:
                record.rc_header_rel_field_id = record.rc_header_rel_field_ids[0]
            else:
                record.rc_header_rel_field_id = False
            
        
    
        
    @api.depends('report_config_id')
    def _compute_header_model_relation(self):
        for record in self:
            #one2many_field_ids = record.report_config_id.rc_header_model_id.field_id.filtered(lambda field: field.ttype == 'one2many')
            #record.rc_header_model_relations = [(6, 0, one2many_field_ids.ids)]
        
            model_id = self.env['ir.model']
            for record in self:
                model_ids = self.env['ir.model'].search([
                    ('model','in',record.report_config_id.rc_header_model_id.field_id.filtered(lambda field: field.ttype == 'one2many').mapped('relation'))
                ])
                record.rc_header_model_relations = model_ids

    # actions
    def action_configure_line_model_ields(self):
        self.ensure_one()
        report_id = self.report_config_id
        view = self.env.ref('de_report_builder.report_line_models_wizard_form')
        return {
            'name': _('Line Item Fields'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'rc.line.models',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
            'context': dict(
                self.env.context,
            ),
        }

class LineModelsFields(models.Model):
    _name = 'rc.line.models.fields'
    _description = 'Custom Report Header Fields'

    line_model_id = fields.Many2one('rc.line.models', string='Line Model', required=True, ondelete='cascade', index=True, copy=False)
    rc_line_model_id = fields.Many2one(related='line_model_id.rc_line_model_id')
    field_id = fields.Many2one('ir.model.fields', string='Field', ondelete="cascade", required=True,
                               domain="[('model_id','=',rc_line_model_id),('ttype','not in',['one2many'])]"
                              )
    field_type = fields.Selection(related='field_id.ttype')
    field_model = fields.Char(related='field_id.relation')
    link_field_id = fields.Many2one('ir.model.fields', string='Link Field', help="Relational Field Reference ")