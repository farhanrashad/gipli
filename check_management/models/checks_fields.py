# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions,_
import odoo.addons.decimal_precision as dp
from datetime import datetime
from datetime import timedelta
from odoo.fields import Date as fDate

class check_management(models.Model):

    _name = 'check.management'
    _description = 'Check'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name="check_number"

    check_number = fields.Char(string=_("Check Number"),required=True,default="0")
    from_check_number = fields.Char(string=_("From Check Number"),required=True,default="0")
    from_check_date = fields.Date(string=_("From Check Date"),required=False)
    check_date = fields.Date(string=_("Check Date"),required=False)
    check_payment_id = fields.Many2one('normal.payments', string=_('Check Payment'))
    payment_date = fields.Date(string="Payment Date", required=True, default=datetime.today(),related='check_payment_id.payment_date',store=True)
    deliver_to_customer_date = fields.Date(string="deliver to customer")
    reject_date = fields.Date(string="Reject Date")
    reject_reason = fields.Text(string="Rejection reason")


    old_payment_id_id = fields.Integer(compute='_calc_old_payment_id_url', store=True, string='Old Payment ID')
    old_payment_id_url = fields.Char(compute='_calc_old_payment_id_url', store=True, string='Old Payment Url')

    def _calc_old_payment_id_url(self):
        for rec in self:
            if rec.check_payment_id.old_payment_id:
                rec.old_payment_id_id = rec.check_payment_id.old_payment_id.id
                rec.old_payment_id_url = """https://themarq2020-themarq-test-13-master-9334849.dev.odoo.com/web#id={id}&action=173&model=account.payment&view_type=form&cids=14,1,2,3,9,10,11,12,13&menu_id=163""".format(
                    id=rec.check_payment_id.old_payment_id.id)
            else:
                rec.old_payment_id_id = 0
                rec.old_payment_id_url = ''

    check_bank = fields.Many2one('payment.bank', string=_('Check Bank'))
    dep_bank = fields.Many2one('payment.bank', string=_('Depoist Bank'))
    amount = fields.Float(string=_('Check Amount'),digits=dp.get_precision('Product Price'))

    amount_reg = fields.Float(string="Check Regular Amount", digits=dp.get_precision('Product Price'))


    open_amount_reg = fields.Float(string="Check Regular Open Amount", digits=dp.get_precision('Product Price'))

    open_amount = fields.Float(string=_('Open Amount'), digits=dp.get_precision('Product Price'),track_visibility='onchange')
    investor_id = fields.Many2one('res.partner',string=_("Partner"))
    currency_id = fields.Many2one(comodel_name="res.currency")






    type = fields.Selection(string="Type", selection=[('reservation', 'Reservation instalment'),
                                                      ('contracting', 'Contracting instalment'),
                                                      ('regular', 'Regular instalment'),
                                                      ('ser', 'Services instalment'),
                                                      ('garage', 'Garage instalment'),
                                                      ('mod', 'Modification instalment'),
                                                      ], required=True,
                            default="regular")
    state = fields.Selection(selection=[('holding','Posted'),('depoisted','Under collection'),
                                         ('approved','Withdrawal'),
                                        ('rejected','Rejected'),
                                        ('send_to_lagel', 'Send To Legal'),
                                        ('deliver', 'Deliver'),
                                        ('refund_deliver', 'Refund Deliver'),
                                        ('refund', 'Refund'),
                                        ('refund_send_to_lagel','Refund Send To Legal')
                                         , ('returned', 'Refund Under collection'), ('handed', 'Handed'),
                                        ('debited', 'Withdrawal Payable'),
                                        ('canceled', 'Canceled'),
                                        ('cs_return','Refund Notes Receivable'),
                                        ('payment_cancel','Payment Canceled'),
                                        ('payment_draft','Payment Draft'),
                                        ('delivery_to_customer', 'Delivery To Customer'),

                                        ]
                            ,track_visibility='onchange')

    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)


    notes_rece_id = fields.Many2one('account.account')
    under_collect_id  = fields.Many2one('account.account')
    notespayable_id = fields.Many2one('account.account')
    under_collect_jour = fields.Many2one('account.journal')
    check_type = fields.Selection(selection=[('rece','Notes Receivable'),('pay','Notes Payable')])
    check_state = fields.Selection(selection=[('active','Active'),('suspended','Suspended')],default='active')
    check_from_check_man = fields.Boolean(string="Check Managment",default=False)
    #will_collection = fields.Date(string="Maturity Date" , compute = "_compute_days")
    will_collection_user = fields.Date(string="Bank Maturity Date"  ,track_visibility='onchange')
    reservation_id = fields.Many2one(comodel_name="res.reservation", string="Reservation", required=False, readonly=False,related='check_payment_id.reservation_id',store=True)
    custoemr_payment_id = fields.Many2one(comodel_name="customer.payment", string="Customer Payment", required=False,
                                          readonly=True,related='check_payment_id.custoemr_payment_id',store=True)
    property_id = fields.Many2one(related="reservation_id.property_id", comodel_name="product.product", string="Unit",
                                required=False, store=True, readonly=False)

    request_reservation_id = fields.Many2one(comodel_name="request.reservation", string="Request Reservation",
                                             required=False, readonly=False,related='check_payment_id.request_reservation_id',store=True)
    payment_method = fields.Many2one(comodel_name="account.journal", string="Payment Journal", related ='check_payment_id.payment_method', store = True)
    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner Name", related ='check_payment_id.partner_id', store = True)
    receipt_number = fields.Char(string="Reference", related ='check_payment_id.receipt_number', store = True)
    customer_type_id = fields.Many2one(comodel_name="customer.types", string="Customer Type",related ='check_payment_id.customer_type_id',store=True)




    send_to_lagel_move_id = fields.Many2one(
        comodel_name='account.move',
        string='Send To Legal',
        required=False)

    handed_move_id = fields.Many2one(
        comodel_name='account.move',
        string='Handed Move',
        required=False)

    depoist_move_id = fields.Many2one(
        comodel_name='account.move',
        string='Depoist Move',
        required=False)

    deliver_move_id = fields.Many2one(
        comodel_name='account.move',
        string='deliver Move',
        required=False)

    amount_paid = fields.Float(string='Amount Paid',compute='_calc_amount_paid',store=False)
    amount_due = fields.Float(string='Amount Due',compute='_calc_amount_paid',store=False)
    is_split = fields.Boolean(string='Is Split')
    batch = fields.Char(
        string='Batch', 
        required=False)

    @api.depends('check_payment_id','amount')
    def _calc_amount_paid(self):
        for rec in self:
            payments=self.env['normal.payments'].search([('parent_payment_id','=',rec.check_payment_id.id)])
            rec.amount_paid=sum(payments.mapped('amount'))
            rec.amount_due=rec.amount- rec.amount_paid





    def button_journal_entries(self):
        return {
            'name': _('Journal Items'),
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': ['|',('move_id.check_id', 'in', self.ids),('jebal_con_pay_id', 'in', self.check_payment_id.ids)],
        }

    # @api.multi
    # def _compute_days(self):
    #     d1=datetime.strptime(str(self.check_date),'%Y-%m-%d')
    #     self.will_collection= d1 + timedelta(days=10)



    @api.model
    def create(self,vals):
        if 'amount' in vals:
            vals['open_amount'] = vals['amount']
        return super(check_management,self).create(vals)

    # @api.multi
    def write(self, vals):
        for rec in self:
            if 'amount' in vals:
                rec.open_amount = vals['amount']
        return super(check_management, self).write(vals)




    @api.model
    def get_views(self, views, options=None):
        res = super().get_views(views, options)
        menus=[]
        if 'menu_sent' in self.env.context:
            if options.get('toolbar'):
                for view_type in res['views']:
                    if self.env.context['menu_sent'] == 'handed':
                        for  menu in res['views'][view_type]['toolbar'].get('action',[]):
                            if menu['name'] not in ['Deliver To Customer','Send To Legal','Depoist Checks','Customer Return','Refund Deliver','Withdrawal Payable Checks','Cancel Checks','Reject Checks','Split','Reject Checks', 'Company Return', 'Approve Checks','Split-Merge','Refund Send To Legal']:
                                menus.append(menu)
                            if menus:
                                res['views'][view_type]['toolbar']['action']=menus
                    if self.env.context['menu_sent'] == 'cs_return':
                        for  menu in res['views'][view_type]['toolbar'].get('action',[]):
                            if menu['name'] not in ['Refund Deliver','Withdrawal Payable Checks','Refund','Send To Legal','Depoist Checks','Customer Return','Deliver','Cancel Checks','Reject Checks','Split','Reject Checks', 'Company Return', 'Approve Checks','Split-Merge','Refund Send To Legal']:
                                menus.append(menu)
                            if menus:
                                res['views'][view_type]['toolbar']['action']=menus
                    if self.env.context['menu_sent'] == 'deliver':
                        for  menu in res['views'][view_type]['toolbar'].get('action',[]):
                            if menu['name'] not in ['Deliver To Customer','Refund','Send To Legal','Depoist Checks','Customer Return','Deliver','Cancel Checks','Reject Checks','Split','Reject Checks', 'Company Return', 'Approve Checks','Split-Merge','Refund Send To Legal']:
                                menus.append(menu)
                            if menus:
                                res['views'][view_type]['toolbar']['action']=menus
                    if self.env.context['menu_sent'] == 'refund_deliver':
                        for  menu in res['views'][view_type]['toolbar'].get('action',[]):

                            if menu['name'] not in [  'Deliver To Customer','Withdrawal Payable Checks','Refund Deliver','Send To Legal', 'Depoist Checks', 'Customer Return',
                                                     'Cancel Checks', 'Reject Checks', 'Split', 'Reject Checks',
                                                    'Company Return', 'Approve Checks', 'Split-Merge',
                                                    'Refund Send To Legal']:
                                menus.append(menu)
                        if menus:
                            res['views'][view_type]['toolbar']['action'] = menus
                    if self.env.context['menu_sent'] == 'debited':
                        for  menu in res['views'][view_type]['toolbar'].get('action',[]):
                            res['views'][view_type]['toolbar']['action']=menus
                    if self.env.context['menu_sent'] == 'refund':
                        for  menu in res['views'][view_type]['toolbar'].get('action',[]):
                            res['views'][view_type]['toolbar']['action']=menus
                    if self.env.context['menu_sent'] == 'holding':
                        for  menu in res['views'][view_type]['toolbar'].get('action',[]):
                            if menu['name'] not in ['Deliver To Customer','Withdrawal Payable Checks','Refund','Reject Checks', 'Company Return', 'Approve Checks','Split-Merge','Refund Send To Legal','Deliver','Refund Deliver']:
                                menus.append(menu)
                            if menus:
                                res['views'][view_type]['toolbar']['action']=menus
                    if self.env.context['menu_sent'] == 'depoist':
                        for  menu in res['views'][view_type]['toolbar'].get('action',[]):
                            if menu['name'] not in ['Deliver To Customer','Refund','Split','Deliver','Refund Deliver','Company Return', 'Withdrawal Payable Checks','Split-Merge','Customer Return','Depoist Checks','Cancel Checks','Send To Legal','Refund Send To Legal']:
                                menus.append(menu)
                            if menus:
                                res['views'][view_type]['toolbar']['action']=menus
                    if self.env.context['menu_sent'] == 'rejected':
                        for  menu in res['views'][view_type]['toolbar'].get('action',[]):
                            if menu['name'] not in ['Deliver To Customer','Refund','Split','Deliver','Refund Deliver','Reject Checks','Split-Merge','Customer Return','Cancel Checks','Withdrawal Payable Checks','Send To Legal','Refund Send To Legal']:
                                menus.append(menu)
                            if menus:
                                res['views'][view_type]['toolbar']['action']=menus
                    if self.env.context['menu_sent'] == 'send_to_lagel':
                        for  menu in res['views'][view_type]['toolbar'].get('action',[]):
                            if menu['name'] not in ['Deliver To Customer','Customer Return','Depoist Checks','Split-Merge','Refund','Reject Checks','Deliver','Refund Deliver','Cancel Checks','Withdrawal Payable Checks','Company Return', 'Approve Checks','Send To Legal']:
                                menus.append(menu)
                            if menus:
                                res['views'][view_type]['toolbar']['action']=menus
                    if self.env.context['menu_sent'] == 'refund_send_to_lagel':
                        for  menu in res['views'][view_type]['toolbar'].get('action',[]):
                            if menu['name'] not in ['Deliver To Customer','Refund Send To Legal','Split-Merge','Refund','Deliver','Reject Checks','Refund Deliver','Cancel Checks','Withdrawal Payable Checks','Company Return', 'Approve Checks','Send To Legal']:
                                menus.append(menu)
                            if menus:
                                res['views'][view_type]['toolbar']['action']=menus
                    if self.env.context['menu_sent'] == 'returned':
                        for  menu in res['views'][view_type]['toolbar'].get('action',[]):
                            if menu['name'] not in ['Deliver To Customer','Refund','Reject Checks','Deliver','Refund Deliver','Split-Merge','Company Return',
                                                    'Cancel Checks','Withdrawal Payable Checks','Approve Checks','Refund Send To Legal']:
                                menus.append(menu)
                            if menus:
                                res['views'][view_type]['toolbar']['action']=menus
                    if self.env.context['menu_sent'] in  ['approved','canceled','delivery_to_customer']:
                        res['views'][view_type]['toolbar']['action'] = menus



        return res

    def action_cancel(self):
        self.check_payment_id.action_cancel()

    def action_reset_draft(self):
        self.check_payment_id.action_reset_draft()





