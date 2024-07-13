"""
    THIS MODULE WAS DEPENDING ON ACCOUNT MODULE BUT DUE TO CHANGE IN REQUIREMENTS ACCOUNT MODULE WAS REMOVED.

     THE COMMENTED LINES ARE THE PART OF CODE THAT DEPENDS ON ACCOUNT MODULE, THEY ARE COMMENTED FOR NOW UNTIL
        THE MODULE IS TESTED AND TO BE VERIFIED THAT IT IS STABLE.
"""

# # -*- coding: utf-8 -*-
# from odoo import fields, models, api, _
#
#
# class AccountInvoiceLine(models.Model):
#     _inherit = 'account.invoice.line'
#
#     @api.multi
#     def asset_create(self):
#         for rec in self:
#             if rec.asset_category_id:
#                 vals = {
#                     'name': rec.name,
#                     'code': rec.invoice_id.number or False,
#                     'category_id': rec.asset_category_id.id,
#                     # 'value': rec.price_subtotal_signed,
#                     'partner_id': rec.invoice_id.partner_id.id,
#                     'company_id': rec.invoice_id.company_id.id,
#                     'currency_id': rec.invoice_id.company_currency_id.id,
#                     'date': rec.invoice_id.date_invoice,
#                     'invoice_id': rec.invoice_id.id,
#                 }
#                 # changed_vals = rec.env['account.asset.asset'].onchange_category_id_values(vals['category_id'])
#                 # vals.update(changed_vals['value'])
#                 if rec.uom_id.id == rec.env.ref('product.product_uom_unit').id:
#                     vals['value'] = rec.price_subtotal_signed / rec.quantity
#                     changed_vals = rec.env['account.asset.asset'].onchange_category_id_values(vals['category_id'])
#                     vals.update(changed_vals['value'])
#                     for i in range(int(rec.quantity)):
#                         if 'message_follower_ids' in vals:
#                             del vals['message_follower_ids']
#                         vals['code'] = str(rec.invoice_id.number) + ' - ' + str(i+1)
#                         asset = rec.env['account.asset.asset'].create(vals)
#                         if rec.asset_category_id.open_asset:
#                             asset.validate()
#                 else:
#                     vals['value'] = rec.price_subtotal_signed
#                     changed_vals = rec.env['account.asset.asset'].onchange_category_id_values(vals['category_id'])
#                     vals.update(changed_vals['value'])
#                     asset = rec.env['account.asset.asset'].create(vals)
#                     if rec.asset_category_id.open_asset:
#                         asset.validate()
#             return True
