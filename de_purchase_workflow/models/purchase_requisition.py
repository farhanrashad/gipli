# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from datetime import date

class PurchaseRequisitionType(models.Model):
    _inherit = 'purchase.requisition.type'
    
    group_id = fields.Many2one('res.groups', string='Security Group')
    
    
class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'
    
    def _get_default_stage_id(self):
        """ Gives default stage_id """
        type_id = self.env.context.get('default_type_id')
        if not type_id:
            return False
        return self.stage_find(type_id, [('fold', '=', False)])
    
    stage_id = fields.Many2one('purchase.requisition.stage', string='Stage', store=True,  ondelete='restrict', tracking=True, index=True, compute="_compute_stage_id", domain="[('requisition_type_ids', '=', type_id)]", copy=False)
    stage_category = fields.Selection(related='stage_id.stage_category')
    next_stage_id = fields.Many2one('purchase.requisition.stage',compute='_compute_requisition_stage')
    prv_stage_id = fields.Many2one('purchase.requisition.stage',compute='_compute_requisition_stage')
    
    date_submit = fields.Datetime('Submission Date', readonly=True)
    date_approved = fields.Datetime('Approved Date', readonly=True)
    
    requisition_stage_ids = fields.One2many('purchase.requisition.stage.workflow', 'requisition_id', string='Stage', copy=False)
    
    def _compute_requisition_stage(self):
        for requisition in self:
            next_stage = prv_stage = False
            for stage in requisition.requisition_stage_ids.filtered(lambda t: t.stage_id.id == requisition.stage_id.id):
                    next_stage = stage.next_stage_id.id
                    prv_stage = stage.prv_stage_id.id
            requisition.next_stage_id = next_stage
            requisition.prv_stage_id = prv_stage
            
    @api.depends('type_id')
    def _compute_stage_id(self):
        for requisition in self:
            if requisition.type_id:
                if requisition.type_id not in requisition.stage_id.requisition_type_ids:
                    requisition.stage_id = requisition.stage_find(requisition.type_id.id, [('fold', '=', False)])
            else:
                requisition.stage_id = False
    
    def stage_find(self, section_id, domain=[], order='sequence'):
        """ Override of the base.stage method
            Parameter of the stage search taken from the lead:
            - section_id: if set, stages must belong to this section or
              be a default stage; if not set, stages must be default
              stages
        """
        # collect all section_ids
        section_ids = []
        if section_id:
            section_ids.append(section_id)
        section_ids.extend(self.mapped('type_id').ids)
        search_domain = []
        if section_ids:
            search_domain = [('|')] * (len(section_ids) - 1)
            for section_id in section_ids:
                search_domain.append(('requisition_type_ids', '=', section_id))
        search_domain += list(domain)
        # perform search, return the first found
        return self.env['purchase.requisition.stage'].search(search_domain, order=order, limit=1).id

    def button_submit(self):
        #self.ensure_one()
        for requisition in self.sudo():
            group_id = requisition.type_id.group_id
            if group_id:
                if not (group_id & self.env.user.groups_id):
                    raise UserError(_("You are not authorize to submit requisition in category '%s'.", requisition.type_id.name))
            if not requisition.line_ids:
                raise UserError(_("You cannot submit transaction '%s' because there is no line.", self.name))
            if self.type_id.quantity_copy == 'none' and self.vendor_id:
                for requisition_line in self.line_ids:
                    if requisition_line.price_unit <= 0.0:
                        raise UserError(_('You cannot confirm the blanket order without price.'))
                    if requisition_line.product_qty <= 0.0:
                        raise UserError(_('You cannot confirm the blanket order without quantity.'))
                    requisition_line.create_supplier_info()
                #self.write({'state': 'ongoing'})
            #else:
                #self.write({'state': 'in_progress'})
            # Set the sequence number regarding the requisition type
            if self.name == 'New':
                if self.is_quantity_copy != 'none':
                    self.name = self.env['ir.sequence'].next_by_code('purchase.requisition.purchase.tender')
                else:
                    self.name = self.env['ir.sequence'].next_by_code('purchase.requisition.blanket.order')
        self.sudo()._compute_requisition_stages()
        self.update({
            'date_submit' : fields.Datetime.now(),
            'stage_id' : self.next_stage_id.id,
        })
        
   
    def action_cancel(self):
        res = super(PurchaseRequisition, self).action_cancel()
        stage_id = self.env['purchase.requisition.stage'].search([('stage_category','=','Cancel')],limit=1)
        self.update({
            'stage_id': stage_id.id,
        })
        return res
    
    def action_draft(self):
        res = super(PurchaseRequisition, self).action_draft()
        stage_id = self.env['purchase.requisition.stage'].search([('requisition_type_ids','=',self.type_id.id),('stage_category','=','draft')],limit=1)
        self.update({
            'stage_id': stage_id.id,
        })
        return res
        
    def _compute_requisition_stages(self):
        stages_list = []
        next_stage = prv_stage = False
        if self.requisition_stage_ids:
            self.requisition_stage_ids.unlink()
        for requisition in self:
            stage_ids = self.env['purchase.requisition.stage'].search([('requisition_type_ids', '=', requisition.type_id.id)])
            for stage in stage_ids:
                stages_list.append({
                    'requisition_id': requisition.id,
                    'stage_id': stage.id, 
                    'sequence': stage.sequence,
                })
            requisition.requisition_stage_ids.create(stages_list)
            #order.order_stage_ids = lines_data
            #===================================
            #++++++++Assign Next Stage++++++++++++++
            stages = self.env['purchase.requisition.stage.workflow'].search([('requisition_id','=', requisition.id)], order="sequence desc")
            for stage in stages:
                stage.update({
                    'next_stage_id': next_stage,
                })
                next_stage = stage.stage_id.id
            #++++++++++++++++++++++++++++++++++++++++
            #+++++++++++Assign Previous Stage++++++++++
            stages = self.env['purchase.requisition.stage.workflow'].search([('requisition_id','=', requisition.id)], order="sequence asc")
            for stage in stages:
                stage.update({
                    'prv_stage_id': prv_stage,
                })
                prv_stage = stage.stage_id.id
                
                
    def button_confirm(self):
        for requisition in self.sudo():
            group_id = requisition.stage_id.group_id
            if group_id:
                if not (group_id & self.env.user.groups_id):
                    raise UserError(_("You are not authorize to approve '%s'.", requisition.stage_id.name))
                    
        self.update({
            'date_approved' : fields.Datetime.now(),
            'stage_id' : self.next_stage_id.id,
        })
        if self.next_stage_id.stage_category == 'confirm':
            self.sudo().action_in_progress()
    
    def button_refuse(self):
        for requisition in self.sudo():
            group_id = requisition.stage_id.group_id
            if group_id:
                if not (group_id & self.env.user.groups_id):
                    raise UserError(_("You are not authorize to refuse '%s'.", requisition.stage_id.name))                    
        self.update({
            'stage_id' : self.prv_stage_id.id,
        })
        
class PurchaseRequisitionStageWorkflow(models.Model):
    _name = 'purchase.requisition.stage.workflow'
    _description = 'Requisition Stage Workflows'
    _order = 'sequence'
    
    requisition_id = fields.Many2one('purchase.requisition', string='Requisition', index=True, required=True, ondelete='cascade')
    
    stage_id = fields.Many2one('purchase.requisition.stage', string='Stage', readonly=False, ondelete='restrict', tracking=True, index=True, copy=False)
    sequence = fields.Integer(string='Sequence')
    next_stage_id = fields.Many2one('purchase.requisition.stage', string='Next Stage', readonly=False, ondelete='restrict', tracking=True, index=True, copy=False)
    prv_stage_id = fields.Many2one('purchase.requisition.stage', string='Previous Stage', readonly=False, ondelete='restrict', tracking=True, index=True, copy=False)
