from odoo import models, fields, api,_


class de_stock_gatepass(models.Model):
    _name = 'stock.gatepass'
    
    name = fields.Char(
        string="Gate pass number",
        required=True, copy=False, readonly=True,
       
        # states={'draft': [('readonly', False)]},
        default=lambda self: _('New'))
    gp_date  = fields.Date(string="Date") 
    partner_id= fields.Many2one("res.partner", string ="Partner")
    description= fields.Text(string="Description")
    state =  fields.Selection(
        selection=[
            ('draft', "Draft"),
            ('done', "Validated"),
            ('cancel', "Cancelled"),
            
       ],
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=True,
        default=          'draft')
    
    picking_ids = fields.Many2many('stock.picking' , string ="pickings")
    gatepass_line = fields.One2many('stock.gatepass.line', 'gatepass_id', string='Gatepass Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)
    
    
    prd_ids_cs=fields.Many2many('product.product' , 'product_gatepass_custom_rel', 'gatepass_id', 'prod_id', string='test Product' ,compute ="get_ol_prd")
    
    @api.depends('picking_ids')
    def get_ol_prd(self):
         
        for rec in self:
            if rec.picking_ids:
                if rec.picking_ids.move_ids_without_package:
                    prds = rec.picking_ids.move_ids_without_package.mapped('product_id')
                    rec.prd_ids_cs =rec.prd_ids_cs+prds
            
            else:            
                rec.prd_ids_cs = rec.prd_ids_cs 
    def button_validate(self):
        self.state= 'done'        
    
    
    def button_cancel(self):
        self.state= 'cancel'  
    
            
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('stock.gatepass') or _('New')
        res = super(de_stock_gatepass, self).create(vals_list)
        return res
    
     
     
     
     
     
 
class de_stock_gatepass_line(models.Model):
    _name = 'stock.gatepass.line'   
    
    # name = fields.Text(string='Description', required=True)
    product_id= fields.Many2one("product.product" , string ="Product" ,required= True)
    uom_id  =  fields.Many2one('uom.uom', string='Unit of Measure' ,domain="[('category_id', '=', product_uom_category_id)]")
    quantity=   product_qty = fields.Float(string='Quantity', digits='Product Unit of Measure')
    gatepass_id = fields.Many2one("stock.gatepass", string="Gatepass")
    
    # product_uom = fields.Many2one('uom.uom', string='Unit of Measure', domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')

#
#     @api.onchange('gatepass_id.')
#     def onchange_subject_ids(self):
# #         for l in self:
# #             listids=[]
# #             domain={}
# #             list1 = l.y.x.mapped('stock.id')
# #     q
# #             return {'domain':{'stock':[('id','not in',list1)]}}       
#
#
