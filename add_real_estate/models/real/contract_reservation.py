from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import  datetime

try:
    from num2words import num2words
except ImportError:
    _logger.warning("The num2words python library is not installed, amount-to-text features won't be fully available.")
    num2words = None


class Contract(models.Model):
    _name='contract.reservation'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", required=True)
    date = fields.Date(string="Date", required=True)
    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner", required=True)
    property_id = fields.Many2one('product.product', ('Property'), required=False,context="{'form_view_ref': 'add_real_estate.rs_property_product2_form_view2'}",domain=[('state', '=', 'available')], )
    property_price = fields.Float(string="Property Price", required=False)
    property_space = fields.Float(string="Property Space", required=False)
    reservation_id = fields.Many2one(comodel_name="res.reservation", string="Reservation")
    day_name = fields.Char(compute='_calc_day_name', store=True)
    state = fields.Selection(string="Status", selection=[('draft', 'Draft'), ('confirmed', 'Confirmed'), ('cancel', 'Cancel') ], default='draft',tracking=True)

    def get_price(self):
        return num2words(self.property_price, lang="ar").title()


    def cancel(self):
        self.write({'state':'cancel'})
    def confirmed(self):
        self.write({'state':'confirmed'})
    def reset_to_draft(self):
        self.write({'state':'draft'})


    @api.depends('date')
    def _calc_day_name(self):
        for rec in self:
            if rec.date:
                date = datetime.strptime(str(rec.date), "%Y-%m-%d").strftime("%A")
                if date == 'Saturday':
                    rec.day_name = "السبت"

                if date == 'Sunday':
                    rec.day_name = "الاحد"

                if date == 'Monday':
                    rec.day_name = "الاثنين"

                if date == 'Tuesday':
                    rec.day_name = "الثلاثاء"

                if date == 'Wednesday':
                    rec.day_name = "الاربعاء"

                if date == 'Thursday':
                    rec.day_name = "الخميس"
                if date == 'Friday':
                    rec.day_name = "الجمعة"
                print(date)


