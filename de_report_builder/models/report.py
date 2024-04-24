# -*- coding: utf-8 -*-

from odoo import models, fields, exceptions, api, _
from odoo.exceptions import ValidationError, AccessError, UserError
from copy import deepcopy

"""

<field name="report_menu_id" />
<field name="report_window_action_id" />
<field name="report_action_id" />
<field name="report_wizard_view_id" />
"""

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
    report_orientation = fields.Selection([
        ('portrait', 'Portrait'),
        ('landscape', 'Landscape'),
    ], string='orientation', default='portrait')
    
    report_window_action_id = fields.Many2one('ir.actions.act_window', string='Window Action', readonly=True)
    report_wizard_view_id = fields.Many2one('ir.ui.view', string='Wizard View', readonly=True)
    #report_action_id = fields.Many2one('ir.actions.report', string='Report Action', readonly=True)
    #report_template_view_id = fields.Many2one('ir.ui.view', string='Template View', readonly=True)

    rc_header_field_ids = fields.One2many('rc.header.fields', 'report_config_id', string='Header Fields', copy=True, auto_join=True)

    rc_param_line = fields.One2many('rc.param.line', 'report_config_id', string='Parameters', copy=True, auto_join=True)
    
    rc_line_model_ids = fields.One2many('rc.line.models', 'report_config_id', string='Header Fields', copy=True, auto_join=True)

    #Action Buttons
    def button_publish(self):
        if not self.report_parent_menu_id:
            raise UserError('Menu is Required')

        # Create Wizard View
        #if not self.report_wizard_view_id:
        view_id = self._create_wizard_view()
        self.report_wizard_view_id = view_id.id
            
        # Create Menu Item
        #if not self.report_menu_id:
        menu_id = self._create_menu()
        self.report_menu_id = menu_id.id

        # Create Action
        #if not self.report_window_action_id:
        action_id = self._create_window_action()
        self.report_window_action_id = action_id.id

        #report_action_id = self._create_report_action()
        #self.report_action_id = report_action_id
        # Assign Action to Menu Item
        menu_id.action = 'ir.actions.act_window,%s' % action_id.id
        action_id.view_id = view_id.id

        self.state = 'publish'

        
        
    def _create_menu(self):
        parent_menu = self.report_parent_menu_id
        menu_item = self.env['ir.ui.menu'].create({
            'name': self.name,
            'parent_id': parent_menu.id,
            'sequence': 1,
        })
        return menu_item

    def _create_window_action(self):
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

    def _create_report_action(self):
        view = self._create_report_template_view()
        action_vals = {
            'name': self.name.replace(' ', '_').lower(),
            'model': 'report.config',
            'report_type': 'qweb-pdf',
            'report_name': view.name,
            'binding_model_id': self.env.ref('de_report_builder.model_report_config').id,
            'binding_view_types': 'form',
        }
        action = self.env['ir.actions.report'].create(action_vals)
        return action

    def _create_report_template_view(self):
        view_id = self.env['ir.ui.view'].create({
            'name': self.name.replace(' ', '_').lower() + '_report_template_view',
            'type': 'qweb',
            'model': 'report.config',
            'arch': """
                <odoo>
                    <data>
                        <template id="{}">
                            <div class="oe_structure"></div>
                            <t t-call="web.html_container">
                                <t t-call="web.internal_layout">
                                    <span t-raw="html_data" />
                                </t>
                            </t>
                        </template>
                    </data>
                </odoo>
            """.format(self.name.replace(' ', '_').lower() + '_report_template_view'),
        })
        return view_id

        
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
                <sheet>
                    <group col="4">
        """ + self._get_parameters_output() + """
                    </group>
                    <notebook>
        """ + self._get_parameters_page_output() + """
                    </notebook>
                <footer>
                    <button name="generate_report" string="Print PDF" type="object" class="btn-primary" />
                    <button name="action_report_excel" type="object" default_focus="1"
                            string="Print Excel"
                            class="oe_highlight"
                            icon="fa-download"/>
                    <button string="Cancel" class="btn-secondary" special="cancel" data-hotkey="x" />
                </footer>
                </sheet>
            </form>
        """
        return arch

    def _get_parameters_output(self):
        output = ''
        report_model_id = self.env['ir.model'].search([('model','=','rc.report.wizard')], limit=1)
        for param in self.rc_param_line:
            field_tech_name = 'x_' + param.field_name.replace(' ', '_').lower()
            field_exist_id = self.env['ir.model.fields'].search([
                ('name','=',field_tech_name), ('model','=','rc.report.wizard')
            ]).unlink()
            
            #if not field_exist_id:
            new_field_id = self.env['ir.model.fields'].create({
                'name': field_tech_name,
                'field_description': param.field_name,
                'model_id': report_model_id.id,
                'relation': param.field_id.relation,
                'ttype': 'many2many' if param.is_multi_vals else param.field_id.ttype,
            })
            param.report_param_field_id = new_field_id.id
            if not param.is_multi_vals:
                output += self._generate_field_output(new_field_id)
            #else:
            #    param.report_param_field_id = field_exist_id.id
            #    output += self._generate_field_output(field_exist_id)
        return output
    
    def _generate_field_output(self, field):
        if field.ttype == 'many2many':
            output = """<field name='{}' widget="many2many_tags" />""".format(field.name)
        else:
            output = """<field name='{}' />""".format(field.name)
        return output

    def _get_parameters_page_output(self):
        output = ''
        for param in self.rc_param_line:
            if param.is_multi_vals:
                output += """
                    <page string="{}">
                        <field name="{}" widget="one2many_list" />
                    </page>
                """.format(param.field_name, param.report_param_field_id.name)
        return output
            
    def button_unpublish(self):
        self.report_menu_id.unlink()
        self.report_window_action_id.unlink()
        self.report_wizard_view_id.unlink()
        #self.report_action_id.unlink()
        #self.report_template_view_id.unlink()
        self.state = 'draft'

    # Override unlink method to control deletion based on state
    def unlink(self):
        for record in self:
            if record.state == 'publish':
                raise UserError("You cannot delete a record in 'Publish' state.")
        return super(ReportConfig, self).unlink()

    
    @api.model
    def uninstall_hook(self):
        # Find and delete actions associated with 'report.config'
        actions = self.env['ir.actions.act_window'].search([('res_model', '=', 'report.config')])
        actions.unlink()

        report_actions = self.env['ir.actions.report'].search([('model', '=', 'report.config')])
        report_actions.unlink()

        # Find and delete views associated with 'report.config'
        views = self.env['ir.ui.view'].search([('model', '=', 'report.config')])
        views.unlink()

        # Find and delete menus associated with 'report.config'
        menus = self.env['ir.ui.menu'].search([('action', 'in', actions.ids)])
        menus.unlink()

        self.search([]).unlink()

        return super(ReportConfig, self).uninstall_hook()
        
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
    