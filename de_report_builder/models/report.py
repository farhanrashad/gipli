# -*- coding: utf-8 -*-

from odoo import models, fields, exceptions, api, _
from odoo.exceptions import ValidationError, AccessError, UserError
   

class ReportConfig(models.Model):
    _name = 'report.config'
    _description = 'Custom Report Configuration'

    name = fields.Char(string='Name', required=True, translate=True, )
    active = fields.Boolean(default=True)
    description = fields.Char(string='Description')

    rc_header_model_id = fields.Many2one('ir.model', string='Model', ondelete='cascade', required=True)
    report_parent_menu_id = fields.Many2one('ir.ui.menu', string='Menu',
                                     domain="[('action','=',False)]"
                                    )
    report_menu_id = fields.Many2one('ir.ui.menu', string='Menu', readonly=True,
                                    )
    report_window_action_id = fields.Many2one('ir.actions.act_window', string='Window Action', readonly=True)

    rc_header_field_ids = fields.One2many('rc.header.fields', 'report_config_id', string='Header Fields', copy=True, auto_join=True)
    rc_line_model_ids = fields.One2many('rc.line.models', 'report_config_id', string='Header Fields', copy=True, auto_join=True)

    #Action Buttons
    def button_validate(self):
        if not self.report_parent_menu_id:
            raise UserError('Menu is Required')
        # Create Menu Item
        if not self.report_menu_id:
            self.report_menu_id = self._create_menu().id

        # Create Action
        if not self.report_window_action_id:
            self.report_window_action_id = self._create_action().id
        # Assign Action to Menu Item
        self.report_menu_id.action = 'ir.actions.act_window,%s' % self.report_window_action_id.id

    def _create_menu(self):
        parent_menu = self.report_parent_menu_id
        menu_item = self.env['ir.ui.menu'].create({
            'name': self.name,
            'parent_id': parent_menu.id,
            'sequence': 1,
        })
        return menu_item

    def _create_action(self):
        action = self.env['ir.actions.act_window'].create({
            'name': 'Action' + self.name,
            'res_model': 'report.config',
            'view_mode': 'tree,form',
            'target': 'new',
            'context': {},
        })
        return action
    def button_delete(self):
        self.report_menu_id.unlink()
        self.report_window_action_id.unlink()

    @api.model
    def uninstall_hook(self):
        # Find and delete the action
        action = self.env.ref('de_report_builder.action_report_config', raise_if_not_found=False)
        if action:
            action.unlink()
    
        # Find and delete the dynamically created menu item
        menu_item = self.env['ir.ui.menu'].search([('name', '=', 'Report Config')], limit=1)
        if menu_item:
            menu_item.unlink()
        
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
    


    


