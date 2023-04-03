# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from datetime import date

class purchase_requisition_type(models.Model):
    _inherit = 'purchase.requisition.type'
    
    force_issuance = fields.Boolean(string='Allow and force issuance', help='Allow or force issuenace on the site if product is already issue to the project')
    
    
class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'
    
    allow_submission_with_exception = fields.Boolean(string='Allow submission with exception')
           
        
    def button_submit(self):
        #self.ensure_one()
        old_requisition_lines = self.env['purchase.requisition.line']
        days = 0
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
            if not requisition.type_id.force_issuance:
                for line in requisition.line_ids:
                    old_requisition_lines = self.env['purchase.requisition.line'].search([('product_id','=',line.product_id.id),('project_id','=',line.project_id.id),('requisition_id','!=',requisition.id)])
                    if len(old_requisition_lines):
                        for oline in old_requisition_lines:
                            if line.requisition_id.ordering_date and oline.requisition_id.ordering_date:
                                days = (line.requisition_id.ordering_date - oline.requisition_id.ordering_date).days
                            if abs(days) < 365:
                                if not requisition.allow_submission_with_exception:
                                    raise UserError(_('The Product %s has already issued to Site (%s) %s days ago') % (line.product_id.name, line.project_id.name, str(abs(days))))

            
            
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