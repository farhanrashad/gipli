import json

from odoo import models, fields, api, exceptions,_
from datetime import date, datetime, time, timedelta
from dateutil.relativedelta import relativedelta

class check_cycle_accs(models.TransientModel):

    _name = 'check.cycle.accounts.default'

    @api.model
    def get_check_lines(self):
        checks = self.env['check.management'].search([('id', 'in', self.env.context['active_ids'])])
        app_checks = []
        for ch in reversed(checks):
            val = {}
            val['check_number'] = ch.check_number
            val['check_id'] = ch.id
            val['check_amt'] = ch.amount
            val['paid_amt'] = ch.open_amount
            val['open_amt'] = ch.open_amount
            val['open_amt'] = ch.open_amount
            line = self.env['appove.check.lines'].create(val)
            # app_checks.append((0,0, val))
            app_checks.append(line.id)
        return app_checks

    name = fields.Char(default="Please choose the bank Account",readonly=True)
    name_cancel = fields.Char(default="Are you sure you want to cancel the checks", readonly=True)
    name_reject = fields.Char(default="Are you sure you want to reject the checks", readonly=True)
    name_return = fields.Char(default="Are you sure you want to return the checks to company", readonly=True)
    name_approve = fields.Char(default="Please choose the bank Account", readonly=True)
    name_debit = fields.Char(default="Please choose the bank Account", readonly=True)
    name_csreturn = fields.Char(default="Are you sure you want to return the checks to customer", readonly=True)
    name_split_merge = fields.Char(default="Please create the new checks", readonly=True)
    account_id = fields.Many2one('account.account',string="Account")
    journal_id = fields.Many2one('account.journal',string="Journal")
    reject_reason = fields.Text(string="Rejection reason")
    approve_check = fields.Many2many('appove.check.lines',ondelete="cascade",default=get_check_lines)
    total_amt_checks = fields.Float(string="total Amount of Checks",compute="getcheckstotamt")
    merge_split_checks = fields.Many2many('split.merge.check',ondelete="cascade")
    investor_spilt = fields.Many2one('res.partner',string=_("Partner"))
    date = fields.Date(string='Date')

    action_wiz = fields.Char()

    @api.onchange('action_wiz')
    def _compute_journal_domain(self):
        if self.action_wiz=='depoist':
            journal_domain = "[('depoist','=',True)]"



        elif self.action_wiz=='send_to_lagel':
           journal_domain = [('send_to_lagel','=',True)]

        elif self.action_wiz=='deliver':
            journal_domain = [('deliver','=',True)]

        elif self.action_wiz== 'debit':
            journals=[]
            checks = self.env['check.management'].search([('id', 'in', self.env.context['active_ids'])])
            for chk in checks:
                if chk.handed_move_id:
                    journals.append(chk.handed_move_id.journal_id.id)
            if journals:
                journal_domain = [('payable_withdrawal', '=', True),('payable_withdrawal_journal_id','in',journals)]
            else:
                journal_domain = []
        elif self.action_wiz== 'approve':
            journals=[]
            checks = self.env['check.management'].search([('id', 'in', self.env.context['active_ids'])])
            for chk in checks:
                if chk.depoist_move_id:
                    journals.append(chk.depoist_move_id.journal_id.id)
            if journals:
                journal_domain = [('withdrawal', '=', True),('receivable_withdrawal_journal_id','in',journals)]
            else:
                journal_domain = []
        else:
           journal_domain = []
        print(">D>>D>DD>D>D>",journal_domain)
        return {'domain': {'journal_id': journal_domain}}









    # @api.multi
    @api.depends('name_split_merge')
    def getcheckstotamt(self):
        print("D>D>D>D")
        #check same customer
        if self.env.context['action_wiz']=='split_merge':
            checks = self.env['check.management'].search([('id', 'in', self.env.context['active_ids'])])
            if any(inv.investor_id != checks[0].investor_id for inv in checks):
                raise exceptions.ValidationError(_("u cant split checks for different customers ."))

        for rec in self:
            rec.total_amt_checks = 0
            checks = rec.env['check.management'].search([('id', 'in', self.env.context['active_ids'])])
            for ch in checks:
                rec.total_amt_checks += ch.open_amount
                rec.investor_spilt = ch.investor_id.id
    # @api.multi
    def action_save(self):
        if 'action_wiz' in self.env.context:
            if self.env.context['action_wiz'] == 'depoist':
                if not self.journal_id:
                    raise exceptions.ValidationError(_('Please provide the bank account'))
                checks = self.env['check.management'].search([('id', 'in', self.env.context['active_ids'])])
                batch=self.env['ir.sequence'].next_by_code('check.payment.batch') or _("New")
                for check in checks:
                    # if not check.dep_bank:
                    #     raise exceptions.ValidationError(_('Please provide the deposit bank '))
                    # if not check.will_collection_user:
                    #     raise exceptions.ValidationError(_('Please Put Bank Maturity Date For Reporting  '))
                    move = {
                        'journal_id': self.journal_id.id,
                        'date': self.date,
                        'ref': 'Depoisting Check number ' + check.check_number,
                        'company_id': self.env.company.id,
                        'reservation_id': check.reservation_id.id,
                        'check_payment_id': check.check_payment_id.id,
                        'check_id': check.id,
                        'due_date': check.check_date,
                        'cheque': check.check_number,
                    }

                    move_line = {
                        'name': 'Depoisting Check number ' + check.check_number,
                        'partner_id': check.investor_id.id,
                        'ref': 'Depoisting Check number ' + check.check_number,
                    }

                    debit_account = []
                    credit_account = []
                    debit_account.append({'account': self.journal_id.default_debit_account_id.id, 'percentage': 100})
                    if check.notes_rece_id:
                        credit_account.append({'account': check.notes_rece_id.id, 'percentage': 100})
                    else:
                        credit_account.append({'account': check.unit_id.project_id.NotesReceivableAccount.id, 'percentage': 100})
                    depoist_move_id=self.sudo().env['create.moves'].create_move_lines(move=move, move_line=move_line,
                                                               debit_account=debit_account,
                                                               credit_account=credit_account,
                                                               src_currency=check.currency_id,
                                                               amount=check.open_amount)
                    check.state = 'depoisted'
                    check.under_collect_id = self.journal_id.default_debit_account_id.id
                    check.under_collect_jour = self.journal_id.id
                    check.depoist_move_id = depoist_move_id.id
                    check.batch=batch
            elif self.env.context['action_wiz'] == 'send_to_lagel':
                if not self.journal_id:
                    raise exceptions.ValidationError(_('Please provide the bank account'))
                checks = self.env['check.management'].search([('id', 'in', self.env.context['active_ids'])])
                for check in checks:
                    # if not check.dep_bank:
                    #     raise exceptions.ValidationError(_('Please provide the deposit bank '))
                    # if not check.will_collection_user:
                    #     raise exceptions.ValidationError(_('Please Put Bank Maturity Date For Reporting  '))
                    move = {
                        'journal_id': self.journal_id.id,
                        'date': self.date,
                        'ref': 'Send To Legal Check number ' + check.check_number,
                        'company_id': self.env.company.id,
                        'reservation_id': check.reservation_id.id,
                        'check_payment_id': check.check_payment_id.id,
                        'check_id': check.id,
                        'due_date': check.check_date,
                        'cheque': check.check_number,

                    }

                    move_line = {
                        'name': 'Send To Legal Check number ' + check.check_number,
                        'partner_id': check.investor_id.id,
                        'ref': 'Send To Legal Check number ' + check.check_number,
                    }

                    debit_account = []
                    credit_account = []
                    debit_account.append({'account': self.journal_id.default_debit_account_id.id, 'percentage': 100})
                    if check.notes_rece_id:
                        credit_account.append({'account': check.notes_rece_id.id, 'percentage': 100})
                    else:
                        credit_account.append({'account': check.unit_id.project_id.NotesReceivableAccount.id, 'percentage': 100})
                    move_id=self.sudo().env['create.moves'].create_move_lines(move=move, move_line=move_line,
                                                               debit_account=debit_account,
                                                               credit_account=credit_account,
                                                               src_currency=check.currency_id,
                                                               amount=check.open_amount)
                    check.state = 'send_to_lagel'
                    check.under_collect_id = self.journal_id.default_debit_account_id.id
                    check.under_collect_jour = self.journal_id.id
                    check.send_to_lagel_move_id=move_id.id
            elif self.env.context['action_wiz'] == 'approve':
                if not self.journal_id:
                    raise exceptions.ValidationError(_('Please provide the bank account'))
                for approve_ch_line in self.approve_check:
                    z=""
                    for x in self.approve_check:
                        z=z+(str(x.open_amt))+","
                    if approve_ch_line.open_amt < approve_ch_line.paid_amt:
                        raise exceptions.ValidationError(_('The paid amount is greater than open amount for some checks\n'+z))
                checks = self.env['check.management'].search([('id', 'in', self.env.context['active_ids'])])
                for check in checks:
                    debit_account = []
                    credit_account = []
                    move = {
                        'journal_id': self.journal_id.id,
                        'date': self.date,
                        'ref': 'Approving Check number ' + check.check_number,
                        'company_id': self.env.company.id,
                        'reservation_id': check.reservation_id.id,
                        'check_payment_id': check.check_payment_id.id,
                        'check_id': check.id,
                        'due_date': check.check_date,
                        'cheque': check.check_number,

                    }
                    move_line = {
                        'name': 'Approving Check number ' + check.check_number,
                        'partner_id': check.investor_id.id,
                        'ref': 'Approving Check number ' + check.check_number,
                    }
                    checkamt = check.amount
                    for approve_ch_line in self.approve_check:
                        if approve_ch_line.check_id == check.id:
                            checkamt = approve_ch_line.paid_amt
                            check.open_amount -= approve_ch_line.paid_amt
                    if check.investor_id:
                        debit_account.append({'account': self.journal_id.default_debit_account_id.id, 'percentage': 100})
                        if check.under_collect_id:
                            credit_account.append({'account': check.under_collect_id.id, 'percentage': 100})
                        else:
                            credit_account.append({'account': check.notes_rece_id.id, 'percentage': 100})

                        if check.state == 'returned':
                            if check.notes_rece_id:
                                credit_account.append({'account': check.notes_rece_id.id, 'percentage': 100})
                            else:
                                credit_account.append(
                                    {'account': check.unit_id.project_id.NotesReceivableAccount.id, 'percentage': 100})
                        # elif check.state != 'returned':
                        #     if check.under_collect_id:
                        #         credit_account.append(
                        #             {'account': check.under_collect_id.id, 'percentage': 100})
                        #     else:
                        #         if check.notes_rece_id:
                        #             credit_account.append({'account': check.notes_rece_id.id, 'percentage': 100})
                        #         else:
                        #             credit_account.append(
                        #                 {'account': check.unit_id.project_id.NotesReceivableAccount.id, 'percentage': 100})

                    if checkamt > 0.0:
                        self.sudo().env['create.moves'].create_move_lines(move=move, move_line=move_line,
                                                               debit_account=debit_account,
                                                               credit_account=credit_account,
                                                               src_currency=check.currency_id,
                                                               amount=checkamt)
                    if check.open_amount == 0.0:
                        check.state = 'approved'
            elif self.env.context['action_wiz'] == 'reject':
                checks = self.env['check.management'].search([('id', 'in', self.env.context['active_ids'])])
                for check in checks:
                    check.state = 'rejected'
                    check.reject_date =self.date
                    message = "Rejection Reason is " + str(self.reject_reason)
                    check.message_post(body=message)
            elif self.env.context['action_wiz'] == 'return':
                checks = self.env['check.management'].search([('id', 'in', self.env.context['active_ids'])])
                for check in checks:
                    move = {
                        'journal_id': check.under_collect_jour.id,
                        'date': self.date,
                        'ref': 'Returning Check number ' + check.check_number,
                        'company_id': self.env.company.id,
                        'reservation_id': check.reservation_id.id,
                        'check_payment_id': check.check_payment_id.id,
                        'check_id': check.id,
                        'due_date': check.check_date,
                        'cheque': check.check_number,

                    }

                    move_line = {
                        'name': 'Returning Check number ' + check.check_number,
                        'partner_id':  check.investor_id.id,#check.partner_id.id or
                        'ref': 'Returning Check number ' + check.check_number,
                    }
                    debit_account = []
                    credit_account = []
                    credit_account.append({'account': check.under_collect_jour.default_debit_account_id.id, 'percentage': 100})
                    if check.notes_rece_id:
                        debit_account.append({'account': check.notes_rece_id.id, 'percentage': 100})
                    else:
                        debit_account.append({'account': check.unit_id.project_id.NotesReceivableAccount.id, 'percentage': 100})
                    self.sudo().env['create.moves'].create_move_lines(move=move, move_line=move_line,
                                                               debit_account=debit_account,
                                                               credit_account=credit_account,
                                                                      src_currency=check.currency_id,
                                                               amount=check.open_amount)
                    check.state = 'returned'
                    check.reject_reason =self.reject_reason

            elif self.env.context['action_wiz'] == 'debit':
                if not self.journal_id:
                    raise exceptions.ValidationError(_('Please provide the bank account'))
                checks = self.env['check.management'].search([('id', 'in', self.env.context['active_ids'])])
                for check in checks:
                    move = {
                        'journal_id': self.journal_id.id,
                        'date': self.date,
                        'ref': 'Debiting Check number ' + check.check_number,
                        'company_id': self.env.company.id,
                        'reservation_id': check.reservation_id.id,
                        'check_payment_id': check.check_payment_id.id,
                        'check_id': check.id,
                        'due_date': check.check_date,
                        'cheque': check.check_number,

                    }
                    move_line = {
                        'name': 'Debiting Check number ' + check.check_number,
                        'partner_id': check.investor_id.id,
                        'ref': 'Debiting Check number ' + check.check_number,
                    }


                    debit_account = []
                    credit_account = []
                    credit_account.append({'account': self.journal_id.default_debit_account_id.id, 'percentage': 100})
                    if check.deliver_move_id:
                        debit_account.append({'account':check.deliver_move_id.journal_id.default_debit_account_id.id, 'percentage': 100})
                    else:
                        debit_account.append({'account':check.notespayable_id.id, 'percentage': 100})
                    self.sudo().env['create.moves'].create_move_lines(move=move, move_line=move_line,
                                                               debit_account=debit_account,
                                                               credit_account=credit_account,
                                                               src_currency=check.currency_id,
                                                               amount=check.amount)
                    check.state = 'debited'
            elif self.env.context['action_wiz'] == 'deliver':
                if not self.journal_id:
                    raise exceptions.ValidationError(_('Please provide the bank account'))
                checks = self.env['check.management'].search([('id', 'in', self.env.context['active_ids'])])
                for check in checks:
                    move = {
                        'journal_id': self.journal_id.id,
                        'date': self.date,
                        'ref': 'Debiting Check number ' + check.check_number,
                        'company_id': self.env.company.id,
                        'reservation_id': check.reservation_id.id,
                        'check_payment_id': check.check_payment_id.id,
                        'check_id': check.id,
                        'due_date': check.check_date,
                        'cheque': check.check_number,

                    }
                    move_line = {
                        'name': 'Debiting Check number ' + check.check_number,
                        'partner_id': check.investor_id.id,
                        'ref': 'Debiting Check number ' + check.check_number,
                    }


                    debit_account = []
                    credit_account = []
                    credit_account.append({'account': self.journal_id.default_debit_account_id.id, 'percentage': 100})
                    debit_account.append({'account': check.notespayable_id.id, 'percentage': 100})
                    move_id=self.sudo().env['create.moves'].create_move_lines(move=move, move_line=move_line,
                                                               debit_account=debit_account,
                                                               credit_account=credit_account,
                                                                              src_currency=check.currency_id,
                                                               amount=check.amount)
                    check.state = 'deliver'
                    check.deliver_move_id = move_id.id
            elif self.env.context['action_wiz'] == 'cs_return':
                checks = self.env['check.management'].search([('id', 'in', self.env.context['active_ids'])])
                journal_id = self.env['account.journal'].search([('payment_subtype','=','rece_check'),('type','=','bank')],limit=1).id
                for check in checks:
                    move = {
                        'journal_id': journal_id,
                        'date': self.date,
                        'ref': 'Returning Check number ' + check.check_number + ' to customer',
                        'company_id': self.env.company.id,
                        'reservation_id': check.reservation_id.id,
                        'check_payment_id': check.check_payment_id.id,
                        'check_id': check.id,
                        'due_date': check.check_date,
                        'cheque': check.check_number,

                    }
                    move_line = {
                        'name': 'Returning Check number ' + check.check_number + ' to customer',
                        'partner_id': check.investor_id.id,
                        'ref': 'Returning Check number ' + check.check_number + ' to customer',
                    }

                    if check.investor_id:
                        debit_account = [{'account':check.check_payment_id.account_id.id , 'percentage' : 100}]
                        credit_account = [{'account': check.notespayable_id.id,'percentage' : 100}]
                        self.env['create.moves'].create_move_lines(move=move, move_line=move_line,
                                                                   debit_account=debit_account,
                                                                   credit_account=credit_account,
                                                                   src_currency=check.currency_id,
                                                                   amount=check.amount)


                    check.state = 'cs_return'
                    check.check_state = 'suspended'
            elif self.env.context['action_wiz'] == 'refund_send_to_lagel':
                checks = self.env['check.management'].search([('id', 'in', self.env.context['active_ids'])])
                for check in checks:
                    if check.send_to_lagel_move_id:
                        new_move=check.send_to_lagel_move_id._reverse_moves()
                        new_move.write({'date':self.date})
                        new_move.action_post()
                    check.state = 'refund_send_to_lagel'
                    check.check_state = 'suspended'
            elif self.env.context['action_wiz'] == 'refund_deliver':
                checks = self.env['check.management'].search([('id', 'in', self.env.context['active_ids'])])
                for check in checks:
                    if check.deliver_move_id:
                        new_move=check.deliver_move_id._reverse_moves()
                        new_move.write({'date':self.date})
                        new_move.action_post()
                    check.state = 'refund_deliver'
                    check.check_state = 'suspended'
            elif self.env.context['action_wiz'] == 'refund':
                checks = self.env['check.management'].search([('id', 'in', self.env.context['active_ids'])])
                for check in checks:
                    if check.handed_move_id:
                        new_move=check.handed_move_id._reverse_moves()
                        new_move.write({
                            'date':self.date,
                            'reservation_id':check.deliver_move_id.reservation_id.id,
                            'check_payment_id': check.check_payment_id.id,
                            'check_id':check.deliver_move_id.check_id.id,
                            # 'due_date': check.check_date,
                            'cheque':check.check_number,

                                        })
                        new_move.action_post()
                    check.state = 'refund'
                    check.check_state = 'suspended'
            elif self.env.context['action_wiz'] == 'deliver_to_customer':
                checks = self.env['check.management'].search([('id', 'in', self.env.context['active_ids'])])
                for check in checks:
                    check.state = "delivery_to_customer"
                    check.deliver_to_customer_date = self.date
            elif self.env.context['action_wiz'] == 'split_merge':
                checks = self.env['check.management'].search([('id', 'in', self.env.context['active_ids'])])
                #check same customer
                if any(inv.investor_id != checks[0].investor_id for inv in checks):
                    raise exceptions.ValidationError(_("u cant split checks for different customers ."))

                for x in checks:
                    if not x.notes_rece_id:
                        raise exceptions.ValidationError(_('Action not allowed on normal checks'))
                new_tot_amt = 0
                notes_rece_id = 0
                ch_state = 'holding'
                ch_patner = x.investor_id.id
                if checks[0]:

                    notes_rece_id = checks[0].notes_rece_id.id
                    ch_state = checks[0].state
                else:
                    raise exceptions.ValidationError(_('Action not allowed on normal checks'))
                for ch in checks:
                    if notes_rece_id != ch.notes_rece_id.id:
                        raise exceptions.ValidationError(
                            _('You can not merge checks from different journals'))
                for sp_mr_checks in self.merge_split_checks:
                    new_tot_amt += sp_mr_checks.amount
                if new_tot_amt != self.total_amt_checks:
                    raise exceptions.ValidationError(_('Amount of new Checks is not equal to amount of selected checks'))

                for sp_mr_checks in self.merge_split_checks:
                    check_line_val = {}
                    check_line_val['check_number'] = sp_mr_checks.check_number
                    check_line_val['check_date'] = sp_mr_checks.check_date
                    check_line_val['check_bank'] = sp_mr_checks.bank.id
                    check_line_val['dep_bank'] = sp_mr_checks.dep_bank.id
                    check_line_val['amount'] = sp_mr_checks.amount
                    check_line_val['open_amount'] = sp_mr_checks.amount
                    check_line_val['amount_res'] = 0
                    check_line_val['amount_con'] = 0
                    check_line_val['amount_gar'] = 0
                    check_line_val['amount_mod'] = 0
                    check_line_val['amount_ser'] = 0
                    check_line_val['amount_reg'] = 0
                    check_line_val['state'] = ch_state
                    check_line_val['investor_id'] = ch_patner
                    check_line_val['type'] = 'regular'
                    check_line_val['check_type'] = 'rece'
                    check_line_val['notes_rece_id'] = notes_rece_id
                    check_line_val['notespayable_id'] = notes_rece_id
                    new_check = self.env['check.management'].create(check_line_val)
                for x in checks:
                    x.unlink()
        else:
            raise exceptions.ValidationError(_('Unknown Action'))
        return True






class approve_check_lines(models.Model):

    _name = 'appove.check.lines'

    check_number = fields.Char()
    check_id = fields.Integer()
    check_amt = fields.Float()
    paid_amt = fields.Float()
    open_amt = fields.Float()



class split_merge_check(models.Model):

    _name = 'split.merge.check'
    _order = 'check_number asc'

    check_number = fields.Char(string=_("Check number"),required=True)
    check_date = fields.Date(string=_('Check Date'),required=True)
    amount = fields.Float(string=_('Amount'),required=True)
    bank = fields.Many2one('payment.bank',string=_("Check Bank Name"))
    dep_bank = fields.Many2one('payment.bank',string=_("Depoist Bank"))

