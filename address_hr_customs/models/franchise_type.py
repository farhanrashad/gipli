# -*- coding: utf-8 -*-

from odoo import models, fields, api

class franchise_type(models.Model):
    _name = 'franchise.type'

    name=fields.Char('Name')

    @api.model
    def create(self, values):
        res=super(franchise_type, self).create(values)
        self.env['account.analytic.account'].sudo().create({
            'name':res.name,
            'code':"franchise",
            'franchise_id':res.id,
            'plan_id': self.env.ref('address_hr_customs.analytic_plan_projects_4').id,
        })
        return  res

    def write(self, values):
        res=super(franchise_type, self).write(values)
        for rec in self:
            analytic_account_id=self.env['account.analytic.account'].sudo().search([('franchise_id','=',rec.id)],limit=1)
            if analytic_account_id:
                analytic_account_id.write({
                    'name': rec.name,
                    'code': "franchise",
                    'plan_id': self.env.ref('address_hr_customs.analytic_plan_projects_4').id,

                })
        return res

    def unlink(self):
        analytic_account_id = self.env['account.analytic.account'].sudo().search([('franchise_id', '=', self.id)], limit=1)
        if analytic_account_id:
            analytic_account_id.sudo().unlink()
        return super(franchise_type, self).unlink()

class AccountAnalytic(models.Model):
    _inherit='account.analytic.account'
    franchise_id = fields.Many2one(comodel_name='franchise.type')
