# -*- coding: utf-8 -*-
from lxml import etree
from odoo import api, fields, models 



class Model(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def get_views(self, views, options=None):
        res=super().get_views(views,options)
        for key,value in res['views'].items():
            if key in ['list','form']:
                if self.env.user.has_group('hide_create_edit_delete_action.group_hide_create_button'):
                    if self._name != 'res.users':
                        if not self.env.ref(
                                'hide_create_edit_delete_action.group_hide_create_button').sudo().hide_create_objects:
                            temp = etree.fromstring(value['arch'])
                            temp.set('create', '0')
                            value['arch'] = etree.tostring(temp)
                        else:
                            models = self.env.ref(
                                'hide_create_edit_delete_action.group_hide_create_button').sudo().hide_create_objects
                            if self._name in models.mapped('model'):
                                temp = etree.fromstring(value['arch'])
                                temp.set('create', '0')
                                value['arch'] = etree.tostring(temp)
                if self.env.user.has_group('hide_create_edit_delete_action.group_hide_edit_button'):
                    if self._name != 'res.users':
                        if not self.env.ref(
                                'hide_create_edit_delete_action.group_hide_edit_button').sudo().hide_edit_objects:
                            temp = etree.fromstring(value['arch'])
                            temp.set('edit', '0')
                            value['arch'] = etree.tostring(temp)
                        else:
                            models = self.env.ref(
                                'hide_create_edit_delete_action.group_hide_edit_button').sudo().hide_edit_objects
                            if self._name in models.mapped('model'):
                                temp = etree.fromstring(value['arch'])
                                temp.set('edit', '0')
                                value['arch'] = etree.tostring(temp)
                if self.env.user.has_group('hide_create_edit_delete_action.group_hide_delete_button'):
                    if self._name != 'res.users':
                        if not self.env.ref(
                                'hide_create_edit_delete_action.group_hide_delete_button').sudo().hide_delete_objects:
                            temp = etree.fromstring(value['arch'])
                            temp.set('delete', '0')
                            value['arch'] = etree.tostring(temp)
                        else:
                            models = self.env.ref(
                                'hide_create_edit_delete_action.group_hide_delete_button').sudo().hide_delete_objects
                            if self._name in models.mapped('model'):
                                temp = etree.fromstring(value['arch'])
                                temp.set('delete', '0')
                                value['arch'] = etree.tostring(temp)
        return res
