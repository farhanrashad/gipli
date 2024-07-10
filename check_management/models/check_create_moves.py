from odoo import models, fields, api, exceptions,_
from datetime import date, datetime, time, timedelta
from odoo.exceptions import RedirectWarning, UserError, ValidationError


# class acc_move(models.Model):
#
#     _inherit = 'account.move'

class move_lines(models.Model):

    _inherit = 'account.move.line'

    jebal_pay_id = fields.Integer(string="Jebal Payment",index=True)
    jebal_check_id = fields.Integer(string="Jebal Check",index=True)
    jebal_nrom_pay_id = fields.Integer(string="Jebal Check", index=True)
    jebal_con_pay_id = fields.Integer(string="Jebal Check", index=True)
    date_maturity = fields.Date(string='Due date', index=True, required=False,
                                help="This field is used for payable and receivable journal entries. You can put the limit date for the payment of this line.")
    check_payment_id = fields.Many2one('normal.payments', string=_('Check Payment'),related='move_id.check_payment_id',store=True)
    from_check_number = fields.Char(string=_("From Check Number"), required=False, default="0",related='move_id.from_check_number',store=True)
    from_check_date = fields.Date(string=_("From Check Date"), required=False,related='move_id.from_check_date',store=True)
    customer_type_id = fields.Many2one(comodel_name="customer.types", string="Customer Type",related='move_id.customer_type_id',store=True)

    # @api.model
    # def create(self,vals):
    #     res = super(move_lines,self).create(vals)
    #     res.date_maturity = False
    #     return res

    @api.constrains('currency_id', 'account_id','move_id')
    def _check_account_currency(self):
        for line in self:
            account_currency = line.check_payment_id.currency_id
            if account_currency and account_currency != line.company_currency_id and account_currency != line.currency_id:
                pass

    @api.model
    def _compute_amount_fields(self, amount, src_currency, company_currency,date,company):
        self = self.sudo()
        """ Helper function to compute value for fields debit/credit/amount_currency based on an amount and the currencies given in parameter"""
        amount_currency = amount
        currency_id = company_currency.id
        company=self.env['res.company'].browse(company)
        # date = self.env.context.get('date') or fields.Date.today()

        if src_currency and src_currency != company_currency:
            amount_currency = amount
            amount = src_currency._convert(amount, company_currency, company, date)
            print("D>D>D>",company, date,amount_currency,amount, src_currency.name, company_currency.name)
            currency_id = src_currency.id
        debit = amount > 0 and amount or 0.0
        credit = amount < 0 and -amount or 0.0
        return debit, credit, amount_currency, currency_id
class Move(models.Model):

    _inherit = 'account.move'
    check_id= fields.Many2one(comodel_name='check.management')
    check_payment_id = fields.Many2one('normal.payments', string=_('Check Payment'))
    from_check_number = fields.Char(string=_("From Check Number"), required=False, default="0",related='check_payment_id.from_check_number',store=True
                                   )
    from_check_date = fields.Date(string=_("From Check Date"), required=False,related='check_payment_id.from_check_date',store=True,readonly=False)
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        compute='_compute_journal_id', inverse='_inverse_journal_id', store=True, readonly=False, precompute=True,
        required=True,
        states={'draft': [('readonly', False)]},
        check_company=True,
        domain="[]",
    )
    customer_type_id = fields.Many2one(comodel_name="customer.types", string="Customer Type", required=False,track_visibility='onchange')
    custom_unit_price = fields.Float(
        string='مبلغ الوحده',
        required=False)


class PaymentStrgRequest(models.Model):
    _inherit= 'payment.strg.request'
    check_payment_id = fields.Many2one('normal.payments', _('Check Payment'))
class PaymentStrg(models.Model):
    _inherit= 'payment.strg'
    check_payment_id = fields.Many2one('normal.payments', _('Check Payment'))


class create_moves(models.Model):
    _name = 'create.moves'

    # @api.multi
    def create_move_lines(self, **kwargs):
        self.accounts_agg(**kwargs)
        self.adjust_move_percentage(**kwargs)
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        company_currency = self.env['res.users'].search([('id', '=', self._uid)]).company_id.currency_id
        date = kwargs.get('date')
        due_date=kwargs.get('due_date')

        if kwargs.get('move'):
            if kwargs.get('move').get('date'):
                date = kwargs.get('move').get('date')
        if kwargs.get('move'):
            if kwargs.get('move').get('due_date'):
                due_date = kwargs.get('move').get('due_date')

        debit, credit, amount_currency, currency_id = aml_obj.with_context(
            date=datetime.today())._compute_amount_fields(kwargs['amount'], kwargs['src_currency'],
                                                         company_currency,date,kwargs['move']['company_id'])
        cheque=kwargs.get('cheque')
        reservation_id=kwargs.get('reservation_id')

        check_payment_id=kwargs.get('check_payment_id')
        check_id=False

        if kwargs.get('move'):
            if  kwargs.get('move').get('reservation_id') :
                reservation_id=kwargs.get('move').get('reservation_id')
        if kwargs.get('move'):
            if  kwargs.get('move').get('check_id') :
                check_id=kwargs.get('move').get('check_id')
        if kwargs.get('move'):
            if  kwargs.get('move').get('cheque') :
                cheque=kwargs.get('move').get('cheque')
        if kwargs.get('move'):
            if  kwargs.get('move').get('check_payment_id') :
                check_payment_id=kwargs.get('move').get('check_payment_id')

        if check_payment_id:
            check_payment_id_rec=self.env['normal.payments'].sudo().browse(check_payment_id)
        else:
            check_payment_id_rec=False


        # debit, credit, amount_currency, currency_id = str(kwargs['amount'])
        move_vals = {
            'journal_id': kwargs['move']['journal_id'],
            'date': date,
            'ref': kwargs['move']['ref'],
            'company_id': kwargs['move']['company_id'],
            'cheque': cheque,
            'reservation_id':  reservation_id,
            'check_id':check_id,
            'check_payment_id': check_payment_id,
            'document_type_id':check_payment_id_rec.document_type_id.id if check_payment_id_rec else False,
            'external_document_number':check_payment_id_rec.external_document_number if check_payment_id_rec else "",
            'external_document_type':check_payment_id_rec.external_document_type if check_payment_id_rec else "",
            'customer_type_id':check_payment_id_rec.customer_type_id.id if check_payment_id_rec else False,
        }


        move = self.env['account.move'].with_context(check_move_validity=False).create(move_vals)


        for index in kwargs['debit_account']:
            debit_line_vals = {
                'account_id': index['account'],
                'partner_id': kwargs['move_line']['partner_id'],
                'debit': debit,
                'credit': credit,
                'amount_currency': amount_currency,
                'currency_id': currency_id,
                'date_maturity': due_date,
            }
            if index.get('analyitc_id'):
                debit_line_vals['analytic_distribution'] = {
                    index['analyitc_id']: 100,
                }
            # if 'analyitc_id' in index:
            #     debit_line_vals['analytic_account_id'] = index['analyitc_id']
            if 'jebal_pay_id' in kwargs['move_line']:
                debit_line_vals['jebal_pay_id'] =  kwargs['move_line']['jebal_pay_id']
            if 'jebal_check_id' in  kwargs['move_line']:
                debit_line_vals['jebal_check_id'] = kwargs['move_line']['jebal_check_id']
            if 'jebal_nrom_pay_id' in  kwargs['move_line']:
                debit_line_vals['jebal_nrom_pay_id'] = kwargs['move_line']['jebal_nrom_pay_id']
            if 'jebal_con_pay_id' in  kwargs['move_line']:
                debit_line_vals['jebal_con_pay_id'] = kwargs['move_line']['jebal_con_pay_id']
            debit_line_vals['move_id'] = move.id
            aml_obj.create(debit_line_vals)
            print("D>DD>1", debit_line_vals)

        for index in kwargs['credit_account']:
            credit_line_vals = {
                'account_id': index['account'],
                'partner_id': kwargs['move_line']['partner_id'],
                'debit': credit,
                'credit': debit,
                'amount_currency': -1 * amount_currency,
                'currency_id': currency_id,
                'date_maturity': due_date,
            }
            if index.get('analyitc_id'):
                credit_line_vals['analytic_distribution'] = {
                    index['analyitc_id']: 100,
                }
            # if 'analyitc_id' in index:
            #     credit_line_vals['analytic_account_id'] = index['analyitc_id']
            if 'jebal_pay_id' in kwargs['move_line']:
                credit_line_vals['jebal_pay_id'] =  kwargs['move_line']['jebal_pay_id']
            if 'jebal_check_id' in  kwargs['move_line']:
                credit_line_vals['jebal_check_id'] = kwargs['move_line']['jebal_check_id']
            if 'jebal_nrom_pay_id' in  kwargs['move_line']:
                credit_line_vals['jebal_nrom_pay_id'] = kwargs['move_line']['jebal_nrom_pay_id']

            if 'jebal_con_pay_id' in kwargs['move_line']:
                credit_line_vals['jebal_con_pay_id'] = kwargs['move_line']['jebal_con_pay_id']

            credit_line_vals['move_id'] = move.id
            aml_obj.create(credit_line_vals)
        move.action_post()
        return move
    def create_move_lines2(self, **kwargs):
        self.accounts_agg(**kwargs)
        self.adjust_move_percentage(**kwargs)
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        company_currency = self.env.company.currency_id
        date=kwargs.get('date')
        due_date=kwargs.get('due_date')
        company_id=kwargs.get('company_id')
        if kwargs.get('move'):
            if kwargs.get('move').get('company_id'):
                company_id = kwargs.get('move').get('company_id')

        if kwargs.get('move'):
            if kwargs.get('move').get('date'):
                date = kwargs.get('move').get('date')
        if kwargs.get('move'):
            if kwargs.get('move').get('due_date'):
                due_date = kwargs.get('move').get('due_date')
        print("D>D>D>Dwwwww",kwargs['src_currency'])
        debit, credit, amount_currency, currency_id = aml_obj.with_context(
            date=datetime.today())._compute_amount_fields(kwargs['amount'], kwargs['src_currency'],
                                                         company_currency,date,company_id)
        cheque=kwargs.get('cheque')
        reservation_id=kwargs.get('reservation_id')
        check_payment_id=kwargs.get('check_payment_id')
        check_id=False
        if kwargs.get('move'):
            if  kwargs.get('move').get('reservation_id') :
                reservation_id=kwargs.get('move').get('reservation_id')
        if kwargs.get('move'):
            if  kwargs.get('move').get('check_id') :
                check_id=kwargs.get('move').get('check_id')
        if kwargs.get('move'):
            if  kwargs.get('move').get('cheque') :
                cheque=kwargs.get('move').get('cheque')
        if kwargs.get('move'):
            if  kwargs.get('move').get('check_payment_id') :
                check_payment_id=kwargs.get('move').get('check_payment_id')



        if kwargs.get('check_payment_id'):
            if kwargs.get('move').get('check_payment_id'):
                check_payment_id = kwargs.get('move').get('check_payment_id')

        if check_payment_id:
            check_payment_id_rec = self.env['normal.payments'].sudo().browse(check_payment_id)
        else:
            check_payment_id_rec = False

        # debit, credit, amount_currency, currency_id = str(kwargs['amount'])
        print("D>D>D>D",kwargs['move'])
        move_vals = {
            'journal_id': kwargs['move']['journal_id'],
            'date': date,
            'ref': kwargs['move']['ref'],
            'company_id': company_id,
            'cheque': cheque,
            'reservation_id':  reservation_id,
            'check_id':check_id,
            'check_payment_id': check_payment_id,
            'document_type_id': check_payment_id_rec.document_type_id.id if check_payment_id_rec else False,
            'external_document_number': check_payment_id_rec.external_document_number if check_payment_id_rec else "",
            'external_document_type': check_payment_id_rec.external_document_type if check_payment_id_rec else "",
            'customer_type_id': check_payment_id_rec.customer_type_id.id if check_payment_id_rec else False,

        }

        move = self.env['account.move'].with_context(check_move_validity=False).create(move_vals)
        normal_payment=self.env['normal.payments'].browse(check_payment_id)



        for index in kwargs['debit_account']:
            debit_line_vals = {
                'account_id': index['account'],
                'partner_id': kwargs['move_line']['partner_id'],
                'debit': debit,
                'credit': credit,
                'amount_currency': amount_currency,
                'currency_id': currency_id,
                'date_maturity': due_date,
            }
            if index.get('analyitc_id'):
                debit_line_vals['analytic_distribution'] = {
                   index['analyitc_id']: 100,
                }
            # if 'analyitc_id' in index:
            #     debit_line_vals['analytic_account_id'] = index['analyitc_id']
            if 'jebal_pay_id' in kwargs['move_line']:
                debit_line_vals['jebal_pay_id'] =  kwargs['move_line']['jebal_pay_id']
            if 'jebal_check_id' in  kwargs['move_line']:
                debit_line_vals['jebal_check_id'] = kwargs['move_line']['jebal_check_id']
            if 'jebal_nrom_pay_id' in  kwargs['move_line']:
                debit_line_vals['jebal_nrom_pay_id'] = kwargs['move_line']['jebal_nrom_pay_id']
            if 'jebal_con_pay_id' in  kwargs['move_line']:
                debit_line_vals['jebal_con_pay_id'] = kwargs['move_line']['jebal_con_pay_id']
            debit_line_vals['move_id'] = move.id
            if normal_payment.multi_accounts and normal_payment.send_rec_money=='send':
                for mline in normal_payment.multi_account_ids:
                    debit_line_vals['account_id']=mline.account_id.id
                    debit_line_vals['partner_id']=mline.partner_id.id
                    debit_line_vals['name']=mline.label
                    debit_line_vals['debit']=mline.amount
                    debit_line_vals['amount_currency']=mline.amount
                    debit_line_vals['budget_company_id']=mline.budget_company_id.id
                    debit_line_vals['branch_id']=mline.branch_id.id
                    debit_line_vals['project_id']=mline.project_id.id
                    debit_line_vals['franchise_id']=mline.franchise_id.id
                    debit_line_vals['department_id']=mline.department_id.id
                    debit_line_vals['credit']=0
                    if mline.analyitc_id:
                        debit_line_vals['analytic_distribution']={
                            mline.analyitc_id.id: 100,
                        }
                    debit_line_vals['move_id'] = move.id
                    print(">D>D>D>",debit_line_vals)
                    aml_obj.create(debit_line_vals)
            else:
                debit_line_vals['move_id'] = move.id
                aml_obj.create(debit_line_vals)

        for index in kwargs['credit_account']:
            credit_line_vals = {
                'account_id': index['account'],
                'partner_id': kwargs['move_line']['partner_id'],
                'debit': credit,
                'credit': debit,
                'amount_currency': -1 * amount_currency,
                'currency_id': currency_id,
                'date_maturity': due_date,
            }
            if  index.get('analyitc_id'):
                credit_line_vals['analytic_distribution'] = {
                    index['analyitc_id']: 100,
                }
            # if 'analyitc_id' in index:
            #     credit_line_vals['analytic_account_id'] = index['analyitc_id']
            if 'jebal_pay_id' in kwargs['move_line']:
                credit_line_vals['jebal_pay_id'] =  kwargs['move_line']['jebal_pay_id']
            if 'jebal_check_id' in  kwargs['move_line']:
                credit_line_vals['jebal_check_id'] = kwargs['move_line']['jebal_check_id']
            if 'jebal_nrom_pay_id' in  kwargs['move_line']:
                credit_line_vals['jebal_nrom_pay_id'] = kwargs['move_line']['jebal_nrom_pay_id']

            if 'jebal_con_pay_id' in kwargs['move_line']:
                credit_line_vals['jebal_con_pay_id'] = kwargs['move_line']['jebal_con_pay_id']
            if normal_payment.multi_accounts and normal_payment.send_rec_money=='rece':
                for mline in normal_payment.multi_account_ids:
                    credit_line_vals['account_id']=mline.account_id.id
                    credit_line_vals['partner_id']=mline.partner_id.id
                    credit_line_vals['name']=mline.label
                    credit_line_vals['credit']=mline.amount
                    credit_line_vals['amount_currency']=-1*mline.amount
                    credit_line_vals['debit']=0
                    if mline.analyitc_id:
                        credit_line_vals['analytic_distribution'] = {
                            mline.analyitc_id.id: 100,
                        }
                    credit_line_vals['move_id'] = move.id
                    print(">D>D>D>", credit_line_vals)
                    aml_obj.create(credit_line_vals)
            else:
                credit_line_vals['move_id'] = move.id
                aml_obj.create(credit_line_vals)


        move.action_post()
        return move

    def adjust_move_percentage(self,**kwargs):
        # Debit
        tot_dens = 0.0
        tot_crds = 0.0
        for debs in kwargs['debit_account']:
            tot_dens+=debs['percentage']
        for crds in kwargs['credit_account']:
            tot_crds+=crds['percentage']
        percent = 100.0
        if tot_crds < 99 or tot_crds > 101:
            percent = tot_crds
        for i in range(len(kwargs['debit_account'])):
            kwargs['debit_account'][i]['percentage'] = round(kwargs['debit_account'][i]['percentage'],8)
        for index in kwargs['debit_account']:
            percent -= index['percentage']
        diff = 0.0
        if percent !=0.0:
            diff = percent / len(kwargs['debit_account'])
            for i in range(len(kwargs['debit_account'])):
                kwargs['debit_account'][i]['percentage'] +=diff
        #Credit
        percent = 100.0
        if tot_crds < 99 or tot_crds > 101:
            percent = tot_crds
        for i in range(len(kwargs['credit_account'])):
            kwargs['credit_account'][i]['percentage'] = round(kwargs['credit_account'][i]['percentage'], 8)
        for index in kwargs['credit_account']:
            percent -= index['percentage']
        diff = 0.0
        if percent != 0.0:
            diff = percent / len(kwargs['credit_account'])
            for i in range(len(kwargs['credit_account'])):
                kwargs['credit_account'][i]['percentage'] += diff

    def accounts_agg(self,**kwargs):
        all_crd_accs = {}
        for crd_accs in kwargs['credit_account']:
            if all_crd_accs and crd_accs['account'] in all_crd_accs:
                all_crd_accs[crd_accs['account']] += crd_accs['percentage']
            else:
                all_crd_accs[crd_accs['account']] = crd_accs['percentage']
        credit_account = []
        for acc_key in all_crd_accs:
            credit_account.append({'account': acc_key, 'percentage': all_crd_accs[acc_key]})
        kwargs['credit_account'] = credit_account
        all_crd_accs = {}
        for crd_accs in kwargs['debit_account']:
            if all_crd_accs and crd_accs['account'] in all_crd_accs:
                all_crd_accs[crd_accs['account']] += crd_accs['percentage']
            else:
                all_crd_accs[crd_accs['account']] = crd_accs['percentage']
        debit_account = []
        for acc_key in all_crd_accs:
            debit_account.append({'account': acc_key, 'percentage': all_crd_accs[acc_key]})
        kwargs['debit_account'] = debit_account
