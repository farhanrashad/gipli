"""
    THIS MODULE WAS DEPENDING ON ACCOUNT MODULE BUT DUE TO CHANGE IN REQUIREMENTS ACCOUNT MODULE WAS REMOVED.

     THE COMMENTED LINES ARE THE PART OF CODE THAT DEPENDS ON ACCOUNT MODULE, THEY ARE COMMENTED FOR NOW UNTIL
        THE MODULE IS TESTED AND TO BE VERIFIED THAT IT IS STABLE.
"""

# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

LOGGER = logging.getLogger(__name__)

class HrCustody(models.Model):
    _name = 'hr.custody'
    _rec_name = 'name'
    _description = 'Employee Custody'
    _order = 'name asc, id desc'
    # _inherit = ['mail.thread', 'ir.needaction_mixin']

    name = fields.Char(string="Name", required=False, )
    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee", required=False, )
    item_name = fields.Char(string="Item Name")
    serial_number = fields.Char(string="Serial Number")
    delivery_date = fields.Date(string="Delivery Date", required=False, )
    return_date = fields.Date(string="Return Date", required=False, )
    type = fields.Selection(string="Type", selection=[('item', 'Item'), ('money', 'Money'), ], required=False, )
    currency_id = fields.Many2one(comodel_name="res.currency", string="Currency", default=lambda self:self.env.user.company_id.currency_id.id)
    # is_asset = fields.Boolean(string="Is Asset",)
    # asset_id = fields.Many2one(comodel_name="account.asset.asset", string="Asset Name", required=False, )
    # value_residual = fields.Float(related='asset_id.value_residual',readonly='True',  required=False, )
    amount = fields.Monetary(string="Amount",  required=False, )
    return_amount = fields.Monetary(string="Return Amount",  required=False, )
    status = fields.Selection(string="Status When Returned", selection=[('good', 'Good and Working'), ('fix','Need Some Fix'),('scrap', 'Scrap') ], required=False, )
    state = fields.Selection(string="State", selection=[('draft','Draft'),('delivered', 'Delivered'), ('return', 'Returned'), ], default='draft' )


    @api.model
    def create(self,vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('hr.custody')
        return super(HrCustody, self).create(vals)

    @api.constrains('delivery_date','return_date')
    def delivery_return_constrains(self):
        if self.return_date and self.return_date < self.delivery_date:
            raise ValidationError(_('Return Date Can not Be Before the Delivery Date'))

    def return_action(self):
        return {
            'name': _('Custody Return'),
            'type': 'ir.actions.act_window',
            'res_model': 'custody.return.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }

    def deliver_action(self):
        self.write({'state':'delivered'})
        # if self.asset_id and self.is_asset:
        #     self.asset_id.write({'is_custody':True})