# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo import models, api, _, _lt, fields
from odoo.tools.misc import format_date
from datetime import timedelta

from collections import defaultdict

class dePartnerLedgerExtended(models.AbstractModel):
    _inherit = 'account.partner.ledger'
    
    
    def _get_columns_name(self, options):
        if self.env.context.get('print_mode', False) == True:
            columns = [
            {},
            # {'name': _('JRNL')},
            # {'name': _('Account')},
            {'name': _('Ref')},
            # {'name': _('Due Date'), 'class': 'date'},
            # {'name': _('Matching Number')},
            # {'name': _('Initial Balance'), 'class': 'number'},
            {'name': _('Debit'), 'class': 'number'},
            {'name': _('Credit'), 'class': 'number'}]
        else:
            columns = [
                {},
                {'name': _('JRNL')},
                {'name': _('Account')},
                {'name': _('Ref')},
                {'name': _('Due Date'), 'class': 'date'},
                {'name': _('Matching Number')},
                {'name': _('Initial Balance'), 'class': 'number'},
                {'name': _('Debit'), 'class': 'number'},
                {'name': _('Credit'), 'class': 'number'}]

        if self.user_has_groups('base.group_multi_currency'):
            columns.append({'name': _('Amount Currency'), 'class': 'number'})

        columns.append({'name': _('Balance'), 'class': 'number'})

        return columns

    
    @api.model
    def _get_report_line_partner(self, options, partner, initial_balance, debit, credit, balance):
        company_currency = self.env.company.currency_id
        unfold_all = self._context.get('print_mode') and not options.get('unfolded_lines')
        if self.env.context.get('print_mode', False) == True:
            columns = [
                # {'name': self.format_value(initial_balance), 'class': 'number'},
                {'name': self.format_value(debit), 'class': 'number'},
                {'name': self.format_value(credit), 'class': 'number'},
            ]
            colspan = 2
            
        else:
            columns = [
                {'name': self.format_value(initial_balance), 'class': 'number'},
                {'name': self.format_value(debit), 'class': 'number'},
                {'name': self.format_value(credit), 'class': 'number'},
            ]   
            colspan= 6 
        if self.user_has_groups('base.group_multi_currency'):
            columns.append({'name': ''})
        columns.append({'name': self.format_value(balance), 'class': 'number'})

        res = {
            'id': 'partner_%s' % (partner.id if partner else 0),
            'name': partner is not None and (partner.name or '')[:128] or _('Unknown Partner'),
            'columns': columns,
            'level': 2,
            'trust': partner.trust if partner else None,
            'unfoldable': not company_currency.is_zero(debit) or not company_currency.is_zero(credit),
            'unfolded': 'partner_%s' % (partner.id if partner else 0) in options['unfolded_lines'] or unfold_all,
            'colspan': colspan,
        }
        return res

    
    @api.model
    def _get_report_line_move_line(self, options, partner, aml, cumulated_init_balance, cumulated_balance):
        if aml['payment_id']:
            caret_type = 'account.payment'
        elif aml['move_type'] in ('in_refund', 'in_invoice', 'in_receipt'):
            caret_type = 'account.invoice.in'
        elif aml['move_type'] in ('out_refund', 'out_invoice', 'out_receipt'):
            caret_type = 'account.invoice.out'
        else:
            caret_type = 'account.move'

        date_maturity = aml['date_maturity'] and format_date(self.env, fields.Date.from_string(aml['date_maturity']))
        if self.env.context.get('print_mode', False) == True:
            columns = [
                # {'name': aml['journal_code']},
                # {'name': aml['account_code']},
                {'name': self._format_aml_name(aml['name'], aml['ref'], aml['move_name'])},
                # {'name': date_maturity or '', 'class': 'date'},
                # {'name': aml['full_rec_name'] or ''},
                # {'name': self.format_value(cumulated_init_balance), 'class': 'number'},
                {'name': self.format_value(aml['debit'], blank_if_zero=True), 'class': 'number'},
                {'name': self.format_value(aml['credit'], blank_if_zero=True), 'class': 'number'},
            ]
        else:
            columns = [
                {'name': aml['journal_code']},
                {'name': aml['account_code']},
                {'name': self._format_aml_name(aml['name'], aml['ref'], aml['move_name'])},
                {'name': date_maturity or '', 'class': 'date'},
                {'name': aml['full_rec_name'] or ''},
                {'name': self.format_value(cumulated_init_balance), 'class': 'number'},
                {'name': self.format_value(aml['debit'], blank_if_zero=True), 'class': 'number'},
                {'name': self.format_value(aml['credit'], blank_if_zero=True), 'class': 'number'},
            ] 
        if self.user_has_groups('base.group_multi_currency'):
            if aml['currency_id']:
                currency = self.env['res.currency'].browse(aml['currency_id'])
                formatted_amount = self.format_value(aml['amount_currency'], currency=currency, blank_if_zero=True)
                columns.append({'name': formatted_amount, 'class': 'number'})
            else:
                columns.append({'name': ''})
        columns.append({'name': self.format_value(cumulated_balance), 'class': 'number'})
        return {
            'id': aml['id'],
            'parent_id': 'partner_%s' % (partner.id if partner else 0),
            'name': format_date(self.env, aml['date']),
            'class': 'date' + aml.get('class', ''),
            'columns': columns,
            'caret_options': caret_type,
            'level': 4,
        }

    @api.model
    def _get_report_line_total(self, options, initial_balance, debit, credit, balance):
        if self.env.context.get('print_mode', False) == True:
            columns = [
                # {'name': self.format_value(initial_balance), 'class': 'number'},
                {'name': self.format_value(debit), 'class': 'number'},
                {'name': self.format_value(credit), 'class': 'number'},
            ]
            colspan=2
        else:
            columns = [
                {'name': self.format_value(initial_balance), 'class': 'number'},
                {'name': self.format_value(debit), 'class': 'number'},
                {'name': self.format_value(credit), 'class': 'number'},
            ]   
            
            colspan=6
        if self.user_has_groups('base.group_multi_currency'):
            columns.append({'name': ''})
        columns.append({'name': self.format_value(balance), 'class': 'number'})
        return {
            'id': 'partner_ledger_total_%s' % self.env.company.id,
            'name': _('Total'),
            'class': 'total',
            'level': 1,
            'columns': columns,
            'colspan': colspan,
        }