from odoo import models, fields, api, _


class HrCustody(models.Model):
    _inherit = 'hr.custody'

    is_asset = fields.Boolean(string="Is Asset",)
    asset_id = fields.Many2one(comodel_name="account.asset", string="Asset Name", required=False, )
    value_residual = fields.Monetary(related='asset_id.value_residual',readonly='True',  required=False, )

    def deliver_action(self):
        res = super(HrCustody, self).deliver_action()
        if self.asset_id and self.is_asset:
            self.asset_id.write({'is_custody': True})
        return res