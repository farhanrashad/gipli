from odoo import api, exceptions, fields, models, _


class SaleCommission(models.Model):
    _name = "sale.commission"
    _description = "Commission in sales"

    def calculate_section(self, base):
        self.ensure_one()
        for section in self.sections:
            if section.amount_from <= base <= section.amount_to:
                return base * section.percent / 100.0
        return 0.0

    salesmen2 = fields.Many2many(comodel_name='res.partner')
    salesmen = fields.Many2many(comodel_name='res.users')
    sales_team = fields.Many2many(comodel_name='crm.team')

    name = fields.Char('Name', required=True)
    commission_type = fields.Selection(
        selection=[("fixed", "Fixed percentage"),
                   ("section", "By sections")],
        string="Type", required=True, default="fixed")
    apply_to = fields.Selection(
        selection=[("salesman", "Salesman"),
                   ("team", "Sales Team")],
        string="Apply to", required=True, default="salesman")

    fix_qty = fields.Float(string="Fixed percentage")
    leader_fix_qty = fields.Float(string="Leader Fixed percentage")
    sections = fields.One2many(
        comodel_name="sale.commission.section", inverse_name="commission")
    active = fields.Boolean(default=True)
    contract_state = fields.Selection(
        [('open', 'Contract Based'),
         ('paid', 'Payment Based')], string='Contract Status',
        required=True, default='open')

class SaleCommissionSection(models.Model):
    _name = "sale.commission.section"
    _description = "Commission section"

    commission = fields.Many2one("sale.commission", string="Commission")
    amount_from = fields.Float(string="From")
    amount_to = fields.Float(string="To")
    percent = fields.Float(string="Percent", required=True)
    leader_percent = fields.Float(string="Leader Percent", required=True)

    @api.constrains('amount_from', 'amount_to')
    def _check_amounts(self):
        if self.amount_to < self.amount_from:
            raise exceptions.ValidationError(
                _("The lower limit cannot be greater than upper one."))

class CommissionLine(models.Model):
    _name = "commission.line"
    _description = "Commission line"

    salesman = fields.Many2one(
        comodel_name="res.users", required=True, ondelete="restrict")
    amount = fields.Float(string="Amount", digits=(16, 4))
    date = fields.Date(string="Date")


