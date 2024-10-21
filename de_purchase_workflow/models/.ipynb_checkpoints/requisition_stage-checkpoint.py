# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from datetime import date

class PurchaseRequisitionStage(models.Model):
    _name = 'purchase.requisition.stage'
    _description = 'Requisition Stage'
    _order = 'sequence, stage_category, id'
    
    def _get_default_requisition_type_ids(self):
        default_requisition_type_id = self.env.context.get('default_requisition_type_id')
        return [default_requisition_type_id] if default_requisition_type_id else None
    
    name = fields.Char(string='Stage Name', translate=True)
    stage_code = fields.Char(string='Stage Code', size=3, copy=False)
    active = fields.Boolean('Active', default=True, help="If unchecked, it will allow you to hide the stage without removing it.")

    description = fields.Text(
        "Requirements", help="Enter here the internal requirements for this stage. It will appear "
                             "as a tooltip over the stage's name.", translate=True)
    sequence = fields.Integer(default=1)
    fold = fields.Boolean(string='Folded in Kanban',
                          help='This stage is folded in the kanban view when there are no records in that stage to display.')
    requisition_type_ids = fields.Many2many('purchase.requisition.type', 'requisition_type_stage_rel', 'requisition_stage_id', 'requisition_type_id', string='Requisition Types', default=_get_default_requisition_type_ids)
    
    stage_category = fields.Selection([
        ('draft', 'Draft'),
        ('progress', 'In Progress'),
        ('confirm', 'Confirmed'),
        ('done', 'Done'),
        ('Cancel', 'Cancelled'),
    ], string='Stage Category', default='draft')
    

    group_id = fields.Many2one('res.groups', string='Security Group')
    

    _sql_constraints = [
        ('code_uniq', 'unique (stage_code)', "Code already exists!"),
    ]
    
   