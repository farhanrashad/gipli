# -*- coding: utf-8 -*-

from odoo import models, fields, exceptions, api, _
from odoo.exceptions import ValidationError, AccessError, UserError
   

class ReportConfig(models.Model):
    _name = 'report.config'
    _description = 'Custom Report Configuration'

    name = fields.Char(string='Name', required=True, translate=True, )
    active = fields.Boolean(default=True)
    description = fields.Char(string='Description')
    state = fields.Selection([
        ('draft', 'New'),
        ('publish', 'Publish'),
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    rc_header_model_id = fields.Many2one('ir.model', string='Model', ondelete='cascade', required=True)
    report_parent_menu_id = fields.Many2one('ir.ui.menu', string='Menu',
                                     domain="[('action','=',False)]"
                                    )
    report_menu_id = fields.Many2one('ir.ui.menu', string='Menu', readonly=True,
                                    )
    report_window_action_id = fields.Many2one('ir.actions.act_window', string='Window Action', readonly=True)
    report_wizard_view_id = fields.Many2one('ir.ui.view', string='Wizard View', readonly=True)

    rc_header_field_ids = fields.One2many('rc.header.fields', 'report_config_id', string='Header Fields', copy=True, auto_join=True)

    rc_param_line = fields.One2many('rc.param.line', 'report_config_id', string='Parameters', copy=True, auto_join=True)
    
    rc_line_model_ids = fields.One2many('rc.line.models', 'report_config_id', string='Header Fields', copy=True, auto_join=True)

    #Action Buttons
    def button_publish(self):
        if not self.report_parent_menu_id:
            raise UserError('Menu is Required')

        # Create Wizard View
        if not self.report_wizard_view_id:
            self.report_wizard_view_id = self._create_wizard_view().id
            
        # Create Menu Item
        if not self.report_menu_id:
            self.report_menu_id = self._create_menu().id

        # Create Action
        if not self.report_window_action_id:
            self.report_window_action_id = self._create_action().id
        
        # Assign Action to Menu Item
        self.report_menu_id.action = 'ir.actions.act_window,%s' % self.report_window_action_id.id

        self.state = 'publish'

        
        
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
            'name': self.name + ' Wizard',
            'res_model': 'rc.report.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'report_id': self.id,
            },
        })
        return action
        
    def _create_wizard_view(self):
        #raise UserError(self._get_view_arch)
        view_id = self.env['ir.ui.view'].create({
            'name': self.name.replace(' ', '_').lower() + '_report_wizard_view',
            'type': 'form',
            'model': 'rc.report.wizard',
            #'mode': 'primary',
            #'active': True,
            'arch': self._get_view_arch(),
        })
        return view_id

    def _get_view_arch(self):
        arch = """
            <form string="Report Wizard" class="oe_form_container" version="14.0" edit="true">
                <group>
                    <group string="hello">
                        <!-- Add your fields here -->
                    </group>
                    <group>
                        <!-- Add more groups or fields as needed -->
                    </group>
                </group>
                <footer>
                    <button name="generate_report" string="Print" type="object" class="btn-primary" data-hotkey="q"/>
                    <button string="Cancel" class="btn-secondary" special="cancel" data-hotkey="x" />
                </footer>
            </form>
        """
        return arch
        
    def button_unpublish(self):
        self.report_menu_id.unlink()
        self.report_window_action_id.unlink()
        self.report_wizard_view_id.unlink()
        self.state = 'draft'

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
                               domain="[('model_id','=',rc_header_model_id),('ttype','not in',['one2many'])]"
                              )
    field_type = fields.Selection(related='field_id.ttype')
    field_model = fields.Char(related='field_id.relation')
    link_field_id = fields.Many2one('ir.model.fields', string='Link Field', help="Relational Field Reference ")
    