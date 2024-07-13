from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
import base64
from odoo.exceptions import UserError, ValidationError
import time

class Account(models.Model):
    _inherit='account.account'
    account_ref = fields.Boolean(string="Account Reference?")
    account_ref_id = fields.Many2one(comodel_name="account.ref")
    paid_or_no = fields.Selection(string='Paid/Unpaid',
        selection=[('paid', 'Paid'),
                   ('unpaid', 'Unpaid'), ],
        required=False, )
    petty = fields.Boolean(string="سلف", )
    custody = fields.Boolean(string="عهد")
    accrued = fields.Boolean(string="مصروف رواتب مستحقة")
    other = fields.Boolean(string="مصروف عمولات مستحقة")
    expenses_for_unit_check = fields.Boolean(string="Expenses For Unit")
    is_batch_deposit = fields.Boolean()
    accounting_allocation = fields.Selection(
        string='Accounting Allocation',
        selection=[('maintenance', 'Maintenance'),
                   ('deposit', 'Deposit'),
                   ('insurance', 'Insurance'),
                   ('eoi', 'EOI'),
                   ],
        required=False, )
    
    partner_required_in_journal_entry = fields.Boolean(
        string='Partner Required In Journal Entry?',
        required=False)
        


    # @api.model
    # def check_access_rights(self, operation, raise_exception=True):
    #     res = super(Account, self).check_access_rights(operation, raise_exception=raise_exception)
    #     if operation == 'create':
    #         if self.env.user.has_group('add_real_estate.group_create_account') == False:
    #             return False
    #         else:
    #             return res
    #     if operation == 'write':
    #         if self.env.user.has_group('add_real_estate.group_create_account') == False:
    #             return False
    #         else:
    #             return res
    #     return res




class StatementLine(models.Model):
    _inherit='account.bank.statement.line'
    account_ref_id = fields.Many2one(comodel_name="account.ref")
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', groups="analytic.group_analytic_accounting")
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')


    @api.onchange('account_ref_id')
    def onchange_account_ref_id(self):
        if self.account_ref_id:
            self.ref=self.account_ref_id.name
            account=self.env['account.account'].search([('account_ref_id','=',self.account_ref_id.id),('account_ref','=',True)],limit=1)
            if account:
                self.account_id=account.id

    def fast_counterpart_creation(self):
        """This function is called when confirming a bank statement and will allow to automatically process lines without
        going in the bank reconciliation widget. By setting an account_id on bank statement lines, it will create a journal
        entry using that account to counterpart the bank account
        """
        payment_list = []
        move_list = []
        account_type_receivable = self.env.ref('account.data_account_type_receivable')
        already_done_stmt_line_ids = [a['statement_line_id'][0] for a in self.env['account.move.line'].read_group([('statement_line_id', 'in', self.ids)], ['statement_line_id'], ['statement_line_id'])]
        managed_st_line = []
        for st_line in self:
            # Technical functionality to automatically reconcile by creating a new move line
            if st_line.account_id and not st_line.id in already_done_stmt_line_ids:
                managed_st_line.append(st_line.id)
                # Create payment vals
                total = st_line.amount
                payment_methods = (total > 0) and st_line.journal_id.inbound_payment_method_ids or st_line.journal_id.outbound_payment_method_ids
                currency = st_line.journal_id.currency_id or st_line.company_id.currency_id
                partner_type = 'customer' if st_line.account_id.user_type_id == account_type_receivable else 'supplier'
                payment_list.append({
                    'payment_method_id': payment_methods and payment_methods[0].id or False,
                    'payment_type': total > 0 and 'inbound' or 'outbound',
                    'partner_id': st_line.partner_id.id,
                    'partner_type': partner_type,
                    'journal_id': st_line.statement_id.journal_id.id,
                    'date': st_line.date,
                    'state': 'reconciled',
                    'currency_id': currency.id,
                    'amount': abs(total),
                    'communication': st_line._get_communication(payment_methods[0] if payment_methods else False),
                    # 'name': st_line.statement_id.name or _("Bank Statement %s") % st_line.date,
                    'name':self.get_payment_no(partner_type,total > 0 and 'inbound' or 'outbound',st_line.date)
                })

                # Create move and move line vals
                move_vals = st_line._prepare_reconciliation_move(st_line.statement_id.name)
                move_vals['document_type_id'] = self.statement_id.document_type_id.id
                move_vals['external_document_number'] = self.statement_id.external_document_number
                move_vals['external_document_type'] = self.statement_id.external_document_type
                move_vals['ref'] = self.statement_id.name
                move_vals['statement_ref'] = self.statement_id.name
                print("D>D>",move_vals)
                aml_dict = {
                    'name': st_line.name,
                    'debit': st_line.amount < 0 and -st_line.amount or 0.0,
                    'credit': st_line.amount > 0 and st_line.amount or 0.0,
                    'account_id': st_line.account_id.id,
                    'partner_id': st_line.partner_id.id,
                    'statement_line_id': st_line.id,
                }
                st_line._prepare_move_line_for_currency(aml_dict, st_line.date or fields.Date.context_today())
                move_vals['line_ids'] = [(0, 0, aml_dict)]
                balance_line = self._prepare_reconciliation_move_line(
                    move_vals, -aml_dict['debit'] if st_line.amount < 0 else aml_dict['credit'])
                move_vals['line_ids'].append((0, 0, balance_line))
                for mline in  move_vals['line_ids']:
                    print(">S>S>",mline)
                    mline[2]['analytic_tag_ids']=[(6, 0,  st_line.analytic_tag_ids.ids or [])]
                    mline[2]['analytic_account_id']=st_line.analytic_account_id.id

                move_list.append(move_vals)

        # Creates
        payment_ids = self.env['account.payment'].create(payment_list)
        for payment_id, move_vals in zip(payment_ids, move_list):
            for line in move_vals['line_ids']:
                line[2]['payment_id'] = payment_id.id
        move_ids = self.env['account.move'].create(move_list)
        # move_ids.post()

        for move, st_line, payment in zip(move_ids, self.browse(managed_st_line), payment_ids):
            st_line.write({'move_name': move.name})
            payment.write({'payment_reference': move.name})

    def get_payment_no(self,partner_type,payment_type,date):
        if partner_type == 'customer':
            if payment_type == 'inbound':
                sequence_code = 'account.payment.customer.invoice'
            if payment_type == 'outbound':
                sequence_code = 'account.payment.customer.refund'
        if partner_type == 'supplier':
            if payment_type == 'inbound':
                sequence_code = 'account.payment.supplier.refund'
            if payment_type == 'outbound':
                sequence_code = 'account.payment.supplier.invoice'
        name=self.env['ir.sequence'].next_by_code(sequence_code, sequence_date=date)
        return name






class AccountReference(models.Model):
    _name='account.ref'
    name = fields.Char(string="Name", required=True)


class Statemen(models.Model):
    _inherit='account.bank.statement'
    move_stat = fields.Char(string="Move Status",compute="_calc_move_state",store=False,search="search_filter_move_stat")
    document_type_id = fields.Many2one(comodel_name="move.doc.type", string="نوع المستند", required=False)
    external_document_number = fields.Char(string="رقم المستند الخارجي", required=False)
    external_document_type = fields.Char(string="نوع المستند الخارجي", required=False)


    # @api.depends('move_line_ids')
    def _calc_move_state(self):
        for rec in self:
            state="draft"
            for move in self.mapped('move_line_ids').mapped('move_id'):
                state=move.state
            rec.move_stat =state

    def search_filter_move_stat(self, operator, value):
        vls = []
        if operator == '=' and value:
            for rec in self.env['account.bank.statement'].search([]):
                for move in rec.mapped('move_line_ids').mapped('move_id'):
                    print(">>>",move.state,value)
                    if move.state==value:
                        vls.append(rec.id)
            return [('id', 'in', vls)]

    
    
    def button_confirm_bank(self):
        self._balance_check()
        statements = self.filtered(lambda r: r.state == 'open')
        accounts2=[]
        for statement in statements:
            moves = self.env['account.move']
            # `line.journal_entry_ids` gets invalidated from the cache during the loop
            # because new move lines are being created at each iteration.
            # The below dict is to prevent the ORM to permanently refetch `line.journal_entry_ids`
            line_journal_entries = {line: line.journal_entry_ids for line in statement.line_ids}
            for st_line in statement.line_ids:
                if st_line.account_id.id not in accounts2:
                    accounts2.append(st_line.account_id.id)
                #upon bank statement confirmation, look if some lines have the account_id set. It would trigger a journal entry
                #creation towards that account, with the wanted side-effect to skip that line in the bank reconciliation widget.
                journal_entries = line_journal_entries[st_line]
                st_line.fast_counterpart_creation()
                if not st_line.account_id and not journal_entries.ids and not st_line.statement_id.currency_id.is_zero(st_line.amount):
                    raise UserError(_('All the account entries lines must be processed in order to close the statement.'))
            moves = statement.mapped('line_ids.journal_entry_ids.move_id')
            lines=[]
            accounts=moves.mapped('line_ids.account_id.id')

            if moves:
                for account_id in accounts:
                    line_ids = moves.line_ids.filtered(lambda line: line.account_id.id == account_id)
                    print("D>",account_id,line_ids)
                    if line_ids:
                        if len(line_ids)>1 and line_ids.filtered(lambda line: line.account_id.id in accounts2) :
                            for line in line_ids:
                                lline = (0, 0, {
                                    'account_id': line.account_id.id,
                                    'partner_id': line.partner_id.id,
                                    'name': line.name,
                                    'currency_id': line.currency_id.id,
                                    'debit': line.debit,
                                    'credit': line.credit,
                                    'statement_line_id': line.statement_line_id.id,
                                    'analytic_account_id': line.analytic_account_id.id,
                                    'analytic_tag_ids': [(6, 0, line.analytic_tag_ids.ids or [])],
                                })
                                lines.append(lline)
                        else:
                            lline = (0, 0, {
                                'account_id': line_ids[0].account_id.id,
                                'partner_id': line_ids[0].partner_id.id,
                                'name': line_ids[0].name,
                                'currency_id': line_ids[0].currency_id.id,
                                'debit': sum(line_ids.mapped('debit')),
                                'credit': sum(line_ids.mapped('credit')),
                                'statement_line_id': line_ids[0].statement_line_id.id,
                                'analytic_account_id': line_ids[0].analytic_account_id.id,
                                'analytic_tag_ids': [(6, 0, line_ids[0].analytic_tag_ids.ids or [])],
                            })
                            lines.append(lline)
                merged_move =moves[0].copy()
                merged_move.line_ids.unlink()
                merged_move['line_ids']=lines
                moves.unlink()
                print("D>D>",merged_move)
                # moves.filtered(lambda m: m.state != 'posted').post()
            statement.message_post(body=_('Statement %s confirmed, journal items were created.') % (statement.name,))
            if statement.journal_id.type == 'bank':
                # Attach report to the Bank statement
                content, content_type = self.env.ref('account.action_report_account_statement').render_qweb_pdf(statement.id)
                self.env['ir.attachment'].create({
                    'name': statement.name and _("Bank Statement %s.pdf") % statement.name or _("Bank Statement.pdf"),
                    'type': 'binary',
                    'datas': base64.encodestring(content),
                    'res_model': statement._name,
                    'res_id': statement.id
                })

    def makeconfirm(self):
        for stat in self:
            stat.write({'state': 'confirm', 'date_done': time.strftime("%Y-%m-%d %H:%M:%S")})

class Tax(models.Model):
    _inherit='account.tax'
    tax_code = fields.Char(string='كود')
    deal = fields.Selection(string='طبيعة التعامل',selection=[('s', 'خدمات'), ('i', 'توريد'),('c', 'استشارات وسمسرة') ])

