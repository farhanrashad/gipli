from odoo import models, fields, api, _

class account_journal(models.Model):

    _inherit = 'account.journal'
    default_debit_account_id = fields.Many2one('account.account', string='Default Debit Account',
                                               domain="[('deprecated', '=', False), ('company_id', '=', company_id)]",
                                               help="It acts as a default account for debit amount",
                                               ondelete='restrict')

    payment_subtype = fields.Selection([('issue_check',_('Issued Checks')),('rece_check',_('Received Checks'))],string="Payment Subtype")
    bank_required= fields.Boolean( string='Bank Required')
    depoist= fields.Boolean( string='Depoist')
    send_to_lagel= fields.Boolean( string='Send To Legal')
    deliver= fields.Boolean( string='Deliver')
    withdrawal= fields.Boolean( string='Receivable Withdrawal')
    payable_withdrawal= fields.Boolean( string='Payable Withdrawal')
    payable_withdrawal_journal_id = fields.Many2one('account.journal', string='Payable Withdrawal Journal')
    receivable_withdrawal_journal_id = fields.Many2one('account.journal', string='Receivable Withdrawal Journal')
    petty_cash = fields.Boolean(
        string='Petty Cash',
        required=False)
class account_account(models.Model):

    _inherit = 'account.account'
    english_name = fields.Char(string='English Name')
    account_1_id = fields.Many2one(comodel_name="accounts.account1", string="Account1")
    account_2_id = fields.Many2one(comodel_name="accounts.account2", string="Account2")
    account_3_id = fields.Many2one(comodel_name="accounts.account3", string="Account3")
    dimensions_parent_id = fields.Many2one(comodel_name="dimensions.parent", string="Dimensions Parent")
    dimensions_name_id = fields.Many2one(comodel_name="dimensions.name", string="Dimensions Name")

